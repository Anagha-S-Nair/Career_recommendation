"""
Helper utilities, decorators, structured logging, and standard response formatters.
"""

import logging
from functools import wraps
from flask import jsonify, session, request, redirect, url_for, flash
from flask_login import current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s (%(funcName)s): %(message)s'
)
logger = logging.getLogger('career_guidance_app')


def admin_required(f):
    """Decorator to enforce Admin role access control."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required', 'code': 'UNAUTHORIZED'}), 401
            flash('Please log in as an administrator to access this area.', 'warning')
            return redirect(url_for('auth.login_page'))

        if current_user.role != 'admin':
            logger.warning(f"Unauthorized admin access attempt by User ID {current_user.id} ({current_user.username})")
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Administrative privileges required', 'code': 'FORBIDDEN'}), 403
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('student.dashboard'))

        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to enforce Student role access control."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required', 'code': 'UNAUTHORIZED'}), 401
            return redirect(url_for('auth.login_page'))

        if current_user.role != 'student' or not current_user.student:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Student profile required', 'code': 'FORBIDDEN'}), 403
            return redirect(url_for('admin.admin_dashboard'))

        return f(*args, **kwargs)
    return decorated_function


def api_response(data=None, message="Success", status_code=200, meta=None):
    """Standardized JSON API response structure."""
    payload = {
        'success': 200 <= status_code < 300,
        'message': message,
        'data': data
    }
    if meta is not None:
        payload['meta'] = meta
    return jsonify(payload), status_code


def api_error(message="An error occurred", status_code=400, errors=None, code="BAD_REQUEST"):
    """Standardized JSON API error response."""
    payload = {
        'success': False,
        'error': message,
        'code': code
    }
    if errors:
        payload['details'] = errors
    return jsonify(payload), status_code


# -------------------------------------------------------------------
# Data Normalization & Formatting Helpers
# -------------------------------------------------------------------

DOMAIN_CODES = {
    'Technology': 'TECH',
    'Information Technology': 'IT',
    'Healthcare': 'HLTH',
    'Medicine': 'MED',
    'Engineering': 'ENG',
    'Pure Science': 'SCI',
    'Research': 'RES',
    'Business': 'BUS',
    'Finance': 'FIN',
    'Law': 'LAW',
    'Arts': 'ART',
    'Design': 'DES',
    'Media': 'MEDA',
    'Government': 'GOV',
    'Agriculture': 'AGR',
    'Environment': 'ENV',
    'Sports': 'SPT',
    'Hospitality': 'HOSP',
    'Aviation': 'AVI',
    'Manufacturing': 'MFG',
    'Construction': 'CONS',
    'Skilled Trades': 'TRD',
    'Transportation': 'TRN',
    'Psychology and Social Sciences': 'PSY',
    'Psychology And Social Sciences': 'PSY',
    'Education': 'EDU',
    'Biotechnology': 'BIO',
    'Pharmaceuticals': 'PHAR',
    'Defence and Security': 'DEF',
    'Defence And Security': 'DEF',
    'Fashion': 'FASH',
    'Food': 'FOOD',
    'Real Estate': 'REST',
    'Emerging Careers': 'EMG',
    'Interdisciplinary': 'INT'
}


def normalize_text(text: str) -> str:
    """Cleans and standardizes text strings with proper title casing and standard acronyms."""
    if not text:
        return ''
    cleaned = ' '.join(str(text).strip().split())
    words = cleaned.split()
    result = []
    for w in words:
        upper = w.upper()
        lower = w.lower()
        if upper in ['AI', 'IT', 'UI', 'UX', 'CAD', 'CAM', 'VFX', '3D', '2D', 'CA', 'IAS', 'IPS', 'IFS', 'GIS', 'CFO', 'CEO', 'CTO', 'SOC', 'SEO', 'NEET', 'JEE', 'CLAT', 'UPSC', 'MBBS', 'BCA', 'MCA', 'BBA', 'MBA']:
            result.append(upper)
        elif lower in ['and', '&', 'of', 'in', 'the', 'for', 'to', 'with', 'on', 'at', 'by', 'a', 'an']:
            result.append(lower if len(result) > 0 else w.capitalize())
        else:
            result.append(w.capitalize())
    return ' '.join(result)


def parse_numeric(value, default=0) -> int:
    """Safely converts numeric values to integer bounded 0..5."""
    try:
        val = int(round(float(value)))
        return max(0, min(5, val))
    except (ValueError, TypeError):
        return default


def generate_career_code(domain_name: str, cid_raw: str, index: int) -> str:
    """Generates a deterministic, standard career code."""
    import re
    prefix = DOMAIN_CODES.get(domain_name, 'GEN')
    clean_cid = re.sub(r'[^0-9A-Za-z]', '', str(cid_raw or ''))
    if clean_cid.startswith('CID'):
        clean_cid = clean_cid[3:]
    if clean_cid:
        return f"CAR-{prefix}-{clean_cid}"
    return f"CAR-{prefix}-{index:04d}"

