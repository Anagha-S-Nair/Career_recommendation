"""
Authentication Routes and APIs.
Handles registration, login, logout, session persistence, and password verification.
"""

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student, AcademicScore
from backend.utils.validators import validate_student_registration
from backend.utils.helpers import api_response, api_error, logger

auth_bp = Blueprint('auth', __name__)


# ------------------------------------------------------------
# HTML View Routes
# ------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()  # email or username
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember', False))

        if not identifier or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier)
        ).first()

        if not user or not user.check_password(password):
            flash('Invalid credentials. Please verify your email/username and password.', 'danger')
            return render_template('login.html')

        login_user(user, remember=remember)
        logger.info(f"User login successful: {user.username} (ID: {user.id})")
        flash(f'Welcome back, {user.username}!', 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('student.dashboard'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip().lower(),
            'password': request.form.get('password', '').strip(),
            'confirm_password': request.form.get('confirm_password', '').strip(),
            'class_level': request.form.get('class_level', '').strip(),
            'age': request.form.get('age', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'board': request.form.get('board', 'CBSE').strip(),
            'medium': request.form.get('medium', 'English').strip(),
            'stream': request.form.get('stream', 'General').strip()
        }

        if data['password'] != data['confirm_password']:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', form_data=data)

        # Generate username if omitted
        if not data['username']:
            data['username'] = f"{data['first_name'].lower()}_{data['last_name'].lower()}_{data['class_level']}"

        is_valid, err_msg = validate_student_registration(data)
        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('register.html', form_data=data)

        if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
            flash('An account with this email or username already exists. Please login.', 'warning')
            return redirect(url_for('auth.login_page'))

        # Create unified user & student profile (Table 1 of 5)
        user = User(
            username=data['username'],
            email=data['email'],
            role='student',
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=int(data['age']) if data['age'] else (int(data['class_level']) + 5),
            gender=data.get('gender'),
            class_level=int(data['class_level']),
            board=data.get('board'),
            medium=data.get('medium'),
            stream=data.get('stream', 'General'),
            academic_scores_data={}
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        # Set student code using generated user.id
        user.student_code = f"STU-{data['class_level']}-{user.id:04d}"
        db.session.commit()

        login_user(user)
        logger.info(f"New student registration: {user.username} (Class {user.class_level})")
        flash('Registration successful! Please fill in your academic scores to prepare your career assessment.', 'success')
        return redirect(url_for('student.profile_page', onboarding=1))

    return render_template('register.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been safely logged out.', 'info')
    return redirect(url_for('main.index'))


# ------------------------------------------------------------
# JSON REST API Endpoints
# ------------------------------------------------------------

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    is_valid, err_msg = validate_student_registration(data)
    if not is_valid:
        return api_error(err_msg, status_code=400)

    username = data.get('username') or f"{data['first_name'].lower()}_{data['last_name'].lower()}_{data['class_level']}"
    if User.query.filter((User.email == data['email'].lower()) | (User.username == username)).first():
        return api_error('Email or username is already registered.', status_code=409, code='USER_EXISTS')

    user = User(username=username, email=data['email'].lower(), role='student')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        student_code=f"STU-{data['class_level']}-{user.id:04d}",
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=int(data.get('age', int(data['class_level']) + 5)),
        gender=data.get('gender'),
        class_level=int(data['class_level']),
        board=data.get('board'),
        medium=data.get('medium'),
        stream=data.get('stream', 'General')
    )
    db.session.add(student)
    db.session.flush()

    academic = AcademicScore(student_id=student.id, overall_percentage=75.0)
    db.session.add(academic)
    db.session.commit()

    return api_response({
        'user': user.to_dict(),
        'student': student.to_dict()
    }, message="Registration successful.", status_code=201)


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '').strip()

    if not identifier or not password:
        return api_error("Both identifier (email/username) and password are required.", status_code=400)

    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()

    if not user or not user.check_password(password):
        return api_error("Invalid credentials.", status_code=401, code="INVALID_CREDENTIALS")

    login_user(user, remember=data.get('remember', False))
    return api_response({
        'user': user.to_dict(),
        'student': user.student.to_dict() if user.student else None
    }, message="Login successful.")


@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return api_response(message="Logged out successfully.")
