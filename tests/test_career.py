import unittest
from backend.app import create_app
from backend.extensions import db
from backend.models.career import CareerDomain, Career, CareerSkill, CareerEducation
from backend.services.career_service import CareerService


class CareerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Seed test domain & career
        dom = CareerDomain(domain_name="Technology", description="Tech", icon="bi-cpu", display_order=1)
        db.session.add(dom)
        db.session.flush()

        career = Career(
            career_code="CAR-TEST-01",
            career_name="Software Engineer",
            domain_id=dom.id,
            description="Builds software applications.",
            minimum_education="Bachelor's Degree",
            typical_education="B.Tech Computer Science",
            is_active=True
        )
        db.session.add(career)
        db.session.flush()

        skill = CareerSkill(career_id=career.id, skill_name="Python", importance_level=5, importance_label="Critical")
        edu = CareerEducation(career_id=career.id, education_level="Undergraduate", degree_name="B.Tech CSE", sequence_order=1)
        db.session.add_all([skill, edu])
        db.session.commit()
        self.career_id = career.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_career_search_and_filter(self):
        # Search by keyword
        res = CareerService.search_careers(search_query="Software")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['career_name'], "Software Engineer")

        # Search by non-matching query
        res_empty = CareerService.search_careers(search_query="Doctor")
        self.assertEqual(len(res_empty), 0)

    def test_career_detail_payload(self):
        detail = CareerService.get_career_by_id(self.career_id)
        self.assertIsNotNone(detail)
        self.assertEqual(detail['career_code'], "CAR-TEST-01")
        self.assertEqual(len(detail['skills']), 1)
        self.assertEqual(detail['skills'][0]['skill_name'], "Python")
        self.assertEqual(len(detail['education_pathways']), 0)


if __name__ == '__main__':
    unittest.main()
