"""
Assessment Question Selection & Balancing Test Suite.
Verifies cohort question counts, section quotas, difficulty distributions,
stream filtering, and session persistence across page refreshes.
"""

import os
import sys
import json
import unittest
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student
from backend.models.question import Question, QuestionSection, QuestionOption
from backend.models.assessment import AssessmentSession
from backend.services.assessment_selection_service import AssessmentSelectionService
from backend.services.assessment_service import AssessmentService
from database.build_questions_dataset import MASTER_QUESTIONS


class TestAssessmentSelection(unittest.TestCase):
    """Unit tests for AssessmentSelectionService."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Seed sections
        sections_data = [
            (1, 'Academic Profile'), (2, 'Mathematical Ability'), (3, 'Logical Reasoning'),
            (4, 'Scientific Thinking'), (5, 'Problem Solving'), (6, 'Analytical Thinking'),
            (7, 'Communication'), (8, 'Creativity'), (9, 'Digital Ability'),
            (10, 'Learning Ability'), (11, 'Spatial Ability'), (12, 'Practical Ability'),
            (13, 'Interests'), (14, 'Activities'), (15, 'Teamwork'),
            (16, 'Leadership'), (17, 'Work Preferences'), (18, 'Career Awareness'),
            (19, 'Career Preferences')
        ]
        for s_id, s_name in sections_data:
            sec = QuestionSection(id=s_id, name=s_name, display_order=s_id, is_active=True)
            db.session.add(sec)
        db.session.commit()

        # Seed master questions
        for q in MASTER_QUESTIONS:
            q_obj = Question(
                question_code=q['question_code'],
                question_text=q['question_text'],
                section_id=q['section_id'],
                question_type=q['question_type'],
                class_min=q['class_min'],
                class_max=q['class_max'],
                difficulty=q['difficulty'],
                skill_category=q['skill_category'],
                stream_specific=q['stream_specific'],
                is_required=True,
                display_order=q['display_order'],
                is_active=True
            )
            db.session.add(q_obj)
            db.session.flush()

            for opt in q.get('options', []):
                opt_obj = QuestionOption(
                    question_id=q_obj.id,
                    option_text=opt['option_text'],
                    option_value=opt['option_value'],
                    score=float(opt.get('score', 0.0)),
                    is_correct=bool(opt.get('is_correct', False)),
                    display_order=opt.get('display_order', 1)
                )
                db.session.add(opt_obj)

        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_cohort_target_counts(self):
        """Verify selected question count falls into target bounds (19 to 21, target 20) for all classes."""
        # Class 7-8: target 20
        for c in [7, 8]:
            selected = AssessmentSelectionService.select_balanced_questions(c)
            self.assertGreaterEqual(len(selected), 19, f"Class {c} question count < 19: {len(selected)}")
            self.assertLessEqual(len(selected), 21, f"Class {c} question count > 21: {len(selected)}")

        # Class 9-10: target 20
        for c in [9, 10]:
            selected = AssessmentSelectionService.select_balanced_questions(c)
            self.assertGreaterEqual(len(selected), 19, f"Class {c} question count < 19: {len(selected)}")
            self.assertLessEqual(len(selected), 21, f"Class {c} question count > 21: {len(selected)}")

        # Class 11-12: target 20
        for c in [11, 12]:
            for stream in ['Science-PCM', 'Commerce', 'Humanities']:
                selected = AssessmentSelectionService.select_balanced_questions(c, stream=stream)
                self.assertGreaterEqual(len(selected), 19, f"Class {c} ({stream}) question count < 19: {len(selected)}")
                self.assertLessEqual(len(selected), 21, f"Class {c} ({stream}) question count > 21: {len(selected)}")

    def test_section_coverage_across_cohorts(self):
        """Verify selected questions include all major sections and ability dimensions."""
        for c in [7, 9, 11]:
            stream = 'Science-PCM' if c == 11 else 'General'
            selected = AssessmentSelectionService.select_balanced_questions(c, stream=stream)
            section_ids = set(q.section_id for q in selected)

            # Ensure presence of cognitive & interest sections
            for s_id in range(1, 20):
                self.assertIn(s_id, section_ids, f"Class {c} missing Section ID {s_id}")

    def test_difficulty_balancing(self):
        """Verify difficulty distribution matches pedagogical cohort guidelines."""
        # Class 7: mostly Easy + Medium across all questions
        sel_7 = AssessmentSelectionService.select_balanced_questions(7)
        diff_7 = Counter(q.difficulty for q in sel_7)
        self.assertGreater(diff_7.get('Easy', 0) + diff_7.get('Medium', 0), diff_7.get('Hard', 0))

        # Class 11: Cognitive questions (Sections 1-12) are predominantly Medium + Hard
        sel_11 = AssessmentSelectionService.select_balanced_questions(11, stream='Science-PCM')
        cognitive_q11 = [q for q in sel_11 if q.section_id <= 12]
        diff_cog11 = Counter(q.difficulty for q in cognitive_q11)
        self.assertGreater(diff_cog11.get('Medium', 0) + diff_cog11.get('Hard', 0), diff_cog11.get('Easy', 0))

    def test_session_question_persistence_on_refresh(self):
        """Verify session.selected_question_ids preserves exact questions across multiple retrievals."""
        user = User(username='sel_test_user', email='sel_test@test.com', role='student')
        user.set_password('Pass1234!')
        db.session.add(user)
        db.session.commit()

        student = Student(user_id=user.id, student_code='STU-SEL-01', first_name='Sel', last_name='Test', class_level=10, stream='General')
        db.session.add(student)
        db.session.commit()

        # Start session
        session = AssessmentService.start_new_session(student.id)
        self.assertIsNotNone(session.selected_question_ids)

        # First retrieval
        q_first = AssessmentService.get_questions_for_session(session)
        q_first_ids = [q.id for q in q_first]

        # Simulate page refresh / subsequent retrieval
        q_second = AssessmentService.get_questions_for_session(session)
        q_second_ids = [q.id for q in q_second]

        self.assertEqual(q_first_ids, q_second_ids, "Questions changed on session re-fetch / refresh!")

    def test_distinct_questions_across_multiple_attempts_for_same_student(self):
        """Verify that when a student takes a 2nd attempt, the selection engine selects fresh, non-overlapping questions."""
        import uuid
        uid = uuid.uuid4().hex[:6]
        user = User(username=f'retake_u_{uid}', email=f'retake_{uid}@test.com', role='student')
        user.set_password('Pass1234!')
        db.session.add(user)
        db.session.commit()

        student = Student(user_id=user.id, student_code=f'STU-RET-{uid}', first_name='Retake', last_name='Student', class_level=8, stream='General')
        db.session.add(student)
        db.session.commit()

        # Attempt 1
        session_1 = AssessmentService.start_new_session(student.id)
        q_ids_1 = set(json.loads(session_1.selected_question_ids))
        self.assertGreaterEqual(len(q_ids_1), 20)

        # Mark Attempt 1 completed
        session_1.status = 'completed'
        db.session.commit()

        # Attempt 2
        session_2 = AssessmentService.start_new_session(student.id)
        q_ids_2 = set(json.loads(session_2.selected_question_ids))
        self.assertGreaterEqual(len(q_ids_2), 20)

        # Verify Attempt 2 has substantial fresh questions (overlap < 20%)
        overlap = q_ids_1.intersection(q_ids_2)
        overlap_pct = len(overlap) / len(q_ids_2)
        self.assertLessEqual(overlap_pct, 0.20, f"Attempt 2 had too much overlap with Attempt 1: {len(overlap)} questions ({overlap_pct*100:.1f}%)")

    def test_different_students_receive_distinct_question_sets(self):
        """Verify that two students in the same grade cohort receive uniquely randomized question sets."""
        import uuid
        uid1 = uuid.uuid4().hex[:6]
        uid2 = uuid.uuid4().hex[:6]

        u1 = User(username=f'rand1_{uid1}', email=f'rand1_{uid1}@test.com', role='student')
        u1.set_password('Pass1234!')
        u2 = User(username=f'rand2_{uid2}', email=f'rand2_{uid2}@test.com', role='student')
        u2.set_password('Pass1234!')
        db.session.add_all([u1, u2])
        db.session.commit()

        s1 = Student(user_id=u1.id, student_code=f'STU-R1-{uid1}', first_name='Student', last_name='One', class_level=10, stream='General')
        s2 = Student(user_id=u2.id, student_code=f'STU-R2-{uid2}', first_name='Student', last_name='Two', class_level=10, stream='General')
        db.session.add_all([s1, s2])
        db.session.commit()

        sess1 = AssessmentService.start_new_session(s1.id)
        sess2 = AssessmentService.start_new_session(s2.id)

        q_ids_1 = json.loads(sess1.selected_question_ids)
        q_ids_2 = json.loads(sess2.selected_question_ids)

        # Verify not identical in composition/order
        self.assertNotEqual(q_ids_1, q_ids_2, "Two different students received identical question sets!")

    def test_class_7_cannot_receive_class_12_advanced_questions(self):
        """Verify strict level-wise eligibility bounds: Class 7 only gets Class 7-8 eligible questions."""
        selected_7 = AssessmentSelectionService.select_balanced_questions(7)
        for q in selected_7:
            self.assertLessEqual(q.class_min, 7, f"Question {q.question_code} has class_min {q.class_min} > 7!")
            self.assertGreaterEqual(q.class_max, 7, f"Question {q.question_code} has class_max {q.class_max} < 7!")


if __name__ == '__main__':
    unittest.main()
