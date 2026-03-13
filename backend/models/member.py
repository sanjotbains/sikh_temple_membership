"""
Member model - Core membership data
"""
from datetime import datetime
from . import db


class Member(db.Model):
    """Member model representing a temple member"""
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Name fields
    first_name = db.Column(db.String(100), nullable=False, index=True)
    last_name = db.Column(db.String(100), nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)

    # Address fields
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='Canada')

    # Contact fields
    phone_primary = db.Column(db.String(20))
    phone_secondary = db.Column(db.String(20))
    email = db.Column(db.String(200))

    # Membership fields
    date_of_birth = db.Column(db.Date)
    date_joined = db.Column(db.Date)
    membership_status = db.Column(db.String(20), default='active', index=True)  # active, inactive, pending
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100), default='system')
    updated_by = db.Column(db.String(100), default='system')

    # Relationships
    submissions = db.relationship('FormSubmission', back_populates='member', lazy='dynamic')
    duplicate_candidates = db.relationship('DuplicateCandidate', foreign_keys='DuplicateCandidate.existing_member_id', back_populates='existing_member', lazy='dynamic')

    def __repr__(self):
        return f'<Member {self.id}: {self.full_name}>'

    def to_dict(self, include_relationships=False):
        """Convert member to dictionary"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'phone_primary': self.phone_primary,
            'phone_secondary': self.phone_secondary,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'membership_status': self.membership_status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }

        if include_relationships:
            data['submissions_count'] = self.submissions.count()

        return data

    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))
