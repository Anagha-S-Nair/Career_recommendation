"""
Application Factory and Main Blueprint.
Assembles extensions, blueprints, error handlers, and application context.
Configured for MySQL Server via SQLAlchemy.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path for direct script execution
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, render_template, request, jsonify, Blueprint
from backend.config import config_by_name
from backend.extensions import db, login_manager, bcrypt
from backend.models.career import CareerDomain, Career
from backend.utils.helpers import api_error, logger

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home landing page with interactive features, domain highlights, and clear AI-readiness disclosure."""
    domains = CareerDomain.query.order_by(CareerDomain.display_order.asc()).all()
    sample_careers = Career.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', domains=domains, sample_careers=sample_careers)


@main_bp.route('/favicon.ico')
def favicon():
    """Serve branded SVG favicon for browser tab icon requests."""
    from flask import send_from_directory
    return send_from_directory(str(BASE_DIR / 'frontend' / 'static'), 'favicon.svg', mimetype='image/svg+xml')



def create_app(config_name=None):
    """Factory function to configure and create Flask application instances connected to MySQL."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / 'frontend' / 'templates'),
        static_folder=str(BASE_DIR / 'frontend' / 'static')
    )

    # Load Configuration
    app_config = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(app_config)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.student_routes import student_bp
    from backend.routes.assessment_routes import assessment_bp
    from backend.routes.career_routes import career_bp
    from backend.routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(admin_bp)

    # Custom Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.is_json or request.path.startswith('/api/'):
            return api_error("Requested resource not found.", status_code=404, code="NOT_FOUND")
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def handle_forbidden(e):
        if request.is_json or request.path.startswith('/api/'):
            return api_error("Access forbidden.", status_code=403, code="FORBIDDEN")
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def handle_server_error(e):
        logger.error(f"Internal Server Error on {request.path}: {str(e)}")
        if request.is_json or request.path.startswith('/api/'):
            return api_error("An internal server error occurred. Please try again later.", status_code=500, code="INTERNAL_SERVER_ERROR")
        return render_template('500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app('development')
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
