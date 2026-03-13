"""
Form submission models - Track uploaded forms and their images
"""
from datetime import datetime
from . import db


class FormSubmission(db.Model):
    """Form submission model representing an uploaded form"""
    __tablename__ = 'form_submissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Batch tracking
    submission_batch_id = db.Column(db.String(100), nullable=False, index=True)

    # File information
    file_name = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, jpg, png
    file_path = db.Column(db.String(1000), nullable=False)

    # Processing status
    processing_status = db.Column(db.String(20), default='pending', index=True)  # pending, processing, completed, error
    ocr_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, error
    validation_status = db.Column(db.String(20), default='pending', index=True)  # pending, in_progress, completed

    # Member link
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)

    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    validated_at = db.Column(db.DateTime)

    # Error tracking
    error_message = db.Column(db.Text)

    # Relationships
    member = db.relationship('Member', back_populates='submissions')
    images = db.relationship('FormImage', back_populates='submission', lazy='dynamic', cascade='all, delete-orphan')
    ocr_results = db.relationship('OCRResult', back_populates='submission', lazy='dynamic', cascade='all, delete-orphan')
    corrections = db.relationship('ValidationCorrection', back_populates='submission', lazy='dynamic', cascade='all, delete-orphan')
    duplicate_candidates = db.relationship('DuplicateCandidate', back_populates='submission', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FormSubmission {self.id}: {self.file_name}>'

    def to_dict(self, include_images=False, include_ocr=False):
        """Convert submission to dictionary"""
        data = {
            'id': self.id,
            'submission_batch_id': self.submission_batch_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'processing_status': self.processing_status,
            'ocr_status': self.ocr_status,
            'validation_status': self.validation_status,
            'member_id': self.member_id,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'error_message': self.error_message
        }

        if include_images:
            data['images'] = [img.to_dict() for img in self.images]

        if include_ocr:
            ocr_list = self.ocr_results.all()
            data['ocr_results'] = [ocr.to_dict() for ocr in ocr_list]

        return data


class FormImage(db.Model):
    """Form image model representing individual pages or images from a submission"""
    __tablename__ = 'form_images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Submission link
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id', ondelete='CASCADE'), nullable=False)

    # Image information
    image_path = db.Column(db.String(1000), nullable=False)
    page_number = db.Column(db.Integer, default=1)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = db.relationship('FormSubmission', back_populates='images')
    ocr_results = db.relationship('OCRResult', back_populates='image', lazy='dynamic')

    def __repr__(self):
        return f'<FormImage {self.id}: Page {self.page_number} of Submission {self.submission_id}>'

    def to_dict(self):
        """Convert image to dictionary"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'image_path': self.image_path,
            'page_number': self.page_number,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
