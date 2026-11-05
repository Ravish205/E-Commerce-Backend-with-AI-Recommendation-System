from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.cart_schema import CartItemAddSchema, CartItemUpdateSchema, ApplyCouponSchema
from backend.app.services.cart_service import CartService
from backend.app.repositories.cart_repo import CartRepository
from backend.app.middleware.auth import optional_jwt, jwt_required_custom
from backend.app.utils.response import api_response

cart_bp = Blueprint("cart", __name__, url_prefix="/api")

add_item_schema = CartItemAddSchema()
update_item_schema = CartItemUpdateSchema()
coupon_schema = ApplyCouponSchema()

def get_auth_identifiers():
    user_id = g.current_user.id if hasattr(g, "current_user") and g.current_user else None
    session_token = request.headers.get("X-Session-Token") or request.cookies.get("session_token")
    return user_id, session_token


@cart_bp.route("/cart", methods=["GET"])
@optional_jwt
def get_cart():
    user_id, session_token = get_auth_identifiers()
    coupon_code = request.args.get("coupon_code")
    cart_summary = CartService.get_cart(user_id=user_id, session_token=session_token, coupon_code=coupon_code)
    return api_response(success=True, message="Cart retrieved", data=cart_summary, status_code=200)


@cart_bp.route("/cart/items", methods=["POST"])
@optional_jwt
def add_to_cart():
    try:
        data = add_item_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    user_id, session_token = get_auth_identifiers()
    success, message, result = CartService.add_to_cart(
        product_id=data["product_id"],
        quantity=data.get("quantity", 1),
        user_id=user_id,
        session_token=session_token,
    )

    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@cart_bp.route("/cart/items/<string:item_id>", methods=["PUT"])
@optional_jwt
def update_cart_item(item_id: str):
    try:
        data = update_item_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    success, message, result = CartService.update_cart_item_quantity(item_id=item_id, quantity=data["quantity"])
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message=message, data=result, status_code=200)


@cart_bp.route("/cart/items/<string:item_id>", methods=["DELETE"])
@optional_jwt
def remove_cart_item(item_id: str):
    success, message, result = CartService.remove_cart_item(item_id=item_id)
    if not success:
        return api_response(success=False, message=message, status_code=404)
    return api_response(success=True, message=message, data=result, status_code=200)


@cart_bp.route("/cart", methods=["DELETE"])
@optional_jwt
def clear_cart():
    user_id, session_token = get_auth_identifiers()
    CartService.clear_cart(user_id=user_id, session_token=session_token)
    return api_response(success=True, message="Cart cleared", status_code=200)


# --- Wishlist Routes ---
@cart_bp.route("/wishlist", methods=["GET"])
@jwt_required_custom
def get_wishlist():
    wishlist = CartRepository.get_or_create_wishlist(g.current_user.id)
    items = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "name": item.product.name,
            "slug": item.product.slug,
            "sku": item.product.sku,
            "brand": item.product.brand,
            "price": float(item.product.price),
            "discount_price": float(item.product.discount_price) if item.product.discount_price else None,
            "effective_price": item.product.effective_price,
            "is_in_stock": item.product.stock > 0,
            "primary_image": item.product.primary_image,
        }
        for item in wishlist.items
        if item.product and item.product.is_active
    ]
    return api_response(success=True, message="Wishlist retrieved", data={"items": items}, status_code=200)


@cart_bp.route("/wishlist/<string:product_id>", methods=["POST"])
@jwt_required_custom
def add_to_wishlist(product_id: str):
    wishlist = CartRepository.get_or_create_wishlist(g.current_user.id)
    CartRepository.add_to_wishlist(wishlist.id, product_id)
    return api_response(success=True, message="Product added to wishlist", status_code=200)


@cart_bp.route("/wishlist/<string:product_id>", methods=["DELETE"])
@jwt_required_custom
def remove_from_wishlist(product_id: str):
    wishlist = CartRepository.get_or_create_wishlist(g.current_user.id)
    CartRepository.remove_from_wishlist(wishlist.id, product_id)
    return api_response(success=True, message="Product removed from wishlist", status_code=200)


@cart_bp.route("/wishlist/<string:product_id>/move-to-cart", methods=["POST"])
@jwt_required_custom
def move_wishlist_to_cart(product_id: str):
    wishlist = CartRepository.get_or_create_wishlist(g.current_user.id)
    CartRepository.remove_from_wishlist(wishlist.id, product_id)
    success, message, result = CartService.add_to_cart(product_id=product_id, quantity=1, user_id=g.current_user.id)
    if not success:
        return api_response(success=False, message=message, status_code=400)
    return api_response(success=True, message="Item moved from wishlist to cart", data=result, status_code=200)
