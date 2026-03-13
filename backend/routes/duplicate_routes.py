"""
Duplicate detection routes for finding and managing duplicate members
"""
from flask import Blueprint, request, jsonify

from services.duplicate_detection_service import DuplicateDetectionService
from models import DuplicateCandidate, db

duplicate_bp = Blueprint('duplicates', __name__)
duplicate_service = DuplicateDetectionService()


@duplicate_bp.route('/check', methods=['POST'])
def check_duplicates():
    """
    Check for potential duplicate members based on extracted fields

    Request body:
        - extracted_fields: Dictionary of extracted field values
        - submission_id: Optional submission ID
        - threshold: Optional custom similarity threshold (default: 70)
        - limit: Maximum number of duplicates to return (default: 10)

    Returns:
        List of potential duplicate members with similarity scores
    """
    data = request.get_json()

    if not data or 'extracted_fields' not in data:
        return jsonify({'error': 'extracted_fields is required'}), 400

    extracted_fields = data['extracted_fields']
    submission_id = data.get('submission_id')
    limit = data.get('limit', 10)

    try:
        # Find potential duplicates
        duplicates = duplicate_service.find_duplicates(
            extracted_fields,
            submission_id=submission_id,
            limit=limit
        )

        return jsonify({
            'duplicates': duplicates,
            'count': len(duplicates)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@duplicate_bp.route('/create', methods=['POST'])
def create_duplicate_candidate():
    """
    Create a duplicate candidate record

    Request body:
        - submission_id: ID of the submission being validated
        - existing_member_id: ID of the potentially duplicate member
        - similarity_data: Dictionary with similarity scores and matched fields

    Returns:
        Created duplicate candidate
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    required_fields = ['submission_id', 'existing_member_id', 'similarity_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    try:
        duplicate_candidate = duplicate_service.create_duplicate_candidate(
            submission_id=data['submission_id'],
            existing_member_id=data['existing_member_id'],
            similarity_data=data['similarity_data']
        )

        return jsonify({
            'message': 'Duplicate candidate created successfully',
            'duplicate': duplicate_candidate.to_dict(include_member=True)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@duplicate_bp.route('/pending', methods=['GET'])
def get_pending_duplicates():
    """
    Get all pending duplicate candidates

    Query params:
        - limit: Maximum number of results (default: 50)
        - offset: Pagination offset (default: 0)

    Returns:
        List of pending duplicate candidates with member and submission data
    """
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    try:
        result = duplicate_service.get_pending_duplicates(limit=limit, offset=offset)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@duplicate_bp.route('/<int:duplicate_id>', methods=['GET'])
def get_duplicate(duplicate_id):
    """
    Get a single duplicate candidate by ID

    Returns:
        Duplicate candidate with member and submission data
    """
    duplicate = DuplicateCandidate.query.get(duplicate_id)

    if not duplicate:
        return jsonify({'error': 'Duplicate candidate not found'}), 404

    return jsonify({
        'duplicate': duplicate.to_dict(include_member=True, include_submission=True)
    }), 200


@duplicate_bp.route('/<int:duplicate_id>/resolve', methods=['POST'])
def resolve_duplicate(duplicate_id):
    """
    Resolve a duplicate candidate

    Request body:
        - resolution: Resolution status (merged, ignored, new_member)
        - resolved_by: Username of resolver (optional, default: 'user')
        - notes: Optional notes about resolution

    Returns:
        Updated duplicate candidate
    """
    data = request.get_json()

    if not data or 'resolution' not in data:
        return jsonify({'error': 'resolution is required'}), 400

    resolution = data['resolution']
    if resolution not in ['merged', 'ignored', 'new_member']:
        return jsonify({'error': 'resolution must be one of: merged, ignored, new_member'}), 400

    resolved_by = data.get('resolved_by', 'user')
    notes = data.get('notes')

    try:
        duplicate = duplicate_service.resolve_duplicate(
            duplicate_id=duplicate_id,
            resolution=resolution,
            resolved_by=resolved_by,
            notes=notes
        )

        return jsonify({
            'message': 'Duplicate resolved successfully',
            'duplicate': duplicate.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@duplicate_bp.route('/stats', methods=['GET'])
def get_duplicate_stats():
    """
    Get duplicate detection statistics

    Returns:
        Statistics about duplicate candidates
    """
    try:
        total = DuplicateCandidate.query.count()
        pending = DuplicateCandidate.query.filter_by(resolution_status='pending').count()
        merged = DuplicateCandidate.query.filter_by(resolution_status='merged').count()
        ignored = DuplicateCandidate.query.filter_by(resolution_status='ignored').count()
        new_member = DuplicateCandidate.query.filter_by(resolution_status='new_member').count()

        return jsonify({
            'total': total,
            'pending': pending,
            'merged': merged,
            'ignored': ignored,
            'new_member': new_member
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
