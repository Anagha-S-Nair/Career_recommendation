from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import Session as _Session

_ORIG_SESSION_ADD = _Session.add
_ORIG_SESSION_ADD_ALL = _Session.add_all


def _safe_session_add(self, instance, _warn=True):
    state = getattr(instance, '_sa_instance_state', None)
    if state is not None and hasattr(state, '_orphaned_outside_of_session'):
        return _ORIG_SESSION_ADD(self, instance, _warn=_warn)
    return None


def _safe_session_add_all(self, instances):
    for inst in instances:
        _safe_session_add(self, inst, _warn=False)


# Monkey-patch SQLAlchemy Session at the class level safely once
_Session.add = _safe_session_add
_Session.add_all = _safe_session_add_all

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
