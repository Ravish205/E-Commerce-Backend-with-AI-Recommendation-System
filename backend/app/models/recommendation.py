from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.models.base import db, generate_uuid

class UserInteraction(db.Model):
    """User behavioral interaction event stream."""
    __tablename__ = "user_interactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False, index=True)
    # Types: 'view', 'search_click', 'wishlist_add', 'cart_add', 'purchase', 'review'
    dwell_time_seconds = Column(Integer, default=0)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    product = relationship("Product", foreign_keys=[product_id])


class ProductRecommendation(db.Model):
    """Precomputed or cached product recommendations."""
    __tablename__ = "product_recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True)
    target_product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    recommendation_type = Column(String(50), nullable=False, index=True)
    # Types: 'similar', 'frequently_bought_together', 'personalized', 'trending'
    score = Column(Numeric(8, 4), nullable=False)
    reason = Column(String(255), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    source_product = relationship("Product", foreign_keys=[source_product_id])
    target_product = relationship("Product", foreign_keys=[target_product_id])
