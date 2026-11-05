from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from backend.app.models.base import db
from backend.app.models.review import ProductReview
from backend.app.models.order import Order, OrderItem
from backend.app.models.catalog import Product

class ReviewRepository:
    @staticmethod
    def list_for_product(product_id: str, page: int = 1, limit: int = 10, approved_only: bool = True) -> Tuple[List[ProductReview], int]:
        query = ProductReview.query.options(
            joinedload(ProductReview.user)
        ).filter(ProductReview.product_id == product_id)
        if approved_only:
            query = query.filter(ProductReview.is_approved == True)
        query = query.order_by(desc(ProductReview.created_at))
        total = query.count()
        reviews = query.offset((page - 1) * limit).limit(limit).all()
        return reviews, total

    @staticmethod
    def list_pending_moderation(page: int = 1, limit: int = 20) -> Tuple[List[ProductReview], int]:
        query = ProductReview.query.options(
            joinedload(ProductReview.user),
            joinedload(ProductReview.product),
        ).order_by(desc(ProductReview.created_at))
        total = query.count()
        reviews = query.offset((page - 1) * limit).limit(limit).all()
        return reviews, total

    @staticmethod
    def get_by_id(review_id: str) -> Optional[ProductReview]:
        return ProductReview.query.filter_by(id=review_id).first()

    @staticmethod
    def verify_purchase(user_id: str, product_id: str) -> Optional[str]:
        """Check if user completed a purchase for this product. Returns order_id if verified."""
        order = (
            db.session.query(Order)
            .join(OrderItem, OrderItem.order_id == Order.id)
            .filter(
                Order.user_id == user_id,
                OrderItem.product_id == product_id,
                Order.status.in_(["delivered", "confirmed", "processing", "shipped"]),
            )
            .first()
        )
        return order.id if order else None

    @staticmethod
    def create_review(
        product_id: str,
        user_id: str,
        rating: int,
        title: str,
        comment: str,
        order_id: Optional[str] = None,
        is_verified_purchase: bool = False,
    ) -> ProductReview:
        review = ProductReview(
            product_id=product_id,
            user_id=user_id,
            order_id=order_id,
            rating=rating,
            title=title.strip(),
            comment=comment.strip(),
            is_verified_purchase=is_verified_purchase,
            is_approved=True,  # Default auto-approved, subject to admin moderation
        )
        db.session.add(review)
        db.session.commit()
        ReviewRepository.recalculate_product_ratings(product_id)
        return review

    @staticmethod
    def moderate_review(review: ProductReview, is_approved: bool, admin_id: str) -> ProductReview:
        review.is_approved = is_approved
        review.moderated_by = admin_id
        review.moderated_at = datetime.now(timezone.utc)
        db.session.commit()
        ReviewRepository.recalculate_product_ratings(review.product_id)
        return review

    @staticmethod
    def recalculate_product_ratings(product_id: str) -> None:
        """Update average_rating and reviews_count based on approved reviews."""
        stats = (
            db.session.query(
                func.coalesce(func.avg(ProductReview.rating), 0.0),
                func.count(ProductReview.id),
            )
            .filter(
                ProductReview.product_id == product_id,
                ProductReview.is_approved == True,
            )
            .first()
        )
        avg_rating = round(float(stats[0]), 2)
        count = int(stats[1])

        Product.query.filter_by(id=product_id).update({
            "average_rating": avg_rating,
            "reviews_count": count,
        })
        db.session.commit()
