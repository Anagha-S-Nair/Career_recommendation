"""
Adaptive Assessment Engine Routes & APIs.
Handles adaptive question loading, live question stepping, answer autosaving,
review before submission, and final scoring evaluation.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.assessment import AssessmentSession
from backend.models.recommendation import CareerRecommendation
from backend.models.question import Question, QuestionSection
from backend.services.assessment_service import AssessmentService
from backend.services.scoring_service import ScoringService
from backend.services.recommendation_service import RecommendationService
from backend.services.student_profile_service import StudentProfileService
from backend.utils.helpers import student_required, api_response, api_error, logger

assessment_bp = Blueprint('assessment', __name__)


# ------------------------------------------------------------
# HTML View Routes
# ------------------------------------------------------------

def is_academic_profile_complete(student) -> bool:
    """Returns True if the student has provided academic subject marks or overall percentage."""
    if not student or not student.academic_scores:
        return False
    ac = student.academic_scores
    if ac.overall_percentage is not None:
        return True
    subject_scores = [
        ac.mathematics_score, ac.science_score, ac.physics_score, ac.chemistry_score,
        ac.biology_score, ac.computer_science_score, ac.english_score, ac.malayalam_score,
        ac.hindi_score, ac.social_science_score, ac.history_score, ac.geography_score,
        ac.political_science_score, ac.economics_score, ac.accountancy_score,
        ac.business_studies_score, ac.psychology_score
    ]
    return any(s is not None for s in subject_scores)


@assessment_bp.route('/assessment/instructions')
@login_required
@student_required
def instructions_page():
    student = current_user.student
    if not is_academic_profile_complete(student):
        flash('Please complete your academic scores and profile details before starting the assessment.', 'info')
        return redirect(url_for('student.profile_page', onboarding=1))
    return render_template('instructions.html', student=student)


@assessment_bp.route('/assessment/start', methods=['POST', 'GET'])
@login_required
@student_required
def start_assessment_action():
    student = current_user.student
    if not is_academic_profile_complete(student):
        flash('Please complete your academic scores and profile details before starting the assessment.', 'info')
        return redirect(url_for('student.profile_page', onboarding=1))

    # Check if there is already an in-progress session
    active_session = AssessmentSession.query.filter_by(student_id=student.id, status='in_progress').first()
    if not active_session:
        active_session = AssessmentService.start_new_session(student.id)
        logger.info(f"Student {student.student_code} started Assessment Session {active_session.id}")

    return redirect(url_for('assessment.assessment_page', session_id=active_session.id))


@assessment_bp.route('/assessment')
@login_required
@student_required
def assessment_page():
    student = current_user.student
    session_id = request.args.get('session_id')

    session = None
    if session_id:
        session = AssessmentSession.query.filter_by(id=session_id, student_id=student.id).first()

    if not session or session.status != 'in_progress':
        session = AssessmentSession.query.filter_by(student_id=student.id, status='in_progress').first()

    if not session:
        return redirect(url_for('assessment.instructions_page'))

    # Load adaptive questions for student session (using persisted selection)
    questions = AssessmentService.get_questions_for_session(session)

    # Load existing answers
    existing_answers = {
        a.question_id: a.selected_option or a.answer_text
        for a in session.answers.all()
    }

    # Group questions by section
    sections = QuestionSection.query.filter_by(is_active=True).order_by(QuestionSection.display_order.asc()).all()

    return render_template(
        'assessment.html',
        session=session,
        student=student,
        questions=questions,
        sections=sections,
        existing_answers=existing_answers
    )


@assessment_bp.route('/assessment/review')
@login_required
@student_required
def review_page():
    student = current_user.student
    session = AssessmentSession.query.filter_by(student_id=student.id, status='in_progress').order_by(AssessmentSession.id.desc()).first()

    if not session:
        # Check if the student has a completed session, redirect directly to results
        last_completed = AssessmentSession.query.filter_by(student_id=student.id, status='completed').order_by(AssessmentSession.id.desc()).first()
        if last_completed:
            return redirect(url_for('assessment.results_page', assessment_id=last_completed.id))
        flash('No active assessment session to review.', 'info')
        return redirect(url_for('student.dashboard'))

    questions = AssessmentService.get_questions_for_session(session)
    answers_map = {
        a.question_id: a
        for a in session.answers.all()
    }

    return render_template(
        'review.html',
        session=session,
        student=student,
        questions=questions,
        answers_map=answers_map
    )


@assessment_bp.route('/assessment/results/<int:assessment_id>')
@login_required
def results_page(assessment_id):
    session = AssessmentSession.query.get_or_404(assessment_id)

    # Authorization: Student must own the assessment or user must be Admin
    if not current_user.is_admin and (not current_user.student or session.student_id != current_user.student.id):
        flash('You are not authorized to view results of another student.', 'danger')
        return redirect(url_for('student.dashboard'))

    # Fetch recommendations, or auto-generate on the fly if missing for completed session
    detailed_recommendations = RecommendationService.get_detailed_career_explanations(session.id)
    if not detailed_recommendations and session.status == 'completed':
        try:
            RecommendationService.generate_recommendations_for_session(session, top_k=5)
            detailed_recommendations = RecommendationService.get_detailed_career_explanations(session.id)
        except Exception as e:
            logger.error(f"Failed to auto-generate recommendations on results view for session {session.id}: {e}")

    # Generate full student profile
    student_profile = StudentProfileService.generate_student_profile(session.id)

    return render_template(
        'results.html',
        session=session,
        student=session.student,
        profile=student_profile,
        recommendations=detailed_recommendations
    )


@assessment_bp.route('/assessment/<int:assessment_id>/delete', methods=['POST'])
@login_required
def delete_assessment_session(assessment_id):
    """Allows student or admin to delete an assessment attempt."""
    session = db.session.get(AssessmentSession, assessment_id)
    if not session:
        flash('Assessment attempt not found.', 'warning')
        return redirect(url_for('student.dashboard'))

    # Authorization: Student must own the assessment or user must be Admin
    is_owner = current_user.student and session.student_id == current_user.student.id
    if not current_user.is_admin and not is_owner:
        flash('You are not authorized to delete this assessment attempt.', 'danger')
        return redirect(url_for('student.dashboard'))

    try:
        CareerRecommendation.query.filter_by(assessment_id=session.id).delete()
        db.session.delete(session)
        db.session.commit()
        logger.info(f"User {current_user.username} deleted assessment session {assessment_id}")
        flash('Assessment attempt deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete assessment session {assessment_id}: {e}")
        flash('Failed to delete assessment attempt. Please try again.', 'danger')

    return redirect(url_for('student.dashboard'))


# ------------------------------------------------------------
# JSON REST API Endpoints
# ------------------------------------------------------------

@assessment_bp.route('/api/questions/<int:class_level>', methods=['GET'])
def api_get_questions(class_level):
    stream = request.args.get('stream')
    section_name = request.args.get('section')
    questions = AssessmentService.get_adaptive_questions_for_student(
        class_level=class_level,
        stream=stream,
        section_name=section_name
    )
    return api_response(
        data=[q.to_dict(include_correct=False) for q in questions],
        meta={'class_level': class_level, 'count': len(questions)}
    )


@assessment_bp.route('/api/assessment/start', methods=['POST'])
@login_required
def api_start_assessment():
    student = current_user.student
    if not student:
        return api_error("Only enrolled students can start assessments.", status_code=403)

    session = AssessmentService.start_new_session(student.id)
    return api_response(session.to_dict(), message="Assessment session started.", status_code=201)


@assessment_bp.route('/api/assessment/answer', methods=['POST'])
@login_required
def api_save_answer():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')
    answer_text = data.get('answer_text')
    numeric_value = data.get('numeric_value')
    time_taken = data.get('time_taken_seconds', 0)

    if not session_id or not question_id:
        return api_error("Missing session_id or question_id.", status_code=400)

    session = db.session.get(AssessmentSession, session_id)
    if not session or (not current_user.is_admin and session.student_id != current_user.student.id):
        return api_error("Unauthorized access to assessment session.", status_code=403)

    if session.status == 'completed':
        return api_error("Cannot modify answers for a completed assessment.", status_code=400)

    answer = AssessmentService.save_or_update_answer(
        session_id=session.id,
        question_id=question_id,
        selected_option=selected_option,
        answer_text=answer_text,
        numeric_value=numeric_value,
        time_taken_seconds=time_taken
    )

    return api_response({
        'answer': answer.to_dict(),
        'completion_percentage': session.completion_percentage
    }, message="Answer recorded.")


@assessment_bp.route('/api/assessment/submit', methods=['POST'])
@login_required
def api_submit_assessment():
    data = request.get_json() or {}
    session_id = data.get('session_id')

    if not session_id:
        return api_error("Missing session_id parameter.", status_code=400)

    session = db.session.get(AssessmentSession, session_id)
    if not session or (not current_user.is_admin and session.student_id != current_user.student.id):
        return api_error("Unauthorized access to assessment session.", status_code=403)

    if session.status == 'completed':
        return api_response({
            'status': 'completed',
            'session_id': session.id,
            'redirect_url': url_for('assessment.results_page', assessment_id=session.id)
        }, message="Assessment already evaluated.")

    try:
        result_payload = AssessmentService.complete_and_evaluate_assessment(session.id)
        result_payload['redirect_url'] = url_for('assessment.results_page', assessment_id=session.id)
        logger.info(f"Assessment {session.id} submitted and scored successfully for student {session.student_id}")
        return api_response(result_payload, message="Assessment submitted and evaluated successfully.")
    except ValueError as ve:
        return api_error(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Assessment submission error for session {session.id}: {str(e)}")
        return api_error("Failed to complete and evaluate assessment.", status_code=500)


@assessment_bp.route('/api/assessment/<int:id>/scores', methods=['GET'])
@login_required
def api_get_assessment_scores(id):
    session = AssessmentSession.query.get_or_404(id)
    if not current_user.is_admin and (not current_user.student or session.student_id != current_user.student.id):
        return api_error("Unauthorized to access scores.", status_code=403)

    if not session.scores_data:
        return api_error("Scores have not been calculated yet for this session.", status_code=404)

    return api_response(session.scores.to_dict())


@assessment_bp.route('/api/assessment/<int:assessment_id>/profile', methods=['GET'])
@login_required
def api_get_student_profile(assessment_id):
    """
    Returns full synthesized student profile containing:
    academic, abilities, interests, activities, work_preferences, strengths, and development_areas.
    """
    session = AssessmentSession.query.get_or_404(assessment_id)
    if not current_user.is_admin and (not current_user.student or session.student_id != current_user.student.id):
        return api_error("Unauthorized to access student profile.", status_code=403)

    if session.status != 'completed':
        return api_error("Assessment is not completed yet.", status_code=400)

    profile_data = StudentProfileService.generate_student_profile(session.id)
    return api_response(profile_data, message="Student profile synthesized successfully.")
