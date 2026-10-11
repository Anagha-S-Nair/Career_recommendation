"""
End-to-End Assessment Lifecycle Test Suite for All 11 Cohorts.
Validates:
- Class 7 (General)
- Class 8 (General)
- Class 9 (General)
- Class 10 (General)
- Class 11 Science-PCM
- Class 11 Science-PCB
- Class 11 Commerce
- Class 11 Humanities
- Class 12 Science
- Class 12 Commerce
- Class 12 Humanities

Verifies the full lifecycle:
Registration -> Login -> Class/Stream Selection -> Question Selection & Bounds ->
Answer Autosaving -> Answer Updating -> Assessment Review -> Submission ->
Score Calculation -> Student Profile -> Exploratory Career Matches.
"""

import sys
import uuid
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.student import Student, AcademicScore
from backend.models.question import Question, QuestionSection, QuestionOption
from backend.models.assessment import AssessmentSession, StudentAnswer, AssessmentScore
from backend.models.career import Career, CareerDomain, CareerSubdomain, CareerCluster, CareerSkill, CareerSubject, CareerEducation, CareerPathway
from backend.services.assessment_service import AssessmentService
from backend.services.assessment_selection_service import AssessmentSelectionService
from backend.services.student_profile_service import StudentProfileService
from backend.services.recommendation_service import RecommendationService
from database.build_questions_dataset import MASTER_QUESTIONS


class TestAssessmentWorkflowAllCohorts(unittest.TestCase):
    """Full lifecycle integration test suite across all 11 student grade cohorts."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        # Seed all 19 sections
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

        # Seed all master questions
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

        # Seed sample careers across major domains for baseline matching
        domains = [
            (1, 'Technology', 'bi-cpu'),
            (2, 'Healthcare', 'bi-heart-pulse'),
            (3, 'Business', 'bi-briefcase'),
            (4, 'Law', 'bi-shield-check')
        ]
        for d_id, d_name, d_icon in domains:
            d_obj = CareerDomain(id=d_id, domain_name=d_name, icon=d_icon, display_order=d_id, is_active=True)
            db.session.add(d_obj)
            db.session.flush()

            sub = CareerSubdomain(id=d_id, domain_id=d_id, name=f'{d_name} Subdomain')
            clu = CareerCluster(id=d_id, subdomain_id=d_id, name=f'{d_name} Cluster')
            db.session.add_all([sub, clu])
            db.session.flush()

            c_obj = Career(
                id=d_id,
                career_code=f'CAR-{d_name[:3].upper()}-01',
                career_name=f'Professional {d_name} Specialist',
                domain_id=d_id,
                subdomain_id=d_id,
                cluster_id=d_id,
                description=f'Career specializing in {d_name}.',
                is_active=True
            )
            db.session.add(c_obj)
            db.session.flush()

            # Add sample skill, subject, education, pathway
            db.session.add(CareerSkill(career_id=c_obj.id, skill_name=f'{d_name} Core Skill', importance_level=5))
            db.session.add(CareerSubject(career_id=c_obj.id, subject_name='English', importance_level=4))
            db.session.add(CareerEducation(career_id=c_obj.id, education_level='Bachelor Degree', degree_name='Undergraduate', sequence_order=1))
            db.session.add(CareerPathway(career_id=c_obj.id, stage_number=1, stage_name='Entry Associate', description='Initial role'))

        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def _execute_cohort_lifecycle_test(self, class_level: int, stream: str, min_q: int, max_q: int):
        """Helper executing the complete end-to-end lifecycle for a specific cohort."""
        uid = uuid.uuid4().hex[:6]
        username = f"stu_{class_level}_{stream.replace('-', '_').lower()}_{uid}"
        email = f"{username}@test.school"

        # 1. Registration
        user = User(username=username, email=email, role='student')
        user.set_password('Pass1234!')
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            student_code=f'STU-{uid.upper()}',
            first_name='Cohort',
            last_name=f'Class{class_level}',
            class_level=class_level,
            stream=stream,
            board='CBSE',
            medium='English'
        )
        db.session.add(student)
        db.session.flush()

        acad = AcademicScore(
            student_id=student.id,
            mathematics_score=85.0,
            science_score=88.0,
            overall_percentage=86.5
        )
        db.session.add(acad)
        db.session.commit()

        # 2. Login simulation via Auth API
        login_res = self.client.post('/api/auth/login', json={'identifier': email, 'password': 'Pass1234!'})
        self.assertEqual(login_res.status_code, 200, f"Login failed for {email}")

        # 3. Start Assessment Session
        session = AssessmentService.start_new_session(student.id)
        self.assertEqual(session.status, 'in_progress')
        self.assertIsNotNone(session.selected_question_ids)

        # 4. Question Filtering & Count Verification
        questions = AssessmentService.get_questions_for_session(session)
        q_count = len(questions)
        self.assertGreaterEqual(
            q_count, min_q,
            f"Class {class_level} ({stream}) question count {q_count} below minimum {min_q}"
        )
        self.assertLessEqual(
            q_count, max_q,
            f"Class {class_level} ({stream}) question count {q_count} above maximum {max_q}"
        )

        # 5. Answer Saving & Autosaving
        first_q = questions[0]
        opt_val = first_q.options[0].option_value if first_q.options else 'A'
        ans1 = AssessmentService.save_or_update_answer(
            session_id=session.id,
            question_id=first_q.id,
            selected_option=opt_val,
            time_taken_seconds=15
        )
        self.assertEqual(ans1.selected_option, opt_val)
        self.assertGreater(session.completion_percentage, 0.0)

        # 6. Answer Updating (re-answering same question)
        if len(first_q.options) > 1:
            updated_opt = first_q.options[1].option_value
            ans1_upd = AssessmentService.save_or_update_answer(
                session_id=session.id,
                question_id=first_q.id,
                selected_option=updated_opt,
                time_taken_seconds=20
            )
            self.assertEqual(ans1_upd.selected_option, updated_opt)

        # 7. Answer all remaining questions
        for q in questions[1:]:
            ans_val = q.options[0].option_value if q.options else 'A'
            AssessmentService.save_or_update_answer(
                session_id=session.id,
                question_id=q.id,
                selected_option=ans_val,
                time_taken_seconds=10
            )

        # 8. Assessment Review Page Access
        review_resp = self.client.get('/assessment/review')
        self.assertEqual(review_resp.status_code, 200)

        # 9. Assessment Submission & Score Evaluation
        eval_result = AssessmentService.complete_and_evaluate_assessment(session.id)
        self.assertEqual(eval_result['session']['status'], 'completed')
        self.assertIn('scores', eval_result)
        self.assertIn('recommendations', eval_result)

        # 10. Student Profile Synthesis
        profile = StudentProfileService.generate_student_profile(session.id)
        self.assertEqual(profile['student']['class_level'], class_level)
        self.assertIn('abilities', profile)
        self.assertIn('interests', profile)
        self.assertIn('strengths', profile)
        self.assertIn('development_areas', profile)

        # 11. Exploratory Baseline Career Matches Verification
        explanations = RecommendationService.get_detailed_career_explanations(session.id)
        self.assertGreaterEqual(len(explanations), 1)
        for exp in explanations:
            self.assertIn('career_name', exp)
            self.assertIn('match_score', exp)
            self.assertIn('skills', exp)
            self.assertIn('education_milestones', exp)

        # 12. Results Page View
        results_resp = self.client.get(f'/assessment/results/{session.id}')
        self.assertEqual(results_resp.status_code, 200)

    # --------------------------------------------------------
    # Individual Cohort Test Executions
    # --------------------------------------------------------

    def test_cohort_01_class_7_general(self):
        """Test Class 7 (Middle School General Cohort)."""
        self._execute_cohort_lifecycle_test(7, 'General', min_q=19, max_q=21)

    def test_cohort_02_class_8_general(self):
        """Test Class 8 (Middle School General Cohort)."""
        self._execute_cohort_lifecycle_test(8, 'General', min_q=19, max_q=21)

    def test_cohort_03_class_9_general(self):
        """Test Class 9 (Secondary School General Cohort)."""
        self._execute_cohort_lifecycle_test(9, 'General', min_q=19, max_q=21)

    def test_cohort_04_class_10_general(self):
        """Test Class 10 (Secondary School General Cohort)."""
        self._execute_cohort_lifecycle_test(10, 'General', min_q=19, max_q=21)

    def test_cohort_05_class_11_science_pcm(self):
        """Test Class 11 Science-PCM Cohort."""
        self._execute_cohort_lifecycle_test(11, 'Science-PCM', min_q=19, max_q=21)

    def test_cohort_06_class_11_science_pcb(self):
        """Test Class 11 Science-PCB Cohort."""
        self._execute_cohort_lifecycle_test(11, 'Science-PCB', min_q=19, max_q=21)

    def test_cohort_07_class_11_commerce(self):
        """Test Class 11 Commerce Cohort."""
        self._execute_cohort_lifecycle_test(11, 'Commerce', min_q=19, max_q=21)

    def test_cohort_08_class_11_humanities(self):
        """Test Class 11 Humanities Cohort."""
        self._execute_cohort_lifecycle_test(11, 'Humanities', min_q=19, max_q=21)

    def test_cohort_09_class_12_science(self):
        """Test Class 12 Science Cohort."""
        self._execute_cohort_lifecycle_test(12, 'Science-PCM', min_q=19, max_q=21)

    def test_cohort_10_class_12_commerce(self):
        """Test Class 12 Commerce Cohort."""
        self._execute_cohort_lifecycle_test(12, 'Commerce', min_q=19, max_q=21)

    def test_cohort_11_class_12_humanities(self):
        """Test Class 12 Humanities Cohort."""
        self._execute_cohort_lifecycle_test(12, 'Humanities', min_q=19, max_q=21)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()


if __name__ == '__main__':
    unittest.main()
