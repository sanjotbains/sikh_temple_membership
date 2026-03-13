"""
Duplicate Detection Service - Find potential duplicate members
"""
from fuzzywuzzy import fuzz
from datetime import datetime
import json

from models import Member, DuplicateCandidate, db


class DuplicateDetectionService:
    """Service for detecting potential duplicate members"""

    # Similarity thresholds
    NAME_THRESHOLD = 85  # Fuzzy match threshold for names
    ADDRESS_THRESHOLD = 80  # Fuzzy match threshold for addresses
    OVERALL_THRESHOLD = 70  # Overall similarity threshold to flag as duplicate

    # Field weights for overall score
    WEIGHTS = {
        'name': 0.35,
        'phone': 0.25,
        'email': 0.15,
        'address': 0.15,
        'dob': 0.10
    }

    def __init__(self):
        """Initialize the duplicate detection service"""
        pass

    def find_duplicates(self, extracted_fields, submission_id=None, limit=10):
        """
        Find potential duplicate members based on extracted fields

        Args:
            extracted_fields: Dictionary of extracted field values
            submission_id: Optional submission ID to exclude from search
            limit: Maximum number of duplicates to return

        Returns:
            List of potential duplicates with similarity scores
        """
        # Get all active members
        members = Member.query.filter_by(membership_status='active').all()

        duplicates = []

        for member in members:
            # Calculate similarity
            similarity_data = self._calculate_similarity(extracted_fields, member)

            # If similarity is above threshold, add to duplicates list
            if similarity_data['overall_score'] >= self.OVERALL_THRESHOLD:
                duplicates.append({
                    'member': member.to_dict(),
                    'similarity_score': similarity_data['overall_score'],
                    'match_fields': similarity_data
                })

        # Sort by similarity score (highest first)
        duplicates.sort(key=lambda x: x['similarity_score'], reverse=True)

        return duplicates[:limit]

    def create_duplicate_candidate(self, submission_id, existing_member_id, similarity_data):
        """
        Create a duplicate candidate record

        Args:
            submission_id: ID of the submission being validated
            existing_member_id: ID of the potentially duplicate member
            similarity_data: Dictionary with similarity scores and matched fields

        Returns:
            Created DuplicateCandidate object
        """
        # Check if duplicate candidate already exists
        existing = DuplicateCandidate.query.filter_by(
            submission_id=submission_id,
            existing_member_id=existing_member_id
        ).first()

        if existing:
            # Update existing record
            existing.similarity_score = similarity_data['overall_score']
            existing.match_fields = json.dumps(similarity_data)
            db.session.commit()
            return existing

        # Create new duplicate candidate
        duplicate_candidate = DuplicateCandidate(
            submission_id=submission_id,
            existing_member_id=existing_member_id,
            similarity_score=similarity_data['overall_score'],
            match_fields=json.dumps(similarity_data),
            resolution_status='pending'
        )

        db.session.add(duplicate_candidate)
        db.session.commit()

        return duplicate_candidate

    def _calculate_similarity(self, extracted_fields, member):
        """
        Calculate similarity between extracted fields and an existing member

        Returns:
            Dictionary with field-level scores and overall score
        """
        scores = {}

        # Name similarity
        extracted_name = extracted_fields.get('full_name', '').strip().upper()
        member_name = (member.full_name or '').strip().upper()

        if extracted_name and member_name:
            scores['name'] = {
                'score': fuzz.token_sort_ratio(extracted_name, member_name),
                'extracted': extracted_name,
                'existing': member_name,
                'match': fuzz.token_sort_ratio(extracted_name, member_name) >= self.NAME_THRESHOLD
            }
        else:
            scores['name'] = {'score': 0, 'match': False}

        # Phone similarity (exact match or normalized)
        extracted_phone = self._normalize_phone(extracted_fields.get('phone_primary', ''))
        member_phone_primary = self._normalize_phone(member.phone_primary or '')
        member_phone_secondary = self._normalize_phone(member.phone_secondary or '')

        phone_match = False
        phone_score = 0

        if extracted_phone:
            if extracted_phone == member_phone_primary or extracted_phone == member_phone_secondary:
                phone_match = True
                phone_score = 100

        scores['phone'] = {
            'score': phone_score,
            'extracted': extracted_fields.get('phone_primary', ''),
            'existing': member.phone_primary or '',
            'match': phone_match
        }

        # Email similarity (exact match, case-insensitive)
        extracted_email = (extracted_fields.get('email', '') or '').strip().lower()
        member_email = (member.email or '').strip().lower()

        email_match = False
        email_score = 0

        if extracted_email and member_email:
            email_match = extracted_email == member_email
            email_score = 100 if email_match else 0

        scores['email'] = {
            'score': email_score,
            'extracted': extracted_fields.get('email', ''),
            'existing': member.email or '',
            'match': email_match
        }

        # Address similarity
        extracted_address = self._format_address(
            extracted_fields.get('address_line1', ''),
            extracted_fields.get('city', ''),
            extracted_fields.get('state', ''),
            extracted_fields.get('postal_code', '')
        )
        member_address = self._format_address(
            member.address_line1 or '',
            member.city or '',
            member.state or '',
            member.postal_code or ''
        )

        if extracted_address and member_address:
            address_score = fuzz.token_sort_ratio(extracted_address, member_address)
            scores['address'] = {
                'score': address_score,
                'extracted': extracted_address,
                'existing': member_address,
                'match': address_score >= self.ADDRESS_THRESHOLD
            }
        else:
            scores['address'] = {'score': 0, 'match': False}

        # Date of birth similarity (exact match)
        extracted_dob = extracted_fields.get('date_of_birth')
        member_dob = member.date_of_birth

        dob_match = False
        dob_score = 0

        if extracted_dob and member_dob:
            # Handle string dates
            if isinstance(extracted_dob, str):
                try:
                    extracted_dob = datetime.strptime(extracted_dob, '%Y-%m-%d').date()
                except:
                    pass

            if isinstance(extracted_dob, datetime):
                extracted_dob = extracted_dob.date()

            if extracted_dob == member_dob:
                dob_match = True
                dob_score = 100

        scores['dob'] = {
            'score': dob_score,
            'extracted': str(extracted_fields.get('date_of_birth', '')),
            'existing': str(member_dob) if member_dob else '',
            'match': dob_match
        }

        # Calculate weighted overall score
        overall_score = 0
        for field, weight in self.WEIGHTS.items():
            if field in scores:
                overall_score += scores[field]['score'] * weight

        scores['overall_score'] = round(overall_score, 2)
        scores['matched_fields'] = [field for field, data in scores.items() if isinstance(data, dict) and data.get('match', False)]

        return scores

    def _normalize_phone(self, phone):
        """Normalize phone number to digits only"""
        if not phone:
            return ''
        return ''.join(filter(str.isdigit, str(phone)))

    def _format_address(self, line1, city, state, postal):
        """Format address for comparison"""
        parts = [
            (line1 or '').strip().upper(),
            (city or '').strip().upper(),
            (state or '').strip().upper(),
            (postal or '').strip().upper()
        ]
        return ' '.join(filter(None, parts))

    def resolve_duplicate(self, duplicate_id, resolution, resolved_by='user', notes=None):
        """
        Resolve a duplicate candidate

        Args:
            duplicate_id: ID of the duplicate candidate
            resolution: Resolution status (merged, ignored, new_member)
            resolved_by: Username of resolver
            notes: Optional notes about resolution

        Returns:
            Updated duplicate candidate
        """
        duplicate = DuplicateCandidate.query.get(duplicate_id)

        if not duplicate:
            raise ValueError(f"Duplicate candidate {duplicate_id} not found")

        duplicate.resolution_status = resolution
        duplicate.resolved_at = datetime.utcnow()
        duplicate.resolved_by = resolved_by
        if notes:
            duplicate.notes = notes

        db.session.commit()

        return duplicate

    def get_pending_duplicates(self, limit=50, offset=0):
        """
        Get all pending duplicate candidates

        Returns:
            List of pending duplicate candidates with member and submission data
        """
        duplicates = DuplicateCandidate.query.filter_by(
            resolution_status='pending'
        ).order_by(
            DuplicateCandidate.similarity_score.desc()
        ).limit(limit).offset(offset).all()

        total = DuplicateCandidate.query.filter_by(resolution_status='pending').count()

        return {
            'duplicates': [d.to_dict(include_member=True, include_submission=True) for d in duplicates],
            'total': total,
            'limit': limit,
            'offset': offset
        }
