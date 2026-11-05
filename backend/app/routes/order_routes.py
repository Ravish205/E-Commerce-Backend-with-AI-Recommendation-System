from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.order_schema import OrderCreateSchema
from backend.app.services.order_service import OrderService
from backend.app.repositories.order_repo import OrderRepository
from backend.app.middleware.auth import jwt_required_custom
from backend.app.utils.response import api_response

order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

order_create_schema = OrderCreateSchema()

@order_bp.route("", methods=["POST"])
@jwt_required_custom
def create_order():
    try:
        data = order_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = OrderService.create_order(user_id=g.current_user.id, order_data=data)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=201)


@order_bp.route("", methods=["GET"])
@jwt_required_custom
def list_orders():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    orders, total = OrderRepository.list_user_orders(user_id=g.current_user.id, page=page, limit=limit)
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return api_response(
        success=True,
        message="Orders retrieved",
        data=[OrderService.serialize_order(o, include_items=True) for o in orders],
        meta={"page": page, "limit": limit, "total": total, "pages": total_pages},
        status_code=200,
    )


@order_bp.route("/<string:id_or_number>", methods=["GET"])
@jwt_required_custom
def get_order_detail(id_or_number: str):
    order = OrderRepository.get_by_id(id_or_number)
    if not order:
        order = OrderRepository.get_by_order_number(id_or_number)

    if not order or (order.user_id != g.current_user.id and g.current_user.role != "admin"):
        return api_response(success=False, message="Order not found", status_code=404)

    return api_response(
        success=True,
        message="Order retrieved",
        data=OrderService.serialize_order(order, include_items=True),
        status_code=200,
    )


@order_bp.route("/<string:order_id>/cancel", methods=["POST"])
@jwt_required_custom
def cancel_order(order_id: str):
    data = request.get_json() or {}
    reason = data.get("reason", "Customer requested cancellation")

    success, message, result = OrderService.cancel_order(
        order_id=order_id,
        user_id=g.current_user.id if g.current_user.role != "admin" else None,
        reason=reason,
    )
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@order_bp.route("/<string:order_id>/invoice", methods=["GET"])
@jwt_required_custom
def get_order_invoice(order_id: str):
    invoice = OrderService.get_order_invoice(
        order_id=order_id,
        user_id=g.current_user.id if g.current_user.role != "admin" else None,
    )
    if not invoice:
        return api_response(success=False, message="Invoice not found", status_code=404)
    return api_response(success=True, message="Invoice generated", data=invoice, status_code=200)
