"""
Configuration file for Sikh Temple Membership System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Database
    DATABASE_URI = os.getenv('DATABASE_URI', f'sqlite:///{BASE_DIR}/data/database.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'data' / 'uploads'))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 256 * 1024 * 1024))  # 256MB
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'tiff'}

    # Google Cloud Vision API
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')

    # Google Maps API
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD_HIGH = float(os.getenv('OCR_CONFIDENCE_THRESHOLD_HIGH', 0.90))
    OCR_CONFIDENCE_THRESHOLD_MEDIUM = float(os.getenv('OCR_CONFIDENCE_THRESHOLD_MEDIUM', 0.70))

    # Duplicate Detection
    DUPLICATE_THRESHOLD_HIGH = float(os.getenv('DUPLICATE_THRESHOLD_HIGH', 0.85))
    DUPLICATE_THRESHOLD_MEDIUM = float(os.getenv('DUPLICATE_THRESHOLD_MEDIUM', 0.70))

    # Pagination
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')

    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(BASE_DIR / 'data', exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Allow all origins in development for LAN access
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',') if os.getenv('CORS_ORIGINS') != '*' else '*'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = DATABASE_URI


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='default'):
    """Get configuration by name"""
    return config.get(config_name, DevelopmentConfig)
