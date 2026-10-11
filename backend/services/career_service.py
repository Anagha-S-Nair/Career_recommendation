"""
Career Knowledge Base & Exploration Service.
Provides domain hierarchies, searchable career profiles, skill importance mapping,
and step-by-step education roadmap pathways.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.models.career import (
    CareerDomain, CareerSubdomain, CareerCluster, Career
)


class CareerService:
    """Service handling career exploration, search, filters, and roadmaps."""

    @classmethod
    def get_all_domains(cls) -> List[Dict[str, Any]]:
        """Returns all career domains and their nested subdomains."""
        domains = CareerDomain.query.filter_by(is_active=True).order_by(CareerDomain.display_order.asc(), CareerDomain.domain_name.asc()).all()
        return [d.to_dict() for d in domains]

    @classmethod
    def get_subdomains_by_domain(cls, domain_id: int) -> List[Dict[str, Any]]:
        """Returns all subdomains under a domain."""
        subdomains = CareerSubdomain.query.filter_by(domain_id=domain_id).order_by(CareerSubdomain.name.asc()).all()
        return [s.to_dict() for s in subdomains]

    @classmethod
    def get_clusters_by_subdomain(cls, subdomain_id: int) -> List[Dict[str, Any]]:
        """Returns all clusters under a subdomain."""
        clusters = CareerCluster.query.filter_by(subdomain_id=subdomain_id).order_by(CareerCluster.name.asc()).all()
        return [c.to_dict() for c in clusters]

    @classmethod
    def search_careers(
        cls,
        search_query: Optional[str] = None,
        domain_id: Optional[int] = None,
        subdomain_id: Optional[int] = None,
        cluster_id: Optional[int] = None,
        education_level: Optional[str] = None,
        work_environment: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> Any:
        """
        Searches and filters active careers across domain, subdomain, cluster, and keywords.
        Supports optional pagination.
        """
        query = Career.query.filter(Career.is_active == True)

        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query = query.filter(
                (Career.career_name.ilike(sq)) |
                (Career.description.ilike(sq)) |
                (Career.domain_name.ilike(sq)) |
                (Career.subdomain_val.ilike(sq)) |
                (Career.cluster_val.ilike(sq))
            )

        if domain_id:
            try:
                all_doms = CareerDomain.query.all()
                target_dom = next((d for d in all_doms if d.id == int(domain_id)), None)
                if target_dom:
                    query = query.filter(Career.domain_name == target_dom.domain_name)
            except (ValueError, TypeError):
                pass

        if education_level and education_level != 'all':
            query = query.filter(Career.minimum_education.ilike(f"%{education_level}%"))

        query = query.order_by(Career.domain_name.asc(), Career.career_name.asc())

        if page and per_page:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                'items': [c.to_dict() for c in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            }

        careers = query.all()
        return [c.to_dict() for c in careers]

    @classmethod
    def get_career_by_id(cls, career_id: int) -> Optional[Dict[str, Any]]:
        """Fetches complete career profile with skills, subjects, and education pathways."""
        from backend.extensions import db
        career = db.session.get(Career, career_id)
        return career.to_dict() if career else None

    @classmethod
    def get_career_by_code(cls, career_code: str) -> Optional[Dict[str, Any]]:
        """Fetches complete career profile by unique career code."""
        career = Career.query.filter_by(career_code=career_code).first()
        return career.to_dict() if career else None
