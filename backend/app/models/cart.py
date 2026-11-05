from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.models.base import db, generate_uuid, TimestampMixin

class Cart(db.Model, TimestampMixin):
    """Shopping cart container for authenticated user or guest."""
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True)
    session_token = Column(String(255), unique=True, nullable=True, index=True)

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(db.Model, TimestampMixin):
    """Line item in shopping cart."""
    __tablename__ = "cart_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")


class Wishlist(db.Model, TimestampMixin):
    """Customer saved wishlist container."""
    __tablename__ = "wishlists"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    user = relationship("User", back_populates="wishlist")
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")


class WishlistItem(db.Model):
    """Individual item in customer wishlist."""
    __tablename__ = "wishlist_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    wishlist_id = Column(String(36), ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product", back_populates="wishlist_items")
