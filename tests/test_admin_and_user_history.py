"""
Comprehensive Test Suite for Admin Panel and Student Assessment History.
Verifies user management, user deletion with cascade cleanup, test history inspection,
question bank CRUD, student dashboard multi-attempt rendering, and home page delivery.
"""

import json
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student, AcademicScore
from backend.models.question import QuestionSection, Question, QuestionOption
from backend.models.assessment import AssessmentSession, AssessmentScore, StudentAnswer
from backend.models.recommendation import CareerRecommendation
from backend.models.career import CareerDomain, Career
from database.build_questions_dataset import MASTER_QUESTIONS


class TestAdminAndUserHistory(unittest.TestCase):
    """Test suite for Admin controls and student assessment history."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Seed 19 sections
        for s_id in range(1, 20):
            sec = QuestionSection(id=s_id, name=f"Section {s_id}", display_order=s_id, is_active=True)
            db.session.add(sec)
        db.session.commit()

        # Seed sample careers & domain
        dom = CareerDomain(id=1, domain_name="Technology & Computing", display_order=1)
        db.session.add(dom)
        db.session.commit()

        car = Career(
            id=1,
            career_code="TECH_001",
            career_name="Software Engineer",
            domain_id=1,
            description="Builds software applications.",
            minimum_education="B.Tech CS",
            typical_education="B.Tech / M.Tech",
            is_active=True
        )
        db.session.add(car)
        db.session.commit()

        # Seed sample questions
        for q in MASTER_QUESTIONS[:30]:
            q_obj = Question(
                question_code=q['question_code'],
                question_text=q['question_text'],
                section_id=q['section_id'],
                question_type=q['question_type'],
                class_min=q['class_min'],
                class_max=q['class_max'],
                difficulty=q['difficulty'],
                skill_category=q['skill_category'],
                stream_specific=q.get('stream_specific', 'All'),
                is_required=True,
                display_order=q.get('display_order', 1),
                is_active=True
            )
            db.session.add(q_obj)
            db.session.flush()
            for opt in q.get('options', []):
                opt_obj = QuestionOption(
                    question_id=q_obj.id,
                    option_text=opt['option_text'],
                    option_value=str(opt['option_value']),
                    score=float(opt.get('score', 0.0)),
                    is_correct=bool(opt.get('is_correct', False)),
                    display_order=int(opt.get('display_order', 1))
                )
                db.session.add(opt_obj)
        db.session.commit()

        # Create Admin User
        self.admin_user = User(username='super_admin', email='admin@platform.com', role='admin')
        self.admin_user.set_password('AdminPass123!')
        db.session.add(self.admin_user)

        # Create Student User
        self.student_user = User(username='test_student_1', email='student1@test.com', role='student')
        self.student_user.set_password('StudentPass123!')
        db.session.add(self.student_user)
        db.session.commit()

        self.student = Student(
            user_id=self.student_user.id,
            student_code='STU-TEST-001',
            first_name='Rohan',
            last_name='Sharma',
            class_level=10,
            stream='General',
            board='CBSE',
            medium='English'
        )
        db.session.add(self.student)
        db.session.commit()

        # Add academic marks
        marks = AcademicScore(
            student_id=self.student.id,
            mathematics_score=90.0,
            science_score=88.0,
            computer_science_score=95.0,
            english_score=85.0
        )
        db.session.add(marks)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login_as_admin(self):
        return self.client.post('/api/auth/login', json={
            'identifier': 'super_admin',
            'password': 'AdminPass123!'
        })

    def _login_as_student(self):
        return self.client.post('/api/auth/login', json={
            'identifier': 'test_student_1',
            'password': 'StudentPass123!'
        })

    # ------------------------------------------------------------
    # 1. Home Page Verification
    # ------------------------------------------------------------
    def test_home_page_rendering(self):
        """Verify home page loads with intuitive structure and no errors."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Discover the Right Career & Stream', resp.data)
        self.assertIn(b'How This Helps Students', resp.data)
        self.assertIn(b'How It Works in 3 Steps', resp.data)

    # ------------------------------------------------------------
    # 2. Student Dashboard & Assessment History
    # ------------------------------------------------------------
    def test_student_dashboard_history_rendering(self):
        """Verify student dashboard displays multiple assessment attempts in history log."""
        self._login_as_student()

        t0 = datetime.now(timezone.utc) - timedelta(hours=2)
        t1 = datetime.now(timezone.utc)

        # Create Attempt 1 (Completed)
        sess1 = AssessmentSession(
            student_id=self.student.id,
            status='completed',
            current_question=35,
            completion_percentage=100.0,
            selected_question_ids='[1, 2, 3]',
            created_at=t0
        )
        db.session.add(sess1)
        db.session.flush()

        score1 = AssessmentScore(assessment_id=sess1.id, mathematical_ability=85.0, logical_reasoning=90.0)
        rec1 = CareerRecommendation(assessment_id=sess1.id, career_id=1, rank_position=1, score=92.5)
        db.session.add_all([score1, rec1])
        db.session.commit()

        # Create Attempt 2 (In Progress)
        sess2 = AssessmentSession(
            student_id=self.student.id,
            status='in_progress',
            current_question=10,
            completion_percentage=28.0,
            selected_question_ids='[4, 5, 6]',
            created_at=t1
        )
        db.session.add(sess2)
        db.session.commit()

        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Assessment History & Retake Log', resp.data)
        self.assertIn(b'Attempt #1', resp.data)
        self.assertIn(b'Attempt #2', resp.data)
        self.assertIn(b'Software Engineer', resp.data)
        self.assertIn(b'92.5%', resp.data)

    # ------------------------------------------------------------
    # 3. Admin Dashboard Overview
    # ------------------------------------------------------------
    def test_admin_dashboard_access(self):
        """Verify admin dashboard displays summary metrics and navigation links."""
        self._login_as_admin()
        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Platform Overview & Administrative Controls', resp.data)
        self.assertIn(b'Registered Students', resp.data)
        self.assertIn(b'Master Questions', resp.data)

    # ------------------------------------------------------------
    # 4. Admin User Management (List & Filter)
    # ------------------------------------------------------------
    def test_admin_manage_users_list_and_filter(self):
        """Verify admin user directory displays students and supports filtering."""
        self._login_as_admin()

        resp = self.client.get('/admin/users')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Rohan Sharma', resp.data)
        self.assertIn(b'STU-TEST-001', resp.data)

        # Search filter
        resp_search = self.client.get('/admin/users?search=Rohan')
        self.assertEqual(resp_search.status_code, 200)
        self.assertIn(b'Rohan Sharma', resp_search.data)

        # Non-matching search
        resp_nomatch = self.client.get('/admin/users?search=NonExistentPerson')
        self.assertEqual(resp_nomatch.status_code, 200)
        self.assertIn(b'No Students Found', resp_nomatch.data)

    # ------------------------------------------------------------
    # 5. Admin View User Details & Test Results
    # ------------------------------------------------------------
    def test_admin_view_user_detail_and_test_history(self):
        """Verify admin can view student profile, academic marks, and all assessment attempts."""
        self._login_as_admin()

        sess = AssessmentSession(
            student_id=self.student.id,
            status='completed',
            current_question=35,
            completion_percentage=100.0,
            selected_question_ids='[1, 2]'
        )
        db.session.add(sess)
        db.session.flush()

        score = AssessmentScore(assessment_id=sess.id, mathematical_ability=95.0, logical_reasoning=88.0)
        rec = CareerRecommendation(assessment_id=sess.id, career_id=1, rank_position=1, score=94.0)
        db.session.add_all([score, rec])
        db.session.commit()

        resp = self.client.get(f'/admin/users/{self.student_user.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Rohan Sharma', resp.data)
        self.assertIn(b'Mathematics', resp.data)
        self.assertIn(b'90%', resp.data)
        self.assertIn(b'Attempt #1', resp.data)
        self.assertIn(b'Software Engineer', resp.data)

    # ------------------------------------------------------------
    # 6. Admin Delete User with Cascade Cleanup
    # ------------------------------------------------------------
    def test_admin_delete_user_cascade(self):
        """Verify admin can delete a user and cascade clean their student, session, and recommendation records."""
        self._login_as_admin()

        # Create temporary student to delete
        del_user = User(username='user_to_delete', email='del@test.com', role='student')
        del_user.set_password('Pass1234!')
        db.session.add(del_user)
        db.session.commit()

        del_stu = Student(user_id=del_user.id, student_code='STU-DEL-01', first_name='Delete', last_name='Me', class_level=9)
        db.session.add(del_stu)
        db.session.commit()

        del_sess = AssessmentSession(student_id=del_stu.id, status='completed', completion_percentage=100.0, selected_question_ids='[1]')
        db.session.add(del_sess)
        db.session.commit()

        del_user_id = del_user.id
        del_stu_id = del_stu.id
        del_sess_id = del_sess.id

        # Delete user
        resp = self.client.post(f'/admin/users/{del_user_id}/delete', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'have been deleted', resp.data)

        # Verify DB records removed
        self.assertIsNone(db.session.get(User, del_user_id))
        self.assertIsNone(db.session.get(Student, del_stu_id))
        self.assertIsNone(db.session.get(AssessmentSession, del_sess_id))

    # ------------------------------------------------------------
    # 7. Admin Question Bank Management (Add, Toggle, Delete)
    # ------------------------------------------------------------
    def test_admin_add_toggle_and_delete_question(self):
        """Verify admin can add new question, toggle active state, and delete it."""
        self._login_as_admin()

        # 1. Add MCQ Question
        new_q_data = {
            'question_code': 'TEST_MATH_99',
            'question_text': 'What is the square root of 144?',
            'section_id': 2,
            'question_type': 'MCQ',
            'class_min': 7,
            'class_max': 10,
            'difficulty': 'Easy',
            'skill_category': 'mathematical_ability',
            'stream_specific': 'All',
            'option_1': '12',
            'option_2': '14',
            'option_3': '10',
            'option_4': '16',
            'correct_option': '1'
        }
        resp_add = self.client.post('/admin/questions', data=new_q_data, follow_redirects=True)
        self.assertEqual(resp_add.status_code, 200)
        self.assertIn(b'TEST_MATH_99 successfully added', resp_add.data)

        q_obj = Question.query.filter_by(question_code='TEST_MATH_99').first()
        self.assertIsNotNone(q_obj)
        self.assertEqual(len(q_obj.options), 4)
        correct_opt = [opt for opt in q_obj.options if opt.is_correct]
        self.assertEqual(len(correct_opt), 1)
        self.assertEqual(correct_opt[0].option_text, '12')

        # 2. Toggle Status
        resp_toggle = self.client.post(f'/admin/questions/{q_obj.id}/toggle', follow_redirects=True)
        self.assertEqual(resp_toggle.status_code, 200)
        db.session.refresh(q_obj)
        self.assertFalse(q_obj.is_active)

        # 3. Delete Question
        q_id = q_obj.id
        resp_del = self.client.post(f'/admin/questions/{q_id}/delete', follow_redirects=True)
        self.assertEqual(resp_del.status_code, 200)
        self.assertIn(b'successfully removed', resp_del.data)
        self.assertIsNone(db.session.get(Question, q_id))


if __name__ == '__main__':
    unittest.main()
