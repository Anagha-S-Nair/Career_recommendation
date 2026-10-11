import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.question import QuestionSection, Question, QuestionOption
from backend.models.assessment import AssessmentSession, StudentAnswer, AssessmentScore
from backend.services.scoring_service import ScoringService


class ScoringTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        sec = QuestionSection(name="Mathematical Ability", display_order=1)
        db.session.add(sec)
        db.session.flush()

        q = Question(
            question_code="MATH-Q1",
            question_text="Sample Math Question",
            section_id=sec.id,
            question_type="MCQ",
            class_min=7,
            class_max=12,
            skill_category="mathematical_ability"
        )
        db.session.add(q)
        db.session.flush()

        opt_correct = QuestionOption(question_id=q.id, option_text="Correct", option_value="C", score=1.0, is_correct=True)
        opt_wrong = QuestionOption(question_id=q.id, option_text="Wrong", option_value="W", score=0.0, is_correct=False)
        db.session.add_all([opt_correct, opt_wrong])

        user = User(username='test_user', email='user@test.edu')
        user.set_password('Pass123')
        db.session.add(user)
        db.session.flush()

        student = Student(user_id=user.id, student_code='STU-001', first_name='A', last_name='B', age=14, class_level=8)
        db.session.add(student)
        db.session.flush()

        self.session = AssessmentSession(student_id=student.id, status='in_progress')
        db.session.add(self.session)
        db.session.flush()

        # Add correct answer
        ans = StudentAnswer(assessment_id=self.session.id, question_id=q.id, selected_option="C")
        db.session.add(ans)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_score_calculation_normalization(self):
        score_record = ScoringService.calculate_and_save_scores(self.session)
        self.assertIsNotNone(score_record)
        # Should be 100.0 for mathematical_ability because 1 out of 1 answered correctly
        self.assertEqual(score_record.mathematical_ability, 100.0)

    def test_score_guidance_categories(self):
        cat_excellent = ScoringService.get_score_category(95.0)
        self.assertEqual(cat_excellent['label'], 'Excellent')

        cat_good = ScoringService.get_score_category(75.0)
        self.assertEqual(cat_good['label'], 'Good')

        cat_avg = ScoringService.get_score_category(50.0)
        self.assertEqual(cat_avg['label'], 'Average')

        cat_low = ScoringService.get_score_category(30.0)
        self.assertEqual(cat_low['label'], 'Low')


if __name__ == '__main__':
    unittest.main()
