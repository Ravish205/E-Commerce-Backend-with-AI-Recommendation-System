from typing import Optional, List
from backend.app.models.base import db
from backend.app.models.user import User, UserAddress

class UserRepository:
    @staticmethod
    def get_by_id(user_id: str) -> Optional[User]:
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email.strip().lower()).first()

    @staticmethod
    def create(email: str, password_hash: str, first_name: str, last_name: str, phone_number: Optional[str] = None, role: str = "customer") -> User:
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone_number=phone_number.strip() if phone_number else None,
            role=role,
            is_active=True,
            is_email_verified=False,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def get_addresses(user_id: str) -> List[UserAddress]:
        return UserAddress.query.filter_by(user_id=user_id).order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc()).all()

    @staticmethod
    def get_address_by_id(address_id: str, user_id: str) -> Optional[UserAddress]:
        return UserAddress.query.filter_by(id=address_id, user_id=user_id).first()

    @staticmethod
    def create_address(user_id: str, data: dict) -> UserAddress:
        if data.get("is_default"):
            # Unset existing default address
            UserAddress.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

        address = UserAddress(
            user_id=user_id,
            address_type=data.get("address_type", "shipping"),
            recipient_name=data["recipient_name"].strip(),
            phone=data["phone"].strip(),
            street_address=data["street_address"].strip(),
            landmark=data.get("landmark", "").strip() if data.get("landmark") else None,
            city=data["city"].strip(),
            state=data["state"].strip(),
            postal_code=data["postal_code"].strip(),
            country=data.get("country", "India").strip(),
            is_default=data.get("is_default", False),
        )
        db.session.add(address)
        db.session.commit()
        return address

    @staticmethod
    def delete_address(address: UserAddress) -> None:
        db.session.delete(address)
        db.session.commit()
