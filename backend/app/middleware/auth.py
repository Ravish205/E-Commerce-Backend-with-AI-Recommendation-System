from functools import wraps
from flask import g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from backend.app.models.user import User
from backend.app.utils.response import api_response

def jwt_required_custom(fn):
    """Decorator requiring valid JWT token and attaching User to g.current_user."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user:
                return api_response(
                    success=False,
                    message="Authenticated user account not found or deactivated",
                    status_code=401,
                )
            g.current_user = user
            return fn(*args, **kwargs)
        except Exception as e:
            return api_response(
                success=False,
                message=f"Authentication required: {str(e)}",
                status_code=401,
            )
    return wrapper


def admin_required(fn):
    """Decorator requiring valid JWT and admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user:
                return api_response(
                    success=False,
                    message="Authenticated user not found",
                    status_code=401,
                )
            if user.role != "admin":
                return api_response(
                    success=False,
                    message="Administrator privileges required for this action",
                    status_code=403,
                )
            g.current_user = user
            return fn(*args, **kwargs)
        except Exception as e:
            return api_response(
                success=False,
                message=f"Authorization failure: {str(e)}",
                status_code=403,
            )
    return wrapper


def optional_jwt(fn):
    """Optional JWT decorator attaching user to g.current_user if token is present."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        g.current_user = None
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                if user_id:
                    g.current_user = User.query.filter_by(id=user_id, is_active=True).first()
        except Exception:
            g.current_user = None
        return fn(*args, **kwargs)
    return wrapper
