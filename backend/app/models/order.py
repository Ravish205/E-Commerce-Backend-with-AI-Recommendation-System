from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.models.base import db, generate_uuid, TimestampMixin

class Order(db.Model, TimestampMixin):
    """Customer order record."""
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    # Statuses: 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'
    
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(12, 2), nullable=False, default=0.00)
    shipping_amount = Column(Numeric(12, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(12, 2), nullable=False)
    coupon_code = Column(String(50), nullable=True)
    
    # Immutable address snapshots at checkout time
    shipping_address_snapshot = Column(JSON, nullable=False)
    billing_address_snapshot = Column(JSON, nullable=True)
    
    tracking_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    inventory_transactions = relationship("InventoryTransaction", back_populates="order")


class OrderItem(db.Model):
    """Immutable order line item capturing price and SKU snapshot."""
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Payment(db.Model, TimestampMixin):
    """Payment gateway transaction record."""
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True)
    gateway = Column(String(50), nullable=False, default="razorpay")  # 'razorpay' or 'stripe'
    gateway_order_id = Column(String(100), nullable=False, index=True)
    gateway_payment_id = Column(String(100), unique=True, nullable=True, index=True)
    gateway_signature = Column(String(255), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    status = Column(String(30), nullable=False, default="pending", index=True)
    # 'pending', 'authorized', 'captured', 'failed', 'refunded'
    
    idempotency_key = Column(String(100), unique=True, nullable=False)
    error_code = Column(String(100), nullable=True)
    error_description = Column(Text, nullable=True)
    refund_id = Column(String(100), nullable=True)
    refund_amount = Column(Numeric(12, 2), nullable=True)

    order = relationship("Order", back_populates="payments")


class InventoryTransaction(db.Model):
    """Auditable double-entry inventory ledger."""
    __tablename__ = "inventory_transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    change_quantity = Column(Integer, nullable=False)  # positive for restock, negative for deduction
    balance_after = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    # 'order_placement', 'order_cancellation', 'restock', 'manual_adjustment', 'damaged'
    notes = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    product = relationship("Product", back_populates="inventory_transactions")
    order = relationship("Order", back_populates="inventory_transactions")


class Coupon(db.Model, TimestampMixin):
    """Promotional coupon discount code."""
    __tablename__ = "coupons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(String(20), nullable=False)  # 'percentage' or 'fixed_amount'
    discount_value = Column(Numeric(10, 2), nullable=False)
    min_order_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    max_discount = Column(Numeric(10, 2), nullable=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    redemptions = relationship("CouponUsage", back_populates="coupon", cascade="all, delete-orphan")


class CouponUsage(db.Model):
    """Record of coupon redemption by a customer."""
    __tablename__ = "coupon_usage"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    coupon_id = Column(String(36), ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    discount_given = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    coupon = relationship("Coupon", back_populates="redemptions")
