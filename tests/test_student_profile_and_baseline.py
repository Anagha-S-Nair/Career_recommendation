"""
Student Profile Engine & Exploratory Career Baseline Test Suite.
Verifies profile synthesis, strengths and development areas extraction,
multi-factor rule-based baseline matching, and full career explanation roadmaps.
"""

import sys
import uuid
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student, AcademicScore
from backend.models.assessment import AssessmentSession, AssessmentScore, StudentAnswer
from backend.models.career import Career, CareerDomain, CareerSubdomain, CareerCluster, CareerSkill, CareerSubject, CareerEducation, CareerPathway
from backend.services.student_profile_service import StudentProfileService
from backend.services.recommendation_service import RecommendationService


class TestStudentProfileAndBaseline(unittest.TestCase):
    """Test suite for StudentProfileService and RecommendationService."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Seed sample domain, subdomain, cluster, and career
        domain = CareerDomain(id=1, domain_name='Technology', icon='bi-cpu', display_order=1, is_active=True)
        subdomain = CareerSubdomain(id=1, domain_id=1, name='Software Engineering')
        cluster = CareerCluster(id=1, subdomain_id=1, name='Web & Cloud Development')
        db.session.add_all([domain, subdomain, cluster])
        db.session.commit()

        career = Career(
            id=1,
            career_code='CAR-TECH-TEST',
            career_name='Cloud Software Architect',
            domain_id=1,
            subdomain_id=1,
            cluster_id=1,
            description='Designs enterprise cloud systems.',
            work_environment='Modern Office / Tech Hub',
            work_style='Collaborative agile team',
            is_active=True
        )
        db.session.add(career)
        db.session.flush()

        # Add skill, subject, education, progression
        skill = CareerSkill(career_id=career.id, skill_name='Distributed Systems', importance_level=5, importance_label='Critical')
        subj = CareerSubject(career_id=career.id, subject_name='Computer Science', importance_level=5, importance_label='High')
        edu = CareerEducation(career_id=career.id, education_level='B.Tech', degree_name='Computer Science', sequence_order=1)
        prog = CareerPathway(career_id=career.id, stage_number=1, stage_name='Junior Cloud Developer', description='Build cloud services')
        db.session.add_all([skill, subj, edu, prog])
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        uid = uuid.uuid4().hex[:6]
        self.user = User(username=f'prof_user_{uid}', email=f'{uid}@prof.com', role='student')
        self.user.set_password('Pass1234!')
        db.session.add(self.user)
        db.session.flush()

        self.student = Student(
            user_id=self.user.id,
            student_code=f'STU-{uid.upper()}',
            first_name='Profile',
            last_name='Tester',
            class_level=11,
            stream='Science-PCM'
        )
        db.session.add(self.student)
        db.session.flush()

        # Academic Score
        acad = AcademicScore(
            student_id=self.student.id,
            mathematics_score=92.0,
            physics_score=88.0,
            chemistry_score=84.0,
            computer_science_score=95.0,
            overall_percentage=89.5
        )
        db.session.add(acad)

        # Assessment Session & Scores
        self.session = AssessmentSession(student_id=self.student.id, status='completed')
        db.session.add(self.session)
        db.session.flush()

        self.scores = AssessmentScore(
            assessment_id=self.session.id,
            mathematical_ability=95.0,
            logical_reasoning=90.0,
            scientific_reasoning=85.0,
            problem_solving=88.0,
            digital_ability=92.0,
            analytical_ability=80.0,
            communication=75.0,
            creativity=70.0,
            learning_ability=85.0,
            spatial_ability=65.0,
            practical_ability=60.0,
            teamwork=78.0,
            leadership=72.0,
            technology_interest=94.0,
            science_interest=88.0,
            healthcare_interest=40.0,
            business_interest=60.0,
            creative_interest=50.0,
            research_interest=80.0,
            social_interest=55.0
        )
        db.session.add(self.scores)
        db.session.commit()

    def test_student_profile_generation(self):
        """Verify StudentProfileService generates complete profile with strengths and growth areas."""
        profile = StudentProfileService.generate_student_profile(self.session.id)

        self.assertIn('academic', profile)
        self.assertIn('abilities', profile)
        self.assertIn('interests', profile)
        self.assertIn('work_preferences', profile)
        self.assertIn('strengths', profile)
        self.assertIn('development_areas', profile)

        # Top strengths should include mathematical and digital ability (scored >= 90)
        strength_dims = [s['dimension'] for s in profile['strengths']]
        self.assertIn('mathematical_ability', strength_dims)
        self.assertIn('digital_ability', strength_dims)

        # Development areas should include lowest scoring dimensions (practical/spatial)
        growth_dims = [g['dimension'] for g in profile['development_areas']]
        self.assertTrue('practical_ability' in growth_dims or 'spatial_ability' in growth_dims)

    def test_baseline_career_matching_and_explanations(self):
        """Verify RecommendationService produces high-compatibility match with full explanation roadmap."""
        recs = RecommendationService.generate_recommendations_for_session(self.session, top_k=5)
        self.assertGreaterEqual(len(recs), 1)

        first_rec = recs[0]
        self.assertGreaterEqual(first_rec.score, 70.0, "Tech student should score high for Cloud Architect")
        self.assertTrue(
            "Career Alignment" in first_rec.recommendation_reason or "Career Match" in first_rec.recommendation_reason,
            f"Unexpected reason: {first_rec.recommendation_reason}"
        )

        # Detailed explanations
        explanations = RecommendationService.get_detailed_career_explanations(self.session.id)
        self.assertGreaterEqual(len(explanations), 1)

        exp = explanations[0]
        self.assertEqual(exp['career_name'], 'Cloud Software Architect')
        self.assertEqual(exp['domain_name'], 'Technology')
        self.assertGreaterEqual(len(exp['skills']), 1)
        self.assertEqual(len(exp['education_milestones']), 0)
        self.assertEqual(len(exp['progression_stages']), 0)

    def test_profile_api_endpoint(self):
        """Verify GET /api/assessment/<assessment_id>/profile returns 200 with structured JSON."""
        # Login test client
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.user.id)
            sess['_fresh'] = True

        response = self.client.get(f'/api/assessment/{self.session.id}/profile')
        self.assertEqual(response.status_code, 200)

        json_data = response.get_json()
        self.assertTrue(json_data.get('success'))
        self.assertIn('academic', json_data['data'])
        self.assertIn('abilities', json_data['data'])
        self.assertIn('strengths', json_data['data'])

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()


if __name__ == '__main__':
    unittest.main()
