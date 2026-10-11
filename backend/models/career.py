"""
Career Model for MySQL Database.
Stores comprehensive career knowledge profiles in the 'careers' table.
"""

from backend.extensions import db

# Domain icon mapping for UI presentation
DOMAIN_ICONS = {
    'Technology': 'bi-cpu',
    'Information Technology': 'bi-cpu',
    'Healthcare': 'bi-heart-pulse',
    'Medicine': 'bi-heart-pulse',
    'Engineering': 'bi-gear-wide-connected',
    'Pure Science': 'bi-radioactive',
    'Life Sciences': 'bi-virus',
    'Research': 'bi-search',
    'Business': 'bi-briefcase',
    'Finance': 'bi-graph-up-arrow',
    'Law': 'bi-shield-check',
    'Arts': 'bi-palette',
    'Design': 'bi-brush',
    'Media': 'bi-camera-reels',
    'Government': 'bi-building',
    'Agriculture': 'bi-tree',
    'Environment': 'bi-globe',
    'Sports': 'bi-trophy',
    'Hospitality': 'bi-cup-hot',
    'Aviation': 'bi-airplane',
    'Manufacturing': 'bi-tools',
    'Construction': 'bi-cone-striped',
    'Skilled Trades': 'bi-hammer',
    'Transportation': 'bi-truck',
    'Psychology and Social Sciences': 'bi-people',
    'Education': 'bi-mortarboard',
    'Biotechnology': 'bi-virus',
    'Pharmaceuticals': 'bi-capsule',
    'Defence and Security': 'bi-shield',
    'Fashion': 'bi-handbag',
    'Food': 'bi-egg-fried',
    'Real Estate': 'bi-house',
    'Emerging Careers': 'bi-stars',
    'Interdisciplinary': 'bi-diagram-3'
}


class DomainProxy:
    """Proxy representing a career domain."""

    def __init__(self, name="General", icon=None, domain_id=1):
        self.id = domain_id
        if hasattr(name, '__getitem__') and not isinstance(name, str):
            name = name[0]
        self.domain_name = str(name) if name else "General"
        self.description = f"{self.domain_name} Industry Sector"
        self.icon = icon or DOMAIN_ICONS.get(self.domain_name, 'bi-briefcase')
        self.display_order = 1
        self.is_active = True

    def __str__(self):
        return self.domain_name

    def __eq__(self, other):
        if isinstance(other, DomainProxy):
            return self.domain_name == other.domain_name
        return self.domain_name == str(other)

    def to_dict(self):
        return {
            'id': self.id,
            'domain_name': self.domain_name,
            'description': self.description,
            'icon': self.icon,
            'display_order': self.display_order,
            'subdomains': [],
            'career_count': Career.query.filter_by(domain_name=self.domain_name, is_active=True).count() if db.session else 0
        }

    def __repr__(self):
        return f"<CareerDomain {self.domain_name}>"


class SubdomainProxy:
    def __init__(self, name="General", domain_id=1):
        self.id = 1
        self.domain_id = domain_id
        self.name = name or "General"
        self.description = f"{self.name} Subdomain"

    def __str__(self):
        return self.name

    def to_dict(self):
        return {'id': self.id, 'domain_id': self.domain_id, 'name': self.name, 'description': self.description, 'clusters': []}


class ClusterProxy:
    def __init__(self, name="General Practice", subdomain_id=1):
        self.id = 1
        self.subdomain_id = subdomain_id
        self.name = name or "General Practice"
        self.description = f"{self.name} Cluster"

    def __str__(self):
        return self.name

    def to_dict(self):
        return {'id': self.id, 'subdomain_id': self.subdomain_id, 'name': self.name, 'description': self.description}


class CareerSkillProxy:
    def __init__(self, data, career_id=None):
        if isinstance(data, dict):
            self.id = data.get('id', 1)
            self.career_id = career_id or data.get('career_id', 1)
            self.skill_name = data.get('skill_name', '')
            self.importance_level = data.get('importance_level', 'High')
            self.importance_label = data.get('importance_label', self.importance_level)
        else:
            self.id = 1
            self.career_id = career_id or 1
            self.skill_name = str(data)
            self.importance_level = 'High'
            self.importance_label = 'High'

    def to_dict(self):
        return {'id': self.id, 'skill_name': self.skill_name, 'importance_level': self.importance_label or 'High'}


class CareerSubjectProxy:
    def __init__(self, data, career_id=None):
        if isinstance(data, dict):
            self.id = data.get('id', 1)
            self.career_id = career_id or data.get('career_id', 1)
            self.subject_name = data.get('subject_name', '')
            self.importance_level = data.get('importance_level', 'High')
            self.importance_label = data.get('importance_label', self.importance_level)
        else:
            self.id = 1
            self.career_id = career_id or 1
            self.subject_name = str(data)
            self.importance_level = 'High'
            self.importance_label = 'High'

    def to_dict(self):
        return {'id': self.id, 'subject_name': self.subject_name, 'importance_level': self.importance_label or 'High'}


class Career(db.Model):
    """Career Knowledge model in MySQL ('careers' table)."""
    __tablename__ = 'careers'

    id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), primary_key=True, autoincrement=True)
    career_code = db.Column(db.String(50), unique=True, nullable=True, index=True)
    career_name = db.Column(db.String(200), nullable=False, index=True)
    domain_name = db.Column('domain', db.String(150), nullable=False, default='General', index=True)
    subdomain_val = db.Column('subdomain', db.String(150), nullable=True)
    cluster_val = db.Column('cluster', db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    minimum_education = db.Column(db.String(150), nullable=True)
    typical_education = db.Column(db.String(150), nullable=True)
    required_skills = db.Column(db.JSON, default=list)
    recommended_subjects = db.Column(db.JSON, default=list)
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __init__(self, **kwargs):
        # Discard dropped schema columns
        kwargs.pop('market_demand', None)
        kwargs.pop('growth_rate', None)
        kwargs.pop('avg_starting_salary', None)
        kwargs.pop('salary_mid_career', None)
        kwargs.pop('created_at', None)
        domain_id = kwargs.pop('domain_id', None)
        subdomain_id = kwargs.pop('subdomain_id', None)
        cluster_id = kwargs.pop('cluster_id', None)

        title = kwargs.pop('title', None)
        if title and 'career_name' not in kwargs:
            kwargs['career_name'] = title

        LEGACY_DOMAIN_MAP = {
            1: 'Technology', 2: 'Healthcare', 3: 'Engineering', 4: 'Business',
            5: 'Finance', 6: 'Arts', 7: 'Media', 8: 'Government', 9: 'Education', 10: 'Pure Science'
        }
        dom = kwargs.pop('domain', None) or kwargs.pop('domain_name', None)
        if dom:
            kwargs['domain_name'] = getattr(dom, 'domain_name', str(dom))
        elif domain_id:
            if domain_id in _DOMAIN_REGISTRY:
                kwargs['domain_name'] = _DOMAIN_REGISTRY[domain_id].domain_name
            else:
                kwargs['domain_name'] = LEGACY_DOMAIN_MAP.get(domain_id, 'General')

        sub = kwargs.pop('subdomain', None)
        if sub:
            kwargs['subdomain_val'] = getattr(sub, 'name', str(sub))
        elif subdomain_id and subdomain_id in _SUBDOMAIN_REGISTRY:
            kwargs['subdomain_val'] = _SUBDOMAIN_REGISTRY[subdomain_id].name

        clu = kwargs.pop('cluster', None)
        if clu:
            kwargs['cluster_val'] = getattr(clu, 'name', str(clu))
        elif cluster_id and cluster_id in _CLUSTER_REGISTRY:
            kwargs['cluster_val'] = _CLUSTER_REGISTRY[cluster_id].name

        if 'required_skills' not in kwargs:
            kwargs['required_skills'] = []
        if 'recommended_subjects' not in kwargs:
            kwargs['recommended_subjects'] = []

        valid_cols = {'id', 'career_code', 'career_name', 'domain_name', 'subdomain_val', 'cluster_val',
                      'description', 'minimum_education', 'typical_education', 'required_skills',
                      'recommended_subjects', 'is_active'}
        extra_kwargs = {k: v for k, v in kwargs.items() if k not in valid_cols}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_cols}

        super().__init__(**filtered_kwargs)
        for k, v in extra_kwargs.items():
            setattr(self, k, v)

    @property
    def domain(self):
        return DomainProxy(self.domain_name, DOMAIN_ICONS.get(self.domain_name, 'bi-briefcase'), self.id)

    @domain.setter
    def domain(self, val):
        self.domain_name = getattr(val, 'domain_name', str(val)) if val else 'General'

    @property
    def subdomain(self):
        return SubdomainProxy(self.subdomain_val or 'General')

    @property
    def cluster(self):
        return ClusterProxy(self.cluster_val or 'General Practice')

    @property
    def domain_id(self):
        return self.id

    @property
    def subdomain_id(self):
        return 1

    @property
    def cluster_id(self):
        return 1

    @property
    def subdomain_name(self):
        return self.subdomain_val or 'General'

    @property
    def cluster_name(self):
        return self.cluster_val or 'General Practice'

    @property
    def skills(self):
        skills_data = self.required_skills if isinstance(self.required_skills, list) else []
        return [CareerSkillProxy(s, self.id) for s in skills_data]

    @property
    def subjects(self):
        subjects_data = self.recommended_subjects if isinstance(self.recommended_subjects, list) else []
        return [CareerSubjectProxy(s, self.id) for s in subjects_data]

    def to_dict(self):
        return {
            'id': self.id,
            'career_code': self.career_code,
            'career_name': self.career_name,
            'domain_id': self.id,
            'domain_name': self.domain_name,
            'domain_icon': DOMAIN_ICONS.get(self.domain_name, 'bi-briefcase'),
            'subdomain_name': self.subdomain_name,
            'cluster_name': self.cluster_name,
            'description': self.description,
            'minimum_education': self.minimum_education,
            'typical_education': self.typical_education,
            'skills': [s.to_dict() for s in self.skills],
            'subjects': [sub.to_dict() for sub in self.subjects],
            'education_pathways': [],
            'pathways': [],
            'related_careers': []
        }

    def __repr__(self):
        return f"<Career {self.career_code}: {self.career_name}>"


class _AttrProxy:
    def asc(self): return self
    def desc(self): return self


_DOMAIN_REGISTRY = {}
_SUBDOMAIN_REGISTRY = {}
_CLUSTER_REGISTRY = {}
_SKILL_INSTANCES = []
_SUBJECT_INSTANCES = []

class CareerDomain:
    """Query interface for career domains generated dynamically from careers table."""
    display_order = _AttrProxy()
    domain_name = _AttrProxy()
    id = _AttrProxy()

    def __init__(self, domain_name="General", icon=None, description=None, display_order=1, is_active=True, **kwargs):
        self.id = kwargs.get('id', id(self) % 100000)
        self.domain_name = str(domain_name)
        self.description = description or f"{self.domain_name} Domain"
        self.icon = icon or DOMAIN_ICONS.get(self.domain_name, 'bi-briefcase')
        self.display_order = display_order
        _DOMAIN_REGISTRY[self.id] = self

    def to_dict(self):
        return {
            'id': self.id,
            'domain_name': self.domain_name,
            'description': self.description,
            'icon': self.icon,
            'display_order': self.display_order,
            'subdomains': [],
            'career_count': Career.query.filter_by(domain_name=self.domain_name, is_active=True).count() if db.session else 0
        }

    class _Query:
        @staticmethod
        def filter_by(is_active=True, **kwargs):
            return CareerDomain._Query

        @staticmethod
        def order_by(*args):
            return CareerDomain._Query

        @staticmethod
        def all():
            try:
                rows = db.session.query(Career.domain_name).filter(Career.is_active == True).distinct().order_by(Career.domain_name.asc()).all()
                res = []
                for idx, r in enumerate(rows, 1):
                    d_name = str(r[0] if hasattr(r, '__getitem__') else getattr(r, 'domain_name', str(r)))
                    res.append(CareerDomain(id=idx, domain_name=d_name, icon=DOMAIN_ICONS.get(d_name, 'bi-briefcase'), display_order=idx))
                return res
            except Exception:
                return []

        @staticmethod
        def count():
            return len(CareerDomain._Query.all())

        @staticmethod
        def first():
            doms = CareerDomain._Query.all()
            return doms[0] if doms else None

    query = _Query()

    def __repr__(self):
        return f"<CareerDomain {self.domain_name}>"


# Lightweight compatibility aliases
class CareerSubdomain:
    query = type('_Q', (), {'filter_by': staticmethod(lambda **k: type('_Q', (), {'order_by': staticmethod(lambda *a: type('_Q', (), {'all': staticmethod(lambda: [])}))})), 'all': staticmethod(lambda: [])})()
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', id(self) % 100000)
        self.name = kwargs.get('name', 'General')
        self.__dict__.update(kwargs)
        _SUBDOMAIN_REGISTRY[self.id] = self

class CareerCluster:
    query = type('_Q', (), {'filter_by': staticmethod(lambda **k: type('_Q', (), {'order_by': staticmethod(lambda *a: type('_Q', (), {'all': staticmethod(lambda: [])}))})), 'all': staticmethod(lambda: [])})()
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', id(self) % 100000)
        self.name = kwargs.get('name', 'General Practice')
        self.__dict__.update(kwargs)
        _CLUSTER_REGISTRY[self.id] = self

class CareerSkill:
    importance_level = _AttrProxy()
    query = type('_Q', (), {
        'filter_by': staticmethod(lambda **k: type('_Q', (), {'order_by': staticmethod(lambda *a: type('_Q', (), {'all': staticmethod(lambda: list(_SKILL_INSTANCES)), 'count': staticmethod(lambda: len(_SKILL_INSTANCES))}))})),
        'count': staticmethod(lambda: len(_SKILL_INSTANCES)),
        'all': staticmethod(lambda: list(_SKILL_INSTANCES))
    })()
    def __init__(self, *args, **kwargs):
        self.id = 1
        self.__dict__.update(kwargs)
        _SKILL_INSTANCES.append(self)
        career_id = kwargs.get('career_id')
        if career_id and db.session:
            c = db.session.get(Career, career_id)
            if c:
                sk_name = kwargs.get('skill_name', '')
                if sk_name:
                    cur = list(c.required_skills or [])
                    cur.append({'id': self.id, 'skill_name': sk_name, 'importance_level': kwargs.get('importance_label', 'High')})
                    c.required_skills = cur

class CareerSubject:
    importance_level = _AttrProxy()
    query = type('_Q', (), {
        'filter_by': staticmethod(lambda **k: type('_Q', (), {'order_by': staticmethod(lambda *a: type('_Q', (), {'all': staticmethod(lambda: list(_SUBJECT_INSTANCES)), 'count': staticmethod(lambda: len(_SUBJECT_INSTANCES))}))})),
        'count': staticmethod(lambda: len(_SUBJECT_INSTANCES)),
        'all': staticmethod(lambda: list(_SUBJECT_INSTANCES))
    })()
    def __init__(self, *args, **kwargs):
        self.id = 1
        self.__dict__.update(kwargs)
        _SUBJECT_INSTANCES.append(self)
        career_id = kwargs.get('career_id')
        if career_id and db.session:
            c = db.session.get(Career, career_id)
            if c:
                subj_name = kwargs.get('subject_name', '')
                if subj_name:
                    cur = list(c.recommended_subjects or [])
                    cur.append({'id': self.id, 'subject_name': subj_name, 'importance_level': kwargs.get('importance_label', 'High')})
                    c.recommended_subjects = cur

class CareerEducation:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

class CareerPathway:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
