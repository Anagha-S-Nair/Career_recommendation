"""
Dynamic Question Model for MySQL Database.
Stores adaptive assessment questions and choice options directly in 'questions'.
"""

from sqlalchemy import case
from sqlalchemy.ext.hybrid import hybrid_property
from backend.extensions import db


_DEFAULT_SECTIONS = {
    1: 'Academic Profile',
    2: 'Mathematical Ability',
    3: 'Logical Reasoning',
    4: 'Scientific Thinking',
    5: 'Problem Solving',
    6: 'Analytical Thinking',
    7: 'Communication',
    8: 'Creativity',
    9: 'Digital Ability',
    10: 'Learning Ability',
    11: 'Spatial Ability',
    12: 'Practical Ability',
    13: 'Interests',
    14: 'Activities',
    15: 'Teamwork',
    16: 'Leadership',
    17: 'Work Preferences',
    18: 'Career Awareness',
    19: 'Career Preferences'
}

_SECTION_ID_TO_NAME = dict(_DEFAULT_SECTIONS)
_SECTION_NAME_TO_ID = {name.lower(): s_id for s_id, name in _DEFAULT_SECTIONS.items()}


class SectionProxy:
    """Proxy for a question section."""

    def __init__(self, name="General", section_id=1, display_order=1):
        self.id = section_id
        self.name = name or "General"
        self.description = f"{self.name} Assessment Section"
        self.display_order = display_order
        self.is_active = True

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'question_count': Question.query.filter_by(section=self.name, is_active=True).count() if db.session else 0
        }

    def __repr__(self):
        return f"<QuestionSection {self.name}>"


class OptionProxy:
    """Proxy for multiple choice options stored in JSON."""

    def __init__(self, data=None, question_id=None, idx=1, **kwargs):
        if data is None:
            data = kwargs
        elif isinstance(data, dict):
            data = {**data, **kwargs}

        if isinstance(data, dict):
            self.id = data.get('id', idx)
            self.question_id = question_id or data.get('question_id', 1)
            self.option_text = data.get('option_text', '')
            self.option_value = data.get('option_value', '')
            self.score = float(data.get('score', 0.0) or 0.0)
            self.is_correct = bool(data.get('is_correct', False))
            self.display_order = int(data.get('display_order', idx) or idx)
        else:
            self.id = idx
            self.question_id = question_id or 1
            self.option_text = str(data)
            self.option_value = str(data)
            self.score = 0.0
            self.is_correct = False
            self.display_order = idx

        if self.question_id and hasattr(db, 'session'):
            try:
                q = db.session.get(Question, self.question_id)
                if q:
                    cur_opts = list(q.options_data or [])
                    # Avoid duplicate if already present
                    if not any(opt.get('option_value') == self.option_value for opt in cur_opts if isinstance(opt, dict)):
                        cur_opts.append({
                            'id': self.id,
                            'question_id': self.question_id,
                            'option_text': self.option_text,
                            'option_value': self.option_value,
                            'score': self.score,
                            'is_correct': self.is_correct,
                            'display_order': self.display_order
                        })
                        q.options_data = cur_opts
            except Exception:
                pass

    def to_dict(self, include_correct=False):
        d = {
            'id': self.id,
            'question_id': self.question_id,
            'option_text': self.option_text,
            'option_value': self.option_value,
            'display_order': self.display_order
        }
        if include_correct:
            d['score'] = self.score
            d['is_correct'] = self.is_correct
        return d

    def __repr__(self):
        return f"<QuestionOption {self.id}: {self.option_text[:20]}>"


class Question(db.Model):
    """Adaptive assessment question model in MySQL ('questions' table)."""
    __tablename__ = 'questions'

    id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), primary_key=True, autoincrement=True)
    question_text = db.Column(db.Text, nullable=False)
    section = db.Column(db.String(100), nullable=False, default='General', index=True)
    question_type = db.Column(db.String(50), nullable=False, default='MCQ')
    class_min = db.Column(db.SmallInteger, nullable=False, default=7, index=True)
    class_max = db.Column(db.SmallInteger, nullable=False, default=12, index=True)
    difficulty = db.Column(db.String(20), default='Medium')
    skill_category = db.Column(db.String(100), nullable=True, index=True)
    stream_specific = db.Column(db.String(50), nullable=True, default='All')
    display_order = db.Column(db.Integer, default=0)
    options_data = db.Column('options', db.JSON, nullable=False, default=list)
    is_active = db.Column(db.Boolean, default=True, index=True)

    @property
    def question_code(self):
        return getattr(self, '_question_code', None) or (f"Q_{self.id}" if self.id else "Q_NEW")

    @question_code.setter
    def question_code(self, val):
        self._question_code = val

    @hybrid_property
    def section_id(self):
        return _SECTION_NAME_TO_ID.get((self.section or '').lower(), 1)

    @section_id.expression
    def section_id(cls):
        whens = [(cls.section == name, s_id) for s_id, name in _DEFAULT_SECTIONS.items()]
        return case(*whens, else_=1)

    @property
    def is_required(self):
        return True

    @property
    def explanation(self):
        return None

    def __init__(self, **kwargs):
        self._question_code = kwargs.pop('question_code', None)
        kwargs.pop('created_at', None)
        kwargs.pop('is_required', None)
        kwargs.pop('explanation', None)
        sec_id = kwargs.pop('section_id', None)
        sec_name = kwargs.pop('section_name', None)
        sec = kwargs.pop('section', None)
        options = kwargs.pop('options', None)

        final_name = sec or sec_name or (_SECTION_ID_TO_NAME.get(int(sec_id), 'General') if sec_id is not None else 'General')
        kwargs['section'] = final_name

        if options is not None:
            if isinstance(options, list):
                clean_opts = []
                for idx, opt in enumerate(options, 1):
                    if hasattr(opt, 'to_dict'):
                        clean_opts.append(opt.to_dict(include_correct=True))
                    elif isinstance(opt, dict):
                        clean_opts.append(opt)
                    else:
                        clean_opts.append({'id': idx, 'option_text': str(opt), 'score': 0.0, 'is_correct': False})
                kwargs['options_data'] = clean_opts
            else:
                kwargs['options_data'] = []

        super().__init__(**kwargs)

    @property
    def section_name(self):
        return self.section

    @property
    def section_obj(self):
        return SectionProxy(self.section, self.section_id, self.section_id)

    @property
    def options(self):
        opts = self.options_data if isinstance(self.options_data, list) else []
        return [OptionProxy(opt, self.id, idx) for idx, opt in enumerate(opts, 1)]

    @options.setter
    def options(self, value):
        if isinstance(value, list):
            clean_opts = []
            for idx, opt in enumerate(value, 1):
                if hasattr(opt, 'to_dict'):
                    clean_opts.append(opt.to_dict(include_correct=True))
                elif isinstance(opt, dict):
                    clean_opts.append(opt)
                else:
                    clean_opts.append({'id': idx, 'option_text': str(opt), 'score': 0.0, 'is_correct': False})
            self.options_data = clean_opts
        else:
            self.options_data = []

    def to_dict(self, include_correct=False):
        return {
            'id': self.id,
            'question_code': self.question_code,
            'question_text': self.question_text,
            'section_id': self.section_id,
            'section_name': self.section,
            'question_type': self.question_type,
            'class_min': self.class_min,
            'class_max': self.class_max,
            'difficulty': self.difficulty,
            'skill_category': self.skill_category,
            'stream_specific': self.stream_specific,
            'is_required': self.is_required,
            'display_order': self.display_order,
            'explanation': self.explanation if include_correct else None,
            'options': [opt.to_dict(include_correct=include_correct) for opt in self.options]
        }

    def __repr__(self):
        return f"<Question {self.question_code}: {self.question_text[:30]}...>"


class _AttrProxy:
    def asc(self): return self
    def desc(self): return self


class QuestionSection:
    """Helper representing question sections."""
    display_order = _AttrProxy()
    id = _AttrProxy()

    def __init__(self, name="General", id=1, display_order=1, **kwargs):
        self.id = id
        self.name = name
        self.display_order = display_order
        self.is_active = True

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_order': self.display_order,
            'is_active': True,
            'question_count': Question.query.filter_by(section=self.name, is_active=True).count() if db.session else 0
        }

    class _Query:
        @staticmethod
        def filter_by(is_active=True, **kwargs):
            return QuestionSection._Query

        @staticmethod
        def order_by(*args):
            return QuestionSection._Query

        @staticmethod
        def all():
            return [QuestionSection(name=name, id=s_id, display_order=s_id) for s_id, name in _DEFAULT_SECTIONS.items()]

        @staticmethod
        def count():
            return len(_DEFAULT_SECTIONS)

        @staticmethod
        def first():
            return QuestionSection(name=_DEFAULT_SECTIONS[1], id=1, display_order=1)

    query = _Query()

    def __repr__(self):
        return f"<QuestionSection {self.name}>"


# Compatibility alias
QuestionOption = OptionProxy
