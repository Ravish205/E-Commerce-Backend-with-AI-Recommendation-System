from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.models.base import db, generate_uuid, TimestampMixin

class User(db.Model, TimestampMixin):
    """User account model for customers and administrators."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=True)
    role = Column(String(20), nullable=False, default="customer")  # 'customer', 'admin'
    is_active = Column(Boolean, nullable=False, default=True)
    is_email_verified = Column(Boolean, nullable=False, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("ProductReview", back_populates="user", foreign_keys="[ProductReview.user_id]")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class UserAddress(db.Model, TimestampMixin):
    """Saved addresses for billing and shipping."""
    __tablename__ = "user_addresses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    address_type = Column(String(20), nullable=False, default="shipping")  # 'shipping', 'billing'
    recipient_name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=False)
    street_address = Column(Text, nullable=False)
    landmark = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False, index=True)
    country = Column(String(100), nullable=False, default="India")
    is_default = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="addresses")


class Notification(db.Model, TimestampMixin):
    """Transactional notifications for users and admins."""
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="system")
    link_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, index=True)

    user = relationship("User", back_populates="notifications")
