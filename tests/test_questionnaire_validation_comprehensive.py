"""
Automated Tests: Questionnaire and Input Validation Hardening.
"""

import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.question import QuestionSection, Question, QuestionOption
from backend.models.assessment import AssessmentSession, StudentAnswer
from backend.services.assessment_service import AssessmentService
from backend.utils.validators import (
    validate_student_registration,
    validate_academic_score,
    validate_rating_scale,
    validate_email,
    validate_password_strength
)


class TestQuestionnaireValidationComprehensive(unittest.TestCase):
    """Verifies edge cases and boundary conditions in student input and questionnaire validation."""

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_valid_registration(self):
        data = {
            'first_name': 'Rohan',
            'last_name': 'Mehta',
            'email': 'rohan.mehta@example.com',
            'password': 'Password@123',
            'class_level': 10,
            'age': 15
        }
        is_valid, msg = validate_student_registration(data)
        self.assertTrue(is_valid)
        self.assertIsNone(msg)

    def test_invalid_class_bounds(self):
        # Class too low (< 7)
        data_low = {'first_name': 'Rohan', 'last_name': 'Mehta', 'email': 'r@e.com', 'password': 'Pass1234@', 'class_level': 5}
        is_valid, msg = validate_student_registration(data_low)
        self.assertFalse(is_valid)
        self.assertIn("Class level", msg)

        # Class too high (> 12)
        data_high = {'first_name': 'Rohan', 'last_name': 'Mehta', 'email': 'r@e.com', 'password': 'Pass1234@', 'class_level': 13}
        is_valid, msg = validate_student_registration(data_high)
        self.assertFalse(is_valid)

    def test_disallowed_sensitive_fields(self):
        data = {
            'first_name': 'Rohan',
            'last_name': 'Mehta',
            'email': 'r@e.com',
            'password': 'Pass1234@',
            'class_level': 10,
            'religion': 'Hindu'
        }
        is_valid, msg = validate_student_registration(data)
        self.assertFalse(is_valid)
        self.assertIn("prohibited", msg)

    def test_academic_score_bounds(self):
        # Valid scores
        self.assertTrue(validate_academic_score(95.5)[0])
        self.assertTrue(validate_academic_score(0.0)[0])
        self.assertTrue(validate_academic_score(100.0)[0])

        # Out of bounds
        self.assertFalse(validate_academic_score(-5.0)[0])
        self.assertFalse(validate_academic_score(105.0)[0])
        self.assertFalse(validate_academic_score('not_a_number')[0])

    def test_rating_scale_bounds(self):
        self.assertTrue(validate_rating_scale(1))
        self.assertTrue(validate_rating_scale(5))
        self.assertTrue(validate_rating_scale(3))
        self.assertFalse(validate_rating_scale(0))
        self.assertFalse(validate_rating_scale(6))
        self.assertFalse(validate_rating_scale('invalid'))

    def test_empty_assessment_submission_rejected(self):
        # Create student and empty session
        user = User(username="test_student", email="test@student.com", role="student")
        user.set_password("Password@123")
        db.session.add(user)
        db.session.flush()

        student = Student(user_id=user.id, student_code="STU0099", first_name="Test", last_name="Student", class_level=10)
        db.session.add(student)
        db.session.commit()

        session = AssessmentService.start_new_session(student.id)

        # Attempting to submit empty assessment with 0 answers must raise ValueError
        with self.assertRaises(ValueError) as ctx:
            AssessmentService.complete_and_evaluate_assessment(session.id)
        self.assertIn("Cannot submit an empty assessment", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
