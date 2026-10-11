"""
Automated End-to-End Test: Full Real Student Lifecycle Flow.
Tests Registration -> Login -> Questionnaire -> Submission -> Scoring ->
Feature Builder -> XGBoost Prediction -> Recommendation Persistence -> Results Page.
"""

import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.career import CareerDomain, CareerSubdomain, CareerCluster, Career, CareerSkill, CareerEducation, CareerPathway
from backend.models.question import QuestionSection, Question, QuestionOption
from backend.models.assessment import AssessmentSession, AssessmentScore, StudentAnswer
from backend.models.recommendation import CareerRecommendation


class TestE2ERealStudentFlow(unittest.TestCase):
    """Executes a real student's journey through the web application."""

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # 1. Seed Section and Adaptive Questions
        self.sec = QuestionSection(name="Digital & Technology", display_order=1, description="Tech affinity")
        db.session.add(self.sec)
        db.session.flush()

        self.q1 = Question(
            question_code="Q-TECH-01",
            section_id=self.sec.id,
            question_text="How interested are you in building cloud software applications?",
            question_type="RATING",
            skill_category="technology_interest",
            class_min=7,
            class_max=12,
            is_active=True
        )
        self.q2 = Question(
            question_code="Q-LOGIC-01",
            section_id=self.sec.id,
            question_text="When solving complex algorithmic puzzles, how do you approach it?",
            question_type="MCQ",
            skill_category="logical_reasoning",
            class_min=7,
            class_max=12,
            is_active=True
        )
        db.session.add_all([self.q1, self.q2])
        db.session.flush()

        self.opt1 = QuestionOption(question_id=self.q2.id, option_text="Break into logical sub-problems", option_value="A", score=1.0)
        self.opt2 = QuestionOption(question_id=self.q2.id, option_text="Try random guesses", option_value="B", score=0.2)
        db.session.add_all([self.opt1, self.opt2])

        # 2. Seed Career Knowledge Base in DB
        self.domain = CareerDomain(domain_name="Technology")
        db.session.add(self.domain)
        db.session.flush()

        self.subdomain = CareerSubdomain(domain_id=self.domain.id, name="Cloud & Software Architecture")
        db.session.add(self.subdomain)
        db.session.flush()

        self.cluster = CareerCluster(subdomain_id=self.subdomain.id, name="Cloud Infrastructure")
        db.session.add(self.cluster)
        db.session.flush()

        self.career = Career(
            career_code="CAR-TECH-01",
            career_name="Cloud Software Architect",
            domain_id=self.domain.id,
            subdomain_id=self.subdomain.id,
            cluster_id=self.cluster.id,
            description="Designs and scales distributed cloud computing architectures.",
            minimum_education="Bachelor's Degree in Computer Science",
            is_active=True
        )
        db.session.add(self.career)
        db.session.flush()

        self.skill = CareerSkill(career_id=self.career.id, skill_name="Distributed Systems", importance_level=5)
        self.edu = CareerEducation(career_id=self.career.id, education_level="Undergraduate", degree_name="B.Tech Computer Science", sequence_order=1)
        self.pathway = CareerPathway(career_id=self.career.id, stage_number=1, stage_name="Associate Engineer", description="Junior Developer")
        db.session.add_all([self.skill, self.edu, self.pathway])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_complete_real_student_journey(self):
        """
        Step-by-step real student flow:
        1. Register student
        2. Login
        3. Start assessment session
        4. Fetch adaptive questionnaire
        5. Answer questions
        6. Submit assessment -> triggers XGBoost ML recommendation
        7. Verify database persistence
        8. Verify API recommendations
        9. Verify results page rendering
        10. Logout
        """
        # Step 1: Register Student
        reg_payload = {
            'first_name': 'Kavya',
            'last_name': 'Sharma',
            'email': 'kavya.sharma@example.com',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'class_level': '12',
            'stream': 'Science-PCM',
            'board': 'CBSE',
            'age': '17'
        }
        res_reg = self.client.post('/register', data=reg_payload, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)

        # Step 2: Login
        login_payload = {
            'email': 'kavya.sharma@example.com',
            'password': 'Password@123'
        }
        res_login = self.client.post('/login', data=login_payload, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)

        # Step 2.5: Fill Academic Scores Onboarding
        profile_payload = {
            'first_name': 'Kavya',
            'last_name': 'Sharma',
            'class_level': '12',
            'board': 'CBSE',
            'medium': 'English',
            'stream': 'Science-PCM',
            'math_score': '95.0',
            'physics_score': '92.0',
            'chemistry_score': '90.0',
            'cs_score': '96.0',
            'english_score': '88.0'
        }
        res_prof = self.client.post('/profile?onboarding=1', data=profile_payload, follow_redirects=True)
        self.assertEqual(res_prof.status_code, 200)

        # Verify Student & Academic in DB
        student = Student.query.filter_by(first_name='Kavya').first()
        self.assertIsNotNone(student)
        self.assertEqual(student.class_level, 12)
        self.assertIsNotNone(student.academic_scores)
        self.assertEqual(student.academic_scores.mathematics_score, 95.0)

        # Step 3: Start Assessment Session
        res_start = self.client.post('/api/assessment/start')
        self.assertEqual(res_start.status_code, 201)
        session_data = res_start.get_json()['data']
        session_id = session_data['id']

        # Step 4: Fetch Adaptive Questions
        res_q = self.client.get(f'/api/questions/{student.class_level}?stream={student.stream}')
        self.assertEqual(res_q.status_code, 200)
        questions_list = res_q.get_json()['data']
        self.assertGreaterEqual(len(questions_list), 1)

        # Step 5: Answer Questions
        # Answer Q1 (Rating)
        ans1_res = self.client.post('/api/assessment/answer', json={
            'session_id': session_id,
            'question_id': self.q1.id,
            'numeric_value': 5.0,
            'time_taken_seconds': 12
        })
        self.assertEqual(ans1_res.status_code, 200)

        # Answer Q2 (MCQ)
        ans2_res = self.client.post('/api/assessment/answer', json={
            'session_id': session_id,
            'question_id': self.q2.id,
            'selected_option': 'A',
            'time_taken_seconds': 15
        })
        self.assertEqual(ans2_res.status_code, 200)

        # Step 6: Submit Assessment (Triggers Scoring + XGBoost ML Engine)
        res_submit = self.client.post('/api/assessment/submit', json={'session_id': session_id})
        self.assertEqual(res_submit.status_code, 200)
        submit_json = res_submit.get_json()
        self.assertTrue(submit_json['success'])

        # Step 7: Verify Database Persistence
        session_db = db.session.get(AssessmentSession, session_id)
        self.assertEqual(session_db.status, 'completed')

        score_db = AssessmentScore.query.filter_by(assessment_id=session_id).first()
        self.assertIsNotNone(score_db)
        self.assertGreaterEqual(score_db.technology_interest, 80.0)

        recs_db = CareerRecommendation.query.filter_by(assessment_id=session_id).order_by(CareerRecommendation.rank_position.asc()).all()
        self.assertGreaterEqual(len(recs_db), 1)
        first_rec = recs_db[0]
        self.assertEqual(first_rec.rank_position, 1)
        self.assertGreater(first_rec.score, 0.0)
        self.assertIsNotNone(first_rec.career)
        self.assertEqual(first_rec.career.career_name, "Cloud Software Architect")

        # Step 8: Verify API Recommendations Endpoints
        res_rec_api = self.client.get(f'/api/recommendations/{session_id}')
        self.assertEqual(res_rec_api.status_code, 200)
        rec_data = res_rec_api.get_json()['data']
        self.assertIn(rec_data['model'], ['CatBoost', 'XGBoost', 'LightGBM', 'RandomForest'])
        self.assertTrue(rec_data['model_version'].startswith('V'))

        # Test student recommendations endpoint
        res_stu_rec = self.client.get(f'/api/recommendations/student/{student.student_code}')
        self.assertEqual(res_stu_rec.status_code, 200)

        # Step 9: Verify Results Page UI Rendering
        res_page = self.client.get(f'/assessment/results/{session_id}')
        self.assertEqual(res_page.status_code, 200)
        page_html = res_page.get_data(as_text=True)
        self.assertIn("Cloud Software Architect", page_html)
        self.assertIn("Top #1 Primary Recommendation", page_html)

        # Step 10: Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()


if __name__ == '__main__':
    unittest.main()
