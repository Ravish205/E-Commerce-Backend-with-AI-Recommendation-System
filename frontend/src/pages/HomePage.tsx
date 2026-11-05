import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Sparkles, TrendingUp, Cpu, Headphones, Smartphone, Watch, Camera } from "lucide-react";
import { catalogService } from "../services/catalogService";
import { recommendationService } from "../services/recommendationService";
import { Category, Product } from "../types";
import { RecommendationSection } from "../components/product/RecommendationSection";

export const HomePage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [personalized, setPersonalized] = useState<Product[]>([]);
  const [trending, setTrending] = useState<Product[]>([]);
  const [recentlyViewed, setRecentlyViewed] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHomeData() {
      try {
        const [cats, pers, trnd, rec] = await Promise.all([
          catalogService.getCategories(),
          recommendationService.getPersonalized(4),
          recommendationService.getTrending(4),
          recommendationService.getRecentlyViewed(4),
        ]);
        setCategories(cats);
        setPersonalized(pers);
        setTrending(trnd);
        setRecentlyViewed(rec);
      } catch (err) {
        console.error("Failed to load home data", err);
      } finally {
        setLoading(false);
      }
    }
    loadHomeData();
  }, []);

  const categoryIcons: Record<string, any> = {
    "audio-headphones": Headphones,
    "laptops-computing": Cpu,
    "smartphones-tablets": Smartphone,
    "smart-home-wearables": Watch,
    "photography-video": Camera,
  };

  return (
    <div className="space-y-12">
      {/* Hero Banner */}
      <section className="bg-white border border-[#E4E4E7] rounded-md p-8 md:p-12 relative overflow-hidden">
        <div className="max-w-2xl relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-[#ECFDF5] text-[#047857] text-xs font-semibold uppercase tracking-wider mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Guided Hardware Discovery</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-[#18181B] leading-tight mb-4">
            High performance tech curated for your workflow.
          </h1>
          <p className="text-base text-[#71717A] leading-relaxed mb-6">
            Explore authentic audio gear, creator workstations, smartphones, and wearable technologies with transparent pricing and real-time inventory.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/products"
              className="px-5 py-2.5 text-sm font-medium text-white bg-[#059669] hover:bg-[#047857] rounded-md transition-colors flex items-center gap-2"
            >
              <span>Explore Catalog</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/recommendations"
              className="px-5 py-2.5 text-sm font-medium text-[#18181B] bg-[#F9FAFB] hover:bg-[#F4F4F5] border border-[#E4E4E7] rounded-md transition-colors"
            >
              Personalized Recommendations
            </Link>
          </div>
        </div>
      </section>

      {/* Category Navigation Pills */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-[#18181B]">Browse by Category</h2>
          <Link to="/products" className="text-xs font-semibold text-[#059669] hover:underline">
            View all categories
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {categories.map((cat) => {
            const Icon = categoryIcons[cat.slug] || Cpu;
            return (
              <Link
                key={cat.id}
                to={`/products?category_slug=${cat.slug}`}
                className="bg-white border border-[#E4E4E7] rounded-md p-4 flex flex-col items-center text-center hover:border-[#059669] hover:shadow-sm transition-all group"
              >
                <div className="w-10 h-10 rounded bg-[#F9FAFB] flex items-center justify-center text-[#71717A] group-hover:text-[#059669] mb-2 transition-colors">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-xs font-semibold text-[#18181B] group-hover:text-[#059669] transition-colors">
                  {cat.name}
                </h3>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Recommended For You Section */}
      <RecommendationSection
        title="Recommended For You"
        subtitle="Personalized matching based on your recent activity and preferences"
        products={personalized}
        viewAllLink="/recommendations"
      />

      {/* Trending Products */}
      <RecommendationSection
        title="Trending Devices"
        subtitle="Top performing products across views, carts, and verified reviews"
        products={trending}
        viewAllLink="/products?sort_by=popularity"
      />

      {/* Recently Viewed */}
      {recentlyViewed.length > 0 && (
        <RecommendationSection
          title="Recently Viewed Products"
          subtitle="Quickly return to items you inspected in recent sessions"
          products={recentlyViewed}
        />
      )}
    </div>
  );
};

