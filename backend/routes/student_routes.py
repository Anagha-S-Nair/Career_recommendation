"""
Student Profile & Dashboard Routes.
Displays student overview, assessment progress, multi-attempt history, score highlights, and profile settings.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.assessment import AssessmentSession
from backend.models.recommendation import CareerRecommendation
from backend.models.student import AcademicScore
from backend.utils.helpers import student_required, api_response, api_error, logger
from backend.utils.validators import validate_academic_score

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    student = current_user.student
    if not student:
        flash('Student profile not found. Please contact support.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch all sessions in reverse chronological order
    all_sessions = AssessmentSession.query.filter_by(student_id=student.id).order_by(AssessmentSession.started_at.desc(), AssessmentSession.id.desc()).all()
    latest_session = all_sessions[0] if all_sessions else None

    # Build rich attempt history objects with top career recommendation for each completed session
    history_items = []
    for idx, sess in enumerate(reversed(all_sessions), 1):
        top_rec = None
        score_obj = None
        if sess.status == 'completed':
            top_rec = CareerRecommendation.query.filter_by(assessment_id=sess.id, rank_position=1).first()
            score_obj = sess.scores if sess.scores_data else None
        history_items.append({
            'attempt_number': idx,
            'session': sess,
            'top_rec': top_rec,
            'score_obj': score_obj
        })
    history_items.reverse()  # Most recent attempt on top

    recent_scores = None
    recent_recs = []
    if latest_session and latest_session.status == 'completed':
        recent_scores = latest_session.scores if latest_session.scores_data else None
        recent_recs = CareerRecommendation.query.filter_by(assessment_id=latest_session.id).order_by(CareerRecommendation.rank_position.asc()).limit(3).all()

    return render_template(
        'dashboard.html',
        student=student,
        latest_session=latest_session,
        all_sessions=all_sessions,
        history_items=history_items,
        recent_scores=recent_scores,
        recent_recs=recent_recs
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    student = current_user.student
    if not student:
        return redirect(url_for('main.index'))

    is_onboarding = request.args.get('onboarding') == '1' or request.form.get('onboarding') == '1'

    if request.method == 'POST':
        student.first_name = request.form.get('first_name', student.first_name).strip()
        student.last_name = request.form.get('last_name', student.last_name).strip()
        student.board = request.form.get('board', student.board or 'CBSE').strip()
        student.medium = request.form.get('medium', student.medium or 'English').strip()
        
        if request.form.get('age'):
            try:
                student.age = int(request.form.get('age'))
            except (ValueError, TypeError):
                pass
                
        if request.form.get('gender'):
            student.gender = request.form.get('gender').strip()

        if request.form.get('class_level'):
            try:
                new_class = int(request.form.get('class_level'))
                if 7 <= new_class <= 12:
                    student.class_level = new_class
            except (ValueError, TypeError):
                pass

        # Update stream if Grade 11/12
        if student.class_level in [11, 12]:
            student.stream = request.form.get('stream', student.stream or 'Science-PCM').strip()
        else:
            student.stream = 'General'

        # Helper to parse float or None
        def parse_score(val):
            if val is not None and str(val).strip() != '':
                try:
                    score = float(val)
                    return max(0.0, min(100.0, score))
                except (ValueError, TypeError):
                    return None
            return None

        # Update all 17 academic subject scores
        ac = student.academic_scores or AcademicScore(student_id=student.id)
        
        ac.mathematics_score = parse_score(request.form.get('math_score'))
        ac.science_score = parse_score(request.form.get('science_score'))
        ac.physics_score = parse_score(request.form.get('physics_score'))
        ac.chemistry_score = parse_score(request.form.get('chemistry_score'))
        ac.biology_score = parse_score(request.form.get('biology_score'))
        ac.computer_science_score = parse_score(request.form.get('cs_score'))
        ac.english_score = parse_score(request.form.get('english_score'))
        ac.malayalam_score = parse_score(request.form.get('malayalam_score'))
        ac.hindi_score = parse_score(request.form.get('hindi_score'))
        ac.social_science_score = parse_score(request.form.get('social_science_score'))
        ac.history_score = parse_score(request.form.get('history_score'))
        ac.geography_score = parse_score(request.form.get('geography_score'))
        ac.political_science_score = parse_score(request.form.get('polscience_score'))
        ac.economics_score = parse_score(request.form.get('economics_score'))
        ac.accountancy_score = parse_score(request.form.get('accountancy_score'))
        ac.business_studies_score = parse_score(request.form.get('business_score'))
        ac.psychology_score = parse_score(request.form.get('psychology_score'))

        # Calculate Overall Percentage across all entered subjects
        entered_scores = [
            s for s in [
                ac.mathematics_score, ac.science_score, ac.physics_score, ac.chemistry_score,
                ac.biology_score, ac.computer_science_score, ac.english_score, ac.malayalam_score,
                ac.hindi_score, ac.social_science_score, ac.history_score, ac.geography_score,
                ac.political_science_score, ac.economics_score, ac.accountancy_score,
                ac.business_studies_score, ac.psychology_score
            ] if s is not None
        ]

        if entered_scores:
            ac.overall_percentage = round(sum(entered_scores) / len(entered_scores), 2)
        elif request.form.get('overall_percentage'):
            ac.overall_percentage = parse_score(request.form.get('overall_percentage'))
        else:
            ac.overall_percentage = 75.0

        if not student.academic_scores:
            db.session.add(ac)

        db.session.commit()
        
        if is_onboarding:
            flash('Profile and academic marks saved successfully! You are now ready to begin your career assessment.', 'success')
            return redirect(url_for('assessment.instructions_page'))
            
        flash('Profile and academic records updated successfully!', 'success')
        return redirect(url_for('student.profile_page'))

    return render_template(
        'profile.html',
        student=student,
        academic=student.academic_scores,
        is_onboarding=is_onboarding
    )


# ------------------------------------------------------------
# JSON REST API Endpoints
# ------------------------------------------------------------

@student_bp.route('/api/student/profile', methods=['GET'])
@login_required
def api_get_profile():
    if not current_user.student:
        return api_error("Student profile not found.", status_code=404)
    data = current_user.student.to_dict()
    if current_user.student.academic_scores:
        data['academic_scores'] = current_user.student.academic_scores.to_dict()
    return api_response(data)


@student_bp.route('/api/student/profile', methods=['PUT'])
@login_required
def api_update_profile():
    student = current_user.student
    if not student:
        return api_error("Student profile not found.", status_code=404)

    data = request.get_json() or {}
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'class_level' in data:
        student.class_level = int(data['class_level'])
    if 'stream' in data:
        student.stream = data['stream']
    if 'board' in data:
        student.board = data['board']
    if 'medium' in data:
        student.medium = data['medium']
    if 'age' in data:
        student.age = int(data['age'])
    if 'gender' in data:
        student.gender = data['gender']

    if 'academic_scores' in data and isinstance(data['academic_scores'], dict):
        ac_data = data['academic_scores']
        ac = student.academic_scores or AcademicScore(student_id=student.id)
        for field in [
            'mathematics_score', 'science_score', 'physics_score', 'chemistry_score',
            'biology_score', 'computer_science_score', 'english_score', 'malayalam_score',
            'hindi_score', 'social_science_score', 'history_score', 'geography_score',
            'political_science_score', 'economics_score', 'accountancy_score',
            'business_studies_score', 'psychology_score', 'overall_percentage'
        ]:
            if field in ac_data:
                setattr(ac, field, float(ac_data[field]) if ac_data[field] is not None else None)
        if not student.academic_scores:
            db.session.add(ac)

    db.session.commit()
    return api_response(student.to_dict())
