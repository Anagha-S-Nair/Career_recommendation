"""
Prediction Service Module.
Executes batch model inference with feature engineering and confidence calculation.
"""

from typing import Any, Dict, Union, List
import numpy as np
import pandas as pd
from backend.ml.model_loader import ModelLoader, get_model, get_preprocessor, get_model_config, get_model_version


class PredictionService:
    """Manages feature transformation and model predictions."""

    REQUIRED_BASE_COLS = [
        'age', 'class', 'ability_match_component', 'interest_match_component',
        'academic_match_component', 'learning_match_component', 'career_name'
    ]

    @classmethod
    def predict_compatibility(cls, features_data: Union[pd.DataFrame, List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Transforms input feature matrix and predicts compatibility probabilities.
        """
        if isinstance(features_data, list):
            df = pd.DataFrame(features_data)
        elif isinstance(features_data, dict):
            df = pd.DataFrame([features_data])
        elif isinstance(features_data, pd.DataFrame):
            df = features_data.copy()
        else:
            raise ValueError("Unsupported features format. Expected DataFrame or list of dicts.")

        # Check required columns
        missing = [col for col in cls.REQUIRED_BASE_COLS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required feature columns: {missing}")

        # Compute engineered features if not already present
        if 'composite_alignment_index' not in df.columns:
            a = pd.to_numeric(df['ability_match_component'], errors='coerce').fillna(75.0)
            i = pd.to_numeric(df['interest_match_component'], errors='coerce').fillna(75.0)
            ac = pd.to_numeric(df['academic_match_component'], errors='coerce').fillna(75.0)

            df['composite_alignment_index'] = (a * 0.40) + (i * 0.35) + (ac * 0.25)
            df['ability_interest_synergy'] = np.sqrt(np.maximum(a * i, 0.0))
            df['ability_interest_gap'] = np.abs(a - i)
            df['min_core_match'] = np.minimum(np.minimum(a, i), ac)
            df['max_core_match'] = np.maximum(np.maximum(a, i), ac)
            df['harmonic_core_match'] = 3.0 / (1.0/np.maximum(a, 1.0) + 1.0/np.maximum(i, 1.0) + 1.0/np.maximum(ac, 1.0))
            df['geometric_core_synergy'] = np.power(np.maximum(a * i * ac, 0.0), 1.0/3.0)
            df['holistic_synergy'] = (df['composite_alignment_index'] + df['ability_interest_synergy'] + df['harmonic_core_match'] + df['geometric_core_synergy']) / 4.0

        # Ensure default categorical columns if missing
        for cat in ['stream', 'career_domain', 'career_name']:
            if cat not in df.columns:
                df[cat] = 'General'
            else:
                df[cat] = df[cat].astype(str).str.strip().str.title().replace(['Nan', 'None', '?', ''], 'General')

        model = get_model()
        preprocessor = get_preprocessor()
        config = get_model_config()

        # Transform features
        X_proc = preprocessor.transform(df)

        # Predict probabilities
        probs = model.predict_proba(X_proc)[:, 1]

        threshold = float(config.get('threshold', 0.5))
        margin = float(config.get('confidence_margin', 0.27))

        predictions = []
        for p in probs:
            if p >= (threshold + margin):
                predictions.append(1)
            elif p <= (threshold - margin):
                predictions.append(0)
            else:
                predictions.append(1 if p >= threshold else 0)

        return {
            'probabilities': [round(float(p), 4) for p in probs],
            'predictions': predictions,
            'threshold': threshold,
            'version': ModelLoader.get_model_version().get('version', 'V13.0'),
            'count': len(probs)
        }
