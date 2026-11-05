from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from backend.app.models.base import db
from backend.app.models.order import (
    Order,
    OrderItem,
    Payment,
    InventoryTransaction,
    Coupon,
    CouponUsage,
)
from backend.app.models.catalog import Product

class OrderRepository:
    @staticmethod
    def get_by_id(order_id: str) -> Optional[Order]:
        return Order.query.options(
            joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.images),
            joinedload(Order.payments),
            joinedload(Order.user),
        ).filter(Order.id == order_id).first()

    @staticmethod
    def get_by_order_number(order_number: str) -> Optional[Order]:
        return Order.query.options(
            joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.images),
            joinedload(Order.payments),
            joinedload(Order.user),
        ).filter(Order.order_number == order_number).first()

    @staticmethod
    def list_user_orders(user_id: str, page: int = 1, limit: int = 10) -> Tuple[List[Order], int]:
        query = Order.query.options(
            joinedload(Order.items),
            joinedload(Order.payments),
        ).filter(Order.user_id == user_id).order_by(desc(Order.created_at))
        total = query.count()
        orders = query.offset((page - 1) * limit).limit(limit).all()
        return orders, total

    @staticmethod
    def list_all_orders(status: Optional[str] = None, page: int = 1, limit: int = 20) -> Tuple[List[Order], int]:
        query = Order.query.options(
            joinedload(Order.items),
            joinedload(Order.user),
            joinedload(Order.payments),
        )
        if status:
            query = query.filter(Order.status == status)
        query = query.order_by(desc(Order.created_at))
        total = query.count()
        orders = query.offset((page - 1) * limit).limit(limit).all()
        return orders, total

    @staticmethod
    def create_order(
        user_id: str,
        order_number: str,
        subtotal: float,
        discount_amount: float,
        tax_amount: float,
        shipping_amount: float,
        total_amount: float,
        shipping_address: dict,
        billing_address: Optional[dict] = None,
        coupon_code: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Order:
        order = Order(
            user_id=user_id,
            order_number=order_number,
            status="pending",
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            shipping_address_snapshot=shipping_address,
            billing_address_snapshot=billing_address or shipping_address,
            coupon_code=coupon_code,
            notes=notes,
        )
        db.session.add(order)
        db.session.flush()
        return order

    @staticmethod
    def add_order_item(order_id: str, product: Product, quantity: int, unit_price: float) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            product_id=product.id,
            product_name=product.name,
            sku=product.sku,
            unit_price=unit_price,
            quantity=quantity,
            total_price=round(unit_price * quantity, 2),
        )
        db.session.add(item)
        return item

    @staticmethod
    def update_order_status(order: Order, status: str, tracking_number: Optional[str] = None, notes: Optional[str] = None) -> Order:
        order.status = status
        if tracking_number:
            order.tracking_number = tracking_number
        if notes:
            order.notes = notes
        if status == "cancelled":
            order.cancelled_at = datetime.now(timezone.utc)
        db.session.commit()
        return order

    # --- Payment operations ---
    @staticmethod
    def create_payment(
        order_id: str,
        gateway: str,
        gateway_order_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            gateway=gateway,
            gateway_order_id=gateway_order_id,
            amount=amount,
            currency=currency,
            status="pending",
            idempotency_key=idempotency_key,
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def update_payment(payment: Payment, **kwargs) -> Payment:
        for k, v in kwargs.items():
            if hasattr(payment, k) and v is not None:
                setattr(payment, k, v)
        db.session.commit()
        return payment

    # --- Inventory transaction logging ---
    @staticmethod
    def log_inventory(
        product_id: str,
        change_quantity: int,
        balance_after: int,
        transaction_type: str,
        order_id: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> InventoryTransaction:
        tx = InventoryTransaction(
            product_id=product_id,
            order_id=order_id,
            change_quantity=change_quantity,
            balance_after=balance_after,
            transaction_type=transaction_type,
            notes=notes,
            created_by=created_by,
        )
        db.session.add(tx)
        return tx

    # --- Coupon operations ---
    @staticmethod
    def get_coupon_by_code(code: str) -> Optional[Coupon]:
        now = datetime.now(timezone.utc)
        return Coupon.query.filter(
            Coupon.code == code.strip().upper(),
            Coupon.is_active == True,
            Coupon.starts_at <= now,
            Coupon.expires_at >= now,
        ).first()

    @staticmethod
    def record_coupon_usage(coupon_id: str, user_id: str, order_id: str, discount_given: float) -> CouponUsage:
        usage = CouponUsage(
            coupon_id=coupon_id,
            user_id=user_id,
            order_id=order_id,
            discount_given=discount_given,
        )
        db.session.add(usage)
        coupon = Coupon.query.filter_by(id=coupon_id).first()
        if coupon:
            coupon.usage_count += 1
        db.session.commit()
        return usage
