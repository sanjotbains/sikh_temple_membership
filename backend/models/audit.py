"""
Audit log model - Track all system changes
"""
from datetime import datetime
from . import db


class AuditLog(db.Model):
    """Audit log model for tracking all changes in the system"""
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Entity information
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # member, submission, etc.
    entity_id = db.Column(db.Integer, nullable=False, index=True)

    # Action information
    action = db.Column(db.String(20), nullable=False)  # create, update, delete, validate
    changes = db.Column(db.Text)  # JSON blob of what changed

    # Metadata
    performed_by = db.Column(db.String(100), default='user')
    performed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} {self.entity_type} {self.entity_id}>'

    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'changes': self.changes,
            'performed_by': self.performed_by,
            'performed_at': self.performed_at.isoformat() if self.performed_at else None
        }
