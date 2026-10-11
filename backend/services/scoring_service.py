"""
Assessment Scoring Service.
Computes normalized multi-dimensional cognitive aptitude, interest, and work preference scores (0-100 scale).
Categorizes scores into educational guidance bands (Very Low, Low, Average, Good, Excellent).
"""

from typing import Dict, Any, List, Union
from sqlalchemy.orm.attributes import flag_modified
from backend.extensions import db
from backend.models.assessment import AssessmentSession, StudentAnswer, AssessmentScore
from backend.models.question import Question


class ScoringService:
    """Core assessment evaluation and normalization engine."""

    # Educational guidance score bands
    SCORE_BANDS = [
        (80.5, 100.0, "Excellent", "Demonstrates strong conceptual mastery and high affinity."),
        (60.5, 80.4, "Good", "Solid capability with positive aptitude indicators."),
        (40.5, 60.4, "Average", "Moderate proficiency with scope for further exploration and skill building."),
        (20.5, 40.4, "Low", "Developing foundational familiarity; supplementary practice recommended."),
        (0.0, 20.4, "Very Low", "Minimal demonstrated exposure or current interest.")
    ]

    @classmethod
    def get_score_category(cls, score: float) -> Dict[str, str]:
        """Convert a 0-100 numerical score into an educational guidance category and description."""
        score = max(0.0, min(100.0, score))
        for min_val, max_val, label, desc in cls.SCORE_BANDS:
            if min_val <= score <= max_val:
                return {'label': label, 'description': desc, 'score': round(score, 1)}
        return {'label': 'Average', 'description': 'Moderate proficiency.', 'score': round(score, 1)}

    @classmethod
    def calculate_and_save_scores(cls, session: Union[AssessmentSession, int]) -> AssessmentScore:
        """
        Calculates all cognitive, interest, and behavioral dimensions from student answers
        and saves/updates the AssessmentScore record in the database.
        """
        if isinstance(session, int):
            session_obj = db.session.get(AssessmentSession, session)
            if not session_obj:
                raise ValueError(f"AssessmentSession {session} not found.")
            session = session_obj

        answers = session.answers.all()
        
        # Track total points scored and maximum possible points per skill category
        category_scores: Dict[str, float] = {}
        category_max: Dict[str, float] = {}

        # Default list of all tracked cognitive and interest dimensions
        tracked_dimensions = [
            'mathematical_ability', 'logical_reasoning', 'scientific_reasoning',
            'problem_solving', 'analytical_ability', 'communication',
            'creativity', 'digital_ability', 'learning_ability', 'memory',
            'observation', 'spatial_ability', 'practical_ability', 'teamwork', 'leadership',
            'technology_interest', 'science_interest', 'healthcare_interest',
            'business_interest', 'creative_interest', 'research_interest', 'social_interest'
        ]

        for dim in tracked_dimensions:
            category_scores[dim] = 0.0
            category_max[dim] = 0.0

        # Skill alias dictionary mapping question skill_categories to database columns
        SKILL_ALIASES = {
            'medical_interest': 'healthcare_interest',
            'health_interest': 'healthcare_interest',
            'scientific_interest': 'science_interest',
            'engineering_interest': 'technology_interest',
            'governance_interest': 'social_interest',
            'law_interest': 'social_interest',
            'arts_interest': 'creative_interest',
            'design_interest': 'creative_interest',
            'math_ability': 'mathematical_ability',
            'math': 'mathematical_ability',
            'analytical_thinking': 'analytical_ability',
            'spatial_reasoning': 'spatial_ability',
            'digital_fluency': 'digital_ability',
            'computational_thinking': 'digital_ability'
        }

        for ans in answers:
            q = ans.question
            if not q or not q.skill_category:
                continue

            raw_skill = q.skill_category.strip()
            target_skills = [raw_skill]
            if raw_skill in SKILL_ALIASES:
                target_skills.append(SKILL_ALIASES[raw_skill])

            # Also cross-map scientific_interest to research_interest
            if raw_skill in ['scientific_interest', 'science_interest']:
                target_skills.append('research_interest')

            pts = 0.0
            max_pts = 100.0

            if q.question_type in ['MCQ', 'SCENARIO']:
                selected_opt = next((opt for opt in q.options if str(opt.option_value) == str(ans.selected_option)), None)
                raw_score = (selected_opt.score if selected_opt else 0.0)
                all_opts = q.options
                opt_max = max([opt.score for opt in all_opts] or [1.0])
                pts = raw_score
                max_pts = opt_max if opt_max > 0 else 1.0

            elif q.question_type == 'RATING':
                val = ans.numeric_value
                if val is None and ans.selected_option:
                    try:
                        val = float(ans.selected_option)
                    except ValueError:
                        selected_opt = next((opt for opt in q.options if str(opt.option_value) == str(ans.selected_option)), None)
                        val = selected_opt.score if selected_opt else 60.0

                if val is not None:
                    normalized_val = val if val > 5 else (val / 5.0) * 100.0
                    pts = normalized_val
                    max_pts = 100.0

            elif q.question_type == 'MULTI_SELECT':
                selected_vals = [s.strip() for s in (ans.selected_option or '').split(',') if s.strip()]
                opts = q.options
                total_max = sum(opt.score for opt in opts if opt.score > 0) or 1.0
                earned = sum(opt.score for opt in opts if str(opt.option_value) in selected_vals)
                pts = earned
                max_pts = total_max if total_max > 0 else 1.0

            for skill in set(target_skills):
                if skill in category_scores:
                    category_scores[skill] = category_scores.get(skill, 0.0) + pts
                    category_max[skill] = category_max.get(skill, 0.0) + max_pts

        # Calculate final normalized percentage (0 - 100) for each dimension
        normalized_results: Dict[str, float] = {}
        for dim in tracked_dimensions:
            max_p = category_max.get(dim, 0.0)
            if max_p > 0:
                score_pct = (category_scores.get(dim, 0.0) / max_p) * 100.0
                normalized_results[dim] = max(0.0, min(100.0, round(score_pct, 1)))

        # Dynamic correlated baseline for dimensions without direct questions
        def get_dim(d_name: str, fallback: float = 60.0) -> float:
            return normalized_results.get(d_name, fallback)

        # Infer correlated baseline if missing
        if 'research_interest' not in normalized_results:
            normalized_results['research_interest'] = round((get_dim('scientific_reasoning', 65.0) * 0.6 + get_dim('analytical_ability', 65.0) * 0.4), 1)
        if 'science_interest' not in normalized_results:
            normalized_results['science_interest'] = round(get_dim('scientific_reasoning', 65.0), 1)
        if 'technology_interest' not in normalized_results:
            normalized_results['technology_interest'] = round((get_dim('digital_ability', 70.0) * 0.6 + get_dim('logical_reasoning', 70.0) * 0.4), 1)
        if 'healthcare_interest' not in normalized_results:
            normalized_results['healthcare_interest'] = round((get_dim('scientific_reasoning', 60.0) * 0.7 + get_dim('social_interest', 60.0) * 0.3), 1)
        if 'business_interest' not in normalized_results:
            normalized_results['business_interest'] = round((get_dim('mathematical_ability', 60.0) * 0.5 + get_dim('communication', 60.0) * 0.5), 1)
        if 'creative_interest' not in normalized_results:
            normalized_results['creative_interest'] = round(get_dim('creativity', 65.0), 1)
        if 'social_interest' not in normalized_results:
            normalized_results['social_interest'] = round((get_dim('communication', 60.0) * 0.6 + get_dim('teamwork', 60.0) * 0.4), 1)

        # Fill any remaining cognitive dimensions with a personalized baseline
        for dim in tracked_dimensions:
            if dim not in normalized_results:
                normalized_results[dim] = 60.0

        # Update session scores directly in JSON
        session.scores_data = normalized_results
        flag_modified(session, 'scores_data')
        db.session.commit()
        return session.scores
