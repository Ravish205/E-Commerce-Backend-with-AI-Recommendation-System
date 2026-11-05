from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload
from backend.app.models.base import db
from backend.app.models.catalog import Product, Category
from backend.app.models.recommendation import UserInteraction
from backend.app.models.order import Order, OrderItem
from backend.app.models.cart import Cart, CartItem
from backend.app.recommendations.content_based import ContentBasedRecommender
from backend.app.recommendations.collaborative import CollaborativeFilteringRecommender
from backend.app.recommendations.market_basket import MarketBasketRecommender
from backend.app.services.catalog_service import CatalogService

class RecommendationEngine:
    """Unified AI Recommendation Engine combining Content-Based, Collaborative, Basket, and Popularity signals."""

    @staticmethod
    def _format_product_with_reason(product: Product, score: float, reason: str) -> Dict[str, Any]:
        data = CatalogService.serialize_product(product, include_details=False)
        data["recommendation_score"] = round(float(score), 4)
        data["recommendation_reason"] = reason
        return data

    @staticmethod
    def get_similar(product_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        """Content-Based similarity for a given product."""
        target_product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not target_product:
            return []

        all_products = (
            Product.query.options(
                joinedload(Product.images),
                joinedload(Product.attributes),
                joinedload(Product.category),
            )
            .filter(Product.is_active == True, Product.stock > 0)
            .all()
        )

        similar_pairs = ContentBasedRecommender.compute_similarity(all_products, product_id, top_k=limit * 2)
        prod_map = {p.id: p for p in all_products}

        results = []
        for pid, score in similar_pairs:
            p = prod_map.get(pid)
            if p and p.stock > 0:
                reason = f"Similar features & category to '{target_product.name}'"
                results.append(RecommendationEngine._format_product_with_reason(p, score, reason))
            if len(results) >= limit:
                break

        # Fallback to category products if similarity results are sparse
        if len(results) < limit:
            category_fallbacks = (
                Product.query.filter(
                    Product.category_id == target_product.category_id,
                    Product.id != target_product.id,
                    Product.is_active == True,
                    Product.stock > 0,
                )
                .order_by(desc(Product.average_rating), desc(Product.reviews_count))
                .limit(limit - len(results))
                .all()
            )
            for fb in category_fallbacks:
                if not any(r["id"] == fb.id for r in results):
                    results.append(
                        RecommendationEngine._format_product_with_reason(
                            fb, 0.5, f"Popular in {target_product.category.name if target_product.category else 'this category'}"
                        )
                    )

        return results

    @staticmethod
    def get_trending(limit: int = 8) -> List[Dict[str, Any]]:
        """Bayesian-weighted trending products based on recent interactions and ratings."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Aggregate recent interactions
        trending_query = (
            db.session.query(
                Product,
                func.coalesce(func.count(UserInteraction.id), 0).label("interaction_count"),
            )
            .outerjoin(
                UserInteraction,
                (UserInteraction.product_id == Product.id) & (UserInteraction.created_at >= cutoff),
            )
            .filter(Product.is_active == True, Product.stock > 0)
            .group_by(Product.id)
            .order_by(
                desc("interaction_count"),
                desc(Product.average_rating),
                desc(Product.reviews_count),
                desc(Product.created_at),
            )
            .limit(limit)
            .all()
        )

        results = []
        for p, count in trending_query:
            reason = "High popularity and shopper interest"
            score = 1.0 + (int(count) * 0.1) + float(p.average_rating or 0)
            results.append(RecommendationEngine._format_product_with_reason(p, score, reason))

        return results

    @staticmethod
    def get_frequently_bought_together(product_id: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Frequently bought together recommendations based on completed basket co-occurrences."""
        target_product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not target_product:
            return []

        # Find orders that contained target_product
        order_ids_query = (
            db.session.query(OrderItem.order_id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                OrderItem.product_id == product_id,
                Order.status.in_(["confirmed", "processing", "shipped", "delivered"]),
            )
            .distinct()
            .all()
        )
        order_ids = [r[0] for r in order_ids_query]

        if not order_ids:
            # Fallback to category accessories / similar items
            return RecommendationEngine.get_similar(product_id, limit=limit)

        co_order_items = (
            OrderItem.query.filter(
                OrderItem.order_id.in_(order_ids),
                OrderItem.product_id != product_id,
            ).all()
        )

        basket_pairs = MarketBasketRecommender.get_frequently_bought_together(product_id, co_order_items, top_k=limit)
        if not basket_pairs:
            return RecommendationEngine.get_similar(product_id, limit=limit)

        pair_map = {pid: score for pid, score in basket_pairs}
        products = Product.query.filter(Product.id.in_(list(pair_map.keys())), Product.is_active == True, Product.stock > 0).all()

        results = []
        for p in products:
            score = pair_map.get(p.id, 0.5)
            reason = f"Frequently purchased together with '{target_product.name}'"
            results.append(RecommendationEngine._format_product_with_reason(p, score, reason))

        return results

    @staticmethod
    def get_recently_viewed(user_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 6) -> List[Dict[str, Any]]:
        """List recently viewed products for the current user or session."""
        if not user_id and not session_id:
            return []

        query = UserInteraction.query.filter(UserInteraction.interaction_type == "view")
        if user_id:
            query = query.filter(UserInteraction.user_id == user_id)
        else:
            query = query.filter(UserInteraction.session_id == session_id)

        recent_events = query.order_by(desc(UserInteraction.created_at)).limit(30).all()
        seen_pids = set()
        unique_pids = []
        for ev in recent_events:
            if ev.product_id not in seen_pids:
                seen_pids.add(ev.product_id)
                unique_pids.append(ev.product_id)
            if len(unique_pids) >= limit:
                break

        if not unique_pids:
            return []

        products = Product.query.filter(Product.id.in_(unique_pids), Product.is_active == True).all()
        prod_map = {p.id: p for p in products}

        results = []
        for pid in unique_pids:
            p = prod_map.get(pid)
            if p:
                results.append(RecommendationEngine._format_product_with_reason(p, 1.0, "Recently viewed by you"))

        return results

    @staticmethod
    def get_based_on_purchases(user_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        """Recommendations derived from categories and brands the user has previously bought."""
        purchased_items = (
            db.session.query(OrderItem)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                Order.user_id == user_id,
                Order.status.in_(["confirmed", "processing", "shipped", "delivered"]),
            )
            .all()
        )

        if not purchased_items:
            return RecommendationEngine.get_trending(limit=limit)

        purchased_product_ids = {item.product_id for item in purchased_items}
        categories = {item.product.category_id for item in purchased_items if item.product and item.product.category_id}
        brands = {item.product.brand for item in purchased_items if item.product and item.product.brand}

        candidates = (
            Product.query.filter(
                Product.is_active == True,
                Product.stock > 0,
                ~Product.id.in_(purchased_product_ids),
                (Product.category_id.in_(categories) | Product.brand.in_(brands)),
            )
            .order_by(desc(Product.average_rating), desc(Product.reviews_count))
            .limit(limit)
            .all()
        )

        results = []
        for p in candidates:
            reason = f"Because you purchased products in {p.category.name if p.category else p.brand}"
            results.append(RecommendationEngine._format_product_with_reason(p, 0.85, reason))

        if len(results) < limit:
            trending = RecommendationEngine.get_trending(limit=limit - len(results))
            for t in trending:
                if not any(r["id"] == t["id"] for r in results):
                    results.append(t)

        return results

    @staticmethod
    def get_personalized(user_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 8) -> List[Dict[str, Any]]:
        """Hybrid Recommendation Engine with dynamic weight adaptation and cold-start handling."""
        entity_id = user_id or session_id
        if not entity_id:
            return RecommendationEngine.get_trending(limit=limit)

        # 1. Fetch user's interactions
        user_interactions_q = UserInteraction.query
        if user_id:
            user_interactions_q = user_interactions_q.filter(UserInteraction.user_id == user_id)
        else:
            user_interactions_q = user_interactions_q.filter(UserInteraction.session_id == session_id)
        user_interactions = user_interactions_q.all()

        interaction_count = len(user_interactions)

        # Cold-Start Check: 0 interactions -> Pure Trending / Bayesian Popularity
        if interaction_count == 0:
            return RecommendationEngine.get_trending(limit=limit)

        # 2. Retrieve catalog of candidate active products
        all_active_products = (
            Product.query.options(
                joinedload(Product.images),
                joinedload(Product.attributes),
                joinedload(Product.category),
            )
            .filter(Product.is_active == True, Product.stock > 0)
            .all()
        )
        catalog_ids = [p.id for p in all_active_products]
        prod_map = {p.id: p for p in all_active_products}

        # 3. Exclude already purchased products and active cart items
        excluded_ids = set()
        if user_id:
            purchased_q = (
                db.session.query(OrderItem.product_id)
                .join(Order, Order.id == OrderItem.order_id)
                .filter(
                    Order.user_id == user_id,
                    Order.status.in_(["confirmed", "processing", "shipped", "delivered"]),
                )
                .distinct()
                .all()
            )
            for r in purchased_q:
                excluded_ids.add(r[0])

            cart = Cart.query.filter_by(user_id=user_id).first()
            if cart:
                for item in cart.items:
                    excluded_ids.add(item.product_id)

        # 4. Content-Based recommendations from recently interacted items
        last_viewed_product_ids = [
            ev.product_id for ev in reversed(user_interactions)
            if ev.product_id in prod_map
        ][:3]

        cb_scores = {}
        for source_pid in last_viewed_product_ids:
            similar = ContentBasedRecommender.compute_similarity(all_active_products, source_pid, top_k=limit)
            for pid, sim_score in similar:
                if pid not in excluded_ids:
                    cb_scores[pid] = max(cb_scores.get(pid, 0.0), sim_score)

        # 5. Collaborative Filtering recommendations
        all_system_interactions = UserInteraction.query.order_by(desc(UserInteraction.created_at)).limit(5000).all()
        cf_results = CollaborativeFilteringRecommender.get_collaborative_recommendations(
            interactions=all_system_interactions,
            target_entity_id=entity_id,
            catalog_product_ids=catalog_ids,
            top_k=limit,
        )
        cf_scores = {pid: score for pid, score in cf_results if pid not in excluded_ids}

        # 6. Dynamic Weights Formulation
        if interaction_count > 5:
            w_cf, w_cb, w_pop = 0.50, 0.40, 0.10
        else:
            w_cf, w_cb, w_pop = 0.20, 0.60, 0.20

        # 7. Fuse scores
        candidate_ids = set(cb_scores.keys()) | set(cf_scores.keys())
        fused_candidates = []

        for pid in candidate_ids:
            p = prod_map.get(pid)
            if not p or p.stock <= 0:
                continue

            cf_val = cf_scores.get(pid, 0.0)
            cb_val = cb_scores.get(pid, 0.0)
            pop_val = min(1.0, (float(p.average_rating or 0) / 5.0) * 0.7 + (min(p.reviews_count, 50) / 50.0) * 0.3)

            final_score = (w_cf * cf_val) + (w_cb * cb_val) + (w_pop * pop_val)

            # Determine explainability reason
            if cb_val > cf_val and last_viewed_product_ids:
                source_name = prod_map[last_viewed_product_ids[0]].name
                reason = f"Because you showed interest in '{source_name}'"
            elif cf_val > 0.1:
                reason = "Shoppers with similar browsing preferences also loved this"
            else:
                reason = f"Highly rated in {p.category.name if p.category else 'our store'}"

            fused_candidates.append((p, final_score, reason))

        # Sort descending by fused score
        fused_candidates.sort(key=lambda x: x[1], reverse=True)

        results = []
        for p, score, reason in fused_candidates[:limit]:
            results.append(RecommendationEngine._format_product_with_reason(p, score, reason))

        # Fallback to trending if candidates were insufficient
        if len(results) < limit:
            trending = RecommendationEngine.get_trending(limit=limit)
            for t in trending:
                if not any(r["id"] == t["id"] for r in results) and t["id"] not in excluded_ids:
                    results.append(t)
                if len(results) >= limit:
                    break

        return results
