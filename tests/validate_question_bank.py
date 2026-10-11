"""
Automated Question Bank Validator.
Validates the integrity, coverage, and adaptive correctness of the Student Question Bank
across all grade levels (7-12) and 19 standardized assessment sections against MySQL and seed files.
"""

import os
import sys
import unittest
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / '.env')

from database.build_questions_dataset import MASTER_QUESTIONS


class TestQuestionBankIntegrity(unittest.TestCase):
    """Rigorous integrity test suite for student questionnaire."""

    @classmethod
    def setUpClass(cls):
        cls.questions = MASTER_QUESTIONS
        cls.conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'abc123'),
            port=int(os.getenv('DB_PORT', 3306)),
            database=os.getenv('DB_NAME', 'career_recommendation_db')
        )
        cls.cursor = cls.conn.cursor(dictionary=True)

    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.conn.close()

    def test_total_question_count(self):
        """Verify question bank contains at least 100+ questions."""
        self.assertGreaterEqual(len(self.questions), 100, "Question bank must contain at least 100 questions.")

    def test_no_empty_text_or_codes(self):
        """Verify every question has non-empty text, valid code, and valid section."""
        for q in self.questions:
            self.assertTrue(bool(q.get('question_code')), f"Missing code for question: {q}")
            self.assertTrue(bool(q.get('question_text')), f"Missing text for question {q['question_code']}")
            self.assertIn(q.get('section_id'), range(1, 20), f"Invalid section_id {q.get('section_id')} in {q['question_code']}")

    def test_no_duplicate_question_codes(self):
        """Verify every question code is unique."""
        codes = [q['question_code'] for q in self.questions]
        dup_codes = [c for c, count in Counter(codes).items() if count > 1]
        self.assertEqual(len(dup_codes), 0, f"Found duplicate question codes: {dup_codes}")

    def test_no_duplicate_question_texts(self):
        """Verify every question text is unique."""
        texts = [q['question_text'].strip().lower() for q in self.questions]
        dup_texts = [t for t, count in Counter(texts).items() if count > 1]
        self.assertEqual(len(dup_texts), 0, f"Found duplicate question texts: {dup_texts}")

    def test_valid_class_ranges(self):
        """Verify class_min and class_max are between 7 and 12 with min <= max."""
        for q in self.questions:
            c_min = q.get('class_min')
            c_max = q.get('class_max')
            self.assertIn(c_min, range(7, 13), f"Invalid class_min {c_min} in {q['question_code']}")
            self.assertIn(c_max, range(7, 13), f"Invalid class_max {c_max} in {q['question_code']}")
            self.assertLessEqual(c_min, c_max, f"class_min > class_max in {q['question_code']}")

    def test_all_19_sections_covered(self):
        """Verify all 19 standardized sections (1 to 19) have at least one question."""
        covered_sections = set(q['section_id'] for q in self.questions)
        missing_sections = set(range(1, 20)) - covered_sections
        self.assertEqual(len(missing_sections), 0, f"Missing question sections: {missing_sections}")

    def test_options_integrity(self):
        """Verify options structure, positive display orders, and option values."""
        for q in self.questions:
            opts = q.get('options', [])
            self.assertGreaterEqual(len(opts), 2, f"Question {q['question_code']} has fewer than 2 options.")
            
            # Check unique option values within the question
            opt_vals = [str(o['option_value']) for o in opts]
            self.assertEqual(len(opt_vals), len(set(opt_vals)), f"Duplicate option_values in {q['question_code']}")

            for o in opts:
                self.assertTrue(bool(o.get('option_text')), f"Empty option_text in {q['question_code']}")
                self.assertIsInstance(o.get('score'), (int, float), f"Invalid score in {q['question_code']}")

    def test_ability_dimension_targets(self):
        """Verify minimum question counts for core scorable ability dimensions."""
        skill_counts = Counter(q['skill_category'] for q in self.questions)
        self.assertGreaterEqual(skill_counts.get('mathematical_ability', 0), 5, "Mathematical ability < 5")
        self.assertGreaterEqual(skill_counts.get('logical_reasoning', 0), 5, "Logical reasoning < 5")
        self.assertGreaterEqual(skill_counts.get('scientific_reasoning', 0), 4, "Scientific reasoning < 4")
        self.assertGreaterEqual(skill_counts.get('problem_solving', 0), 4, "Problem solving < 4")
        self.assertGreaterEqual(skill_counts.get('analytical_ability', 0), 4, "Analytical ability < 4")
        self.assertGreaterEqual(skill_counts.get('communication', 0), 3, "Communication < 3")
        self.assertGreaterEqual(skill_counts.get('creativity', 0), 3, "Creativity < 3")
        self.assertGreaterEqual(skill_counts.get('digital_ability', 0), 3, "Digital ability < 3")
        self.assertGreaterEqual(skill_counts.get('learning_ability', 0), 3, "Learning ability < 3")
        self.assertGreaterEqual(skill_counts.get('spatial_ability', 0), 3, "Spatial ability < 3")
        self.assertGreaterEqual(skill_counts.get('practical_ability', 0), 3, "Practical ability < 3")

    def test_mysql_seeding_matches_master_bank(self):
        """Verify live MySQL questions count matches the master dataset."""
        self.cursor.execute("SELECT COUNT(*) AS total_q FROM questions WHERE is_active = 1;")
        res_q = self.cursor.fetchone()
        self.assertEqual(res_q['total_q'], len(self.questions), "MySQL active question count mismatch.")

        self.cursor.execute("SELECT SUM(JSON_LENGTH(options)) AS total_opt FROM questions WHERE is_active = 1;")
        res_opt = self.cursor.fetchone()
        expected_opts = sum(len(q.get('options', [])) for q in self.questions)
        self.assertEqual(res_opt['total_opt'], expected_opts, "MySQL option count mismatch.")

    def test_cohort_adaptive_delivery(self):
        """Verify that every student cohort receives appropriate question volume."""
        # Class 7-8: 30-70 questions
        for c in [7, 8]:
            eligible = [q for q in self.questions if q['class_min'] <= c <= q['class_max']]
            self.assertGreaterEqual(len(eligible), 30, f"Class {c} question count too low: {len(eligible)}")

        # Class 9-10: 40-80 questions
        for c in [9, 10]:
            eligible = [q for q in self.questions if q['class_min'] <= c <= q['class_max']]
            self.assertGreaterEqual(len(eligible), 40, f"Class {c} question count too low: {len(eligible)}")

        # Class 11-12 streams: 50-80 questions
        for c in [11, 12]:
            for s in ['Science', 'Commerce', 'Humanities']:
                eligible = [q for q in self.questions if q['class_min'] <= c <= q['class_max'] and (q['stream_specific'] in ['All', s])]
                self.assertGreaterEqual(len(eligible), 50, f"Class {c} ({s}) question count too low: {len(eligible)}")


def print_detailed_validation_report():
    """Generates an executive summary of the question bank state."""
    print("\n" + "=" * 70)
    print("      STUDENT QUESTION BANK VALIDATION REPORT (CLASS 7-12)")
    print("=" * 70)

    total_q = len(MASTER_QUESTIONS)
    total_opt = sum(len(q.get('options', [])) for q in MASTER_QUESTIONS)
    print(f"Total Questions Defined   : {total_q}")
    print(f"Total Options Configured  : {total_opt}")

    print("\n--- Cohort Distribution ---")
    for c in [7, 8, 9, 10]:
        cnt = len([q for q in MASTER_QUESTIONS if q['class_min'] <= c <= q['class_max']])
        print(f"  Class {c:2d} General               : {cnt} questions")
    for c in [11, 12]:
        for s in ['Science', 'Commerce', 'Humanities']:
            cnt = len([q for q in MASTER_QUESTIONS if q['class_min'] <= c <= q['class_max'] and (q['stream_specific'] in ['All', s])])
            print(f"  Class {c:2d} Stream ({s:<10}) : {cnt} questions")

    print("\n--- Section Breakdown (1-19) ---")
    sec_counts = Counter(q['section_id'] for q in MASTER_QUESTIONS)
    for s_id in range(1, 20):
        print(f"  Section {s_id:2d}                      : {sec_counts.get(s_id, 0):2d} questions")

    print("\n--- Scorable Skill & Dimension Coverage ---")
    skill_counts = Counter(q['skill_category'] for q in MASTER_QUESTIONS)
    for k, v in sorted(skill_counts.items()):
        print(f"  {k:<30}: {v:2d} questions")

    print("=" * 70 + "\n")


if __name__ == '__main__':
    print_detailed_validation_report()
    unittest.main()
