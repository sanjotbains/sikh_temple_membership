"""
Duplicate candidate model - Track potential duplicate members
"""
from datetime import datetime
from . import db


class DuplicateCandidate(db.Model):
    """Duplicate candidate model for tracking potential duplicate members"""
    __tablename__ = 'duplicate_candidates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Links
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id', ondelete='CASCADE'), nullable=False)
    existing_member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)

    # Similarity data
    similarity_score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    match_fields = db.Column(db.Text)  # JSON: which fields matched and their scores

    # Resolution
    resolution_status = db.Column(db.String(20), default='pending', index=True)  # pending, merged, ignored, new_member
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = db.relationship('FormSubmission', back_populates='duplicate_candidates')
    existing_member = db.relationship('Member', foreign_keys=[existing_member_id], back_populates='duplicate_candidates')

    def __repr__(self):
        return f'<DuplicateCandidate {self.id}: Submission {self.submission_id} vs Member {self.existing_member_id} (Score: {self.similarity_score:.2f})>'

    def to_dict(self, include_member=False, include_submission=False):
        """Convert duplicate candidate to dictionary"""
        data = {
            'id': self.id,
            'submission_id': self.submission_id,
            'existing_member_id': self.existing_member_id,
            'similarity_score': self.similarity_score,
            'match_fields': self.match_fields,
            'resolution_status': self.resolution_status,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_member and self.existing_member:
            data['existing_member'] = self.existing_member.to_dict()

        if include_submission and self.submission:
            data['submission'] = self.submission.to_dict()

        return data
