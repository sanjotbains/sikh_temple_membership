"""
OCR result models - Store OCR extraction data and manual corrections
"""
from datetime import datetime
from . import db


class OCRResult(db.Model):
    """OCR result model storing extracted text and metadata"""
    __tablename__ = 'ocr_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Submission and image links
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id', ondelete='CASCADE'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('form_images.id', ondelete='SET NULL'))

    # OCR data
    raw_text = db.Column(db.Text)  # Full OCR text
    confidence_score = db.Column(db.Float)  # Average confidence (0.0 to 1.0)
    field_extractions = db.Column(db.Text)  # JSON blob of extracted fields
    ocr_metadata = db.Column(db.Text)  # JSON blob of Vision API response

    # Metadata
    processed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = db.relationship('FormSubmission', back_populates='ocr_results')
    image = db.relationship('FormImage', back_populates='ocr_results')

    def __repr__(self):
        return f'<OCRResult {self.id}: Submission {self.submission_id}>'

    def to_dict(self):
        """Convert OCR result to dictionary"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'image_id': self.image_id,
            'raw_text': self.raw_text,
            'confidence_score': self.confidence_score,
            'field_extractions': self.field_extractions,
            'ocr_metadata': self.ocr_metadata,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


class ValidationCorrection(db.Model):
    """Validation correction model tracking manual edits during validation"""
    __tablename__ = 'validation_corrections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Submission link
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id', ondelete='CASCADE'), nullable=False)

    # Correction data
    field_name = db.Column(db.String(100), nullable=False)
    ocr_value = db.Column(db.Text)  # Original OCR value
    corrected_value = db.Column(db.Text)  # Human-corrected value

    # Metadata
    corrected_by = db.Column(db.String(100), default='user')
    corrected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submission = db.relationship('FormSubmission', back_populates='corrections')

    def __repr__(self):
        return f'<ValidationCorrection {self.id}: {self.field_name} for Submission {self.submission_id}>'

    def to_dict(self):
        """Convert correction to dictionary"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'field_name': self.field_name,
            'ocr_value': self.ocr_value,
            'corrected_value': self.corrected_value,
            'corrected_by': self.corrected_by,
            'corrected_at': self.corrected_at.isoformat() if self.corrected_at else None
        }
