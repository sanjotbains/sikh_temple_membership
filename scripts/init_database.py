#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and sets up initial database structure
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from flask import Flask
from config import get_config
from models import db, Member, FormSubmission, FormImage, OCRResult, ValidationCorrection, DuplicateCandidate, AuditLog


def init_database(app):
    """Initialize the database with all tables"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()

        # Create indexes
        print("Creating indexes...")
        # Indexes are defined in models, so they're created automatically

        print("Database initialized successfully!")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Print table summary
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nCreated {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")


def drop_database(app):
    """Drop all tables (use with caution!)"""
    with app.app_context():
        print("WARNING: This will delete all data!")
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == 'yes':
            print("Dropping all tables...")
            db.drop_all()
            print("All tables dropped successfully!")
        else:
            print("Operation cancelled.")


def main():
    """Main function"""
    # Create Flask app
    app = Flask(__name__)
    config = get_config('development')
    app.config.from_object(config)
    config.init_app(app)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'drop':
            drop_database(app)
        elif command == 'reset':
            drop_database(app)
            init_database(app)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python init_database.py [drop|reset]")
            sys.exit(1)
    else:
        init_database(app)


if __name__ == '__main__':
    main()
