from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return decorator


def admin_required(fn):
    return role_required("admin")(fn)


def editor_required(fn):
    return role_required("admin", "editor")(fn)