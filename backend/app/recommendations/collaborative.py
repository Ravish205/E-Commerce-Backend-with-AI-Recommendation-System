from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.models.recommendation import UserInteraction

INTERACTION_WEIGHTS = {
    "view": 1.0,
    "search_click": 1.5,
    "wishlist_add": 3.0,
    "cart_add": 5.0,
    "purchase": 10.0,
    "review": 6.0,
}

class CollaborativeFilteringRecommender:
    """Item-Item Collaborative Filtering based on implicit & explicit user interaction feedback."""

    @staticmethod
    def compute_interaction_scores(interactions: List[UserInteraction]) -> pd.DataFrame:
        if not interactions:
            return pd.DataFrame(columns=["entity_id", "product_id", "score"])

        rows = []
        now = datetime.now(timezone.utc)

        for event in interactions:
            entity_id = event.user_id or event.session_id
            if not entity_id or not event.product_id:
                continue

            base_weight = INTERACTION_WEIGHTS.get(event.interaction_type, 1.0)

            # Apply exponential time decay: 0.95^(days_elapsed)
            days_elapsed = 0
            if event.created_at:
                diff = (now - event.created_at).total_seconds() / 86400.0
                days_elapsed = max(0.0, diff)
            time_decay = 0.95 ** days_elapsed
            score = base_weight * time_decay

            rows.append({
                "entity_id": entity_id,
                "product_id": event.product_id,
                "score": score,
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        # Aggregate total score per user-product pair
        aggregated = df.groupby(["entity_id", "product_id"])["score"].sum().reset_index()
        return aggregated

    @staticmethod
    def get_collaborative_recommendations(
        interactions: List[UserInteraction],
        target_entity_id: str,
        catalog_product_ids: List[str],
        top_k: int = 10,
    ) -> List[Tuple[str, float]]:
        """Calculates item-item collaborative scores for a given user or session."""
        df = CollaborativeFilteringRecommender.compute_interaction_scores(interactions)
        if df.empty or target_entity_id not in df["entity_id"].values:
            return []

        # Create User-Item matrix
        pivot = df.pivot(index="entity_id", columns="product_id", values="score").fillna(0.0)

        # Transpose to get Item-User matrix for Item-Item similarity
        item_matrix = pivot.T
        if item_matrix.shape[0] < 2:
            return []

        # Compute Item-Item Cosine Similarity
        try:
            item_similarity = cosine_similarity(item_matrix)
            item_sim_df = pd.DataFrame(
                item_similarity,
                index=item_matrix.index,
                columns=item_matrix.index,
            )
        except Exception:
            return []

        # Target user's interaction profile
        user_vector = pivot.loc[target_entity_id]
        interacted_items = user_vector[user_vector > 0].index.tolist()

        if not interacted_items:
            return []

        # Calculate predicted score for each unobserved product:
        # Score(j) = sum(similarity(i, j) * user_score(i)) / sum(|similarity(i, j)|)
        scores = {}
        for target_prod in catalog_product_ids:
            if target_prod in interacted_items or target_prod not in item_sim_df.index:
                continue

            sim_slice = item_sim_df.loc[target_prod, interacted_items]
            ratings_slice = user_vector[interacted_items]

            sim_sum = np.sum(np.abs(sim_slice.values))
            if sim_sum > 0:
                pred_score = np.dot(sim_slice.values, ratings_slice.values) / sim_sum
                if pred_score > 0.01:
                    scores[target_prod] = float(pred_score)

        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_k]
