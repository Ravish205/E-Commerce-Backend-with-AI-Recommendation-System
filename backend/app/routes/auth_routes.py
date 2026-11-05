from flask import Blueprint, request, g
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from backend.app.schemas.auth_schema import RegisterSchema, LoginSchema
from backend.app.services.auth_service import AuthService
from backend.app.middleware.auth import jwt_required_custom
from backend.app.utils.response import api_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = AuthService.register_user(data)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=201)


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = AuthService.login_user(data["email"], data["password"])
    if not success:
        return api_response(success=False, message=message, status_code=401)
    return api_response(success=True, message=message, data=result, status_code=200)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    user = AuthService.get_user_profile(user_id)
    if not user:
        return api_response(success=False, message="User not found", status_code=404)

    new_access_token = create_access_token(
        identity=user["id"],
        additional_claims={"role": user["role"], "email": user["email"]}
    )
    return api_response(
        success=True,
        message="Token refreshed successfully",
        data={"access_token": new_access_token},
        status_code=200,
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required_custom
def get_current_user():
    profile = AuthService.get_user_profile(g.current_user.id)
    return api_response(success=True, message="Profile retrieved", data=profile, status_code=200)


@auth_bp.route("/logout", methods=["POST"])
@jwt_required_custom
def logout():
    # In stateless JWT architecture with refresh token rotation, client drops the tokens
    return api_response(success=True, message="Successfully logged out", status_code=200)
