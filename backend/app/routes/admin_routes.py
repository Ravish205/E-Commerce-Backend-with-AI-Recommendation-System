from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.catalog_schema import ProductCreateSchema, ProductUpdateSchema, CategorySchema
from backend.app.schemas.order_schema import OrderStatusUpdateSchema
from backend.app.schemas.review_schema import ReviewModerateSchema
from backend.app.services.catalog_service import CatalogService, slugify
from backend.app.repositories.catalog_repo import CatalogRepository
from backend.app.repositories.order_repo import OrderRepository
from backend.app.repositories.review_repo import ReviewRepository
from backend.app.repositories.analytics_repo import AnalyticsRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.models.user import User
from backend.app.models.catalog import Product
from backend.app.models.order import Order
from backend.app.models.base import db
from backend.app.middleware.auth import admin_required
from backend.app.utils.response import api_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
category_schema = CategorySchema()
order_status_schema = OrderStatusUpdateSchema()
review_moderate_schema = ReviewModerateSchema()

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def get_dashboard_metrics():
    metrics = AnalyticsRepository.get_dashboard_metrics()
    return api_response(success=True, message="Dashboard metrics retrieved", data=metrics, status_code=200)


@admin_bp.route("/products", methods=["GET"])
@admin_required
def list_admin_products():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    search = request.args.get("search")

    products, total = CatalogRepository.query_products(
        page=page,
        limit=limit,
        search=search,
        active_only=False,  # Admins see active and inactive products
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return api_response(
        success=True,
        message="Products retrieved",
        data=[CatalogService.serialize_product(p, include_details=True) for p in products],
        meta={"page": page, "limit": limit, "total": total, "pages": total_pages},
        status_code=200,
    )


@admin_bp.route("/products", methods=["POST"])
@admin_required
def create_product():
    try:
        data = product_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = CatalogService.create_product(data)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=201)


@admin_bp.route("/products/<string:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id: str):
    try:
        data = product_update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = CatalogService.update_product(product_id, data)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@admin_bp.route("/products/<string:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id: str):
    success, message = CatalogService.delete_product(product_id)
    if not success:
        return api_response(success=False, message=message, status_code=404)
    return api_response(success=True, message=message, status_code=200)


# --- Category Management ---
@admin_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    try:
        data = category_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    slug = data.get("slug") or slugify(data["name"])
    if CatalogRepository.get_category_by_slug(slug):
        return api_response(success=False, message="A category with this slug already exists", status_code=400)

    category = CatalogRepository.create_category(
        name=data["name"],
        slug=slug,
        description=data.get("description"),
        image_url=data.get("image_url"),
        parent_id=data.get("parent_id"),
        sort_order=data.get("sort_order", 0),
    )
    return api_response(
        success=True,
        message="Category created successfully",
        data=CatalogService.serialize_category(category),
        status_code=201,
    )


# --- Order Management ---
@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_admin_orders():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    status = request.args.get("status")

    orders, total = OrderRepository.list_all_orders(status=status, page=page, limit=limit)
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return api_response(
        success=True,
        message="Orders retrieved",
        data=[
            {
                "id": o.id,
                "order_number": o.order_number,
                "customer_name": f"{o.user.first_name} {o.user.last_name}" if o.user else "Customer",
                "customer_email": o.user.email if o.user else "",
                "status": o.status,
                "total_amount": float(o.total_amount),
                "items_count": len(o.items),
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "tracking_number": o.tracking_number,
            }
            for o in orders
        ],
        meta={"page": page, "limit": limit, "total": total, "pages": total_pages},
        status_code=200,
    )


@admin_bp.route("/orders/<string:order_id>/status", methods=["PUT"])
@admin_required
def update_order_status(order_id: str):
    try:
        data = order_status_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    order = OrderRepository.get_by_id(order_id)
    if not order:
        return api_response(success=False, message="Order not found", status_code=404)

    OrderRepository.update_order_status(
        order=order,
        status=data["status"],
        tracking_number=data.get("tracking_number"),
        notes=data.get("notes"),
    )
    return api_response(success=True, message=f"Order status updated to '{data['status']}'", status_code=200)


# --- Inventory Management ---
@admin_bp.route("/inventory/adjust", methods=["POST"])
@admin_required
def adjust_inventory():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity_change = data.get("quantity_change")
    notes = data.get("notes")

    if not product_id or quantity_change is None or not notes:
        return api_response(
            success=False,
            message="product_id, quantity_change (integer), and notes (mandatory audit reason) are required",
            status_code=400,
        )

    product = CatalogRepository.get_product_by_id(product_id)
    if not product:
        return api_response(success=False, message="Product not found", status_code=404)

    new_stock = product.stock + int(quantity_change)
    if new_stock < 0:
        return api_response(
            success=False,
            message=f"Cannot reduce stock below 0 (current: {product.stock}, change: {quantity_change})",
            status_code=400,
        )

    product.stock = new_stock
    OrderRepository.log_inventory(
        product_id=product.id,
        change_quantity=int(quantity_change),
        balance_after=new_stock,
        transaction_type="manual_adjustment",
        notes=notes,
        created_by=g.current_user.id,
    )
    db.session.commit()

    return api_response(
        success=True,
        message=f"Inventory adjusted. New stock balance: {new_stock}",
        data={"product_id": product.id, "name": product.name, "stock": new_stock},
        status_code=200,
    )


# --- Review Moderation ---
@admin_bp.route("/reviews", methods=["GET"])
@admin_required
def list_admin_reviews():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    reviews, total = ReviewRepository.list_pending_moderation(page=page, limit=limit)
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return api_response(
        success=True,
        message="Reviews queue retrieved",
        data=[
            {
                "id": r.id,
                "product_id": r.product_id,
                "product_name": r.product.name if r.product else "",
                "user_name": f"{r.user.first_name} {r.user.last_name}" if r.user else "Customer",
                "rating": r.rating,
                "title": r.title,
                "comment": r.comment,
                "is_verified_purchase": r.is_verified_purchase,
                "is_approved": r.is_approved,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ],
        meta={"page": page, "limit": limit, "total": total, "pages": total_pages},
        status_code=200,
    )


@admin_bp.route("/reviews/<string:review_id>/status", methods=["PUT"])
@admin_required
def moderate_review(review_id: str):
    try:
        data = review_moderate_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    review = ReviewRepository.get_by_id(review_id)
    if not review:
        return api_response(success=False, message="Review not found", status_code=404)

    ReviewRepository.moderate_review(review, is_approved=data["is_approved"], admin_id=g.current_user.id)
    status_label = "approved" if data["is_approved"] else "rejected"
    return api_response(success=True, message=f"Review marked as {status_label}", status_code=200)


# --- Customer Management ---
@admin_bp.route("/customers", methods=["GET"])
@admin_required
def list_customers():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    query = User.query.filter_by(role="customer").order_by(User.created_at.desc())
    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return api_response(
        success=True,
        message="Customers retrieved",
        data=[
            {
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "phone_number": u.phone_number,
                "is_active": u.is_active,
                "orders_count": len(u.orders),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        meta={"page": page, "limit": limit, "total": total, "pages": total_pages},
        status_code=200,
    )
