"""
Career Recommendation Engine Module.
Scores all candidate careers from the knowledge catalogue for a student,
ranks them by compatibility probability, and returns Top-K recommendations.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import yaml
from backend.ml.feature_builder import FeatureBuilder
from backend.ml.model_loader import get_model_config, get_model_version
from backend.ml.prediction_service import PredictionService

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_CATALOGUE_PATH = Path(__file__).resolve().parent / "data" / "career_knowledge_requirements.csv"
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


class CareerRecommendationEngine:
    """Production Career Recommendation Engine."""
    _catalogue: Optional[pd.DataFrame] = None
    _catalogue_path: Optional[Path] = None

    @classmethod
    def get_career_catalogue(cls, path: Optional[Path] = None) -> pd.DataFrame:
        if path is None:
            path = DEFAULT_CATALOGUE_PATH

        if cls._catalogue is None or cls._catalogue_path != path:
            if not path.exists():
                raise FileNotFoundError(f"Career knowledge catalogue missing at {path}")
            df = pd.read_csv(path)
            cls._catalogue = df
            cls._catalogue_path = path
            logger.info(f"CAREER_CATALOGUE_LOADED: {len(df)} careers from {path}")
        return cls._catalogue

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    @classmethod
    def generate_recommendations(
        cls,
        student_profile: Dict[str, Any],
        top_k: int = 10,
        data_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generates ranked Top-K career recommendations for a student profile.
        """
        catalogue = cls.get_career_catalogue(data_path)
        if catalogue.empty:
            raise ValueError("Career knowledge catalogue is empty.")

        total_evaluated = len(catalogue)

        # 1. Build batch features for all catalogue careers
        features_df = FeatureBuilder.build_batch_features(student_profile, catalogue)

        # 2. Run model predictions
        pred_results = PredictionService.predict_compatibility(features_df)
        probs = pred_results['probabilities']
        preds = pred_results['predictions']

        # 3. Attach scores
        catalogue_scored = catalogue.copy()
        catalogue_scored['probability'] = probs
        comp_scores = features_df['composite_alignment_index'].values if 'composite_alignment_index' in features_df.columns else [75.0] * len(probs)
        catalogue_scored['composite_score'] = comp_scores
        catalogue_scored['compatibility_score'] = [
            round(float(c) * 0.80 + float(p) * 20.0, 1) for c, p in zip(comp_scores, probs)
        ]
        catalogue_scored['is_compatible'] = preds
        catalogue_scored['ability_match'] = features_df['ability_match_component'].values
        catalogue_scored['interest_match'] = features_df['interest_match_component'].values

        # 4. Domain & prerequisite threshold check
        cfg = cls._load_config()
        domain_cfg = cfg.get('domain_requirements', {})
        default_cfg = cfg.get('default_requirements', {})

        def _is_compliant(row):
            domain = str(row.get('domain', row.get('career_domain', ''))).lower()
            thresholds = domain_cfg.get(domain, default_cfg)
            scores = student_profile.get('scores', {})
            for field, min_val in thresholds.items():
                if field in scores:
                    if float(scores[field]) < float(min_val):
                        return 0
            return 1

        catalogue_scored['threshold_pass'] = catalogue_scored.apply(_is_compliant, axis=1)

        # 5. Sort descending by compliance, compatibility score, and match scores
        catalogue_sorted = catalogue_scored.sort_values(
            by=['threshold_pass', 'compatibility_score', 'ability_match', 'interest_match'],
            ascending=[False, False, False, False]
        )

        # 6. Deduplicate unique root careers so "X" and "X Specialist" do not crowd top spots
        seen_roots = set()
        distinct_rows = []
        for _, row in catalogue_sorted.iterrows():
            root_name = str(row.get('career_name', '')).replace(' Specialist', '').strip().lower()
            if root_name in seen_roots:
                continue
            seen_roots.add(root_name)
            distinct_rows.append(row)
            if len(distinct_rows) >= top_k:
                break

        catalogue_distinct = pd.DataFrame(distinct_rows).reset_index(drop=True)

        k_val = min(top_k, len(catalogue_distinct))
        recommendations_list = []
        for rank in range(1, k_val + 1):
            row = catalogue_distinct.iloc[rank - 1]
            c_name = str(row.get('career_name', 'Career'))
            c_dom = str(row.get('domain', row.get('career_domain', 'General')))
            c_sub = str(row.get('subdomain', row.get('career_subdomain', 'General')))
            c_clu = str(row.get('cluster', row.get('career_cluster', 'General')))
            score = float(row['compatibility_score'])

            reason = (
                f"High alignment ({score}%) across {c_dom} "
                f"aptitude benchmarks ({row['ability_match']}%) and disciplinary interests ({row['interest_match']}%)."
            )
            strengths_desc = f"Strong compatibility in {c_dom} core aptitudes and {c_clu} functional track."
            gaps_desc = f"Prepare for {row.get('minimum_education_level', 'Degree')} requirements and master essential competencies for {c_name}."

            rec_item = {
                'rank': rank,
                'career_id': row.get('career_id', f'CAR{rank:05d}'),
                'career_name': c_name,
                'domain': c_dom,
                'career_domain': c_dom,
                'subdomain': c_sub,
                'career_subdomain': c_sub,
                'cluster': c_clu,
                'career_cluster': c_clu,
                'compatibility_score': score,
                'probability': round(score / 100.0, 4),
                'is_compatible': bool(row['is_compatible']),
                'recommendation_strength': 'Strong Match' if score >= 75 else ('Moderate Match' if score >= 50 else 'Emerging Match'),
                'confidence_tier': 'Tier 1 (High)' if score >= 75 else 'Tier 2 (Moderate)',
                'match_factors': {
                    'overall': score,
                    'ability_match': float(row['ability_match']),
                    'interest_match': float(row['interest_match'])
                },
                'why_recommended': reason,
                'strengths_summary': strengths_desc,
                'gaps_summary': gaps_desc,
                'description': row.get('description', ''),
                'minimum_education': row.get('minimum_education_level', "Bachelor's Degree"),
                'typical_education': row.get('typical_education', 'Degree')
            }
            recommendations_list.append(rec_item)

        version_info = get_model_version()
        config = get_model_config()
        return {
            'student_id': student_profile.get('student_id', 'STUDENT_001'),
            'total_evaluated_careers': total_evaluated,
            'model_name': config.get('model', 'RandomForest'),
            'model_version': version_info.get('version', 'V13.0-RandomForest-Champion-Benchmark'),
            'top_1': recommendations_list[0] if recommendations_list else None,
            'top_3': recommendations_list[:3],
            'top_5': recommendations_list[:5],
            'top_10': recommendations_list[:10],
            'recommendations': recommendations_list
        }
