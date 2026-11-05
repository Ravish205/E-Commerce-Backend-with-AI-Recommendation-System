import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from backend.app.models.base import db
from backend.app.models.order import Order, OrderItem
from backend.app.models.catalog import Product
from backend.app.repositories.cart_repo import CartRepository
from backend.app.repositories.order_repo import OrderRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.services.cart_service import CartService

class OrderService:
    @staticmethod
    def generate_order_number() -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{unique_suffix}"

    @staticmethod
    def serialize_order(order: Order, include_items: bool = True) -> Dict[str, Any]:
        data = {
            "id": order.id,
            "order_number": order.order_number,
            "user_id": order.user_id,
            "status": order.status,
            "subtotal": float(order.subtotal),
            "discount_amount": float(order.discount_amount),
            "tax_amount": float(order.tax_amount),
            "shipping_amount": float(order.shipping_amount),
            "total_amount": float(order.total_amount),
            "coupon_code": order.coupon_code,
            "shipping_address": order.shipping_address_snapshot,
            "billing_address": order.billing_address_snapshot,
            "tracking_number": order.tracking_number,
            "notes": order.notes,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
            "cancellation_reason": order.cancellation_reason,
        }

        if include_items:
            data["items"] = [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "sku": item.sku,
                    "unit_price": float(item.unit_price),
                    "quantity": item.quantity,
                    "total_price": float(item.total_price),
                    "primary_image": item.product.primary_image if item.product else None,
                }
                for item in order.items
            ]
            data["payments"] = [
                {
                    "id": p.id,
                    "gateway": p.gateway,
                    "gateway_order_id": p.gateway_order_id,
                    "gateway_payment_id": p.gateway_payment_id,
                    "amount": float(p.amount),
                    "currency": p.currency,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in order.payments
            ]

        return data

    @staticmethod
    def create_order(user_id: str, order_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        # 1. Fetch user and cart
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, "User account not found", None

        cart = CartRepository.get_or_create_cart(user_id=user_id)
        if not cart.items:
            return False, "Your shopping cart is empty", None

        # 2. Resolve Shipping Address
        shipping_addr = None
        if order_data.get("shipping_address_id"):
            addr_obj = UserRepository.get_address_by_id(order_data["shipping_address_id"], user_id)
            if addr_obj:
                shipping_addr = {
                    "recipient_name": addr_obj.recipient_name,
                    "phone": addr_obj.phone,
                    "street_address": addr_obj.street_address,
                    "landmark": addr_obj.landmark,
                    "city": addr_obj.city,
                    "state": addr_obj.state,
                    "postal_code": addr_obj.postal_code,
                    "country": addr_obj.country,
                }
        elif order_data.get("shipping_address"):
            shipping_addr = order_data["shipping_address"]

        if not shipping_addr:
            return False, "A valid shipping address is required to place an order", None

        # 3. Calculate authoritative summary
        coupon_code = order_data.get("coupon_code")
        summary = CartService.calculate_cart_summary(cart, coupon_code=coupon_code)

        if not summary["is_checkout_ready"]:
            reasons = "; ".join(summary["warnings"])
            return False, f"Cannot checkout: {reasons}", None

        # 4. Atomic database transaction with row-level locks
        try:
            order_number = OrderService.generate_order_number()
            order = Order(
                user_id=user_id,
                order_number=order_number,
                status="pending",
                subtotal=summary["subtotal"],
                discount_amount=summary["discount_amount"],
                tax_amount=summary["tax_amount"],
                shipping_amount=summary["shipping_amount"],
                total_amount=summary["final_total"],
                coupon_code=coupon_code if summary["coupon"] else None,
                shipping_address_snapshot=shipping_addr,
                billing_address_snapshot=order_data.get("billing_address") or shipping_addr,
                notes=order_data.get("notes"),
            )
            db.session.add(order)
            db.session.flush()

            # Process inventory deductions and create order line items
            for item in cart.items:
                product = (
                    db.session.query(Product)
                    .filter(Product.id == item.product_id)
                    .with_for_update()
                    .first()
                )

                if not product or product.stock < item.quantity:
                    db.session.rollback()
                    return False, f"Product '{item.product.name}' ran out of stock during checkout.", None

                # Deduct inventory
                product.stock -= item.quantity
                new_balance = product.stock

                # Log inventory audit transaction
                OrderRepository.log_inventory(
                    product_id=product.id,
                    change_quantity=-item.quantity,
                    balance_after=new_balance,
                    transaction_type="order_placement",
                    order_id=order.id,
                    notes=f"Deducted for order {order.order_number}",
                )

                # Create OrderItem with frozen price snapshot
                OrderRepository.add_order_item(
                    order_id=order.id,
                    product=product,
                    quantity=item.quantity,
                    unit_price=product.effective_price,
                )

            # Record coupon usage if applicable
            if summary["coupon"]:
                coupon = OrderRepository.get_coupon_by_code(coupon_code)
                if coupon:
                    OrderRepository.record_coupon_usage(
                        coupon_id=coupon.id,
                        user_id=user_id,
                        order_id=order.id,
                        discount_given=summary["discount_amount"],
                    )

            # Clear cart
            CartRepository.clear_cart(cart.id)
            db.session.commit()

            return True, "Order placed successfully", OrderService.serialize_order(order)

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to create order: {str(e)}", None

    @staticmethod
    def cancel_order(order_id: str, user_id: Optional[str] = None, reason: str = "Customer requested cancellation") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        order = OrderRepository.get_by_id(order_id)
        if not order:
            return False, "Order not found", None

        # Check authorization if called by user
        if user_id and order.user_id != user_id:
            return False, "Unauthorized access to order", None

        # Check eligibility: only 'pending', 'confirmed', or 'processing' can be cancelled
        if order.status not in ["pending", "confirmed", "processing"]:
            return False, f"Order cannot be cancelled in its current status: '{order.status}'", None

        try:
            # Restore inventory for each line item
            for item in order.items:
                product = (
                    db.session.query(Product)
                    .filter(Product.id == item.product_id)
                    .with_for_update()
                    .first()
                )
                if product:
                    product.stock += item.quantity
                    OrderRepository.log_inventory(
                        product_id=product.id,
                        change_quantity=item.quantity,
                        balance_after=product.stock,
                        transaction_type="order_cancellation",
                        order_id=order.id,
                        notes=f"Restored stock from cancelled order {order.order_number}",
                    )

            OrderRepository.update_order_status(order, status="cancelled", notes=reason)
            order.cancellation_reason = reason
            db.session.commit()

            return True, "Order cancelled successfully", OrderService.serialize_order(order)

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to cancel order: {str(e)}", None

    @staticmethod
    def get_order_invoice(order_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        order = OrderRepository.get_by_id(order_id)
        if not order:
            return None
        if user_id and order.user_id != user_id:
            return None

        return {
            "invoice_number": f"INV-{order.order_number}",
            "invoice_date": order.created_at.strftime("%B %d, %Y") if order.created_at else "",
            "order": OrderService.serialize_order(order),
            "company": {
                "name": "E-Commerce AI Store",
                "address": "Indiranagar 100ft Road, Bengaluru, Karnataka 560038",
                "tax_id": "29ABCDE1234F1Z5",
                "support_email": "support@ecommerceaistore.com",
            },
        }
