from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.auth_schema import ProfileUpdateSchema, ChangePasswordSchema, AddressSchema
from backend.app.services.auth_service import AuthService
from backend.app.repositories.user_repo import UserRepository
from backend.app.middleware.auth import jwt_required_custom
from backend.app.utils.response import api_response

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

profile_schema = ProfileUpdateSchema()
change_pwd_schema = ChangePasswordSchema()
address_schema = AddressSchema()

@user_bp.route("/profile", methods=["PUT"])
@jwt_required_custom
def update_profile():
    try:
        data = profile_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = AuthService.update_profile(g.current_user.id, data)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@user_bp.route("/change-password", methods=["PUT"])
@jwt_required_custom
def change_password():
    try:
        data = change_pwd_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message = AuthService.change_password(g.current_user.id, data["current_password"], data["new_password"])
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, status_code=200)


@user_bp.route("/addresses", methods=["GET"])
@jwt_required_custom
def list_addresses():
    addresses = UserRepository.get_addresses(g.current_user.id)
    data = [
        {
            "id": a.id,
            "address_type": a.address_type,
            "recipient_name": a.recipient_name,
            "phone": a.phone,
            "street_address": a.street_address,
            "landmark": a.landmark,
            "city": a.city,
            "state": a.state,
            "postal_code": a.postal_code,
            "country": a.country,
            "is_default": a.is_default,
        }
        for a in addresses
    ]
    return api_response(success=True, message="Addresses retrieved", data=data, status_code=200)


@user_bp.route("/addresses", methods=["POST"])
@jwt_required_custom
def create_address():
    try:
        data = address_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    address = UserRepository.create_address(g.current_user.id, data)
    return api_response(
        success=True,
        message="Address added successfully",
        data={
            "id": address.id,
            "address_type": address.address_type,
            "recipient_name": address.recipient_name,
            "phone": address.phone,
            "street_address": address.street_address,
            "landmark": address.landmark,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code,
            "country": address.country,
            "is_default": address.is_default,
        },
        status_code=201,
    )


@user_bp.route("/addresses/<string:address_id>", methods=["DELETE"])
@jwt_required_custom
def delete_address(address_id: str):
    address = UserRepository.get_address_by_id(address_id, g.current_user.id)
    if not address:
        return api_response(success=False, message="Address not found", status_code=404)

    UserRepository.delete_address(address)
    return api_response(success=True, message="Address deleted successfully", status_code=200)
