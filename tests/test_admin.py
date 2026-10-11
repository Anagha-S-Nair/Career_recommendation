import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.question import QuestionSection, Question


class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Admin user
        self.admin = User(username='admin_user', email='admin@test.edu', role='admin')
        self.admin.set_password('AdminPass123')

        # Student user
        self.student_user = User(username='stu_user', email='stu@test.edu', role='student')
        self.student_user.set_password('StuPass123')

        db.session.add_all([self.admin, self.student_user])
        db.session.flush()

        self.student = Student(user_id=self.student_user.id, student_code='STU-001', first_name='S', last_name='T', age=14, class_level=8)
        sec = QuestionSection(name="Logic", display_order=1)
        db.session.add_all([self.student, sec])
        db.session.flush()

        self.q = Question(question_code="LOG-T1", question_text="Logic Q", section_id=sec.id, is_active=True)
        db.session.add(self.q)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_unauthenticated_admin_blocked(self):
        res = self.client.get('/admin/')
        # Redirect to login
        self.assertEqual(res.status_code, 302)

    def test_student_forbidden_from_admin(self):
        # Login as student
        self.client.post('/api/auth/login', json={'identifier': 'stu@test.edu', 'password': 'StuPass123'})
        res = self.client.get('/admin/')
        # Redirected or blocked with warning
        self.assertEqual(res.status_code, 302)

    def test_admin_access_allowed(self):
        # Login as admin
        self.client.post('/api/auth/login', json={'identifier': 'admin@test.edu', 'password': 'AdminPass123'})
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 200)

    def test_admin_toggle_question_status(self):
        self.client.post('/api/auth/login', json={'identifier': 'admin@test.edu', 'password': 'AdminPass123'})
        res = self.client.post(f'/admin/questions/{self.q.id}/toggle')
        self.assertEqual(res.status_code, 302)

        # Verify status flipped
        q_updated = Question.query.get(self.q.id)
        self.assertFalse(q_updated.is_active)


if __name__ == '__main__':
    unittest.main()
