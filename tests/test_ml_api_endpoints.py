"""
Automated Unit & Integration Tests: ML REST API Endpoints.
"""

import unittest
import json
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.career import CareerDomain, CareerSubdomain, CareerCluster, Career
from backend.models.assessment import AssessmentSession, AssessmentScore
from backend.services.assessment_service import AssessmentService


class TestMLApiEndpoints(unittest.TestCase):
    """Integration test suite for ML prediction, recommendation, and model info endpoints."""

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Seed minimal database career
        self.domain = CareerDomain(domain_name="Technology")
        db.session.add(self.domain)
        db.session.flush()

        self.career = Career(
            career_code="CAR-TECH-01",
            career_name="Software Developer",
            domain_id=self.domain.id,
            description="Designs and builds software applications."
        )
        db.session.add(self.career)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_get_model_info(self):
        res = self.client.get('/api/model/info')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        model_info = data['data']
        self.assertIn(model_info['model'], ['CatBoost', 'XGBoost', 'LightGBM', 'RandomForest'])
        self.assertIn('classification_metrics', model_info)
        self.assertIn('recommendation_metrics', model_info)
        self.assertGreaterEqual(model_info['classification_metrics']['accuracy'], 0.80)
        self.assertGreaterEqual(model_info['recommendation_metrics']['hit_at_1'], 0.80)

    def test_get_health(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'healthy')

    def test_post_predictions_valid(self):
        payload = {
            'features': [{
                'age': 17,
                'class': 12,
                'ability_match_component': 79.6,
                'interest_match_component': 60.23,
                'academic_match_component': 90.9,
                'learning_match_component': 54.7,
                'career_name': 'Counsellor',
                'career_domain': 'Technology',
                'stream': 'Science-PCB'
            }]
        }
        res = self.client.post('/api/predictions', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('probabilities', data['data'])
        self.assertEqual(len(data['data']['probabilities']), 1)

    def test_post_predictions_invalid_missing_cols(self):
        payload = {
            'features': [{'age': 17, 'class': 12}]
        }
        res = self.client.post('/api/predictions', json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_post_recommendations_standalone_profile(self):
        payload = {
            'student_id': 'STU001',
            'age': 17,
            'class_level': 12,
            'stream': 'Science-PCM',
            'academic_percentage': 85.0,
            'scores': {
                'mathematical_ability': 80.0,
                'logical_reasoning': 85.0,
                'scientific_reasoning': 90.0,
                'problem_solving': 75.0,
                'analytical_ability': 80.0,
                'communication': 70.0,
                'creativity': 65.0,
                'digital_ability': 85.0,
                'learning_ability': 80.0,
                'technology_interest': 90.0,
                'engineering_interest': 85.0,
                'healthcare_interest': 40.0,
                'business_interest': 50.0,
                'finance_interest': 45.0,
                'arts_interest': 30.0,
                'design_interest': 60.0,
                'research_interest': 75.0,
                'environment_interest': 40.0,
                'agriculture_interest': 35.0
            },
            'top_k': 5
        }
        res = self.client.post('/api/recommendations', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['recommendations']), 5)
        self.assertEqual(data['data']['recommendations'][0]['rank'], 1)


if __name__ == '__main__':
    unittest.main()
