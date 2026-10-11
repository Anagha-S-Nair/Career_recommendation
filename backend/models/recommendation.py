from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from backend.extensions import db


class CareerRecommendation(db.Model):
    """Career recommendation record linked to an assessment session in MySQL."""
    __tablename__ = 'career_recommendations'

    id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), db.ForeignKey('assessment_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    career_id = db.Column(db.Integer().with_variant(db.BigInteger, "mysql"), db.ForeignKey('careers.id', ondelete='CASCADE'), nullable=False)
    rank_position = db.Column(db.Integer, nullable=False, default=1, index=True)
    score = db.Column(db.Float, nullable=True)  # Match score percentage (0.0 to 100.0)
    is_decisive = db.Column(db.Boolean, default=False, index=True)  # Calibrated high confidence (>90% accuracy)
    probability = db.Column(db.Float, nullable=True)  # Raw ML model probability (0.0 to 1.0)
    recommendation_reason = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    skill_gaps = db.Column(db.Text, nullable=True)
    match_breakdown = db.Column(db.JSON, nullable=True)  # Ability, Interest, Academic, Learning match components

    __table_args__ = (
        db.UniqueConstraint('assessment_id', 'career_id', name='uq_assessment_career'),
    )

    # Relationships
    career = db.relationship('Career')

    @property
    def created_at(self):
        """Compatibility property linking to session started_at since created_at was removed from schema."""
        return self.session.started_at if self.session else None

    def __init__(self, **kwargs):
        kwargs.pop('created_at', None)
        if 'rank' in kwargs and 'rank_position' not in kwargs:
            kwargs['rank_position'] = kwargs.pop('rank')
        if 'match_score' in kwargs and 'score' not in kwargs:
            kwargs['score'] = kwargs.pop('match_score')
        if 'fit_reason' in kwargs and 'recommendation_reason' not in kwargs:
            kwargs['recommendation_reason'] = kwargs.pop('fit_reason')
        super().__init__(**kwargs)

    @hybrid_property
    def rank(self):
        return self.rank_position

    @rank.setter
    def rank(self, val):
        self.rank_position = val

    @hybrid_property
    def match_score(self):
        return self.score

    @match_score.setter
    def match_score(self, val):
        self.score = val

    @hybrid_property
    def fit_reason(self):
        return self.recommendation_reason

    @fit_reason.setter
    def fit_reason(self, val):
        self.recommendation_reason = val

    def to_dict(self):
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'career_id': self.career_id,
            'career_name': self.career.career_name if self.career else None,
            'career_code': self.career.career_code if self.career else None,
            'domain_name': self.career.domain.domain_name if self.career and self.career.domain else None,
            'domain_icon': self.career.domain.icon if self.career and self.career.domain else 'bi-briefcase',
            'description': self.career.description if self.career else None,
            'rank': self.rank_position,
            'score': round(self.score, 1) if self.score is not None else 0.0,
            'is_decisive': bool(self.is_decisive) if self.is_decisive is not None else False,
            'probability': round(self.probability, 4) if self.probability is not None else None,
            'match_breakdown': self.match_breakdown or {},
            'recommendation_reason': self.recommendation_reason,
            'strengths': self.strengths,
            'skill_gaps': self.skill_gaps,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<CareerRecommendation Rank {self.rank_position}: Career {self.career_id} for Session {self.assessment_id}>"
