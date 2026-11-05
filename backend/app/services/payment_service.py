import hmac
import hashlib
import uuid
from typing import Dict, Any, Optional, Tuple
from backend.app.config.config import BaseConfig
from backend.app.models.base import db
from backend.app.models.order import Order, Payment
from backend.app.repositories.order_repo import OrderRepository

class PaymentService:
    @staticmethod
    def is_configured() -> bool:
        """Check if production Razorpay credentials are provided."""
        return bool(BaseConfig.RAZORPAY_KEY_ID and BaseConfig.RAZORPAY_KEY_SECRET)

    @staticmethod
    def create_payment_order(order_id: str, user_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Initiate payment session with Razorpay."""
        order = OrderRepository.get_by_id(order_id)
        if not order:
            return False, "Order not found", None

        if order.user_id != user_id:
            return False, "Unauthorized access to order", None

        if order.status != "pending":
            return False, f"Order is not in pending status (currently '{order.status}')", None

        amount_paise = int(round(float(order.total_amount) * 100))  # in paise for INR
        idempotency_key = f"pay_{order.id}_{uuid.uuid4().hex[:8]}"

        gateway_order_id = ""
        is_live = PaymentService.is_configured()

        if is_live:
            try:
                import razorpay
                client = razorpay.Client(auth=(BaseConfig.RAZORPAY_KEY_ID, BaseConfig.RAZORPAY_KEY_SECRET))
                rzp_order = client.order.create({
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": order.order_number,
                    "payment_capture": 1,
                })
                gateway_order_id = rzp_order["id"]
            except Exception as e:
                return False, f"Payment gateway communication error: {str(e)}", None
        else:
            # Deterministic development test order format
            gateway_order_id = f"order_dev_{uuid.uuid4().hex[:14]}"

        # Record payment entry
        payment = OrderRepository.create_payment(
            order_id=order.id,
            gateway="razorpay",
            gateway_order_id=gateway_order_id,
            amount=float(order.total_amount),
            currency="INR",
            idempotency_key=idempotency_key,
        )

        return True, "Payment order initiated", {
            "payment_id": payment.id,
            "gateway": "razorpay",
            "gateway_order_id": gateway_order_id,
            "amount": float(order.total_amount),
            "currency": "INR",
            "key_id": BaseConfig.RAZORPAY_KEY_ID if is_live else "rzp_test_placeholder_key",
            "order_number": order.order_number,
            "customer_name": f"{order.user.first_name} {order.user.last_name}" if order.user else "",
            "customer_email": order.user.email if order.user else "",
            "is_test_mode": not is_live,
        }

    @staticmethod
    def verify_payment(data: Dict[str, Any], user_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Verify payment authenticity via HMAC-SHA256 signature and update order status."""
        order_id = data["order_id"]
        gateway_order_id = data["gateway_order_id"]
        gateway_payment_id = data["gateway_payment_id"]
        signature = data["gateway_signature"]

        order = OrderRepository.get_by_id(order_id)
        if not order:
            return False, "Order not found", None

        if order.user_id != user_id:
            return False, "Unauthorized access to order", None

        payment = Payment.query.filter_by(order_id=order_id, gateway_order_id=gateway_order_id).first()
        if not payment:
            return False, "Matching payment record not found", None

        # Verify idempotency
        if payment.status == "captured" and order.status == "confirmed":
            return True, "Payment already verified and confirmed", {
                "order_id": order.id,
                "order_number": order.order_number,
                "status": "confirmed",
            }

        # Verify Signature
        is_live = PaymentService.is_configured()
        if is_live:
            secret = BaseConfig.RAZORPAY_KEY_SECRET.encode("utf-8")
            body = f"{gateway_order_id}|{gateway_payment_id}".encode("utf-8")
            expected_signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_signature, signature):
                payment.status = "failed"
                payment.error_description = "HMAC signature verification failed"
                db.session.commit()
                return False, "Payment signature verification failed. Untrusted callback.", None
        else:
            # In development mode, verify format
            if not gateway_payment_id:
                return False, "Missing gateway payment identifier", None

        # Update payment and order status
        payment.gateway_payment_id = gateway_payment_id
        payment.gateway_signature = signature
        payment.status = "captured"
        order.status = "confirmed"
        db.session.commit()

        return True, "Payment verified successfully", {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": "confirmed",
            "amount": float(payment.amount),
            "payment_id": payment.id,
        }
