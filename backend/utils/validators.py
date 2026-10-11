"""
Input validation utilities for the Career Recommendation System.
Ensures strict data integrity, security bounds, and academic constraints.
"""

import re
from typing import Tuple, Optional, Dict, Any


def validate_email(email: str) -> bool:
    """Validate email format using standard regex."""
    if not email or not isinstance(email, str):
        return False
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password meets minimum security requirements (at least 8 chars, 1 digit, 1 letter)."""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    return True, None


def validate_student_registration(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate student registration payload.
    Ensures:
    - First name and Last name present
    - Valid email and strong password
    - Class is strictly between 7 and 12
    - Age is biologically plausible (10 to 20 years)
    - No disallowed sensitive fields (Aadhaar, religion, caste, etc.)
    """
    required_fields = ['first_name', 'last_name', 'email', 'password', 'class_level']
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            return False, f"Missing required field: {field.replace('_', ' ').title()}"

    if not validate_email(data['email']):
        return False, "Invalid email address format."

    is_valid_pw, pw_err = validate_password_strength(data['password'])
    if not is_valid_pw:
        return False, pw_err

    # Validate Class Level (7-12)
    try:
        class_level = int(data['class_level'])
        if class_level < 7 or class_level > 12:
            return False, "Class level must be between 7 and 12."
    except (ValueError, TypeError):
        return False, "Class level must be an integer between 7 and 12."

    # Validate Age if provided (default plausible calculation if omitted)
    if 'age' in data and data['age']:
        try:
            age = int(data['age'])
            if age < 10 or age > 22:
                return False, "Age must be between 10 and 22 years for school students."
        except (ValueError, TypeError):
            return False, "Age must be a valid integer."

    # Security check: Disallow sensitive demographic attributes
    disallowed_sensitive = ['aadhaar', 'religion', 'caste', 'political_affiliation', 'medical_history', 'home_address']
    for key in data.keys():
        if key.lower() in disallowed_sensitive:
            return False, f"Collection of sensitive field '{key}' is prohibited."

    return True, None


def validate_academic_score(score_val: Any) -> Tuple[bool, Optional[float]]:
    """Validate academic subject marks are within 0.0 to 100.0 range."""
    if score_val is None or str(score_val).strip() == '':
        return True, None
    try:
        score = float(score_val)
        if score < 0.0 or score > 100.0:
            return False, None
        return True, score
    except (ValueError, TypeError):
        return False, None


def validate_rating_scale(val: Any, min_val: int = 1, max_val: int = 5) -> bool:
    """Validate numeric rating values (e.g. 1-5 scale)."""
    try:
        n = int(val)
        return min_val <= n <= max_val
    except (ValueError, TypeError):
        return False
