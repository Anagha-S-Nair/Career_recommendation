"""
Automated Unit Tests: ML Feature Builder and Contract Validation.
"""

import unittest
import pandas as pd
from backend.ml.feature_builder import FeatureBuilder, PRIMARY_ABILITY_PAIRS, PRIMARY_INTEREST_PAIRS
from backend.ml.model_loader import get_feature_columns


class TestMLFeatureBuilder(unittest.TestCase):
    """Validates feature generation, mathematical match calculations, and feature schema contract."""

    def setUp(self):
        self.sample_scores = {
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
        }

        self.sample_career_reqs = {
            'career_name': 'Software Engineer',
            'career_domain': 'Technology',
            'career_subdomain': 'Software Development',
            'career_cluster': 'Cloud Systems',
            'required_mathematical_ability': 70.0,
            'required_logical_reasoning': 80.0,
            'required_scientific_thinking': 60.0,
            'required_problem_solving': 80.0,
            'required_analytical_thinking': 75.0,
            'required_communication': 65.0,
            'required_creativity': 50.0,
            'required_digital_ability': 90.0,
            'required_technology_interest': 85.0,
            'required_engineering_interest': 70.0,
            'required_healthcare_interest': 20.0,
            'required_business_interest': 40.0,
            'required_finance_interest': 30.0,
            'required_arts_interest': 25.0,
            'required_design_interest': 50.0,
            'required_research_interest': 60.0,
            'required_environment_interest': 30.0,
            'required_agriculture_interest': 20.0,
        }

    def test_calculate_ability_match_score(self):
        ability_match = FeatureBuilder.calculate_ability_match(self.sample_scores, self.sample_career_reqs)
        self.assertIsInstance(ability_match, float)
        self.assertGreaterEqual(ability_match, 0.0)
        self.assertLessEqual(ability_match, 100.0)

    def test_calculate_interest_match_score(self):
        interest_match = FeatureBuilder.calculate_interest_match(self.sample_scores, self.sample_career_reqs)
        self.assertIsInstance(interest_match, float)
        self.assertGreaterEqual(interest_match, 0.0)
        self.assertLessEqual(interest_match, 100.0)

    def test_build_candidate_feature_row_schema(self):
        student_profile = {
            'student_id': 'STU001',
            'age': 17,
            'class_level': 12,
            'stream': 'Science-PCM',
            'academic_percentage': 88.5,
            'scores': self.sample_scores
        }

        row = FeatureBuilder.build_candidate_feature_row(student_profile, self.sample_career_reqs)

        # Validate that student_id is NOT in row
        self.assertNotIn('student_id', row)
        self.assertNotIn('career_id', row)

        # Validate expected keys
        expected_cols = get_feature_columns()
        self.assertEqual(set(row.keys()), set(expected_cols))

        # Validate types
        self.assertIsInstance(row['age'], int)
        self.assertIsInstance(row['class'], int)
        self.assertIsInstance(row['stream'], str)
        self.assertIsInstance(row['career_name'], str)

    def test_build_batch_features(self):
        student_profile = {
            'age': 16,
            'class_level': 11,
            'stream': 'Science-PCM',
            'academic_percentage': 82.0,
            'scores': self.sample_scores
        }

        catalogue_df = pd.DataFrame([self.sample_career_reqs, self.sample_career_reqs])
        batch_df = FeatureBuilder.build_batch_features(student_profile, catalogue_df)

        expected_cols = get_feature_columns()
        self.assertEqual(list(batch_df.columns), expected_cols)
        self.assertEqual(len(batch_df), 2)
        self.assertNotIn('student_id', batch_df.columns)


if __name__ == '__main__':
    unittest.main()
