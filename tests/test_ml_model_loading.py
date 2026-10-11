"""
Automated Unit Tests: ML Model Loader and Artifact Validation.
"""

import unittest
from pathlib import Path
import tempfile
import json
from backend.ml.model_loader import (
    ModelLoader,
    ModelArtifactError,
    get_model,
    get_preprocessor,
    get_feature_columns,
    get_classes,
    get_model_config,
    get_model_version,
    is_model_ready
)


class TestMLModelLoader(unittest.TestCase):
    """Validates production ML artifact loading, integrity, and exception handling."""

    def test_singleton_loader(self):
        loader1 = ModelLoader.get_instance()
        loader2 = ModelLoader.get_instance()
        self.assertIs(loader1, loader2)

    def test_artifacts_exist_and_load(self):
        loader = ModelLoader.get_instance()
        loader.load()
        self.assertTrue(loader.is_loaded())
        self.assertTrue(is_model_ready())

        # Validate Model
        model = get_model()
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict_proba') or hasattr(model, 'predict'))

        # Validate Preprocessor
        preprocessor = get_preprocessor()
        self.assertIsNotNone(preprocessor)
        self.assertTrue(hasattr(preprocessor, 'transform'))

        # Validate Feature Columns
        features = get_feature_columns()
        self.assertIsInstance(features, list)
        self.assertTrue(11 <= len(features) <= 35)
        self.assertIn('ability_match_component', features)
        self.assertIn('interest_match_component', features)

        # Validate Classes
        classes = get_classes()
        self.assertIn('classes', classes)
        self.assertEqual(classes['classes'], [0, 1])

        # Validate Config
        config = get_model_config()
        self.assertIn(config.get('model'), ['CatBoost', 'XGBoost', 'LightGBM', 'RandomForest'])
        self.assertIn('threshold', config)
        self.assertTrue(0.1 <= config['threshold'] <= 0.9)

        # Validate Version
        version_info = get_model_version()
        self.assertIn('version', version_info)

    def test_missing_artifacts_raises_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            empty_path = Path(tmp_dir)
            custom_loader = ModelLoader(model_dir=empty_path)
            with self.assertRaises(ModelArtifactError):
                custom_loader.load(force_reload=True)


if __name__ == '__main__':
    unittest.main()
