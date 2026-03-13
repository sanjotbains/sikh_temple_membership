"""
Main Flask application entry point
Sikh Temple Membership Processing System
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from models import db
import os


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    config.init_app(app)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})

    # Register blueprints (routes)
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Sikh Temple Membership System API is running'
        }), 200

    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'message': 'Sikh Temple Membership Processing System API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'api': '/api'
            }
        }), 200

    return app


def register_blueprints(app):
    """Register Flask blueprints (route modules)"""
    # Import route modules
    try:
        from routes.upload_routes import upload_bp
        app.register_blueprint(upload_bp, url_prefix='/api/upload')
    except ImportError:
        pass

    try:
        from routes.submission_routes import submission_bp
        app.register_blueprint(submission_bp, url_prefix='/api/submissions')
    except ImportError:
        pass

    try:
        from routes.member_routes import member_bp
        app.register_blueprint(member_bp, url_prefix='/api/members')
    except ImportError:
        pass

    try:
        from routes.validation_routes import validation_bp
        app.register_blueprint(validation_bp, url_prefix='/api/validation')
    except ImportError:
        pass

    try:
        from routes.export_routes import export_bp
        app.register_blueprint(export_bp, url_prefix='/api/export')
    except ImportError:
        pass

    try:
        from routes.duplicate_routes import duplicate_bp
        app.register_blueprint(duplicate_bp, url_prefix='/api/duplicates')
    except ImportError:
        pass


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500


def main():
    """Run the Flask application"""
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    # Get configuration
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Sikh Temple Membership Processing System                ║
    ║  Backend API Server                                       ║
    ╚═══════════════════════════════════════════════════════════╝

    Server starting on http://{host}:{port}
    Environment: {os.getenv('FLASK_ENV', 'development')}
    Debug mode: {debug}

    Press CTRL+C to quit
    """)

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
