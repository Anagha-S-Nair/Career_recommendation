"""
Automated Tests: ML Model Loader Concurrency and Multi-Thread Safety.
"""

import unittest
from concurrent.futures import ThreadPoolExecutor
from backend.ml.recommendation_service import CareerRecommendationEngine
from backend.ml.model_loader import ModelLoader, is_model_ready


class TestMLConcurrencyAndPerformance(unittest.TestCase):
    """Verifies that the ML recommendation engine is thread-safe under concurrent requests."""

    def setUp(self):
        self.sample_profiles = [
            {
                'student_id': f'STU_CONCURRENT_{i}',
                'age': 16 + (i % 3),
                'class_level': 10 + (i % 3),
                'stream': 'Science-PCM' if i % 2 == 0 else 'Commerce',
                'academic_percentage': 80.0 + (i * 2),
                'scores': {
                    'mathematical_ability': 70.0 + (i * 3),
                    'logical_reasoning': 75.0 + (i * 2),
                    'scientific_reasoning': 80.0,
                    'problem_solving': 70.0,
                    'analytical_ability': 75.0,
                    'communication': 70.0,
                    'creativity': 65.0,
                    'digital_ability': 80.0,
                    'learning_ability': 75.0,
                    'technology_interest': 85.0 if i % 2 == 0 else 40.0,
                    'engineering_interest': 80.0 if i % 2 == 0 else 35.0,
                    'healthcare_interest': 40.0,
                    'business_interest': 40.0 if i % 2 == 0 else 90.0,
                    'finance_interest': 35.0 if i % 2 == 0 else 85.0,
                    'arts_interest': 30.0,
                    'design_interest': 50.0,
                    'research_interest': 70.0,
                    'environment_interest': 40.0,
                    'agriculture_interest': 30.0
                }
            }
            for i in range(10)
        ]

    def test_concurrent_recommendation_requests_5(self):
        """Tests 5 concurrent recommendation requests simultaneously."""
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(CareerRecommendationEngine.generate_recommendations, self.sample_profiles[i], 5)
                for i in range(5)
            ]
            results = [f.result() for f in futures]

        self.assertEqual(len(results), 5)
        for res in results:
            self.assertEqual(len(res['top_5']), 5)
            self.assertEqual(res['total_evaluated_careers'], 158)
            self.assertGreater(res['top_1']['compatibility_score'], 0.0)

    def test_concurrent_recommendation_requests_10(self):
        """Tests 10 concurrent recommendation requests simultaneously."""
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(CareerRecommendationEngine.generate_recommendations, self.sample_profiles[i], 10)
                for i in range(10)
            ]
            results = [f.result() for f in futures]

        self.assertEqual(len(results), 10)
        for idx, res in enumerate(results):
            self.assertEqual(len(res['top_10']), 10)
            self.assertEqual(res['student_id'], f'STU_CONCURRENT_{idx}')
            self.assertEqual(res['total_evaluated_careers'], 158)


if __name__ == '__main__':
    unittest.main()
