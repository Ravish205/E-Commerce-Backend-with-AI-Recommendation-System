import React, { useEffect, useState } from "react";
import { Sparkles, Brain, Cpu, Flame, History, Info } from "lucide-react";
import { recommendationService } from "../services/recommendationService";
import { Product } from "../types";
import { ProductCard } from "../components/product/ProductCard";

export const RecommendationsPage: React.FC = () => {
  const [personalized, setPersonalized] = useState<Product[]>([]);
  const [purchaseBased, setPurchaseBased] = useState<Product[]>([]);
  const [trending, setTrending] = useState<Product[]>([]);
  const [recentlyViewed, setRecentlyViewed] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAllRecommendations() {
      setLoading(true);
      try {
        const [pers, pur, trn, rec] = await Promise.all([
          recommendationService.getPersonalized(8),
          recommendationService.getPurchaseHistoryRecommendations(6),
          recommendationService.getTrending(6),
          recommendationService.getRecentlyViewed(6),
        ]);
        setPersonalized(pers);
        setPurchaseBased(pur);
        setTrending(trn);
        setRecentlyViewed(rec);
      } catch (err) {
        console.error("Failed to load recommendations", err);
      } finally {
        setLoading(false);
      }
    }
    loadAllRecommendations();
  }, []);

  return (
    <div className="space-y-12">
      {/* Header and Explanation */}
      <div className="bg-white border border-[#E4E4E7] rounded-md p-6 md:p-8 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-[#ECFDF5] text-[#047857] text-xs font-semibold uppercase tracking-wider">
          <Brain className="w-4 h-4" />
          <span>Hybrid Recommendation Architecture</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-[#18181B]">
          AI-Powered Product Recommendations
        </h1>
        <p className="text-sm text-[#71717A] max-w-3xl leading-relaxed">
          Our recommendation engine computes personalized affinities using natural language TF-IDF vectorization, item-item collaborative filtering interaction matrices, and purchase basket co-occurrence. Every recommendation is scored in real time with cold-start fallbacks and out-of-stock exclusions.
        </p>

        {/* Algorithm Weights Box */}
        <div className="p-4 bg-[#F9FAFB] rounded border border-[#E4E4E7] flex flex-wrap items-center gap-6 text-xs text-[#71717A]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#059669]" />
            <span className="font-semibold text-[#18181B]">Content-Based (TF-IDF):</span> 40%
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
            <span className="font-semibold text-[#18181B]">Collaborative Filtering:</span> 50%
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#D97706]" />
            <span className="font-semibold text-[#18181B]">Bayesian Velocity/Popularity:</span> 10%
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-sm text-[#71717A]">
          Computing personalized similarity scores...
        </div>
      ) : (
        <div className="space-y-12">
          {/* Section 1: Personalized For You */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-[#059669]" />
              <h2 className="text-xl font-bold text-[#18181B]">Recommended For You</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
              {personalized.map((p) => (
                <ProductCard key={p.id} product={p} showReason={true} />
              ))}
            </div>
          </section>

          {/* Section 2: Based on Your Purchase History */}
          {purchaseBased.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <History className="w-5 h-5 text-[#059669]" />
                <h2 className="text-xl font-bold text-[#18181B]">Based on Your Past Purchases</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
                {purchaseBased.map((p) => (
                  <ProductCard key={p.id} product={p} showReason={true} />
                ))}
              </div>
            </section>
          )}

          {/* Section 3: Trending Products */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Flame className="w-5 h-5 text-[#D97706]" />
              <h2 className="text-xl font-bold text-[#18181B]">Trending Across Shoppers</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
              {trending.map((p) => (
                <ProductCard key={p.id} product={p} showReason={true} />
              ))}
            </div>
          </section>

          {/* Section 4: Recently Viewed */}
          {recentlyViewed.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Cpu className="w-5 h-5 text-[#059669]" />
                <h2 className="text-xl font-bold text-[#18181B]">Recently Inspected Hardware</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
                {recentlyViewed.map((p) => (
                  <ProductCard key={p.id} product={p} showReason={true} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
};

