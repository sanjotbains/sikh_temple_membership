"""
OCR service for text extraction using Google Cloud Vision API
"""
import os
import json
from google.cloud import vision
from google.api_core import retry

from models import db, OCRResult, FormImage


class OCRService:
    """Service for OCR processing using Google Cloud Vision API"""

    def __init__(self):
        """Initialize Vision API client"""
        try:
            # Try to initialize client
            # Will use Application Default Credentials if GOOGLE_APPLICATION_CREDENTIALS is not set
            self.client = vision.ImageAnnotatorClient()
            print("Vision API client initialized successfully")
        except Exception as e:
            print(f"ERROR: Failed to initialize Vision API client: {e}")
            print("Make sure you have authenticated with: gcloud auth application-default login")
            self.client = None

    def process_submission(self, submission):
        """
        Process all images for a submission with OCR

        Args:
            submission: FormSubmission object

        Returns:
            dict: {'success': bool, 'ocr_result_ids': list, 'error': str or None}
        """
        if not self.client:
            return {
                'success': False,
                'ocr_result_ids': [],
                'error': 'Vision API client not initialized. Check GOOGLE_APPLICATION_CREDENTIALS.'
            }

        try:
            # Get all images for this submission
            images = submission.images.all()

            if not images:
                return {
                    'success': False,
                    'ocr_result_ids': [],
                    'error': 'No images found for submission'
                }

            ocr_result_ids = []

            # Process each image
            for form_image in images:
                result = self._process_image(form_image)
                if result:
                    ocr_result_ids.append(result.id)

            # If every image failed, treat the whole submission as failed
            if not ocr_result_ids:
                submission.ocr_status = 'error'
                submission.error_message = 'OCR error: No images could be processed (check Google Cloud Vision API credentials and billing)'
                db.session.commit()
                return {
                    'success': False,
                    'ocr_result_ids': [],
                    'error': 'No images could be processed'
                }

            # Update submission OCR status
            submission.ocr_status = 'completed'
            db.session.commit()

            return {
                'success': True,
                'ocr_result_ids': ocr_result_ids,
                'error': None
            }

        except Exception as e:
            # Update submission with error
            submission.ocr_status = 'error'
            submission.error_message = f"OCR error: {str(e)}"
            db.session.commit()

            return {
                'success': False,
                'ocr_result_ids': [],
                'error': str(e)
            }

    def _process_image(self, form_image):
        """
        Process a single image with OCR

        Args:
            form_image: FormImage object

        Returns:
            OCRResult object or None
        """
        try:
            # Read image file
            with open(form_image.image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # Perform text detection
            response = self.client.document_text_detection(
                image=image,
                retry=retry.Retry(deadline=60)
            )

            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")

            # Extract text and annotations
            texts = response.text_annotations
            full_text = texts[0].description if texts else ""

            # Calculate average confidence
            confidence_scores = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    confidence_scores.append(block.confidence)

            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

            # Store OCR metadata as JSON
            ocr_metadata = {
                'full_text_annotation': self._serialize_annotation(response.full_text_annotation),
                'text_annotations_count': len(texts),
                'language': self._detect_language(response)
            }

            # Create OCR result record
            ocr_result = OCRResult(
                submission_id=form_image.submission_id,
                image_id=form_image.id,
                raw_text=full_text,
                confidence_score=avg_confidence,
                field_extractions=None,  # Will be filled by field extraction service
                ocr_metadata=json.dumps(ocr_metadata)
            )

            db.session.add(ocr_result)
            db.session.commit()

            return ocr_result

        except Exception as e:
            print(f"Error processing image {form_image.id}: {e}")
            return None

    def _serialize_annotation(self, annotation):
        """
        Serialize full text annotation to JSON-compatible format

        Args:
            annotation: FullTextAnnotation object

        Returns:
            dict: Serialized annotation
        """
        result = {
            'pages': [],
            'text': annotation.text
        }

        for page in annotation.pages:
            page_data = {
                'width': page.width,
                'height': page.height,
                'blocks': len(page.blocks),
                'confidence': page.confidence if hasattr(page, 'confidence') else 0.0
            }
            result['pages'].append(page_data)

        return result

    def _detect_language(self, response):
        """
        Detect primary language from OCR response

        Args:
            response: Vision API response

        Returns:
            str: Language code (e.g., 'en', 'pa')
        """
        try:
            if response.full_text_annotation.pages:
                page = response.full_text_annotation.pages[0]
                if page.property and page.property.detected_languages:
                    return page.property.detected_languages[0].language_code
        except:
            pass

        return 'unknown'

    def get_ocr_result(self, submission_id):
        """
        Get OCR results for a submission

        Args:
            submission_id: Submission ID

        Returns:
            list: List of OCRResult objects
        """
        return OCRResult.query.filter_by(submission_id=submission_id).all()

    def get_ocr_text(self, submission_id):
        """
        Get combined OCR text for all images in a submission

        Args:
            submission_id: Submission ID

        Returns:
            str: Combined text from all pages
        """
        results = self.get_ocr_result(submission_id)
        return '\n\n'.join([r.raw_text or '' for r in results])
