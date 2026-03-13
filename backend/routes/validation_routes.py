"""
Validation routes for reviewing and correcting OCR-extracted data
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import json

from models import db, FormSubmission, Member, ValidationCorrection, OCRResult
from services.field_extraction import FieldExtractionService
from services.duplicate_detection_service import DuplicateDetectionService
from services.address_validation_service import AddressValidationService

validation_bp = Blueprint('validation', __name__)
duplicate_service = DuplicateDetectionService()
address_validation_service = AddressValidationService()


@validation_bp.route('/pending', methods=['GET'])
def get_pending_validations():
    """
    Get submissions pending validation

    Query params:
        - limit: Max number of results (default: 20)
        - offset: Pagination offset (default: 0)
    """
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Get submissions with completed OCR but pending validation
    query = FormSubmission.query.filter_by(
        ocr_status='completed',
        validation_status='pending'
    ).order_by(FormSubmission.uploaded_at.desc())

    total = query.count()
    submissions = query.limit(limit).offset(offset).all()

    return jsonify({
        'submissions': [s.to_dict(include_images=True) for s in submissions],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@validation_bp.route('/<int:submission_id>', methods=['GET'])
def get_validation_data(submission_id):
    """
    Get submission with extracted fields for validation
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    # Get extracted fields
    field_service = FieldExtractionService()

    # Check if fields are already extracted
    ocr_results = submission.ocr_results.all()

    if not ocr_results:
        return jsonify({'error': 'No OCR results found'}), 404

    # If no field extractions exist, extract them now
    if not ocr_results[0].field_extractions:
        extracted_fields = field_service.process_submission(submission)
    else:
        extracted_fields = json.loads(ocr_results[0].field_extractions)

    # Get images
    images = submission.images.all()

    # Get any existing corrections
    corrections = submission.corrections.all()

    # Check for potential duplicates
    potential_duplicates = []
    try:
        # Extract just the values from extracted_fields for duplicate checking
        field_values = {}
        for field_name, field_data in extracted_fields.items():
            if isinstance(field_data, dict) and 'value' in field_data:
                field_values[field_name] = field_data['value']
            elif field_name not in ['extraction_timestamp', 'overall_confidence']:
                field_values[field_name] = field_data

        potential_duplicates = duplicate_service.find_duplicates(
            extracted_fields=field_values,
            submission_id=submission_id,
            limit=5
        )
    except Exception as e:
        print(f"Error checking for duplicates: {e}")
        import traceback
        traceback.print_exc()

    return jsonify({
        'submission': submission.to_dict(include_images=True, include_ocr=True),
        'extracted_fields': extracted_fields,
        'images': [img.to_dict() for img in images],
        'corrections': [c.to_dict() for c in corrections],
        'potential_duplicates': potential_duplicates
    }), 200


@validation_bp.route('/<int:submission_id>/save', methods=['POST'])
def save_validation(submission_id):
    """
    Save validated/corrected field values

    Request body:
        {
            "fields": {
                "first_name": "value",
                "last_name": "value",
                "address_line1": "value",
                ...
            }
        }
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    data = request.get_json()

    if not data or 'fields' not in data:
        return jsonify({'error': 'No fields provided'}), 400

    validated_fields = data['fields']

    # Get original extracted fields
    ocr_results = submission.ocr_results.all()

    if not ocr_results or not ocr_results[0].field_extractions:
        return jsonify({'error': 'No extracted fields found'}), 404

    original_fields = json.loads(ocr_results[0].field_extractions)

    # Track corrections
    corrections_made = []

    for field_name, new_value in validated_fields.items():
        # Get original value
        original_field = original_fields.get(field_name, {})
        original_value = original_field.get('value', '') if isinstance(original_field, dict) else ''

        # If value changed, record correction
        if str(new_value) != str(original_value):
            # Check if correction already exists
            existing_correction = ValidationCorrection.query.filter_by(
                submission_id=submission_id,
                field_name=field_name
            ).first()

            if existing_correction:
                # Update existing correction
                existing_correction.ocr_value = original_value
                existing_correction.corrected_value = new_value
                existing_correction.corrected_at = datetime.utcnow()
            else:
                # Create new correction
                correction = ValidationCorrection(
                    submission_id=submission_id,
                    field_name=field_name,
                    ocr_value=original_value,
                    corrected_value=new_value
                )
                db.session.add(correction)

            corrections_made.append(field_name)

    # Update submission status
    submission.validation_status = 'in_progress'

    db.session.commit()

    return jsonify({
        'message': 'Validation saved successfully',
        'corrections_made': corrections_made,
        'submission': submission.to_dict()
    }), 200


@validation_bp.route('/<int:submission_id>/complete', methods=['POST'])
def complete_validation(submission_id):
    """
    Complete validation and create member record

    Request body:
        {
            "fields": {
                "first_name": "value",
                "last_name": "value",
                ...
            },
            "create_member": true/false (default: true)
        }
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    data = request.get_json()

    if not data or 'fields' not in data:
        return jsonify({'error': 'No fields provided'}), 400

    validated_fields = data['fields']
    create_member = data.get('create_member', True)

    # Save any corrections first
    ocr_results = submission.ocr_results.all()

    if ocr_results and ocr_results[0].field_extractions:
        original_fields = json.loads(ocr_results[0].field_extractions)

        for field_name, new_value in validated_fields.items():
            original_field = original_fields.get(field_name, {})
            original_value = original_field.get('value', '') if isinstance(original_field, dict) else ''

            if str(new_value) != str(original_value):
                existing_correction = ValidationCorrection.query.filter_by(
                    submission_id=submission_id,
                    field_name=field_name
                ).first()

                if existing_correction:
                    existing_correction.corrected_value = new_value
                    existing_correction.corrected_at = datetime.utcnow()
                else:
                    correction = ValidationCorrection(
                        submission_id=submission_id,
                        field_name=field_name,
                        ocr_value=original_value,
                        corrected_value=new_value
                    )
                    db.session.add(correction)

    # Create member record if requested
    member = None
    if create_member:
        # Parse date of birth
        dob = None
        if validated_fields.get('date_of_birth'):
            try:
                dob = datetime.strptime(validated_fields['date_of_birth'], '%Y-%m-%d').date()
            except:
                pass

        # Create member
        member = Member(
            first_name=validated_fields.get('first_name', ''),
            last_name=validated_fields.get('last_name', ''),
            full_name=validated_fields.get('full_name', ''),
            address_line1=validated_fields.get('address_line1', ''),
            address_line2=validated_fields.get('address_line2', ''),
            city=validated_fields.get('city', ''),
            state=validated_fields.get('state', ''),
            postal_code=validated_fields.get('postal_code', ''),
            phone_primary=validated_fields.get('phone_primary', ''),
            email=validated_fields.get('email', ''),
            date_of_birth=dob,
            date_joined=datetime.utcnow().date(),
            membership_status='active'
        )

        db.session.add(member)
        db.session.flush()  # Get member ID

        # Link submission to member
        submission.member_id = member.id

    # Update submission status
    submission.validation_status = 'completed'
    submission.validated_at = datetime.utcnow()

    db.session.commit()

    response = {
        'message': 'Validation completed successfully',
        'submission': submission.to_dict()
    }

    if member:
        response['member'] = member.to_dict()

    return jsonify(response), 200


@validation_bp.route('/<int:submission_id>/skip', methods=['POST'])
def skip_validation(submission_id):
    """
    Skip validation for this submission (mark as pending for later)
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    # Just keep it as pending, no changes needed
    return jsonify({
        'message': 'Submission skipped',
        'submission': submission.to_dict()
    }), 200


@validation_bp.route('/<int:submission_id>/reject', methods=['POST'])
def reject_validation(submission_id):
    """
    Reject/discard an invalid submission

    Request body (optional):
        {
            "reason": "Description of why the submission was rejected"
        }
    """
    submission = FormSubmission.query.get(submission_id)

    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    data = request.get_json() or {}
    reason = data.get('reason', '')

    # Mark submission as rejected
    submission.validation_status = 'rejected'
    submission.validated_at = datetime.utcnow()

    # Optionally store rejection reason in notes or a new field
    # For now, we'll just mark it as rejected

    db.session.commit()

    return jsonify({
        'message': 'Submission rejected successfully',
        'submission': submission.to_dict()
    }), 200


@validation_bp.route('/stats', methods=['GET'])
def get_validation_stats():
    """
    Get validation statistics
    """
    total_pending = FormSubmission.query.filter_by(
        ocr_status='completed',
        validation_status='pending'
    ).count()

    in_progress = FormSubmission.query.filter_by(
        validation_status='in_progress'
    ).count()

    completed = FormSubmission.query.filter_by(
        validation_status='completed'
    ).count()

    rejected = FormSubmission.query.filter_by(
        validation_status='rejected'
    ).count()

    return jsonify({
        'pending': total_pending,
        'in_progress': in_progress,
        'completed': completed,
        'rejected': rejected,
        'total': total_pending + in_progress + completed + rejected
    }), 200


@validation_bp.route('/validate-address', methods=['POST'])
def validate_address():
    """
    Validate an address using Google Maps Geocoding API

    Request body:
        {
            "address_line1": "123 Main St",
            "address_line2": "Apt 4",
            "city": "Springfield",
            "state": "IL",
            "postal_code": "62701"
        }

    Response:
        {
            "is_valid": true,
            "formatted_address": "123 Main St Apt 4, Springfield, IL 62701, USA",
            "confidence": "high",
            "is_exact_match": true,
            "location": {"lat": 39.7817, "lng": -89.6501},
            "address_components": {...},
            "suggestions": {...}
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    address_line1 = data.get('address_line1', '').strip()
    address_line2 = data.get('address_line2', '').strip()
    city = data.get('city', '').strip()
    state = data.get('state', '').strip()
    postal_code = data.get('postal_code', '').strip()

    # Validate at least street address and city are provided
    if not address_line1 or not city:
        return jsonify({
            'error': 'Street address and city are required',
            'is_valid': False
        }), 400

    # Call validation service
    result = address_validation_service.validate_address(
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code
    )

    return jsonify(result), 200
