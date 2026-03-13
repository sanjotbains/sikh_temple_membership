"""
Field extraction service for parsing OCR text into structured fields
"""
import json
from datetime import datetime

from models import db, OCRResult
from utils.text_utils import (
    normalize_text,
    extract_name,
    extract_phone,
    extract_address,
    extract_email
)
from utils.date_parser import parse_date, is_valid_dob


class FieldExtractionService:
    """Service for extracting structured fields from OCR text"""

    def __init__(self, confidence_threshold_high=0.9, confidence_threshold_medium=0.7):
        self.confidence_threshold_high = confidence_threshold_high
        self.confidence_threshold_medium = confidence_threshold_medium

    def extract_fields(self, ocr_result):
        """
        Extract structured fields from OCR result

        Args:
            ocr_result: OCRResult object

        Returns:
            dict: Extracted fields with confidence scores
        """
        if not ocr_result or not ocr_result.raw_text:
            return self._empty_fields()

        text = ocr_result.raw_text

        # Extract each field type
        name_data = extract_name(text)
        phone_data = extract_phone(text)
        address_data = extract_address(text)
        email_data = extract_email(text)
        dob_data = self._extract_date_of_birth(text)

        # Combine into structured output
        fields = {
            # Name fields
            'first_name': {
                'value': name_data['first_name'],
                'confidence': name_data['confidence']
            },
            'last_name': {
                'value': name_data['last_name'],
                'confidence': name_data['confidence']
            },
            'full_name': {
                'value': name_data['full_name'],
                'confidence': name_data['confidence']
            },

            # Contact fields
            'phone_primary': {
                'value': phone_data['formatted'],
                'confidence': phone_data['confidence']
            },
            'email': {
                'value': email_data['email'],
                'confidence': email_data['confidence']
            },

            # Address fields
            'address_line1': {
                'value': address_data['address_line1'],
                'confidence': address_data['confidence']
            },
            'address_line2': {
                'value': address_data['address_line2'],
                'confidence': address_data['confidence']
            },
            'city': {
                'value': address_data['city'],
                'confidence': address_data['confidence']
            },
            'state': {
                'value': address_data['state'],
                'confidence': address_data['confidence']
            },
            'postal_code': {
                'value': address_data['postal_code'],
                'confidence': address_data['confidence']
            },

            # Date of birth
            'date_of_birth': {
                'value': dob_data['formatted'],
                'confidence': dob_data['confidence']
            },

            # Metadata
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'overall_confidence': self._calculate_overall_confidence([
                name_data['confidence'],
                phone_data['confidence'],
                address_data['confidence'],
                dob_data['confidence']
            ])
        }

        # Store extracted fields in OCR result
        ocr_result.field_extractions = json.dumps(fields)
        db.session.commit()

        return fields

    def _extract_date_of_birth(self, text):
        """
        Extract and validate date of birth

        Args:
            text: OCR text

        Returns:
            dict: {'date': datetime or None, 'formatted': str, 'confidence': float}
        """
        import re
        # Look for DOB-specific patterns
        lines = text.split('\n')

        # Look for "5. Date of Birth:" pattern (membership form specific)
        for idx, line in enumerate(lines):
            if re.match(r'^\s*5\.\s*Date\s+of\s+Birth', line, re.IGNORECASE):
                # Check next line for the date
                if idx + 1 < len(lines):
                    date_line = lines[idx + 1].strip()
                    date_data = parse_date(date_line)

                    if date_data['date'] and is_valid_dob(date_data['date']):
                        date_data['confidence'] = 0.9
                        return date_data

        # Look for generic DOB, Birth, or Date labels
        for line in lines:
            # Look for lines with DOB, Birth, or Date labels
            if any(keyword in line.lower() for keyword in ['dob', 'birth', 'date of birth', 'born']):
                # Try to extract date from this line and next line
                date_data = parse_date(line)

                if date_data['date'] and is_valid_dob(date_data['date']):
                    return date_data

        # If no labeled date found, try to find any valid DOB in text
        date_data = parse_date(text)
        if date_data['date'] and is_valid_dob(date_data['date']):
            # Lower confidence since it wasn't labeled
            date_data['confidence'] = max(0, date_data['confidence'] - 0.2)
            return date_data

        return {'date': None, 'formatted': '', 'confidence': 0.0}

    def _calculate_overall_confidence(self, confidence_scores):
        """
        Calculate overall confidence from individual field confidences

        Args:
            confidence_scores: List of confidence scores

        Returns:
            float: Overall confidence (0.0 to 1.0)
        """
        valid_scores = [s for s in confidence_scores if s > 0]

        if not valid_scores:
            return 0.0

        # Use weighted average (fields with higher confidence contribute more)
        return sum(valid_scores) / len(valid_scores)

    def _empty_fields(self):
        """Return empty fields structure"""
        return {
            'first_name': {'value': '', 'confidence': 0.0},
            'last_name': {'value': '', 'confidence': 0.0},
            'full_name': {'value': '', 'confidence': 0.0},
            'phone_primary': {'value': '', 'confidence': 0.0},
            'email': {'value': '', 'confidence': 0.0},
            'address_line1': {'value': '', 'confidence': 0.0},
            'address_line2': {'value': '', 'confidence': 0.0},
            'city': {'value': '', 'confidence': 0.0},
            'state': {'value': '', 'confidence': 0.0},
            'postal_code': {'value': '', 'confidence': 0.0},
            'date_of_birth': {'value': '', 'confidence': 0.0},
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'overall_confidence': 0.0
        }

    def process_submission(self, submission):
        """
        Extract fields from all OCR results for a submission

        Args:
            submission: FormSubmission object

        Returns:
            dict: Combined extracted fields
        """
        # Get all OCR results for this submission
        ocr_results = submission.ocr_results.all()

        if not ocr_results:
            return self._empty_fields()

        # If multiple pages, combine text and extract once
        combined_text = '\n\n'.join([r.raw_text or '' for r in ocr_results])

        # Create a temporary OCR result for extraction
        temp_result = type('obj', (object,), {
            'raw_text': combined_text
        })

        fields = self.extract_fields(temp_result)

        # Store in the first OCR result (or create one if needed)
        if ocr_results:
            ocr_results[0].field_extractions = json.dumps(fields)
            db.session.commit()

        return fields

    def get_confidence_level(self, confidence):
        """
        Get confidence level category

        Args:
            confidence: Confidence score (0.0 to 1.0)

        Returns:
            str: 'high', 'medium', or 'low'
        """
        if confidence >= self.confidence_threshold_high:
            return 'high'
        elif confidence >= self.confidence_threshold_medium:
            return 'medium'
        else:
            return 'low'
