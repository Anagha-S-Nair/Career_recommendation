"""
Student Profile Compatibility Interface.
User and Student are consolidated directly in the 'users' table.
"""

from backend.extensions import db
from backend.models.user import User


class AcademicScoreProxy:
    """Proxy for student academic subject marks stored in JSON on User."""

    def __init__(self, data=None, student=None):
        self._data = dict(data) if isinstance(data, dict) else {}
        self._student = student

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value
            if self._student is not None:
                self._student.academic_scores_data = dict(self._data)

    def __getitem__(self, item):
        return self._data.get(item)

    def __setitem__(self, key, value):
        self._data[key] = value
        if self._student is not None:
            self._student.academic_scores_data = dict(self._data)

    @property
    def overall_percentage(self):
        return self._data.get('overall_percentage', 75.0)

    @overall_percentage.setter
    def overall_percentage(self, val):
        self._data['overall_percentage'] = float(val) if val is not None else 75.0
        if self._student is not None:
            self._student.academic_scores_data = dict(self._data)

    def to_dict(self):
        d = dict(self._data)
        d['overall_percentage'] = self.overall_percentage
        return d

    def __repr__(self):
        return f"<AcademicScore overall={self.overall_percentage}%>"


# Student is an alias to User (table 'users')
Student = User


class AcademicScore:
    """Lightweight compatibility interface for academic scores."""

    def __init__(self, student_id=None, **kwargs):
        self.student_id = student_id
        self._data = dict(kwargs)

    def __getattr__(self, name):
        return self._data.get(name)

    def to_dict(self):
        return dict(self._data)

    class _Query:
        @staticmethod
        def filter_by(student_id=None, **kwargs):
            class _Result:
                def __init__(self, s_id):
                    self.s_id = s_id
                def order_by(self, *args):
                    return self
                def first(self):
                    if not self.s_id or not db.session:
                        return None
                    st = db.session.get(User, self.s_id)
                    return st.academic_scores if st else None
            return _Result(student_id)

    query = _Query()
