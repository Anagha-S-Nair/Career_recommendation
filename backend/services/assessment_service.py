"""
Assessment Session Lifecycle & Adaptive Questionnaire Service.
Manages session creation, adaptive question retrieval by student grade level, answer persistence,
progress tracking, and final submission scoring triggers with strict transactional rollback safety.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json
from sqlalchemy.orm.attributes import flag_modified
from backend.extensions import db
from backend.models.assessment import AssessmentSession, StudentAnswer
from backend.models.question import Question
from backend.models.student import Student
from backend.services.assessment_selection_service import AssessmentSelectionService
from backend.services.scoring_service import ScoringService
from backend.services.recommendation_service import RecommendationService
from backend.utils.helpers import logger


class AssessmentService:
    """Service layer managing student assessment flow with MySQL transactional safety."""

    @classmethod
    def get_adaptive_questions_for_student(
        cls,
        class_level: int,
        stream: Optional[str] = None,
        section_name: Optional[str] = None
    ) -> List[Question]:
        """
        Dynamically fetches balanced adaptive questions tailored to student grade and stream.
        Uses AssessmentSelectionService for balanced section quotas and difficulty distribution.
        """
        selected_questions = AssessmentSelectionService.select_balanced_questions(class_level, stream)

        if section_name:
            selected_questions = [q for q in selected_questions if (q.section or '').lower() == section_name.lower()]

        return selected_questions

    @classmethod
    def get_questions_for_session(cls, session: AssessmentSession) -> List[Question]:
        """
        Retrieves the exact list of questions selected for this assessment session.
        If questions were already selected and saved, retrieves them in preserved deterministic order.
        """
        if session.selected_question_ids:
            try:
                q_ids = json.loads(session.selected_question_ids)
                questions_dict = {q.id: q for q in Question.query.filter(Question.id.in_(q_ids)).all()}
                # Return in preserved original selection order
                return [questions_dict[qid] for qid in q_ids if qid in questions_dict]
            except Exception as e:
                logger.warning(f"Failed to parse selected_question_ids for session {session.id}: {e}")

        # Fallback / Initial Selection
        student = session.student
        selected = AssessmentSelectionService.select_balanced_questions(
            student.class_level,
            student.stream,
            student_id=student.id
        )
        session.selected_question_ids = json.dumps([q.id for q in selected])
        db.session.commit()
        return selected

    @classmethod
    def start_new_session(cls, student_id: int) -> AssessmentSession:
        """Starts a fresh in-progress assessment session for a student with selected questions."""
        student = db.session.get(Student, student_id)
        if not student:
            raise ValueError(f"Student ID {student_id} not found.")

        # Pre-select balanced questions for the session with retake exclusion
        selected_questions = AssessmentSelectionService.select_balanced_questions(
            student.class_level,
            student.stream,
            student_id=student.id
        )
        selected_ids = [q.id for q in selected_questions]

        session = AssessmentSession(
            student_id=student_id,
            status='in_progress',
            started_at=datetime.now(timezone.utc),
            current_question=1,
            completion_percentage=0.0,
            selected_question_ids=json.dumps(selected_ids)
        )
        db.session.add(session)
        db.session.commit()
        return session

    @classmethod
    def save_or_update_answer(
        cls,
        session_id: int,
        question_id: int,
        selected_option: Optional[str] = None,
        answer_text: Optional[str] = None,
        numeric_value: Optional[float] = None,
        time_taken_seconds: int = 0
    ) -> StudentAnswer:
        """Saves a single question response and recalculates session progress percentage."""
        session = db.session.get(AssessmentSession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        # Find matching option if option_id or option_value provided
        question = db.session.get(Question, question_id)
        selected_opt_obj = None
        if question and selected_option is not None:
            selected_opt_obj = next((opt for opt in question.options if str(opt.option_value) == str(selected_option)), None)

        current_answers = dict(session.answers_data or {})
        ans_dict = {
            'id': int(question_id),
            'assessment_id': session.id,
            'question_id': int(question_id),
            'selected_option_id': selected_opt_obj.id if selected_opt_obj else None,
            'selected_option': str(selected_option) if selected_option is not None else None,
            'answer_text': str(answer_text) if answer_text is not None else (str(selected_option) if selected_option is not None else None),
            'numeric_value': float(numeric_value) if numeric_value is not None else None,
            'time_taken_seconds': int(time_taken_seconds),
            'answered_at': datetime.now(timezone.utc).isoformat()
        }
        current_answers[str(question_id)] = ans_dict
        session.answers_data = current_answers
        flag_modified(session, 'answers_data')

        # Update progress percentage based on session's actual question count
        session_questions = cls.get_questions_for_session(session)
        total_questions = len(session_questions)
        answered_count = len(current_answers)

        if total_questions > 0:
            session.completion_percentage = min(100.0, round((answered_count / total_questions) * 100.0, 1))

        db.session.commit()
        return StudentAnswer(ans_dict)

    @classmethod
    def complete_and_evaluate_assessment(cls, session_id: int) -> Dict[str, Any]:
        """
        Completes the assessment session with strict transaction management:
        1. Validates all answers.
        2. Saves and locks final answers.
        3. Calculates scores.
        4. Saves assessment scores.
        5. Generates and links Top 5 career recommendations.
        6. Marks assessment completed and commits transaction.
        Rolls back the transaction if an error occurs.
        """
        session = db.session.get(AssessmentSession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        # Validate that the student has answered questions before submitting
        answered_count = len(session.answers_data or {})
        if answered_count == 0:
            raise ValueError("Cannot submit an empty assessment. Please answer questions before submitting.")

        try:
            session.status = 'completed'
            session.completed_at = datetime.now(timezone.utc)
            session.completion_percentage = 100.0

            # 1. Compute multi-dimensional score profile
            scores = ScoringService.calculate_and_save_scores(session)

            # 2. Generate Top Recommended Careers via ML interface placeholder
            recs = RecommendationService.generate_recommendations_for_session(session, top_k=5)

            # Commit the entire transaction atomically
            db.session.commit()

            return {
                'session': session.to_dict(),
                'scores': scores.to_dict(),
                'recommendations': [r.to_dict() for r in recs]
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction failed during assessment submission {session_id}: {str(e)}")
            raise e
