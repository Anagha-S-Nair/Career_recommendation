import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student


class AuthTestCase(unittest.TestCase):
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

    def test_student_registration_success(self):
        payload = {
            'first_name': 'Aarav',
            'last_name': 'Patel',
            'username': 'aarav_p',
            'email': 'aarav.patel@test.edu',
            'password': 'SecurePassword123',
            'confirm_password': 'SecurePassword123',
            'class_level': 9,
            'age': 14,
            'board': 'CBSE'
        }
        res = self.client.post('/api/auth/register', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user']['username'], 'aarav_p')

        # Verify password is not plain text
        user = User.query.filter_by(username='aarav_p').first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, 'SecurePassword123')
        self.assertTrue(user.check_password('SecurePassword123'))

    def test_duplicate_registration_rejected(self):
        payload = {
            'first_name': 'Aarav',
            'last_name': 'Patel',
            'email': 'aarav@test.edu',
            'password': 'SecurePassword123',
            'class_level': 8
        }
        res1 = self.client.post('/api/auth/register', json=payload)
        self.assertEqual(res1.status_code, 201)

        # Attempt duplicate email
        res2 = self.client.post('/api/auth/register', json=payload)
        self.assertEqual(res2.status_code, 409)

    def test_invalid_class_level_rejected(self):
        payload = {
            'first_name': 'Invalid',
            'last_name': 'Class',
            'email': 'invalid.class@test.edu',
            'password': 'SecurePassword123',
            'class_level': 5  # Below class 7
        }
        res = self.client.post('/api/auth/register', json=payload)
        self.assertEqual(res.status_code, 400)

    def test_login_and_logout(self):
        user = User(username='test_student', email='student@test.edu', role='student')
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

        login_payload = {
            'identifier': 'student@test.edu',
            'password': 'Password123'
        }
        res = self.client.post('/api/auth/login', json=login_payload)
        self.assertEqual(res.status_code, 200)

        # Logout
        res_logout = self.client.post('/api/auth/logout')
        self.assertEqual(res_logout.status_code, 200)


if __name__ == '__main__':
    unittest.main()
