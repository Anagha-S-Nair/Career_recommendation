"""
Admin Control Panel Routes.
Provides full administrative control: user management (view details, test history, delete users),
question bank CRUD (create, filter, toggle, delete), career profile controls, and session analytics.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.assessment import AssessmentSession
from backend.models.question import Question, QuestionSection
from backend.models.career import CareerDomain, Career
from backend.models.recommendation import CareerRecommendation
from backend.utils.helpers import admin_required, api_response, api_error, logger

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ------------------------------------------------------------
# 1. Admin Dashboard Overview
# ------------------------------------------------------------

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_assessments = AssessmentSession.query.count()
    completed_assessments = AssessmentSession.query.filter_by(status='completed').count()
    total_careers = Career.query.count()
    total_questions = Question.query.count()
    domains = CareerDomain.query.all()

    # Recent assessments with student profiles
    recent_sessions = AssessmentSession.query.order_by(AssessmentSession.started_at.desc(), AssessmentSession.id.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_assessments=total_assessments,
        completed_assessments=completed_assessments,
        total_careers=total_careers,
        total_questions=total_questions,
        domains=domains,
        recent_sessions=recent_sessions
    )


# ------------------------------------------------------------
# 2. User Management (List, View Details & Test History, Delete)
# ------------------------------------------------------------

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """List all registered students with search, filters, and attempt statistics."""
    search = request.args.get('search', '').strip()
    class_filter = request.args.get('class_level', type=int)

    query = User.query.filter(User.role == 'student')

    if search:
        query = query.filter(
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%")) |
            (User.student_code.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )

    if class_filter:
        query = query.filter(User.class_level == class_filter)

    students = query.order_by(User.created_at.desc()).all()

    # Build stats per student
    student_records = []
    for s in students:
        assessments_count = s.assessments.count()
        completed_count = s.assessments.filter_by(status='completed').count()
        latest_sess = s.assessments.order_by(AssessmentSession.started_at.desc(), AssessmentSession.id.desc()).first()
        student_records.append({
            'student': s,
            'user': s.user,
            'assessments_count': assessments_count,
            'completed_count': completed_count,
            'latest_sess': latest_sess
        })

    return render_template(
        'admin/users.html',
        student_records=student_records,
        search=search,
        class_filter=class_filter
    )


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user_detail(user_id):
    """View full student profile, academic marks, and all test session histories with results."""
    user = db.session.get(User, user_id)
    if not user:
        flash(f'User ID {user_id} not found.', 'danger')
        return redirect(url_for('admin.manage_users'))

    student = user.student
    if not student:
        flash('Student profile not found for this user account.', 'warning')
        return redirect(url_for('admin.manage_users'))

    # Retrieve all assessment sessions with scores and recommendations
    sessions = AssessmentSession.query.filter_by(student_id=student.id).order_by(AssessmentSession.started_at.desc(), AssessmentSession.id.desc()).all()

    session_details = []
    for idx, sess in enumerate(reversed(sessions), 1):
        top_recs = CareerRecommendation.query.filter_by(assessment_id=sess.id).order_by(CareerRecommendation.rank_position.asc()).limit(5).all()
        session_details.append({
            'attempt_number': idx,
            'session': sess,
            'scores': sess.scores,
            'top_recs': top_recs,
            'answers_count': sess.answers.count()
        })
    session_details.reverse()  # Most recent attempt on top

    return render_template(
        'admin/user_detail.html',
        user=user,
        student=student,
        academic=student.academic_scores,
        session_details=session_details
    )


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account and cascade clean all student records, tests, and answers."""
    user = db.session.get(User, user_id)
    if not user:
        flash(f'User ID {user_id} not found.', 'danger')
        return redirect(url_for('admin.manage_users'))

    if user.id == current_user.id:
        flash('You cannot delete your own logged-in administrator account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    logger.info(f"Admin {current_user.username} deleted user {username} (ID: {user_id})")
    flash(f"User account '{username}' and all associated assessment records have been deleted.", 'success')
    return redirect(url_for('admin.manage_users'))


# ------------------------------------------------------------
# 3. Assessment Session Details (Answers & Scores Inspection)
# ------------------------------------------------------------

@admin_bp.route('/assessments/<int:session_id>')
@login_required
@admin_required
def view_session_detail(session_id):
    """View exact questions, submitted answers, and calculated scores for a specific test session."""
    session = db.session.get(AssessmentSession, session_id)
    if not session:
        flash(f'Assessment Session #{session_id} not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    student = session.student
    scores = session.scores
    recommendations = CareerRecommendation.query.filter_by(assessment_id=session.id).order_by(CareerRecommendation.rank_position.asc()).all()

    # Answers map directly from session JSON
    answers = session.answers.all()
    answers_by_qid = {a.question_id: a for a in answers}

    # Fetch all questions in session
    from backend.services.assessment_service import AssessmentService
    questions = AssessmentService.get_questions_for_session(session)

    qa_list = []
    for q in questions:
        ans = answers_by_qid.get(q.id)
        selected_opt_obj = None
        is_correct = None
        if ans and ans.selected_option:
            for opt in q.options:
                if str(opt.option_value).strip().lower() == str(ans.selected_option).strip().lower():
                    selected_opt_obj = opt
                    is_correct = opt.is_correct
                    break
        qa_list.append({
            'question': q,
            'answer': ans,
            'selected_option': selected_opt_obj,
            'is_correct': is_correct
        })

    return render_template(
        'admin/session_detail.html',
        session=session,
        student=student,
        scores=scores,
        recommendations=recommendations,
        qa_list=qa_list
    )



# ------------------------------------------------------------
# 4. Question Bank Management (CRUD, Filters, Toggle, Delete)
# ------------------------------------------------------------

@admin_bp.route('/questions', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_questions():
    if request.method == 'POST':
        text = request.form.get('question_text', '').strip()
        sec_id = int(request.form.get('section_id'))
        q_type = request.form.get('question_type', 'MCQ')
        c_min = int(request.form.get('class_min', 7))
        c_max = int(request.form.get('class_max', 12))
        diff = request.form.get('difficulty', 'Medium')
        skill = request.form.get('skill_category', '').strip()
        stream = request.form.get('stream_specific', 'All').strip()

        if not text:
            flash('Question text is required.', 'danger')
            return redirect(url_for('admin.manage_questions'))

        q = Question(
            question_text=text,
            section_id=sec_id,
            question_type=q_type,
            class_min=c_min,
            class_max=c_max,
            difficulty=diff,
            skill_category=skill,
            stream_specific=stream,
            is_active=True
        )
        db.session.add(q)
        db.session.flush()

        # Add options if MCQ / Scenario
        opts_list = []
        if q_type in ['MCQ', 'SCENARIO']:
            opt1 = request.form.get('option_1', '').strip()
            opt2 = request.form.get('option_2', '').strip()
            opt3 = request.form.get('option_3', '').strip()
            opt4 = request.form.get('option_4', '').strip()
            correct_opt = int(request.form.get('correct_option', 1))

            raw_opts = [opt1, opt2, opt3, opt4]
            for idx, opt_text in enumerate(raw_opts, 1):
                if opt_text:
                    is_c = (idx == correct_opt)
                    opts_list.append({
                        'id': idx,
                        'option_text': opt_text,
                        'option_value': str(idx),
                        'score': 100.0 if is_c else 0.0,
                        'is_correct': is_c,
                        'display_order': idx
                    })
        elif q_type == 'RATING':
            labels = ["Strongly Disagree / Low", "Disagree / Slight", "Neutral / Moderate", "Agree / Strong", "Strongly Agree / Very High"]
            for idx, label in enumerate(labels, 1):
                opts_list.append({
                    'id': idx,
                    'option_text': label,
                    'option_value': str(idx),
                    'score': float(idx * 20),
                    'is_correct': False,
                    'display_order': idx
                })

        q.options = opts_list
        db.session.commit()
        logger.info(f"Admin {current_user.username} created new question: {q.question_code}")
        flash(f'Question {q.question_code} successfully added to the master question bank!', 'success')
        return redirect(url_for('admin.manage_questions'))

    # GET: Filter questions
    class_filter = request.args.get('class_level', type=int)
    sec_filter = request.args.get('section_id', type=int)
    diff_filter = request.args.get('difficulty', '').strip()
    search = request.args.get('search', '').strip()

    query = Question.query
    if class_filter:
        query = query.filter(Question.class_min <= class_filter, Question.class_max >= class_filter)
    if sec_filter:
        query = query.filter(Question.section_id == sec_filter)
    if diff_filter:
        query = query.filter(Question.difficulty == diff_filter)
    if search:
        query = query.filter(Question.question_text.ilike(f"%{search}%"))

    questions = query.order_by(Question.section_id.asc(), Question.display_order.asc(), Question.id.asc()).all()
    sections = QuestionSection.query.order_by(QuestionSection.display_order.asc()).all()

    return render_template(
        'admin/questions.html',
        questions=questions,
        sections=sections,
        class_filter=class_filter,
        sec_filter=sec_filter,
        diff_filter=diff_filter,
        search=search
    )


@admin_bp.route('/questions/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_question_status(id):
    question = db.session.get(Question, id)
    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('admin.manage_questions'))

    question.is_active = not question.is_active
    db.session.commit()
    logger.info(f"Admin {current_user.username} toggled status of question {question.question_code} to {question.is_active}")
    flash(f"Question {question.question_code} is now {'Active' if question.is_active else 'Inactive'}.", 'info')
    return redirect(url_for('admin.manage_questions'))


@admin_bp.route('/questions/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(id):
    """Delete a question from the bank."""
    question = db.session.get(Question, id)
    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('admin.manage_questions'))

    code = question.question_code
    db.session.delete(question)
    db.session.commit()

    logger.info(f"Admin {current_user.username} deleted question {code}")
    flash(f"Question '{code}' was successfully removed from the question bank.", 'success')
    return redirect(url_for('admin.manage_questions'))


# ------------------------------------------------------------
# 5. Career Profile Management
# ------------------------------------------------------------

@admin_bp.route('/careers', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_careers():
    if request.method == 'POST':
        code = request.form.get('career_code', '').strip().upper()
        name = request.form.get('career_name', '').strip()
        domain_id = int(request.form.get('domain_id'))
        desc = request.form.get('description', '').strip()
        min_edu = request.form.get('minimum_education', '').strip()
        typ_edu = request.form.get('typical_education', '').strip()
        pathway = request.form.get('pathway', '').strip()

        career = Career(
            career_code=code,
            career_name=name,
            domain_id=domain_id,
            description=desc,
            minimum_education=min_edu,
            typical_education=typ_edu,
            is_active=True
        )
        db.session.add(career)
        db.session.commit()
        flash(f'Career profile for {name} created successfully!', 'success')
        return redirect(url_for('admin.manage_careers'))

    careers = Career.query.order_by(Career.domain_id.asc(), Career.career_name.asc()).all()
    domains = CareerDomain.query.all()
    return render_template('admin/careers.html', careers=careers, domains=domains)
