from backend.app.models.base import db, TimestampMixin, generate_uuid
from backend.app.models.user import User, UserAddress, Notification
from backend.app.models.catalog import Category, Product, ProductImage, ProductAttribute
from backend.app.models.cart import Cart, CartItem, Wishlist, WishlistItem
from backend.app.models.order import (
    Order,
    OrderItem,
    Payment,
    InventoryTransaction,
    Coupon,
    CouponUsage,
)
from backend.app.models.review import ProductReview
from backend.app.models.recommendation import UserInteraction, ProductRecommendation

__all__ = [
    "db",
    "TimestampMixin",
    "generate_uuid",
    "User",
    "UserAddress",
    "Notification",
    "Category",
    "Product",
    "ProductImage",
    "ProductAttribute",
    "Cart",
    "CartItem",
    "Wishlist",
    "WishlistItem",
    "Order",
    "OrderItem",
    "Payment",
    "InventoryTransaction",
    "Coupon",
    "CouponUsage",
    "ProductReview",
    "UserInteraction",
    "ProductRecommendation",
]
