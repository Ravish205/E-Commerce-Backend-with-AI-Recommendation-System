import re
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.models.catalog import Product

class ContentBasedRecommender:
    """Content-Based Filtering using TF-IDF vectorization and cosine similarity."""

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    @staticmethod
    def _build_corpus(products: List[Product]) -> Tuple[List[str], List[str]]:
        """Constructs weighted textual document representation for each product."""
        corpus = []
        product_ids = []

        for p in products:
            clean_name = ContentBasedRecommender._clean_text(p.name)
            clean_category = ContentBasedRecommender._clean_text(p.category.name if p.category else "")
            clean_brand = ContentBasedRecommender._clean_text(p.brand)
            clean_desc = ContentBasedRecommender._clean_text(p.description)
            
            # Attributes weighting
            attrs = " ".join([ContentBasedRecommender._clean_text(f"{a.attribute_name} {a.attribute_value}") for a in p.attributes])

            # Weighted combination: Title x3, Category x2, Brand x2, Attributes x1.5, Description x1
            doc = f"{clean_name} {clean_name} {clean_name} {clean_category} {clean_category} {clean_brand} {clean_brand} {attrs} {attrs} {clean_desc}"
            corpus.append(doc)
            product_ids.append(p.id)

        return corpus, product_ids

    @staticmethod
    def compute_similarity(products: List[Product], target_product_id: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Computes top-k similar products for a target product based on content."""
        if not products:
            return []

        corpus, product_ids = ContentBasedRecommender._build_corpus(products)
        if target_product_id not in product_ids:
            return []

        target_idx = product_ids.index(target_product_id)

        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform(corpus)
            similarity_scores = cosine_similarity(tfidf_matrix[target_idx], tfidf_matrix).flatten()
        except Exception:
            return []

        # Sort indices in descending order
        ranked_indices = np.argsort(similarity_scores)[::-1]

        results = []
        for idx in ranked_indices:
            pid = product_ids[idx]
            if pid != target_product_id:
                score = float(similarity_scores[idx])
                if score > 0.05:  # Relevance threshold
                    results.append((pid, score))
            if len(results) >= top_k:
                break

        return results
