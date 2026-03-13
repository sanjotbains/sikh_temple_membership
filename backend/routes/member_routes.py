"""
Member routes for managing temple members
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import or_, func

from models import db, Member, FormSubmission

member_bp = Blueprint('members', __name__)


@member_bp.route('/', methods=['GET'])
def get_members():
    """
    Get members with optional search and filtering

    Query params:
        - search: Search by name, phone, email
        - status: Filter by membership_status (active, inactive, pending)
        - city: Filter by city
        - state: Filter by state
        - limit: Max number of results (default: 50)
        - offset: Pagination offset (default: 0)
        - sort: Sort field (default: full_name)
        - order: Sort order (asc/desc, default: asc)
    """
    # Get query parameters
    search = request.args.get('search', '').strip()
    status = request.args.get('status')
    city = request.args.get('city')
    state = request.args.get('state')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    sort_field = request.args.get('sort', 'full_name')
    sort_order = request.args.get('order', 'asc')

    # Build query - exclude rejected members by default unless specifically filtered
    query = Member.query

    # Exclude rejected members unless status filter is explicitly set to 'rejected'
    if status != 'rejected':
        query = query.filter(Member.membership_status != 'rejected')

    # Apply search filter
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                Member.full_name.ilike(search_pattern),
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.phone_primary.ilike(search_pattern),
                Member.email.ilike(search_pattern)
            )
        )

    # Apply status filter
    if status:
        query = query.filter_by(membership_status=status)

    # Apply city filter
    if city:
        query = query.filter_by(city=city)

    # Apply state filter
    if state:
        query = query.filter_by(state=state)

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(Member, sort_field, Member.full_name)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    members = query.limit(limit).offset(offset).all()

    return jsonify({
        'members': [m.to_dict() for m in members],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@member_bp.route('/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """
    Get a single member by ID with full details
    """
    member = Member.query.get(member_id)

    if not member:
        return jsonify({'error': 'Member not found'}), 404

    # Include relationship data
    member_data = member.to_dict(include_relationships=True)

    # Get linked submissions with images
    submissions = member.submissions.all()
    member_data['submissions'] = [s.to_dict(include_images=True) for s in submissions]

    return jsonify({'member': member_data}), 200


@member_bp.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    """
    Update a member's information

    Request body: JSON with fields to update
    """
    member = Member.query.get(member_id)

    if not member:
        return jsonify({'error': 'Member not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update allowed fields
    allowed_fields = [
        'first_name', 'last_name', 'full_name',
        'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
        'phone_primary', 'phone_secondary', 'email',
        'date_of_birth', 'date_joined', 'membership_status', 'notes'
    ]

    for field in allowed_fields:
        if field in data:
            value = data[field]

            # Handle date fields
            if field in ['date_of_birth', 'date_joined'] and value:
                try:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                except:
                    pass

            setattr(member, field, value)

    # Update metadata
    member.updated_at = datetime.utcnow()
    member.updated_by = data.get('updated_by', 'user')

    db.session.commit()

    return jsonify({
        'message': 'Member updated successfully',
        'member': member.to_dict()
    }), 200


@member_bp.route('/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    """
    Delete a member (soft delete by setting status to inactive)
    """
    member = Member.query.get(member_id)

    if not member:
        return jsonify({'error': 'Member not found'}), 404

    # Soft delete - just mark as inactive
    member.membership_status = 'inactive'
    member.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Member marked as inactive successfully'
    }), 200


@member_bp.route('/<int:member_id>/reject', methods=['POST'])
def reject_member(member_id):
    """
    Reject a member record (e.g., duplicate or invalid entry)
    This will mark the member as rejected and also mark their associated submissions as rejected

    Request body (optional):
        {
            "reason": "Description of why the member was rejected"
        }
    """
    member = Member.query.get(member_id)

    if not member:
        return jsonify({'error': 'Member not found'}), 404

    data = request.get_json() or {}
    reason = data.get('reason', '')

    # Mark member as rejected
    member.membership_status = 'rejected'
    member.updated_at = datetime.utcnow()

    # Optionally add rejection reason to notes
    if reason:
        rejection_note = f"\n[REJECTED: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {reason}"
        if member.notes:
            member.notes += rejection_note
        else:
            member.notes = rejection_note.strip()

    # Also mark all associated submissions as rejected
    submissions = member.submissions.all()
    for submission in submissions:
        submission.validation_status = 'rejected'
        submission.validated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Member rejected successfully',
        'submissions_affected': len(submissions)
    }), 200


@member_bp.route('/stats', methods=['GET'])
def get_member_stats():
    """
    Get member statistics
    """
    total = Member.query.count()
    active = Member.query.filter_by(membership_status='active').count()
    inactive = Member.query.filter_by(membership_status='inactive').count()
    pending = Member.query.filter_by(membership_status='pending').count()
    rejected = Member.query.filter_by(membership_status='rejected').count()

    # Get recent members (last 30 days) - exclude rejected
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent = Member.query.filter(
        Member.created_at >= thirty_days_ago,
        Member.membership_status != 'rejected'
    ).count()

    return jsonify({
        'total': total,
        'active': active,
        'inactive': inactive,
        'pending': pending,
        'rejected': rejected,
        'recent_30_days': recent
    }), 200


@member_bp.route('/search-suggestions', methods=['GET'])
def get_search_suggestions():
    """
    Get unique cities and states for filter dropdowns
    """
    # Get unique cities
    cities = db.session.query(Member.city).distinct().filter(Member.city.isnot(None)).all()
    cities = [c[0] for c in cities if c[0]]

    # Get unique states
    states = db.session.query(Member.state).distinct().filter(Member.state.isnot(None)).all()
    states = [s[0] for s in states if s[0]]

    return jsonify({
        'cities': sorted(cities),
        'states': sorted(states)
    }), 200
