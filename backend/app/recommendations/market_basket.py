from typing import List, Tuple, Dict
from collections import defaultdict
from backend.app.models.order import OrderItem, Order

class MarketBasketRecommender:
    """Co-occurrence mining for frequently bought together products."""

    @staticmethod
    def get_frequently_bought_together(target_product_id: str, order_items: List[OrderItem], top_k: int = 4) -> List[Tuple[str, float]]:
        # Group product IDs by order_id
        order_baskets = defaultdict(set)
        for item in order_items:
            order_baskets[item.order_id].add(item.product_id)

        target_baskets = 0
        co_counts = defaultdict(int)

        for basket in order_baskets.values():
            if target_product_id in basket:
                target_baskets += 1
                for other_id in basket:
                    if other_id != target_product_id:
                        co_counts[other_id] += 1

        if target_baskets == 0:
            return []

        # Association lift / conditional probability: P(other | target) = count(target & other) / count(target)
        results = []
        for other_id, count in co_counts.items():
            prob = round(count / target_baskets, 4)
            results.append((other_id, prob))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
