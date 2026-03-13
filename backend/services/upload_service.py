"""
Upload service for handling file uploads and PDF processing
"""
import os
from datetime import datetime
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

from models import db, FormSubmission, FormImage
from utils.file_utils import (
    save_uploaded_file,
    generate_batch_id,
    create_processed_image_dir,
    get_file_size
)


class UploadService:
    """Service for handling file uploads"""

    def __init__(self, upload_folder, allowed_extensions):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions

    def process_upload(self, files, split_pdf_pages=False):
        """
        Process uploaded files and create database records

        Args:
            files: List of FileStorage objects from request
            split_pdf_pages: If True, split multi-page PDFs into separate submissions (one per page)

        Returns:
            dict: {'batch_id': str, 'submissions': list, 'errors': list}
        """
        # Generate batch ID for this upload session
        batch_id = generate_batch_id()

        submissions = []
        errors = []

        for file in files:
            try:
                # Save the uploaded file
                file_path, original_filename, file_extension = save_uploaded_file(
                    file, self.upload_folder, batch_id
                )

                # Process the file based on type
                if file_extension == 'pdf' and split_pdf_pages:
                    # Split PDF into separate submissions (one per page)
                    page_submissions = self._process_pdf_split_pages(
                        file_path, original_filename, batch_id
                    )
                    submissions.extend(page_submissions)
                else:
                    # Standard processing: one submission per file
                    # Create form submission record
                    submission = FormSubmission(
                        submission_batch_id=batch_id,
                        file_name=original_filename,
                        file_type=file_extension,
                        file_path=file_path,
                        processing_status='pending',
                        ocr_status='pending',
                        validation_status='pending'
                    )

                    db.session.add(submission)
                    db.session.flush()  # Get the submission ID

                    # Process the file based on type
                    if file_extension == 'pdf':
                        self._process_pdf(submission, file_path, batch_id)
                    else:
                        # For images, create a single FormImage record
                        self._process_image(submission, file_path)

                    submissions.append(submission)

            except Exception as e:
                errors.append({
                    'filename': file.filename if hasattr(file, 'filename') else 'unknown',
                    'error': str(e)
                })
                # Rollback this submission if error
                db.session.rollback()
                continue

        # Commit all successful submissions
        if submissions:
            db.session.commit()

        return {
            'batch_id': batch_id,
            'submissions': [s.to_dict() for s in submissions],
            'errors': errors
        }

    def _process_pdf_split_pages(self, pdf_path, original_filename, batch_id):
        """
        Split PDF into separate submissions (one per page)

        Args:
            pdf_path: Path to PDF file
            original_filename: Original filename
            batch_id: Batch ID for organizing files

        Returns:
            list: List of FormSubmission objects (one per page)
        """
        submissions = []

        try:
            # Create processed images directory
            processed_dir = create_processed_image_dir(self.upload_folder, batch_id)

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)

            # Create a separate submission for each page
            for page_num, image in enumerate(images, start=1):
                # Generate image filename
                image_filename = f"{Path(pdf_path).stem}_page_{page_num}.jpg"
                image_path = processed_dir / image_filename

                # Save image
                image.save(str(image_path), 'JPEG', quality=95)

                # Create form submission record for this page
                submission = FormSubmission(
                    submission_batch_id=batch_id,
                    file_name=f"{original_filename} (Page {page_num})",
                    file_type='pdf',
                    file_path=pdf_path,
                    processing_status='pending',
                    ocr_status='pending',
                    validation_status='pending'
                )

                db.session.add(submission)
                db.session.flush()  # Get the submission ID

                # Create FormImage record for this page
                form_image = FormImage(
                    submission_id=submission.id,
                    image_path=str(image_path),
                    page_number=1,  # Each submission has only one page
                    width=image.width,
                    height=image.height
                )

                db.session.add(form_image)

                # Update submission status
                submission.processing_status = 'completed'
                submissions.append(submission)

            return submissions

        except Exception as e:
            # Mark all submissions as error
            for submission in submissions:
                submission.processing_status = 'error'
                submission.error_message = f"PDF processing error: {str(e)}"
            raise

    def _process_pdf(self, submission, pdf_path, batch_id):
        """
        Extract pages from PDF and create FormImage records (all pages in one submission)

        Args:
            submission: FormSubmission object
            pdf_path: Path to PDF file
            batch_id: Batch ID for organizing files
        """
        try:
            # Create processed images directory
            processed_dir = create_processed_image_dir(self.upload_folder, batch_id)

            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)

            # Save each page as an image
            for page_num, image in enumerate(images, start=1):
                # Generate image filename
                image_filename = f"{Path(pdf_path).stem}_page_{page_num}.jpg"
                image_path = processed_dir / image_filename

                # Save image
                image.save(str(image_path), 'JPEG', quality=95)

                # Create FormImage record
                form_image = FormImage(
                    submission_id=submission.id,
                    image_path=str(image_path),
                    page_number=page_num,
                    width=image.width,
                    height=image.height
                )

                db.session.add(form_image)

            # Update submission status
            submission.processing_status = 'completed'

        except Exception as e:
            submission.processing_status = 'error'
            submission.error_message = f"PDF processing error: {str(e)}"
            raise

    def _process_image(self, submission, image_path):
        """
        Process uploaded image and create FormImage record

        Args:
            submission: FormSubmission object
            image_path: Path to image file
        """
        try:
            # Open image to get dimensions
            with Image.open(image_path) as img:
                width, height = img.size

            # Create FormImage record
            form_image = FormImage(
                submission_id=submission.id,
                image_path=image_path,
                page_number=1,
                width=width,
                height=height
            )

            db.session.add(form_image)

            # Update submission status
            submission.processing_status = 'completed'

        except Exception as e:
            submission.processing_status = 'error'
            submission.error_message = f"Image processing error: {str(e)}"
            raise

    def get_submission(self, submission_id):
        """
        Get submission by ID

        Args:
            submission_id: Submission ID

        Returns:
            FormSubmission or None
        """
        return FormSubmission.query.get(submission_id)

    def get_submissions_by_batch(self, batch_id):
        """
        Get all submissions for a batch

        Args:
            batch_id: Batch ID

        Returns:
            list: List of FormSubmission objects
        """
        return FormSubmission.query.filter_by(submission_batch_id=batch_id).all()

    def get_pending_submissions(self, limit=50):
        """
        Get pending submissions that need OCR processing

        Args:
            limit: Maximum number of submissions to return

        Returns:
            list: List of FormSubmission objects
        """
        return FormSubmission.query.filter_by(
            processing_status='completed',
            ocr_status='pending'
        ).limit(limit).all()

    def update_submission_status(self, submission_id, **kwargs):
        """
        Update submission status fields

        Args:
            submission_id: Submission ID
            **kwargs: Fields to update (processing_status, ocr_status, validation_status, etc.)

        Returns:
            bool: True if successful
        """
        submission = self.get_submission(submission_id)
        if not submission:
            return False

        for key, value in kwargs.items():
            if hasattr(submission, key):
                setattr(submission, key, value)

        if 'processed_at' in kwargs or 'ocr_status' in kwargs:
            if submission.ocr_status == 'completed':
                submission.processed_at = datetime.utcnow()

        if 'validated_at' in kwargs or 'validation_status' in kwargs:
            if submission.validation_status == 'completed':
                submission.validated_at = datetime.utcnow()

        db.session.commit()
        return True
