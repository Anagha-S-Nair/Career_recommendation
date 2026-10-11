"""
Deterministic Scoring and Dimension Separation Test Suite.
Verifies exact score calculation and normalization (0%, 50%, 80%, 100%) across
cognitive ability dimensions and confirms strict separation between ability and interest metrics.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.question import Question, QuestionSection, QuestionOption
from backend.models.assessment import AssessmentSession, StudentAnswer, AssessmentScore
from backend.services.scoring_service import ScoringService
from backend.services.assessment_service import AssessmentService


class TestDeterministicScoring(unittest.TestCase):
    """Deterministic validation test suite for scoring engine."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        import uuid
        uid = uuid.uuid4().hex[:6]
        # Create student user
        self.user = User(username=f'user_{uid}', email=f'{uid}@test.com', role='student')
        self.user.set_password('Pass1234!')
        db.session.add(self.user)
        db.session.flush()

        self.student = Student(
            user_id=self.user.id,
            student_code=f'STU-{uid.upper()}',
            first_name='Test',
            last_name='Student',
            class_level=10,
            stream='General'
        )
        db.session.add(self.student)
        db.session.commit()

        # Create sections
        self.sec_math = QuestionSection(name=f"Math Section {uid}", display_order=1, is_active=True)
        self.sec_logic = QuestionSection(name=f"Logic Section {uid}", display_order=2, is_active=True)
        self.sec_interest = QuestionSection(name=f"Interest Section {uid}", display_order=3, is_active=True)
        db.session.add_all([self.sec_math, self.sec_logic, self.sec_interest])
        db.session.commit()

    def _create_mcq_questions(self, count: int, category: str, section_id: int, prefix: str):
        """Helper to create a batch of standard 1.0 point MCQ questions."""
        questions = []
        for i in range(1, count + 1):
            q = Question(
                question_code=f"{prefix}_{i}_{self._testMethodName}",
                question_text=f"Test question {i} for {category}",
                section_id=section_id,
                question_type="MCQ",
                class_min=7,
                class_max=12,
                difficulty="Medium",
                skill_category=category,
                stream_specific="All",
                is_required=True,
                display_order=i,
                is_active=True
            )
            db.session.add(q)
            db.session.flush()

            # Option A: Correct (score = 1.0)
            opt_a = QuestionOption(question_id=q.id, option_text="Correct", option_value="A", score=1.0, is_correct=True, display_order=1)
            # Option B: Incorrect (score = 0.0)
            opt_b = QuestionOption(question_id=q.id, option_text="Incorrect", option_value="B", score=0.0, is_correct=False, display_order=2)
            db.session.add_all([opt_a, opt_b])
            questions.append(q)

        db.session.commit()
        return questions

    def test_score_normalization_100_percent(self):
        """Synthetic student answers 100% of mathematics questions correctly -> Score = 100.0."""
        math_questions = self._create_mcq_questions(4, 'mathematical_ability', self.sec_math.id, 'MATH100')
        session = AssessmentSession(student_id=self.student.id, status='in_progress')
        db.session.add(session)
        db.session.commit()

        # Answer all correctly
        for q in math_questions:
            ans = StudentAnswer(assessment_id=session.id, question_id=q.id, selected_option='A')
            db.session.add(ans)
        db.session.commit()

        scores = ScoringService.calculate_and_save_scores(session.id)
        self.assertEqual(scores.mathematical_ability, 100.0, f"Expected 100.0, got {scores.mathematical_ability}")

    def test_score_normalization_0_percent(self):
        """Synthetic student answers 0% of mathematics questions correctly -> Score = 0.0."""
        math_questions = self._create_mcq_questions(4, 'mathematical_ability', self.sec_math.id, 'MATH0')
        session = AssessmentSession(student_id=self.student.id, status='in_progress')
        db.session.add(session)
        db.session.commit()

        # Answer all incorrectly
        for q in math_questions:
            ans = StudentAnswer(assessment_id=session.id, question_id=q.id, selected_option='B')
            db.session.add(ans)
        db.session.commit()

        scores = ScoringService.calculate_and_save_scores(session.id)
        self.assertEqual(scores.mathematical_ability, 0.0, f"Expected 0.0, got {scores.mathematical_ability}")

    def test_score_normalization_50_percent(self):
        """Synthetic student answers exactly 50% correctly (2 out of 4) -> Score = 50.0."""
        logic_questions = self._create_mcq_questions(4, 'logical_reasoning', self.sec_logic.id, 'LOGIC50')
        session = AssessmentSession(student_id=self.student.id, status='in_progress')
        db.session.add(session)
        db.session.commit()

        # Answer 2 correct ('A') and 2 incorrect ('B')
        for idx, q in enumerate(logic_questions):
            opt = 'A' if idx < 2 else 'B'
            ans = StudentAnswer(assessment_id=session.id, question_id=q.id, selected_option=opt)
            db.session.add(ans)
        db.session.commit()

        scores = ScoringService.calculate_and_save_scores(session.id)
        self.assertEqual(scores.logical_reasoning, 50.0, f"Expected 50.0, got {scores.logical_reasoning}")

    def test_score_normalization_80_percent(self):
        """Synthetic student answers 4 out of 5 correctly -> Score = 80.0."""
        sci_questions = self._create_mcq_questions(5, 'scientific_reasoning', self.sec_logic.id, 'SCI80')
        session = AssessmentSession(student_id=self.student.id, status='in_progress')
        db.session.add(session)
        db.session.commit()

        # 4 correct, 1 incorrect
        for idx, q in enumerate(sci_questions):
            opt = 'A' if idx < 4 else 'B'
            ans = StudentAnswer(assessment_id=session.id, question_id=q.id, selected_option=opt)
            db.session.add(ans)
        db.session.commit()

        scores = ScoringService.calculate_and_save_scores(session.id)
        self.assertEqual(scores.scientific_reasoning, 80.0, f"Expected 80.0, got {scores.scientific_reasoning}")

    def test_separate_ability_and_interest_calculation(self):
        """
        Verify that mathematical ability and technology interest are evaluated independently.
        High Math ability does NOT artificially inflate Math/Tech interest, and vice versa.
        """
        # Math ability question (1 correct answer = 100%)
        q_math = Question(
            question_code=f"MATH_SEP_{self._testMethodName}",
            question_text="Math question",
            section_id=self.sec_math.id,
            question_type="MCQ",
            class_min=7, class_max=12,
            difficulty="Medium",
            skill_category="mathematical_ability",
            stream_specific="All",
            is_required=True,
            display_order=1,
            is_active=True
        )
        db.session.add(q_math)
        db.session.flush()
        db.session.add(QuestionOption(question_id=q_math.id, option_text="Correct", option_value="A", score=1.0, is_correct=True, display_order=1))

        # Technology interest question (Rating 1 out of 5 = 20%)
        q_interest = Question(
            question_code=f"INT_TECH_SEP_{self._testMethodName}",
            question_text="Tech interest rating",
            section_id=self.sec_interest.id,
            question_type="RATING",
            class_min=7, class_max=12,
            difficulty="Easy",
            skill_category="technology_interest",
            stream_specific="All",
            is_required=True,
            display_order=2,
            is_active=True
        )
        db.session.add(q_interest)
        db.session.flush()
        db.session.add(QuestionOption(question_id=q_interest.id, option_text="Low", option_value="1", score=20.0, is_correct=False, display_order=1))
        db.session.commit()

        session = AssessmentSession(student_id=self.student.id, status='in_progress')
        db.session.add(session)
        db.session.commit()

        # Student scores 100% on Math, but only 20% on Tech Interest
        db.session.add(StudentAnswer(assessment_id=session.id, question_id=q_math.id, selected_option='A'))
        db.session.add(StudentAnswer(assessment_id=session.id, question_id=q_interest.id, selected_option='1'))
        db.session.commit()

        scores = ScoringService.calculate_and_save_scores(session.id)
        self.assertEqual(scores.mathematical_ability, 100.0)
        self.assertEqual(scores.technology_interest, 20.0)
        # Verify no cross-pollution
        self.assertNotEqual(scores.mathematical_ability, scores.technology_interest)


if __name__ == '__main__':
    unittest.main()
