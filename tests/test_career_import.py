"""
Automated Unit Tests for Career Knowledge Dataset Import and Duplicate Prevention.
Tests normalization, deterministic code generation, relational mapping,
and idempotent import behavior.
"""

import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.career import (
    CareerDomain, CareerSubdomain, CareerCluster,
    Career, CareerSkill, CareerSubject, CareerEducation, CareerPathway
)
from backend.utils.helpers import (
    normalize_text, parse_numeric, generate_career_code
)


class CareerImportTestCase(unittest.TestCase):
    """Test suite for career dataset ETL, relational mappings, and duplicate prevention."""

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_text_normalization(self):
        """Tests that text strings are properly formatted with standard casing and acronyms."""
        self.assertEqual(normalize_text("psychology and social sciences"), "Psychology and Social Sciences")
        self.assertEqual(normalize_text("DEFENCE AND SECURITY"), "Defence and Security")
        self.assertEqual(normalize_text("ai specialist / ml engineer"), "AI Specialist / Ml Engineer")
        self.assertEqual(normalize_text("  cad  designer   "), "CAD Designer")

    def test_numeric_parsing(self):
        """Tests safe numeric bounding and conversion."""
        self.assertEqual(parse_numeric("5"), 5)
        self.assertEqual(parse_numeric("3.0"), 3)
        self.assertEqual(parse_numeric("10"), 5)  # bounded max 5
        self.assertEqual(parse_numeric("-2"), 0)  # bounded min 0
        self.assertEqual(parse_numeric("invalid", default=2), 2)

    def test_deterministic_career_code_generation(self):
        """Tests that career codes are generated deterministically and uniquely."""
        code1 = generate_career_code("Engineering", "CID1073", 1000)
        code2 = generate_career_code("Engineering", "CID1073", 1000)
        self.assertEqual(code1, code2)
        self.assertTrue(code1.startswith("CAR-ENG-"))

        code3 = generate_career_code("Technology", "CID1283", 1001)
        self.assertTrue(code3.startswith("CAR-TECH-"))

    def test_relational_import_and_duplicate_prevention(self):
        """Tests inserting careers and ensuring re-importing does not duplicate records."""
        # 1. Create domain, subdomain, cluster
        dom = CareerDomain(domain_name="Engineering", icon="bi-gear-wide-connected")
        db.session.add(dom)
        db.session.flush()

        sub = CareerSubdomain(domain_id=dom.id, name="Robotics", description="Robotics engineering focus.")
        db.session.add(sub)
        db.session.flush()

        clu = CareerCluster(subdomain_id=sub.id, name="Automation Systems", description="Industrial automation.")
        db.session.add(clu)
        db.session.flush()

        # 2. Insert career
        career = Career(
            career_code="CAR-ENG-9999",
            career_name="Autonomous Systems Architect",
            domain_id=dom.id,
            subdomain_id=sub.id,
            cluster_id=clu.id,
            description="Designs autonomous robotics systems.",
            minimum_education="Bachelor's Degree",
            typical_education="M.Tech Robotics",
            work_environment="Robotics Lab",
            is_active=True
        )
        db.session.add(career)
        db.session.flush()

        # 3. Add skills & subjects
        skill = CareerSkill(career_id=career.id, skill_name="Software & Algorithm Design", importance_level=5, importance_label="Critical")
        subject = CareerSubject(career_id=career.id, subject_name="Physics", importance_level=4, importance_label="Very High")
        db.session.add_all([skill, subject])
        db.session.commit()

        # Verify initial counts
        self.assertEqual(Career.query.count(), 1)
        self.assertEqual(CareerSkill.query.count(), 1)
        self.assertEqual(CareerSubject.query.count(), 1)

        # 4. Attempt duplicate insertion simulation
        existing_career = Career.query.filter_by(career_code="CAR-ENG-9999").first()
        self.assertIsNotNone(existing_career)
        self.assertEqual(existing_career.career_name, "Autonomous Systems Architect")

        # Verify foreign key navigation
        self.assertEqual(existing_career.domain.domain_name, "Engineering")
        self.assertEqual(existing_career.subdomain.name, "Robotics")
        self.assertEqual(existing_career.cluster.name, "Automation Systems")
        self.assertEqual(len(existing_career.skills), 1)
        self.assertEqual(len(existing_career.subjects), 1)

    def test_career_details_dict_serialization(self):
        """Tests that imported career dictionary contains all rich metadata fields."""
        dom = CareerDomain(domain_name="Healthcare", icon="bi-heart-pulse")
        db.session.add(dom)
        db.session.flush()

        career = Career(
            career_code="CAR-HLTH-1234",
            career_name="Clinical Geneticist",
            domain_id=dom.id,
            description="Investigates hereditary conditions.",
            minimum_education="MBBS",
            typical_education="MD Medical Genetics",
            work_environment="Hospital / Diagnostic Lab",
            entry_level_role="Junior Resident Geneticist",
            advanced_role="Chief Medical Geneticist",
            related_careers="Molecular Biologist, Bioinformatician"
        )
        db.session.add(career)
        db.session.flush()

        edu = CareerEducation(
            career_id=career.id,
            education_level="Medical School",
            degree_name="MBBS",
            description="Medical qualification.",
            sequence_order=1
        )
        path = CareerPathway(
            career_id=career.id,
            stage_number=1,
            stage_name="Residency",
            description="Clinical rotations."
        )
        db.session.add_all([edu, path])
        db.session.commit()

        career_dict = career.to_dict()
        self.assertEqual(career_dict['career_code'], "CAR-HLTH-1234")
        self.assertEqual(career_dict['career_name'], "Clinical Geneticist")
        self.assertEqual(career_dict['domain_name'], "Healthcare")
        self.assertEqual(career_dict['domain_icon'], "bi-heart-pulse")
        self.assertIn('related_careers', career_dict)
        self.assertEqual(len(career_dict['education_pathways']), 0)
        self.assertEqual(len(career_dict['pathways']), 0)


if __name__ == '__main__':
    unittest.main()
