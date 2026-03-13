"""
Submission routes for managing form submissions
"""
from flask import Blueprint, request, jsonify, send_file, current_app
import os

from models import db, FormSubmission, OCRResult
from services.upload_service import UploadService
from services.ocr_service import OCRService

submission_bp = Blueprint('submissions', __name__)


@submission_bp.route('/', methods=['GET'])
def get_submissions():
    """
    Get submissions with optional filtering

    Query params:
        - status: Filter by processing_status
        - ocr_status: Filter by ocr_status
        - validation_status: Filter by validation_status
        - batch_id: Filter by batch ID
        - limit: Max number of results (default: 50)
        - offset: Pagination offset (default: 0)
    """
    # Get query parameters
    processing_status = request.args.get('status')
    ocr_status = request.args.get('ocr_status')
    validation_status = request.args.get('validation_status')
    batch_id = request.args.get('batch_id')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Build query
    query = FormSubmission.query

    if processing_status:
        query = query.filter_by(processing_status=processing_status)
    if ocr_status:
        query = query.filter_by(ocr_status=ocr_status)
    if validation_status:
        query = query.filter_by(validation_status=validation_status)
    if batch_id:
        query = query.filter_by(submission_batch_id=batch_id)

    # Get total count
    total = query.count()

    # Apply pagination
    submissions = query.limit(limit).offset(offset).all()

    return jsonify({
        'submissions': [s.to_dict() for s in submissions],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@submission_bp.route('/<int:submission_id>', methods=['GET'])
def get_submission(submission_id):
    """
    Get a single submission by ID with full details
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    return jsonify({
        'submission': submission.to_dict(include_images=True, include_ocr=True)
    }), 200


@submission_bp.route('/<int:submission_id>/images', methods=['GET'])
def get_submission_images(submission_id):
    """
    Get images for a submission
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    images = submission.images.all()

    return jsonify({
        'images': [img.to_dict() for img in images],
        'count': len(images)
    }), 200


@submission_bp.route('/<int:submission_id>/image/<int:image_id>', methods=['GET'])
def serve_image(submission_id, image_id):
    """
    Serve an image file
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    image = next((img for img in submission.images if img.id == image_id), None)

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    if not os.path.exists(image.image_path):
        return jsonify({'error': 'Image file not found on disk'}), 404

    # Detect mimetype from file extension
    import mimetypes
    mimetype, _ = mimetypes.guess_type(image.image_path)
    if not mimetype:
        mimetype = 'image/jpeg'  # Fallback

    return send_file(image.image_path, mimetype=mimetype)


@submission_bp.route('/<int:submission_id>/ocr', methods=['GET'])
def get_ocr_results(submission_id):
    """
    Get OCR results for a submission
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    ocr_service = OCRService()
    ocr_results = ocr_service.get_ocr_result(submission_id)

    return jsonify({
        'ocr_results': [r.to_dict() for r in ocr_results],
        'count': len(ocr_results),
        'combined_text': ocr_service.get_ocr_text(submission_id)
    }), 200


@submission_bp.route('/<int:submission_id>/extracted-fields', methods=['GET'])
def get_extracted_fields(submission_id):
    """
    Get extracted fields for a submission
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    # Get OCR results
    ocr_results = submission.ocr_results.all()

    if not ocr_results:
        return jsonify({'error': 'No OCR results found'}), 404

    # Get field extractions from first OCR result
    import json
    extracted_fields = json.loads(ocr_results[0].field_extractions) if ocr_results[0].field_extractions else {}

    return jsonify({
        'submission_id': submission_id,
        'extracted_fields': extracted_fields
    }), 200


@submission_bp.route('/<int:submission_id>/status', methods=['PUT'])
def update_status(submission_id):
    """
    Update submission status

    Request body:
        - processing_status: optional
        - ocr_status: optional
        - validation_status: optional
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update allowed fields
    allowed_fields = ['processing_status', 'ocr_status', 'validation_status']

    for field in allowed_fields:
        if field in data:
            setattr(submission, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Status updated successfully',
        'submission': submission.to_dict()
    }), 200


@submission_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get submission statistics
    """
    total = FormSubmission.query.count()
    pending_processing = FormSubmission.query.filter_by(processing_status='pending').count()
    pending_ocr = FormSubmission.query.filter_by(processing_status='completed', ocr_status='pending').count()
    pending_validation = FormSubmission.query.filter_by(ocr_status='completed', validation_status='pending').count()
    completed = FormSubmission.query.filter_by(validation_status='completed').count()

    return jsonify({
        'total_submissions': total,
        'pending_processing': pending_processing,
        'pending_ocr': pending_ocr,
        'pending_validation': pending_validation,
        'completed': completed
    }), 200
