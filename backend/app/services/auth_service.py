from typing import Optional, Dict, Any, Tuple
from flask_jwt_extended import create_access_token, create_refresh_token
from backend.app.models.user import User, UserAddress
from backend.app.repositories.user_repo import UserRepository
from backend.app.utils.security import hash_password, check_password

class AuthService:
    @staticmethod
    def register_user(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        email = data["email"].strip().lower()
        if UserRepository.get_by_email(email):
            return False, "An account with this email address already exists", None

        pwd_hash = hash_password(data["password"])
        user = UserRepository.create(
            email=email,
            password_hash=pwd_hash,
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data.get("phone_number"),
            role=data.get("role", "customer"),
        )

        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role, "email": user.email})
        refresh_token = create_refresh_token(identity=user.id)

        user_dto = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
        }

        return True, "User registered successfully", {
            "user": user_dto,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        user = UserRepository.get_by_email(email)
        if not user or not check_password(password, user.password_hash):
            return False, "Invalid email or password", None

        if not user.is_active:
            return False, "This account has been deactivated. Please contact support.", None

        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role, "email": user.email})
        refresh_token = create_refresh_token(identity=user.id)

        user_dto = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
        }

        return True, "Login successful", {
            "user": user_dto,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    @staticmethod
    def update_profile(user_id: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found", None

        UserRepository.update(
            user,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone_number=data.get("phone_number"),
        )
        return True, "Profile updated successfully", AuthService.get_user_profile(user_id)

    @staticmethod
    def change_password(user_id: str, current_pwd: str, new_pwd: str) -> Tuple[bool, str]:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User not found"
        if not check_password(current_pwd, user.password_hash):
            return False, "Current password does not match"

        user.password_hash = hash_password(new_pwd)
        UserRepository.update(user)
        return True, "Password changed successfully"
