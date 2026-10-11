"""
Assessment Question Selection Engine.
Selects a balanced, grade-appropriate, randomized, and attempt-differentiated subset of questions
from the master question pool in MySQL/SQLite for each student assessment session.
Guarantees section quotas, core cognitive ability coverage, stream filtering, and prevents duplicate
questions across consecutive attempts for the same student.
"""

import json
import random
from typing import List, Dict, Any, Optional, Set
from backend.models.question import Question
from backend.models.assessment import AssessmentSession


class AssessmentSelectionService:
    """Intelligent adaptive question selection, randomization, and attempt-differentiation service."""

    # Target question counts per student grade cohort (set to 20)
    COHORT_TARGETS = {
        'middle_school': {'min_class': 7, 'max_class': 8, 'target_count': 20, 'difficulty_pref': ['Easy', 'Medium']},
        'secondary': {'min_class': 9, 'max_class': 10, 'target_count': 20, 'difficulty_pref': ['Easy', 'Medium', 'Hard']},
        'higher_secondary': {'min_class': 11, 'max_class': 12, 'target_count': 20, 'difficulty_pref': ['Medium', 'Hard', 'Easy']}
    }

    # Minimum questions required per section for a balanced assessment (sums to 19, leaving 1 dynamic slot filled by cohort priority)
    SECTION_QUOTAS = {
        # Section ID: (Min Count Middle School [20], Min Count Secondary [20], Min Count Higher Sec [20])
        1: (1, 1, 1),   # Academic Profile
        2: (1, 1, 1),   # Mathematical Ability
        3: (1, 1, 1),   # Logical Reasoning
        4: (1, 1, 1),   # Scientific Thinking
        5: (1, 1, 1),   # Problem Solving
        6: (1, 1, 1),   # Analytical Thinking
        7: (1, 1, 1),   # Communication
        8: (1, 1, 1),   # Creativity
        9: (1, 1, 1),   # Digital Ability
        10: (1, 1, 1),  # Learning Ability
        11: (1, 1, 1),  # Spatial Ability
        12: (1, 1, 1),  # Practical Ability
        13: (1, 1, 1),  # Interests
        14: (1, 1, 1),  # Activities
        15: (1, 1, 1),  # Teamwork
        16: (1, 1, 1),  # Leadership
        17: (1, 1, 1),  # Work Preferences
        18: (1, 1, 1),  # Career Awareness
        19: (1, 1, 1)   # Career Preferences
    }

    @classmethod
    def get_cohort_key(cls, class_level: int) -> str:
        """Determines the cohort grouping for a given class level."""
        if class_level in [7, 8]:
            return 'middle_school'
        elif class_level in [9, 10]:
            return 'secondary'
        else:
            return 'higher_secondary'

    @classmethod
    def get_student_prior_question_ids(cls, student_id: int) -> Set[int]:
        """
        Retrieves all question IDs previously assigned or answered by a student
        across all past assessment sessions to prevent duplicates in retakes.
        """
        prior_ids: Set[int] = set()
        try:
            sessions = AssessmentSession.query.filter_by(student_id=student_id).all()
            session_ids = [s.id for s in sessions]

            # 1. From session metadata
            for s in sessions:
                if s.selected_question_ids:
                    try:
                        ids = json.loads(s.selected_question_ids)
                        if isinstance(ids, list):
                            prior_ids.update(ids)
                    except Exception:
                        pass

            # 2. From actual answered responses in session JSON
            for s in sessions:
                if s.answers_data and isinstance(s.answers_data, dict):
                    for qid in s.answers_data.keys():
                        if str(qid).isdigit():
                            prior_ids.add(int(qid))
        except Exception:
            pass

        return prior_ids

    @classmethod
    def select_balanced_questions(
        cls,
        class_level: int,
        stream: Optional[str] = None,
        student_id: Optional[int] = None,
        exclude_question_ids: Optional[Set[int]] = None,
        random_seed: Optional[int] = None
    ) -> List[Question]:
        """
        Selects a balanced, curated, randomized, and attempt-differentiated subset of questions:
        1. Queries all eligible active questions for class_level and stream.
        2. Automatically excludes questions previously attempted by student_id in prior sessions.
        3. Fulfills section quotas and ability coverage with randomized balanced sampling.
        4. Fills remaining slots up to target_count with cohort-appropriate difficulty.
        5. Returns selected questions ordered naturally by section and display order.
        """
        cohort_key = cls.get_cohort_key(class_level)
        cohort_config = cls.COHORT_TARGETS[cohort_key]
        target_count = cohort_config['target_count']
        diff_priority = cohort_config['difficulty_pref']

        # Determine index for quota tuple (0 for middle, 1 for secondary, 2 for higher secondary)
        quota_idx = 0 if cohort_key == 'middle_school' else (1 if cohort_key == 'secondary' else 2)

        # 1. Build exclusion set for retakes
        excluded: Set[int] = set()
        if exclude_question_ids:
            excluded.update(exclude_question_ids)
        if student_id is not None:
            excluded.update(cls.get_student_prior_question_ids(student_id))

        # 2. Fetch eligible question pool from database
        query = Question.query.filter(
            Question.is_active == True,
            Question.class_min <= class_level,
            Question.class_max >= class_level
        )

        clean_stream = (stream or 'General').strip()
        if clean_stream.lower() not in ['all', 'general']:
            prefix = clean_stream.split('-')[0].strip()
            query = query.filter(
                (Question.stream_specific == 'All') |
                (Question.stream_specific == 'General') |
                (Question.stream_specific.ilike(f"%{prefix}%"))
            )
        else:
            query = query.filter(
                (Question.stream_specific == 'All') |
                (Question.stream_specific == 'General') |
                (Question.stream_specific.is_(None))
            )

        eligible_pool = query.order_by(Question.section_id.asc(), Question.display_order.asc()).all()
        if not eligible_pool:
            return []

        # 3. Partition eligible pool into Fresh (unattempted) vs Previously Attempted
        fresh_pool = [q for q in eligible_pool if q.id not in excluded]
        fallback_pool = [q for q in eligible_pool if q.id in excluded]

        # Use PRNG for dynamic per-user and per-attempt randomized sampling
        rng = random.Random(random_seed) if random_seed is not None else random.Random()

        # Group fresh questions by section
        fresh_section_buckets: Dict[int, List[Question]] = {}
        for q in fresh_pool:
            fresh_section_buckets.setdefault(q.section_id, []).append(q)

        fallback_section_buckets: Dict[int, List[Question]] = {}
        for q in fallback_pool:
            fallback_section_buckets.setdefault(q.section_id, []).append(q)

        selected_questions_map: Dict[int, Question] = {}

        # 4. Step 1: Satisfy Minimum Section Quotas (prioritizing fresh questions)
        all_section_ids = sorted(list(cls.SECTION_QUOTAS.keys()))
        for section_id in all_section_ids:
            min_required = cls.SECTION_QUOTAS.get(section_id, (1, 1, 1))[quota_idx]
            fresh_q_list = list(fresh_section_buckets.get(section_id, []))
            fallback_q_list = list(fallback_section_buckets.get(section_id, []))

            # Sort candidate pool prioritizing cohort difficulty, then randomize within difficulty
            def sort_key(q):
                p_idx = diff_priority.index(q.difficulty) if q.difficulty in diff_priority else 99
                return (p_idx, rng.random())

            fresh_q_list.sort(key=sort_key)
            fallback_q_list.sort(key=sort_key)

            # Pick from fresh first
            picked_fresh = fresh_q_list[:min_required]
            for q in picked_fresh:
                selected_questions_map[q.id] = q

            # If fresh pool was insufficient for quota, pick shortfall from fallback pool
            shortfall = min_required - len(picked_fresh)
            if shortfall > 0 and fallback_q_list:
                picked_fallback = fallback_q_list[:shortfall]
                for q in picked_fallback:
                    selected_questions_map[q.id] = q

        # 5. Step 2: Fill remaining slots up to target_count using preferred difficulty distribution
        remaining_fresh = [q for q in fresh_pool if q.id not in selected_questions_map]
        remaining_fallback = [q for q in fallback_pool if q.id not in selected_questions_map]

        remaining_fresh.sort(key=lambda q: (
            diff_priority.index(q.difficulty) if q.difficulty in diff_priority else 99,
            rng.random()
        ))
        remaining_fallback.sort(key=lambda q: (
            diff_priority.index(q.difficulty) if q.difficulty in diff_priority else 99,
            rng.random()
        ))

        slots_needed = target_count - len(selected_questions_map)
        if slots_needed > 0 and remaining_fresh:
            for q in remaining_fresh[:slots_needed]:
                selected_questions_map[q.id] = q
            slots_needed = target_count - len(selected_questions_map)

        if slots_needed > 0 and remaining_fallback:
            for q in remaining_fallback[:slots_needed]:
                selected_questions_map[q.id] = q

        # 6. Return final selected questions in natural section, display order, and ID
        final_list = sorted(
            selected_questions_map.values(),
            key=lambda q: (q.section_id, q.display_order, q.id)
        )
        return final_list
