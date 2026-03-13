"""
Upload routes for file upload and processing
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

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
