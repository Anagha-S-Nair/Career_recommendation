"""
Automated Unit Tests: ML Prediction Service and Reference Sanity Test.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from backend.ml.prediction_service import PredictionService
from backend.ml.model_loader import get_feature_columns, get_model_config


class TestMLPredictionService(unittest.TestCase):
    """Validates XGBoost inference, output formatting, thresholding, and error handling."""

    def setUp(self):
        self.valid_features = [{
            'age': 17,
            'class': 12,
            'ability_match_component': 79.6,
            'interest_match_component': 60.23,
            'academic_match_component': 90.9,
            'learning_match_component': 54.7,
            'compatibility_score': 74.5,
            'career_name': 'Counsellor',
            'career_domain': 'Technology',
            'stream': 'Science-PCB'
        }]

    def test_prediction_output_structure(self):
        res = PredictionService.predict_compatibility(self.valid_features)
        self.assertIn('probabilities', res)
        self.assertIn('predictions', res)
        self.assertIn('threshold', res)
        self.assertIn('version', res)
        self.assertEqual(res['count'], 1)

        prob = res['probabilities'][0]
        pred = res['predictions'][0]

        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        self.assertIn(pred, [0, 1])

        # Test threshold logic
        threshold = res['threshold']
        self.assertEqual(pred, int(prob >= threshold))

    def test_missing_feature_column_raises_error(self):
        invalid_data = [{'age': 17, 'class': 12}]  # missing other 9 columns
        with self.assertRaises(ValueError):
            PredictionService.predict_compatibility(invalid_data)

    def test_empty_input_raises_error(self):
        with self.assertRaises(ValueError):
            PredictionService.predict_compatibility([])

    def test_reference_sample_sanity_test(self):
        """
        Sanity test loading the example prediction generated during training
        from Career_Recommendation/Personalized_Career_Recommendation_FINAL_V7_1/K_Model_Testing/example_prediction.csv
        """
        example_csv_path = Path('Career_Recommendation/Personalized_Career_Recommendation_FINAL_V7_1/K_Model_Testing/example_prediction.csv')
        if example_csv_path.exists():
            ex_df = pd.read_csv(example_csv_path)
            req_cols = get_feature_columns()
            input_df = ex_df[req_cols]

            res = PredictionService.predict_compatibility(input_df)
            self.assertEqual(res['count'], len(ex_df))
            self.assertFalse(np.isnan(res['probabilities']).any())
            self.assertFalse(np.isnan(res['predictions']).any())


if __name__ == '__main__':
    unittest.main()
