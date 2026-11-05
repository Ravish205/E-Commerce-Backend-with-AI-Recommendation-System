import React from "react";
import { Link } from "react-router-dom";
import { Sparkles, ArrowRight } from "lucide-react";
import { Product } from "../../types";
import { ProductCard } from "./ProductCard";

interface RecommendationSectionProps {
  title: string;
  subtitle?: string;
  products: Product[];
  viewAllLink?: string;
}

export const RecommendationSection: React.FC<RecommendationSectionProps> = ({
  title,
  subtitle,
  products,
  viewAllLink,
}) => {
  if (!products || products.length === 0) return null;

  return (
    <section className="my-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-[#059669] text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Powered Discovery</span>
          </div>
          <h2 className="text-xl font-bold text-[#18181B] tracking-tight">{title}</h2>
          {subtitle && <p className="text-sm text-[#71717A] mt-0.5">{subtitle}</p>}
        </div>

        {viewAllLink && (
          <Link
            to={viewAllLink}
            className="flex items-center gap-1 text-sm font-semibold text-[#059669] hover:text-[#047857] transition-colors"
          >
            <span>View all</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
};

