"""
Student Profile Synthesis Engine.
Synthesizes cognitive aptitude scores, disciplinary interests, academic performance,
extracurricular activities, and workplace preferences into a holistic student guidance profile.
Identifies standout strengths, tailored developmental areas, and vocational alignment.
"""

from typing import Dict, Any, List, Optional
from backend.extensions import db
from backend.models.assessment import AssessmentSession
from backend.models.student import Student
from backend.services.scoring_service import ScoringService


class StudentProfileService:
    """Core analytical service for student profile generation."""

    ABILITY_DESCRIPTIONS = {
        'mathematical_ability': {
            'title': 'Mathematical & Quantitative Reasoning',
            'strength_text': 'Exceptional precision in numerical computation, algebraic formulations, and quantitative modeling.',
            'growth_text': 'Practice structured step-by-step arithmetic problem sets, algebra puzzles, and practical financial mathematics.'
        },
        'logical_reasoning': {
            'title': 'Logical Deductive Reasoning',
            'strength_text': 'Strong ability to identify patterns, evaluate deductive arguments, and deduce sequential relationships.',
            'growth_text': 'Engage with logic grids, syllogism practice, chess puzzles, and algorithmic flowcharts.'
        },
        'scientific_reasoning': {
            'title': 'Scientific & Empirical Thinking',
            'strength_text': 'Demonstrates high scientific curiosity, variable isolation skills, and cause-effect deduction.',
            'growth_text': 'Conduct hands-on science experiments, read peer-reviewed popular science journals, and test hypotheses.'
        },
        'problem_solving': {
            'title': 'Strategic Problem Solving',
            'strength_text': 'Methodical approach to troubleshooting complex constraints and optimizing solution pathways.',
            'growth_text': 'Break complex everyday challenges into smaller milestones and practice structured root-cause analysis.'
        },
        'analytical_ability': {
            'title': 'Data & Analytical Interpretation',
            'strength_text': 'Sharp capacity to interpret visual graphs, identify data outliers, and synthesize factual conclusions.',
            'growth_text': 'Work with spreadsheet charts, analyze public dataset infographics, and evaluate data arguments.'
        },
        'communication': {
            'title': 'Verbal & Written Communication',
            'strength_text': 'Articulate expression, audience-tailored clarity, and structured presentation capability.',
            'growth_text': 'Participate actively in classroom debates, book reviews, public speaking clubs, and essay writing.'
        },
        'creativity': {
            'title': 'Creative & Divergent Thinking',
            'strength_text': 'Original ideation, design intuition, lateral thinking, and cross-domain innovation.',
            'growth_text': 'Experiment with sketch design, creative storytelling, UI prototyping, and multi-disciplinary maker projects.'
        },
        'digital_ability': {
            'title': 'Computational & Digital Fluency',
            'strength_text': 'High digital comprehension, algorithmic understanding, and cyber awareness.',
            'growth_text': 'Build small computer coding scripts (Python/Scratch), learn database basics, and explore robotics.'
        },
        'learning_ability': {
            'title': 'Active Learning & Cognitive Agility',
            'strength_text': 'Self-driven intellectual curiosity and rapid conceptual absorption in novel domains.',
            'growth_text': 'Adopt active recall techniques, Feynman study methods, and independent online course exploration.'
        },
        'spatial_ability': {
            'title': '3D Spatial & Geometric Reasoning',
            'strength_text': 'High aptitude for mental rotation, structural geometry visualization, and mechanical linkages.',
            'growth_text': 'Practice 3D CAD modeling, origami geometric folding, isometric sketching, and spatial puzzles.'
        },
        'practical_ability': {
            'title': 'Practical & Mechanical Aptitude',
            'strength_text': 'Hands-on dexterity, mechanical tool comfort, and physical systems troubleshooting.',
            'growth_text': 'Assemble DIY electronic kits, disassemble and repair basic appliances, and practice workshop crafting.'
        },
        'teamwork': {
            'title': 'Collaborative Teamwork',
            'strength_text': 'Empathetic consensus building, shared accountability, and cooperative execution.',
            'growth_text': 'Take on collaborative group responsibilities, practice active listening, and support peer teammates.'
        },
        'leadership': {
            'title': 'Initiative & Leadership',
            'strength_text': 'Proactive initiative taking, strengths-based delegation, and high ethical responsibility.',
            'growth_text': 'Volunteer to lead small school initiatives, mentor junior students, and coordinate community events.'
        }
    }

    @classmethod
    def generate_student_profile(cls, assessment_id: int) -> Dict[str, Any]:
        """
        Synthesizes the complete student assessment profile from database records.
        Returns a rich structured dictionary suitable for APIs and UI rendering.
        """
        session = db.session.get(AssessmentSession, assessment_id)
        if not session:
            raise ValueError(f"Assessment session {assessment_id} not found.")

        student = session.student
        scores_record = session.scores
        academic_record = student.academic_scores if student else None

        # 1. Academic Profile Synthesis
        academic_profile = {
            'overall_percentage': float(academic_record.overall_percentage) if academic_record and academic_record.overall_percentage is not None else 80.0,
            'stream': student.stream or 'General',
            'board': student.board or 'CBSE',
            'medium': student.medium or 'English',
            'subject_scores': {}
        }
        if academic_record:
            subject_fields = [
                ('Mathematics', academic_record.mathematics_score),
                ('Science', academic_record.science_score),
                ('Physics', academic_record.physics_score),
                ('Chemistry', academic_record.chemistry_score),
                ('Computer Science', academic_record.computer_science_score),
                ('English', academic_record.english_score),
                ('Social Science', academic_record.social_science_score)
            ]
            for subj_name, val in subject_fields:
                if val is not None:
                    academic_profile['subject_scores'][subj_name] = float(val)

        # 2. Abilities Profile (Cognitive & Behavioral Aptitude)
        abilities_dict = {}
        if scores_record:
            raw_cognitive = scores_record.to_dict()['cognitive_scores']
            for dim, score_val in raw_cognitive.items():
                cat_info = ScoringService.get_score_category(score_val)
                meta = cls.ABILITY_DESCRIPTIONS.get(dim, {})
                abilities_dict[dim] = {
                    'title': meta.get('title', dim.replace('_', ' ').title()),
                    'score': score_val,
                    'label': cat_info['label'],
                    'description': cat_info['description']
                }

        # 3. Interests Profile
        interests_dict = {}
        if scores_record:
            raw_interests = scores_record.to_dict()['interest_scores']
            for dim, score_val in raw_interests.items():
                cat_info = ScoringService.get_score_category(score_val)
                interests_dict[dim] = {
                    'title': dim.replace('_', ' ').title(),
                    'score': score_val,
                    'label': cat_info['label']
                }

        # 4. Extract Work Preferences & Activities from Student Answers
        answers = session.answers.all()
        work_preferences = {
            'environment': 'Modern Tech / Collaborative Office',
            'collaboration_style': 'Balanced Solo & Team Work',
            'task_orientation': 'Balanced Data & People Interaction',
            'travel_preference': 'Occasional Travel'
        }
        activity_scores: Dict[str, float] = {}

        for ans in answers:
            q = ans.question
            if not q:
                continue
            code = q.question_code or ''

            # Work preference matching
            if code == 'WORK_01_ENV' and ans.selected_option:
                opt_map = {
                    'A': 'Modern Technology Office / Studio / Tech Hub',
                    'B': 'Scientific Laboratory / Clinical Healthcare Center',
                    'C': 'Outdoor Field Sites / Environmental Reserves / Projects',
                    'D': 'Flexible Remote Home Office / Global Digital Workflow'
                }
                work_preferences['environment'] = opt_map.get(ans.selected_option, work_preferences['environment'])

            elif code == 'WORK_02_STYLE' and ans.selected_option:
                opt_map = {
                    '1': '100% Solo Independent Focus',
                    '2': 'Mostly Independent with Periodic Check-ins',
                    '3': 'Balanced 50-50 Solo & Team Collaboration',
                    '4': 'Frequent Teamwork & Cross-functional Syncs',
                    '5': 'Constant People-facing Collaboration & Coaching'
                }
                work_preferences['collaboration_style'] = opt_map.get(ans.selected_option, work_preferences['collaboration_style'])

            elif code == 'WORK_03_DATA_PEOPLE' and ans.selected_option:
                opt_map = {
                    '1': 'Deep Data, Code & Quantitative Systems Focus',
                    '2': 'Mostly Technical & Data Focused',
                    '3': 'Balanced Technical Data & People Interaction',
                    '4': 'Frequent Client, Patient & Human Interaction',
                    '5': 'Strictly People-Facing, Public Service & Mentorship'
                }
                work_preferences['task_orientation'] = opt_map.get(ans.selected_option, work_preferences['task_orientation'])

            elif code == 'WORK_04_TRAVEL' and ans.selected_option:
                opt_map = {
                    '1': 'Fixed Stable Workplace (No Travel)',
                    '2': 'Minimal Local Travel',
                    '3': 'Occasional State/National Travel',
                    '4': 'Frequent Travel & Field Expeditions',
                    '5': 'Constant Global Mobility & International Travel'
                }
                work_preferences['travel_preference'] = opt_map.get(ans.selected_option, work_preferences['travel_preference'])

            # Activity frequency mapping
            if code.startswith('ACT_'):
                act_name = code.replace('ACT_', '').title()
                score_val = ans.numeric_value or 60.0
                if ans.selected_option and not ans.numeric_value:
                    try:
                        score_val = (float(ans.selected_option) / 5.0) * 100.0
                    except ValueError:
                        score_val = 60.0
                activity_scores[act_name] = round(score_val, 1)

        # 5. Determine Top Standout Strengths (Top 3-4 Abilities with score >= 60)
        sorted_abilities = sorted(
            abilities_dict.items(),
            key=lambda item: item[1]['score'],
            reverse=True
        )
        strengths = []
        for dim, info in sorted_abilities[:4]:
            meta = cls.ABILITY_DESCRIPTIONS.get(dim, {})
            strengths.append({
                'dimension': dim,
                'title': info['title'],
                'score': info['score'],
                'label': info['label'],
                'description': meta.get('strength_text', info['description'])
            })

        # 6. Determine Developmental Growth Areas (Bottom 2-3 Abilities)
        development_areas = []
        for dim, info in sorted_abilities[-3:]:
            if dim not in [s['dimension'] for s in strengths]:
                meta = cls.ABILITY_DESCRIPTIONS.get(dim, {})
                development_areas.append({
                    'dimension': dim,
                    'title': info['title'],
                    'score': info['score'],
                    'label': info['label'],
                    'growth_tip': meta.get('growth_text', 'Focus on guided conceptual practice and hands-on exercises.')
                })

        scores_flat = {}
        for dim, info in abilities_dict.items():
            scores_flat[dim] = info['score']
        for dim, info in interests_dict.items():
            scores_flat[dim] = info['score']
            short_dim = dim.replace('_interest', '')
            scores_flat[short_dim] = info['score']
            scores_flat[f"{short_dim}_interest"] = info['score']

        return {
            'student': student.to_dict(),
            'academic': academic_profile,
            'abilities': abilities_dict,
            'interests': interests_dict,
            'scores': scores_flat,
            'activities': activity_scores,
            'work_preferences': work_preferences,
            'strengths': strengths,
            'development_areas': development_areas
        }
