"""
Database models package
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models for easy access
from .member import Member
from .submission import FormSubmission, FormImage
from .ocr_result import OCRResult, ValidationCorrection
from .duplicate import DuplicateCandidate
from .audit import AuditLog

__all__ = [
    'db',
    'Member',
    'FormSubmission',
    'FormImage',
    'OCRResult',
    'ValidationCorrection',
    'DuplicateCandidate',
    'AuditLog'
]
