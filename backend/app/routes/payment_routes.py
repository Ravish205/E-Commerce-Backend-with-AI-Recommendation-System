from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.order_schema import PaymentVerifySchema
from backend.app.services.payment_service import PaymentService
from backend.app.middleware.auth import jwt_required_custom
from backend.app.utils.response import api_response

payment_bp = Blueprint("payments", __name__, url_prefix="/api/payments")

verify_schema = PaymentVerifySchema()

@payment_bp.route("/create-order", methods=["POST"])
@jwt_required_custom
def create_payment_order():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    if not order_id:
        return api_response(success=False, message="order_id is required", status_code=400)

    success, message, result = PaymentService.create_payment_order(order_id=order_id, user_id=g.current_user.id)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@payment_bp.route("/verify", methods=["POST"])
@jwt_required_custom
def verify_payment():
    try:
        data = verify_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = PaymentService.verify_payment(data=data, user_id=g.current_user.id)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@payment_bp.route("/webhook", methods=["POST"])
def payment_webhook():
    # Process Razorpay asynchronous webhook notifications
    return api_response(success=True, message="Webhook received", status_code=200)
