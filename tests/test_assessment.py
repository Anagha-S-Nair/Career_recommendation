import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.question import QuestionSection, Question, QuestionOption
from backend.models.assessment import AssessmentSession, StudentAnswer
from backend.services.assessment_service import AssessmentService


class AssessmentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Seed minimal questions
        self.sec = QuestionSection(name="Mathematical Ability", display_order=1)
        db.session.add(self.sec)
        db.session.flush()

        # Class 7-8 question
        self.q_middle = Question(
            question_code="MATH-07-T",
            question_text="Pattern 2, 4, 6, ?",
            section_id=self.sec.id,
            question_type="MCQ",
            class_min=7,
            class_max=8,
            skill_category="mathematical_ability"
        )
        # Class 11-12 question
        self.q_senior = Question(
            question_code="MATH-11-T",
            question_text="Derivative of x^2",
            section_id=self.sec.id,
            question_type="MCQ",
            class_min=11,
            class_max=12,
            skill_category="mathematical_ability"
        )
        db.session.add_all([self.q_middle, self.q_senior])
        db.session.flush()

        opt1 = QuestionOption(question_id=self.q_middle.id, option_text="8", option_value="8", score=1.0, is_correct=True)
        opt2 = QuestionOption(question_id=self.q_middle.id, option_text="7", option_value="7", score=0.0, is_correct=False)
        db.session.add_all([opt1, opt2])

        # Create student user
        self.user = User(username='test_stu', email='stu@test.edu', role='student')
        self.user.set_password('Pass1234')
        db.session.add(self.user)
        db.session.flush()

        self.student = Student(
            user_id=self.user.id,
            student_code='STU-TEST-01',
            first_name='Test',
            last_name='Student',
            age=13,
            class_level=8
        )
        db.session.add(self.student)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_adaptive_class_filtering(self):
        # Class 8 student should only receive Class 7-8 questions, NOT Class 11-12
        q_for_class8 = AssessmentService.get_adaptive_questions_for_student(8)
        self.assertEqual(len(q_for_class8), 1)
        self.assertEqual(q_for_class8[0].question_code, "MATH-07-T")

        # Class 12 student should only receive Class 11-12 questions
        q_for_class12 = AssessmentService.get_adaptive_questions_for_student(12)
        self.assertEqual(len(q_for_class12), 1)
        self.assertEqual(q_for_class12[0].question_code, "MATH-11-T")

    def test_assessment_session_flow(self):
        session = AssessmentService.start_new_session(self.student.id)
        self.assertEqual(session.status, 'in_progress')

        # Answer question
        ans = AssessmentService.save_or_update_answer(
            session_id=session.id,
            question_id=self.q_middle.id,
            selected_option="8",
            time_taken_seconds=15
        )
        self.assertIsNotNone(ans)
        self.assertEqual(ans.selected_option, "8")
        self.assertEqual(session.completion_percentage, 100.0)

    def test_delete_assessment_session(self):
        # Login
        self.client.post('/login', data={'identifier': 'test_stu', 'password': 'Pass1234'}, follow_redirects=True)
        session = AssessmentService.start_new_session(self.student.id)
        self.assertIsNotNone(db.session.get(AssessmentSession, session.id))

        # Delete session
        res = self.client.post(f'/assessment/{session.id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Assert deleted from DB
        self.assertIsNone(db.session.get(AssessmentSession, session.id))


if __name__ == '__main__':
    unittest.main()
