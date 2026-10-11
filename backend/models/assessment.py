"""
Student Assessment Session Model for MySQL Database.
Stores assessment sessions, student answers, and cognitive ability scores directly in 'assessment_sessions'.
"""

from datetime import datetime, timezone
from sqlalchemy.orm.attributes import flag_modified
from backend.extensions import db


class AssessmentScoreProxy:
    """Proxy for cognitive ability & interest scores stored in JSON on AssessmentSession."""
    COGNITIVE_FIELDS = [
        'mathematical_ability', 'logical_reasoning', 'scientific_reasoning',
        'problem_solving', 'analytical_ability', 'communication', 'creativity',
        'digital_ability', 'learning_ability', 'memory', 'observation',
        'spatial_ability', 'practical_ability', 'teamwork', 'leadership'
    ]
    INTEREST_FIELDS = [
        'technology_interest', 'science_interest', 'healthcare_interest',
        'business_interest', 'creative_interest', 'research_interest', 'social_interest'
    ]

    def __init__(self, data=None, session=None, **kwargs):
        self._data = dict(data) if isinstance(data, dict) else {}
        self._data.update({k: float(v) for k, v in kwargs.items() if k not in ['assessment_id', 'id', 'created_at'] and v is not None})
        self.assessment_id = kwargs.get('assessment_id') or (session.id if session else 1)
        if not session and self.assessment_id and hasattr(db, 'session'):
            try:
                session = db.session.get(AssessmentSession, self.assessment_id)
            except Exception:
                session = None
        self._session = session
        if self._session is not None:
            self._session.scores_data = dict(self._data)
            flag_modified(self._session, 'scores_data')

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return float(self._data.get(name, 0.0))

    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'assessment_id':
            super().__setattr__(name, value)
        else:
            self._data[name] = float(value) if value is not None else 0.0
            if self._session is not None:
                self._session.scores_data = dict(self._data)
                flag_modified(self._session, 'scores_data')

    def to_dict(self):
        cog = {k: round(float(self._data.get(k, 0.0)), 1) for k in self.COGNITIVE_FIELDS}
        intr = {k: round(float(self._data.get(k, 0.0)), 1) for k in self.INTEREST_FIELDS}
        return {
            'id': self._session.id if self._session else 1,
            'assessment_id': self._session.id if self._session else 1,
            'cognitive_scores': cog,
            'interest_scores': intr,
            'created_at': self._session.started_at.isoformat() if self._session and self._session.started_at else None
        }

    def __repr__(self):
        return f"<AssessmentScore for Assessment {self.assessment_id}>"


class StudentAnswer:
    """Interface for individual student answer records stored in session JSON."""

    def __init__(self, data_or_session_id=None, **kwargs):
        if isinstance(data_or_session_id, dict):
            data = dict(data_or_session_id)
            data.update(kwargs)
        elif data_or_session_id is not None and not kwargs.get('assessment_id'):
            data = dict(kwargs)
            data['assessment_id'] = data_or_session_id
        else:
            data = dict(kwargs)

        self.id = data.get('id', 1)
        self.assessment_id = data.get('assessment_id', 1)
        self.question_id = int(data.get('question_id', 1)) if str(data.get('question_id', '')).isdigit() else 1
        self.selected_option_id = data.get('selected_option_id')
        self.selected_option = data.get('selected_option')
        self.answer_text = data.get('answer_text') or self.selected_option
        num_v = data.get('numeric_value')
        self.numeric_value = float(num_v) if num_v is not None else None
        self.time_taken_seconds = int(data.get('time_taken_seconds', 0) or 0)
        self.answered_at = str(data.get('answered_at', datetime.now(timezone.utc).isoformat()))

        if self.assessment_id and self.question_id and hasattr(db, 'session'):
            try:
                sess = db.session.get(AssessmentSession, self.assessment_id)
                if sess:
                    current_answers = dict(sess.answers_data or {})
                    current_answers[str(self.question_id)] = self.to_dict()
                    sess.answers_data = current_answers
                    flag_modified(sess, 'answers_data')
            except Exception:
                pass

    @property
    def question(self):
        from backend.models.question import Question
        return db.session.get(Question, self.question_id) if db.session and self.question_id else None

    @property
    def option(self):
        q = self.question
        if q:
            for opt in q.options:
                if self.selected_option_id and opt.id == self.selected_option_id:
                    return opt
                if self.selected_option and opt.option_value == self.selected_option:
                    return opt
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'question_id': self.question_id,
            'selected_option_id': self.selected_option_id,
            'selected_option': self.selected_option,
            'answer_text': self.answer_text,
            'numeric_value': self.numeric_value,
            'time_taken_seconds': self.time_taken_seconds,
            'answered_at': self.answered_at
        }

    class _Query:
        @staticmethod
        def filter_by(assessment_id=None, question_id=None, **kwargs):
            class _AnsResult:
                def __init__(self, a_id, q_id):
                    self.a_id = a_id
                    self.q_id = q_id

                def first(self):
                    if not self.a_id or not db.session:
                        return None
                    sess = db.session.get(AssessmentSession, self.a_id)
                    if not sess or not sess.answers_data:
                        return None
                    ans_map = sess.answers_data if isinstance(sess.answers_data, dict) else {}
                    if self.q_id is not None:
                        item = ans_map.get(str(self.q_id))
                        return StudentAnswer(item) if isinstance(item, dict) else (StudentAnswer(assessment_id=self.a_id, question_id=self.q_id, selected_option=str(item)) if item else None)
                    for qid, item in ans_map.items():
                        return StudentAnswer(item) if isinstance(item, dict) else StudentAnswer(assessment_id=self.a_id, question_id=int(qid) if str(qid).isdigit() else 1, selected_option=str(item))
                    return None

                def all(self):
                    if not self.a_id or not db.session:
                        return []
                    sess = db.session.get(AssessmentSession, self.a_id)
                    if not sess or not sess.answers_data:
                        return []
                    ans_map = sess.answers_data if isinstance(sess.answers_data, dict) else {}
                    if self.q_id is not None:
                        item = ans_map.get(str(self.q_id))
                        if item:
                            return [StudentAnswer(item) if isinstance(item, dict) else StudentAnswer(assessment_id=self.a_id, question_id=self.q_id, selected_option=str(item))]
                        return []
                    res = []
                    for qid, item in ans_map.items():
                        qid_int = int(qid) if str(qid).isdigit() else 1
                        res.append(StudentAnswer(item) if isinstance(item, dict) else StudentAnswer(assessment_id=self.a_id, question_id=qid_int, selected_option=str(item)))
                    return res

                def count(self):
                    return len(self.all())

                def __iter__(self):
                    return iter(self.all())

            return _AnsResult(assessment_id, question_id)

    query = _Query()

    def __repr__(self):
        return f"<StudentAnswer Q{self.question_id}: {self.selected_option}>"


class AnswersCollectionProxy:
    """Collection proxy for student answers in an assessment session."""

    def __init__(self, answers_dict=None, session=None):
        self._answers = dict(answers_dict) if isinstance(answers_dict, dict) else {}
        self._session = session

    def all(self):
        res = []
        for q_id, a_data in self._answers.items():
            qid_int = int(q_id) if str(q_id).isdigit() else 1
            if isinstance(a_data, dict):
                item = dict(a_data)
                item.setdefault('assessment_id', self._session.id if self._session else 1)
                item.setdefault('question_id', qid_int)
                res.append(StudentAnswer(item))
            else:
                res.append(StudentAnswer(assessment_id=self._session.id if self._session else 1, question_id=qid_int, selected_option=str(a_data)))
        return res

    def count(self):
        return len(self._answers)

    def filter_by(self, question_id=None, **kwargs):
        class _FilterRes:
            def __init__(self, parent, q_id):
                self.parent = parent
                self.q_id = str(q_id)

            def first(self):
                if self.q_id in self.parent._answers:
                    item = self.parent._answers[self.q_id]
                    qid_int = int(self.q_id) if str(self.q_id).isdigit() else 1
                    if isinstance(item, dict):
                        d = dict(item)
                        d.setdefault('assessment_id', self.parent._session.id if self.parent._session else 1)
                        d.setdefault('question_id', qid_int)
                        return StudentAnswer(d)
                    return StudentAnswer(assessment_id=self.parent._session.id if self.parent._session else 1, question_id=qid_int, selected_option=str(item))
                return None

        return _FilterRes(self, question_id)

    def __iter__(self):
        return iter(self.all())


class AssessmentSession(db.Model):
    """Student assessment session state and progress in MySQL."""
    __tablename__ = 'assessment_sessions'

    id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(
        db.Enum('not_started', 'in_progress', 'completed', 'abandoned', name='session_status_enum'),
        default='not_started',
        index=True
    )
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    current_question = db.Column(db.Integer, default=0)
    completion_percentage = db.Column(db.Float, default=0.0)
    selected_question_ids = db.Column(db.Text, nullable=True)
    answers_data = db.Column('answers', db.JSON, default=dict)
    scores_data = db.Column('scores', db.JSON, default=dict)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('assessments', lazy='dynamic', cascade='all, delete-orphan'))
    recommendations = db.relationship('CareerRecommendation', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def created_at(self):
        """Compatibility property mapping to started_at since created_at was removed from schema."""
        return self.started_at

    @property
    def user(self):
        return self.student

    @property
    def scores(self):
        return AssessmentScoreProxy(self.scores_data or {}, self)

    @scores.setter
    def scores(self, val):
        if isinstance(val, dict):
            self.scores_data = dict(val)
        elif isinstance(val, AssessmentScoreProxy):
            self.scores_data = dict(val._data)
        else:
            self.scores_data = {}

    @property
    def answers(self):
        return AnswersCollectionProxy(self.answers_data or {}, self)

    @answers.setter
    def answers(self, val):
        self.answers_data = dict(val) if isinstance(val, dict) else {}

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'current_question': self.current_question,
            'completion_percentage': self.completion_percentage,
            'selected_question_ids': self.selected_question_ids,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<AssessmentSession {self.id} - Student {self.student_id} ({self.status})>"


class AssessmentScore:
    """Compatibility interface for assessment scores without a separate database table."""

    def __init__(self, assessment_id=None, **kwargs):
        self.assessment_id = assessment_id
        self._data = dict(kwargs)
        if self.assessment_id and hasattr(db, 'session'):
            try:
                sess = db.session.get(AssessmentSession, self.assessment_id)
                if sess:
                    sess.scores_data = dict(self._data)
                    flag_modified(sess, 'scores_data')
            except Exception:
                pass

    def __getattr__(self, name):
        return self._data.get(name, 0.0)

    def to_dict(self):
        cog = {k: round(float(self._data.get(k, 0.0)), 1) for k in AssessmentScoreProxy.COGNITIVE_FIELDS}
        intr = {k: round(float(self._data.get(k, 0.0)), 1) for k in AssessmentScoreProxy.INTEREST_FIELDS}
        return {
            'id': 1,
            'assessment_id': self.assessment_id,
            'cognitive_scores': cog,
            'interest_scores': intr,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

    class _Query:
        @staticmethod
        def filter_by(assessment_id=None, **kwargs):
            class _QueryResult:
                def __init__(self, a_id):
                    self.a_id = a_id

                def first(self):
                    if not self.a_id or not db.session:
                        return None
                    sess = db.session.get(AssessmentSession, self.a_id)
                    return sess.scores if sess else None

            return _QueryResult(assessment_id)

    query = _Query()

    def __repr__(self):
        return f"<AssessmentScore for Assessment {self.assessment_id}>"
