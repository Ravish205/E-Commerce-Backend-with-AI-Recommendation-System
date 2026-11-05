from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.review_schema import ReviewCreateSchema
from backend.app.repositories.review_repo import ReviewRepository
from backend.app.repositories.catalog_repo import CatalogRepository
from backend.app.middleware.auth import jwt_required_custom
from backend.app.utils.response import api_response

review_bp = Blueprint("reviews", __name__, url_prefix="/api")

review_schema = ReviewCreateSchema()

@review_bp.route("/products/<string:product_id>/reviews", methods=["GET"])
def get_product_reviews(product_id: str):
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    reviews, total = ReviewRepository.list_for_product(product_id, page=page, limit=limit, approved_only=True)
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    data = [
        {
            "id": r.id,
            "product_id": r.product_id,
            "user_name": f"{r.user.first_name} {r.user.last_name[0]}." if r.user else "Customer",
            "rating": r.rating,
            "title": r.title,
            "comment": r.comment,
            "is_verified_purchase": r.is_verified_purchase,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]

    return api_response(
        success=True,
        message="Reviews retrieved",
        data=data,
        meta={"page": page, "limit": limit, "total": total, "pages": total_pages},
        status_code=200,
    )


@review_bp.route("/reviews", methods=["POST"])
@jwt_required_custom
def create_review():
    try:
        data = review_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    product = CatalogRepository.get_product_by_id(data["product_id"])
    if not product:
        return api_response(success=False, message="Product not found", status_code=404)

    # Check verified purchase
    verified_order_id = ReviewRepository.verify_purchase(g.current_user.id, data["product_id"])
    is_verified = bool(verified_order_id)

    review = ReviewRepository.create_review(
        product_id=data["product_id"],
        user_id=g.current_user.id,
        order_id=verified_order_id,
        rating=data["rating"],
        title=data["title"],
        comment=data["comment"],
        is_verified_purchase=is_verified,
    )

    return api_response(
        success=True,
        message="Review submitted successfully",
        data={
            "id": review.id,
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "is_verified_purchase": review.is_verified_purchase,
        },
        status_code=201,
    )
