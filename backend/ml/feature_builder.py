"""
Feature Builder Module.
Constructs standard feature dataframes for model inference.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from backend.ml.model_loader import get_feature_columns

PRIMARY_ABILITY_PAIRS = [
    ('mathematical_ability', 'required_mathematical_ability'),
    ('logical_reasoning', 'required_logical_reasoning'),
    ('scientific_reasoning', 'required_scientific_thinking'),
    ('problem_solving', 'required_problem_solving'),
    ('analytical_ability', 'required_analytical_thinking'),
    ('communication', 'required_communication'),
    ('creativity', 'required_creativity'),
    ('digital_ability', 'required_digital_ability'),
]

PRIMARY_INTEREST_PAIRS = [
    ('technology_interest', 'required_technology_interest'),
    ('engineering_interest', 'required_engineering_interest'),
    ('healthcare_interest', 'required_healthcare_interest'),
    ('business_interest', 'required_business_interest'),
    ('finance_interest', 'required_finance_interest'),
    ('arts_interest', 'required_arts_interest'),
    ('design_interest', 'required_design_interest'),
    ('research_interest', 'required_research_interest'),
    ('environment_interest', 'required_environment_interest'),
    ('agriculture_interest', 'required_agriculture_interest'),
]

# Comprehensive domain-to-ability and domain-to-interest profiles for all 23 career domains
DOMAIN_PROFILES = {
    'agriculture & life sciences': {
        'abilities': ['scientific_reasoning', 'observation', 'practical_ability', 'problem_solving'],
        'interests': ['agriculture_interest', 'environment_interest', 'science_interest']
    },
    'architecture & planning': {
        'abilities': ['spatial_ability', 'creativity', 'mathematical_ability', 'observation'],
        'interests': ['design_interest', 'creative_interest', 'engineering_interest']
    },
    'arts & creative design': {
        'abilities': ['creativity', 'spatial_ability', 'observation', 'communication'],
        'interests': ['creative_interest', 'arts_interest', 'design_interest']
    },
    'aviation & aerospace': {
        'abilities': ['spatial_ability', 'mathematical_ability', 'practical_ability', 'observation', 'problem_solving'],
        'interests': ['engineering_interest', 'technology_interest', 'science_interest']
    },
    'business & management': {
        'abilities': ['leadership', 'communication', 'analytical_ability', 'teamwork', 'problem_solving'],
        'interests': ['business_interest', 'finance_interest', 'social_interest']
    },
    'defense & security': {
        'abilities': ['leadership', 'practical_ability', 'spatial_ability', 'observation', 'teamwork'],
        'interests': ['social_interest', 'technology_interest', 'engineering_interest']
    },
    'education & training': {
        'abilities': ['communication', 'learning_ability', 'teamwork', 'observation', 'memory'],
        'interests': ['social_interest', 'research_interest']
    },
    'energy & environment': {
        'abilities': ['scientific_reasoning', 'problem_solving', 'practical_ability', 'observation'],
        'interests': ['environment_interest', 'science_interest', 'engineering_interest']
    },
    'engineering': {
        'abilities': ['mathematical_ability', 'logical_reasoning', 'spatial_ability', 'practical_ability', 'problem_solving'],
        'interests': ['engineering_interest', 'technology_interest', 'science_interest']
    },
    'finance & commerce': {
        'abilities': ['mathematical_ability', 'analytical_ability', 'logical_reasoning', 'problem_solving'],
        'interests': ['finance_interest', 'business_interest']
    },
    'governance & public policy': {
        'abilities': ['leadership', 'communication', 'analytical_ability', 'logical_reasoning'],
        'interests': ['social_interest', 'business_interest', 'research_interest']
    },
    'healthcare & engineering': {
        'abilities': ['scientific_reasoning', 'problem_solving', 'mathematical_ability', 'practical_ability'],
        'interests': ['healthcare_interest', 'engineering_interest', 'technology_interest']
    },
    'healthcare & life sciences': {
        'abilities': ['scientific_reasoning', 'observation', 'memory', 'problem_solving', 'practical_ability'],
        'interests': ['healthcare_interest', 'science_interest', 'social_interest']
    },
    'hospitality & culinary arts': {
        'abilities': ['creativity', 'practical_ability', 'communication', 'teamwork', 'observation'],
        'interests': ['creative_interest', 'social_interest', 'business_interest']
    },
    'hospitality & tourism': {
        'abilities': ['communication', 'teamwork', 'leadership', 'observation'],
        'interests': ['social_interest', 'business_interest']
    },
    'information technology': {
        'abilities': ['logical_reasoning', 'mathematical_ability', 'problem_solving', 'digital_ability', 'analytical_ability'],
        'interests': ['technology_interest', 'research_interest']
    },
    'law & legal services': {
        'abilities': ['logical_reasoning', 'analytical_ability', 'communication', 'memory'],
        'interests': ['social_interest', 'research_interest', 'business_interest']
    },
    'logistics & supply chain': {
        'abilities': ['analytical_ability', 'problem_solving', 'practical_ability', 'teamwork', 'leadership'],
        'interests': ['business_interest', 'technology_interest']
    },
    'media & communication': {
        'abilities': ['communication', 'creativity', 'observation', 'memory'],
        'interests': ['creative_interest', 'social_interest', 'arts_interest']
    },
    'psychology & social services': {
        'abilities': ['communication', 'observation', 'teamwork', 'problem_solving'],
        'interests': ['social_interest', 'healthcare_interest', 'research_interest']
    },
    'science & research': {
        'abilities': ['scientific_reasoning', 'analytical_ability', 'logical_reasoning', 'observation'],
        'interests': ['research_interest', 'science_interest']
    },
    'sports & fitness': {
        'abilities': ['practical_ability', 'teamwork', 'leadership', 'observation'],
        'interests': ['social_interest']
    },
    'trades & technical services': {
        'abilities': ['practical_ability', 'spatial_ability', 'problem_solving', 'observation'],
        'interests': ['engineering_interest', 'technology_interest']
    }
}


SPECIFIC_ROLE_PROFILES = {
    # Information Technology & Data
    'ai engineer': (['logical_reasoning', 'mathematical_ability', 'digital_ability', 'problem_solving'], ['technology_interest', 'research_interest']),
    'data scientist': (['analytical_ability', 'mathematical_ability', 'scientific_reasoning', 'problem_solving'], ['research_interest', 'technology_interest']),
    'data analyst': (['analytical_ability', 'mathematical_ability', 'logical_reasoning'], ['technology_interest', 'business_interest']),
    'cloud engineer': (['digital_ability', 'logical_reasoning', 'practical_ability', 'problem_solving'], ['technology_interest']),
    'cloud solutions architect': (['digital_ability', 'logical_reasoning', 'practical_ability', 'problem_solving'], ['technology_interest']),
    'cloud software architect': (['digital_ability', 'logical_reasoning', 'mathematical_ability', 'problem_solving'], ['technology_interest']),
    'cloud architect': (['digital_ability', 'logical_reasoning', 'practical_ability', 'problem_solving'], ['technology_interest']),
    'cybersecurity analyst': (['digital_ability', 'observation', 'logical_reasoning', 'problem_solving'], ['technology_interest']),
    'software developer': (['logical_reasoning', 'digital_ability', 'problem_solving', 'creativity'], ['technology_interest']),
    'mobile app developer': (['digital_ability', 'creativity', 'logical_reasoning', 'problem_solving'], ['technology_interest', 'creative_interest']),
    'database administrator': (['digital_ability', 'analytical_ability', 'observation', 'logical_reasoning'], ['technology_interest']),
    'network engineer': (['digital_ability', 'practical_ability', 'logical_reasoning'], ['technology_interest']),
    'ui / ux designer': (['creativity', 'digital_ability', 'observation', 'communication'], ['creative_interest', 'technology_interest']),
    'machine learning engineer': (['logical_reasoning', 'mathematical_ability', 'digital_ability', 'problem_solving'], ['technology_interest', 'research_interest']),
    # Healthcare & Medicine
    'doctor': (['scientific_reasoning', 'observation', 'problem_solving', 'practical_ability'], ['healthcare_interest', 'science_interest']),
    'dentist': (['practical_ability', 'spatial_ability', 'observation', 'scientific_reasoning'], ['healthcare_interest']),
    'nurse': (['communication', 'teamwork', 'observation', 'practical_ability'], ['healthcare_interest', 'social_interest']),
    'biotechnologist': (['scientific_reasoning', 'analytical_ability', 'observation'], ['science_interest', 'research_interest']),
    'pharmacist': (['scientific_reasoning', 'observation', 'memory', 'mathematical_ability'], ['healthcare_interest', 'science_interest']),
    # Finance & Commerce
    'accountant': (['mathematical_ability', 'analytical_ability', 'observation'], ['finance_interest', 'business_interest']),
    'auditor': (['analytical_ability', 'observation', 'logical_reasoning'], ['finance_interest', 'business_interest']),
    'financial analyst': (['analytical_ability', 'mathematical_ability', 'logical_reasoning'], ['finance_interest', 'business_interest']),
    'investment banker': (['mathematical_ability', 'analytical_ability', 'leadership', 'communication'], ['finance_interest', 'business_interest']),
    # Engineering & Architecture
    'architect': (['spatial_ability', 'creativity', 'mathematical_ability', 'observation'], ['creative_interest', 'engineering_interest']),
    'mechanical engineer': (['spatial_ability', 'mathematical_ability', 'practical_ability', 'problem_solving'], ['engineering_interest']),
    'civil engineer': (['spatial_ability', 'mathematical_ability', 'practical_ability', 'observation'], ['engineering_interest']),
    'electrical engineer': (['logical_reasoning', 'mathematical_ability', 'practical_ability', 'problem_solving'], ['engineering_interest']),
    'aerospace engineer': (['mathematical_ability', 'spatial_ability', 'scientific_reasoning', 'problem_solving'], ['engineering_interest', 'technology_interest']),
    # Arts, Media & Design
    'animator': (['creativity', 'spatial_ability', 'digital_ability', 'observation'], ['creative_interest']),
    'graphic designer': (['creativity', 'spatial_ability', 'digital_ability', 'observation'], ['creative_interest']),
    'content creator': (['communication', 'creativity', 'digital_ability'], ['creative_interest', 'social_interest']),
    'journalist': (['communication', 'creativity', 'observation', 'logical_reasoning'], ['social_interest', 'creative_interest']),
    # Law, Education & Management
    'lawyer': (['communication', 'logical_reasoning', 'analytical_ability'], ['social_interest', 'research_interest']),
    'judge': (['logical_reasoning', 'analytical_ability', 'observation', 'communication'], ['social_interest', 'research_interest']),
    'teacher': (['communication', 'learning_ability', 'teamwork', 'observation'], ['social_interest', 'research_interest']),
    'human resources manager': (['communication', 'teamwork', 'leadership', 'observation'], ['social_interest', 'business_interest']),
    'marketing manager': (['communication', 'creativity', 'analytical_ability', 'leadership'], ['business_interest', 'creative_interest']),
    'product manager': (['leadership', 'communication', 'problem_solving', 'analytical_ability'], ['business_interest', 'technology_interest']),
}


def get_domain_profile(domain_name: str, career_name: str = '') -> tuple:
    """Finds matching domain profile and refines by career title keywords."""
    if career_name:
        c_clean = career_name.lower().replace(' specialist', '').strip()
        if c_clean in SPECIFIC_ROLE_PROFILES:
            return SPECIFIC_ROLE_PROFILES[c_clean]
        for k, v in sorted(SPECIFIC_ROLE_PROFILES.items(), key=lambda x: len(x[0]), reverse=True):
            if k in c_clean:
                return v

    d_clean = (domain_name or '').lower().strip()
    profile = None
    for k, v in DOMAIN_PROFILES.items():
        if k in d_clean or d_clean in k:
            profile = v
            break
    if not profile:
        profile = {
            'abilities': ['logical_reasoning', 'problem_solving', 'communication', 'mathematical_ability'],
            'interests': ['technology_interest', 'science_interest', 'business_interest']
        }

    abilities = list(profile['abilities'])
    interests = list(profile['interests'])

    c_clean = (career_name or '').lower().strip()
    if 'analyst' in c_clean and 'analytical_ability' not in abilities:
        abilities.append('analytical_ability')
    if ('manager' in c_clean or 'lead' in c_clean) and 'leadership' not in abilities:
        abilities.append('leadership')
    if ('design' in c_clean or 'art' in c_clean or 'animat' in c_clean) and 'creativity' not in abilities:
        abilities.append('creativity')
    if 'engineer' in c_clean and 'problem_solving' not in abilities:
        abilities.append('problem_solving')
    if ('doctor' in c_clean or 'nurse' in c_clean or 'physician' in c_clean) and 'healthcare_interest' not in interests:
        interests.append('healthcare_interest')

    return abilities, interests


class FeatureBuilder:
    """Constructs multi-dimensional student-career candidate feature rows."""

    @classmethod
    def calculate_ability_match(cls, scores: Dict[str, Any], career_reqs: Dict[str, Any]) -> float:
        """Calculates ability match score between student scores and career requirements."""
        domain = career_reqs.get('career_domain') or career_reqs.get('domain') or career_reqs.get('domain_name') or ''
        cname = career_reqs.get('career_name') or career_reqs.get('title') or ''

        if domain or cname:
            abilities, _ = get_domain_profile(str(domain), str(cname))
            vals = [float(scores.get(ab, 50.0)) for ab in abilities]
            if vals:
                return round(float(np.mean(vals)), 2)

        matches = []
        for s_key, r_key in PRIMARY_ABILITY_PAIRS:
            s_val = float(scores.get(s_key, 75.0))
            r_val = float(career_reqs.get(r_key, 70.0))
            match = max(0.0, 100.0 - abs(s_val - r_val))
            matches.append(match)
        return float(np.mean(matches)) if matches else 75.0

    @classmethod
    def calculate_interest_match(cls, scores: Dict[str, Any], career_reqs: Dict[str, Any]) -> float:
        """Calculates interest match score between student scores and career requirements."""
        domain = career_reqs.get('career_domain') or career_reqs.get('domain') or career_reqs.get('domain_name') or ''
        cname = career_reqs.get('career_name') or career_reqs.get('title') or ''

        if domain or cname:
            _, interests = get_domain_profile(str(domain), str(cname))
            vals = [float(scores.get(it, 50.0)) for it in interests]
            if vals:
                return round(float(np.mean(vals)), 2)

        matches = []
        for s_key, r_key in PRIMARY_INTEREST_PAIRS:
            s_val = float(scores.get(s_key, 50.0))
            r_val = float(career_reqs.get(r_key, 50.0))
            match = max(0.0, 100.0 - abs(s_val - r_val))
            matches.append(match)
        return float(np.mean(matches)) if matches else 50.0

    @classmethod
    def build_candidate_feature_row(
        cls,
        student_profile: Dict[str, Any],
        career_reqs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Builds a single candidate feature row dict conforming to get_feature_columns()."""
        scores = student_profile.get('scores', {})
        age_val = int(student_profile.get('age', 16))
        class_val = int(student_profile.get('class_level', student_profile.get('class', 10)))
        stream_val = str(student_profile.get('stream', 'Science')).strip()

        ability_match = cls.calculate_ability_match(scores, career_reqs)
        interest_match = cls.calculate_interest_match(scores, career_reqs)
        academic_match = float(student_profile.get('academic_percentage', 78.0))
        learning_match = float(scores.get('learning_ability', 75.0))

        comp_idx = (ability_match * 0.40) + (interest_match * 0.35) + (academic_match * 0.25)
        synergy = float(np.sqrt(max(ability_match * interest_match, 0.0)))
        gap = float(abs(ability_match - interest_match))
        min_core = float(min(ability_match, interest_match, academic_match))
        max_core = float(max(ability_match, interest_match, academic_match))
        harmonic = float(3.0 / (1.0/max(ability_match, 1.0) + 1.0/max(interest_match, 1.0) + 1.0/max(academic_match, 1.0)))
        geom = float((max(ability_match * interest_match * academic_match, 0.0)) ** (1.0/3.0))
        holistic = float((comp_idx + synergy + harmonic + geom) / 4.0)

        c_dom = str(career_reqs.get('career_domain', career_reqs.get('domain', 'Technology'))).strip()
        c_name = str(career_reqs.get('career_name', 'Career')).strip()

        return {
            'age': age_val,
            'class': class_val,
            'ability_match_component': round(ability_match, 2),
            'interest_match_component': round(interest_match, 2),
            'academic_match_component': round(academic_match, 2),
            'learning_match_component': round(learning_match, 2),
            'composite_alignment_index': round(comp_idx, 2),
            'ability_interest_synergy': round(synergy, 2),
            'ability_interest_gap': round(gap, 2),
            'min_core_match': round(min_core, 2),
            'max_core_match': round(max_core, 2),
            'harmonic_core_match': round(harmonic, 2),
            'geometric_core_synergy': round(geom, 2),
            'holistic_synergy': round(holistic, 2),
            'stream': stream_val,
            'career_domain': c_dom,
            'career_name': c_name
        }

    @classmethod
    def build_batch_features(
        cls,
        student_profile: Dict[str, Any],
        catalogue: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Builds feature candidate rows for every career in the catalogue:
        Combines student assessment attributes and career candidate attributes.
        """
        rows = []
        for _, c_row in catalogue.iterrows():
            c_dict = c_row.to_dict()
            row = cls.build_candidate_feature_row(student_profile, c_dict)
            rows.append(row)

        df_out = pd.DataFrame(rows)
        # Enforce column order to exactly match get_feature_columns()
        expected_cols = get_feature_columns()
        return df_out[expected_cols]
