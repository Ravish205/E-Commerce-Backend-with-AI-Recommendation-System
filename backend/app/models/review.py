from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import db, generate_uuid, TimestampMixin

class ProductReview(db.Model, TimestampMixin):
    """Customer ratings and reviews with verified purchase check."""
    __tablename__ = "product_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    title = Column(String(200), nullable=False)
    comment = Column(Text, nullable=False)
    is_verified_purchase = Column(Boolean, nullable=False, default=False)
    is_approved = Column(Boolean, nullable=False, default=True)  # Admin moderation flag
    moderated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews", foreign_keys=[user_id])
