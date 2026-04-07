"""
Upload routes for file upload and processing
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from sqlalchemy import exists, or_
from models import db, FormSubmission, OCRResult
from services.upload_service import UploadService
from services.ocr_service import OCRService
from services.field_extraction import FieldExtractionService
from utils.file_utils import allowed_file

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/', methods=['POST'])
def upload_files():
    """
    Upload files endpoint

    Accepts multipart/form-data with files
    Form data:
        - files: List of files to upload
        - split_pdf_pages: (optional) 'true' to split multi-page PDFs into separate submissions

    Returns batch_id and submission details
    """
    # Check if files are in request
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')

    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400

    # Get split_pdf_pages option (default: False)
    split_pdf_pages = request.form.get('split_pdf_pages', 'false').lower() == 'true'

    # Validate file types
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    invalid_files = []

    for file in files:
        if file.filename == '':
            invalid_files.append('Empty filename')
        elif not allowed_file(file.filename, allowed_extensions):
            invalid_files.append(f'{file.filename} - Invalid file type')

    if invalid_files:
        return jsonify({
            'error': 'Invalid files',
            'details': invalid_files
        }), 400

    # Process upload
    upload_service = UploadService(
        current_app.config['UPLOAD_FOLDER'],
        allowed_extensions
    )

    try:
        result = upload_service.process_upload(files, split_pdf_pages=split_pdf_pages)

        return jsonify({
            'message': 'Files uploaded successfully',
            'batch_id': result['batch_id'],
            'submissions': result['submissions'],
            'errors': result['errors'],
            'success_count': len(result['submissions']),
            'error_count': len(result['errors'])
        }), 200

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@upload_bp.route('/process-ocr/<int:submission_id>', methods=['POST'])
def process_ocr(submission_id):
    """
    Trigger OCR processing for a submission

    Args:
        submission_id: ID of the submission to process

    Returns:
        OCR results
    """
    # Get submission
    upload_service = UploadService(
        current_app.config['UPLOAD_FOLDER'],
        current_app.config['ALLOWED_EXTENSIONS']
    )

    submission = upload_service.get_submission(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    if submission.processing_status != 'completed':
        return jsonify({'error': 'Submission not ready for OCR (file processing incomplete)'}), 400

    # Process with OCR
    ocr_service = OCRService()
    ocr_result = ocr_service.process_submission(submission)

    if not ocr_result['success']:
        return jsonify({
            'error': 'OCR processing failed',
            'details': ocr_result['error']
        }), 500

    # Extract fields
    field_service = FieldExtractionService()
    fields = field_service.process_submission(submission)

    return jsonify({
        'message': 'OCR processing completed',
        'submission_id': submission_id,
        'ocr_result_ids': ocr_result['ocr_result_ids'],
        'extracted_fields': fields
    }), 200


def _failed_ocr_query():
    """
    Returns a query for all submissions that need OCR retry:
    - ocr_status='error', OR
    - ocr_status='completed' but no OCR result rows (orphaned by a billing failure)
    """
    has_ocr_results = exists().where(OCRResult.submission_id == FormSubmission.id)
    return FormSubmission.query.filter(
        or_(
            FormSubmission.ocr_status == 'error',
            (FormSubmission.ocr_status == 'completed') & ~has_ocr_results
        )
    )


@upload_bp.route('/failed-ocr', methods=['GET'])
def get_failed_ocr():
    """
    Get submissions where OCR failed or completed without results (orphaned).
    """
    submissions = _failed_ocr_query().order_by(FormSubmission.uploaded_at.desc()).all()

    return jsonify({
        'submissions': [s.to_dict(include_images=True) for s in submissions],
        'count': len(submissions)
    }), 200


@upload_bp.route('/reset-failed-ocr', methods=['POST'])
def reset_failed_ocr():
    """
    Reset OCR-failed and orphaned submissions back to pending so they can be retried.

    Request body (optional):
        { "submission_ids": [1, 2, 3] }  — reset specific IDs only
        Omit to reset all failed/orphaned submissions.
    """
    data = request.get_json(silent=True) or {}
    submission_ids = data.get('submission_ids')

    query = _failed_ocr_query()
    if submission_ids:
        query = query.filter(FormSubmission.id.in_(submission_ids))

    submissions = query.all()

    for submission in submissions:
        submission.ocr_status = 'pending'
        submission.error_message = None

    db.session.commit()

    return jsonify({
        'message': f'Reset {len(submissions)} submission(s) for OCR retry',
        'count': len(submissions)
    }), 200


@upload_bp.route('/batch/<batch_id>', methods=['GET'])
def get_batch(batch_id):
    """
    Get all submissions for a batch

    Args:
        batch_id: Batch ID

    Returns:
        List of submissions
    """
    upload_service = UploadService(
        current_app.config['UPLOAD_FOLDER'],
        current_app.config['ALLOWED_EXTENSIONS']
    )

    submissions = upload_service.get_submissions_by_batch(batch_id)

    return jsonify({
        'batch_id': batch_id,
        'submissions': [s.to_dict(include_images=True) for s in submissions],
        'count': len(submissions)
    }), 200


@upload_bp.route('/pending', methods=['GET'])
def get_pending():
    """
    Get pending submissions that need OCR processing

    Returns:
        List of pending submissions
    """
    limit = request.args.get('limit', 50, type=int)

    upload_service = UploadService(
        current_app.config['UPLOAD_FOLDER'],
        current_app.config['ALLOWED_EXTENSIONS']
    )

    submissions = upload_service.get_pending_submissions(limit=limit)

    return jsonify({
        'submissions': [s.to_dict() for s in submissions],
        'count': len(submissions)
    }), 200
