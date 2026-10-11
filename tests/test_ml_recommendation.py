"""
Automated Unit Tests: ML Career Recommendation Service and Top-K Ranking.
"""

import unittest
import numpy as np
from backend.ml.recommendation_service import CareerRecommendationEngine


class TestMLRecommendationService(unittest.TestCase):
    """Validates full catalogue career recommendation generation and ranking."""

    def setUp(self):
        self.student_profile = {
            'student_id': 'STU000001',
            'age': 18,
            'class_level': 11,
            'stream': 'Science-PCB',
            'academic_percentage': 71.0,
            'scores': {
                'mathematical_ability': 76.2,
                'logical_reasoning': 95.2,
                'scientific_reasoning': 88.4,
                'problem_solving': 51.1,
                'analytical_ability': 76.0,
                'communication': 66.0,
                'creativity': 74.2,
                'digital_ability': 43.3,
                'learning_ability': 60.8,
                'spatial_ability': 95.3,
                'practical_ability': 54.4,
                'technology_interest': 92.4,
                'engineering_interest': 85.1,
                'healthcare_interest': 76.2,
                'business_interest': 79.1,
                'finance_interest': 71.0,
                'arts_interest': 62.6,
                'design_interest': 55.5,
                'research_interest': 62.9,
                'environment_interest': 76.0,
                'agriculture_interest': 72.5
            }
        }

    def test_catalogue_loading(self):
        catalogue = CareerRecommendationEngine.get_career_catalogue()
        self.assertFalse(catalogue.empty)
        self.assertEqual(len(catalogue), 158)
        self.assertIn('career_name', catalogue.columns)
        self.assertIn('career_domain', catalogue.columns)

    def test_recommendation_generation_top_k(self):
        results = CareerRecommendationEngine.generate_recommendations(self.student_profile, top_k=10)
        catalogue = CareerRecommendationEngine.get_career_catalogue()

        self.assertIn('recommendations', results)
        self.assertIn('top_1', results)
        self.assertIn('top_3', results)
        self.assertIn('top_5', results)
        self.assertIn('top_10', results)
        self.assertEqual(results['total_evaluated_careers'], len(catalogue))

        recs = results['recommendations']
        self.assertEqual(len(recs), 10)

        # Validate monotonic rank ordering and descending scores
        prev_score = 100.0
        catalogue = CareerRecommendationEngine.get_career_catalogue()
        cat_ids = set(catalogue['career_id'].astype(str))

        for idx, item in enumerate(recs, start=1):
            self.assertEqual(item['rank'], idx)
            self.assertGreaterEqual(item['compatibility_score'], 0.0)
            self.assertLessEqual(item['compatibility_score'], 100.0)
            self.assertLessEqual(item['compatibility_score'], prev_score + 1e-4)
            prev_score = item['compatibility_score']

            self.assertIn(str(item['career_id']), cat_ids)
            self.assertTrue(item['career_name'])
            self.assertTrue(item['career_domain'])
            self.assertFalse(np.isnan(item['compatibility_score']))
            self.assertFalse(np.isnan(item['probability']))

    def test_top_1_recommendation_structure(self):
        results = CareerRecommendationEngine.generate_recommendations(self.student_profile, top_k=1)
        top1 = results['top_1']
        self.assertIsNotNone(top1)
        self.assertEqual(top1['rank'], 1)
        self.assertIn('career_name', top1)
        self.assertIn('compatibility_score', top1)


if __name__ == '__main__':
    unittest.main()
