"""
File utility functions for handling uploads and file operations
"""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """
    Check if a filename has an allowed extension

    Args:
        filename: The filename to check
        allowed_extensions: Set of allowed extensions (e.g., {'pdf', 'jpg', 'png'})

    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_batch_id():
    """
    Generate a unique batch ID for upload sessions

    Returns:
        str: UUID-based batch ID
    """
    return str(uuid.uuid4())


def save_uploaded_file(file, upload_folder, batch_id):
    """
    Save an uploaded file to the upload folder

    Args:
        file: Werkzeug FileStorage object
        upload_folder: Base upload directory path
        batch_id: Batch ID for organizing uploads

    Returns:
        tuple: (saved_file_path, original_filename, file_extension)
    """
    # Secure the filename
    original_filename = file.filename
    filename = secure_filename(original_filename)

    # Get file extension
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    # Create batch directory
    batch_dir = Path(upload_folder) / batch_id / 'original'
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = batch_dir / unique_filename

    # Save the file
    file.save(str(file_path))

    return str(file_path), original_filename, file_extension


def get_file_size(file_path):
    """
    Get the size of a file in bytes

    Args:
        file_path: Path to the file

    Returns:
        int: File size in bytes
    """
    return os.path.getsize(file_path)


def create_processed_image_dir(upload_folder, batch_id):
    """
    Create directory for processed images

    Args:
        upload_folder: Base upload directory
        batch_id: Batch ID

    Returns:
        Path: Path to processed images directory
    """
    processed_dir = Path(upload_folder) / batch_id / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir


def delete_file(file_path):
    """
    Safely delete a file

    Args:
        file_path: Path to file to delete

    Returns:
        bool: True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False
