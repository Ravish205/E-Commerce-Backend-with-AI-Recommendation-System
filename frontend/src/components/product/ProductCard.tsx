import React from "react";
import { Link } from "react-router-dom";
import { Star, Heart, ShoppingCart, Sparkles } from "lucide-react";
import { Product } from "../../types";
import { useCart } from "../../context/CartContext";

interface ProductCardProps {
  product: Product;
  showReason?: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, showReason = true }) => {
  const { addToCart, toggleWishlist, isInWishlist } = useCart();
  const isWishlisted = isInWishlist(product.id);

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="group bg-white border border-[#E4E4E7] rounded-md overflow-hidden flex flex-col justify-between hover:border-[#059669] transition-all duration-200">
      <div>
        {/* Product Image & Wishlist Button */}
        <div className="relative aspect-square bg-[#F9FAFB] overflow-hidden">
          <Link to={`/products/${product.slug || product.id}`}>
            <img
              src={product.primary_image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80"}
              alt={product.name}
              className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          </Link>
          <button
            onClick={() => toggleWishlist(product)}
            className={`absolute top-2.5 right-2.5 p-2 rounded-md bg-white/90 backdrop-blur-sm border border-[#E4E4E7] transition-colors ${
              isWishlisted ? "text-[#DC2626]" : "text-[#71717A] hover:text-[#18181B]"
            }`}
            title={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
          >
            <Heart className={`w-4 h-4 ${isWishlisted ? "fill-current" : ""}`} />
          </button>

          {/* AI Recommendation Reason Tag */}
          {showReason && product.recommendation_reason && (
            <div className="absolute bottom-2 left-2 right-2 bg-white/95 border border-[#ECFDF5] text-[#047857] text-[11px] font-medium px-2 py-1 rounded shadow-sm flex items-center gap-1.5 truncate">
              <Sparkles className="w-3 h-3 text-[#059669] flex-shrink-0" />
              <span className="truncate">{product.recommendation_reason}</span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="p-4">
          <p className="text-xs font-semibold text-[#71717A] tracking-wider uppercase mb-1">
            {product.brand}
          </p>
          <Link to={`/products/${product.slug || product.id}`}>
            <h3 className="text-sm font-semibold text-[#18181B] line-clamp-2 hover:text-[#059669] transition-colors mb-2">
              {product.name}
            </h3>
          </Link>

          {/* Ratings */}
          <div className="flex items-center gap-1.5 mb-3 text-xs text-[#71717A]">
            <div className="flex items-center text-[#D97706]">
              <Star className="w-3.5 h-3.5 fill-current" />
              <span className="ml-1 font-semibold text-[#18181B]">
                {product.average_rating > 0 ? product.average_rating.toFixed(1) : "New"}
              </span>
            </div>
            {product.reviews_count > 0 && (
              <span>({product.reviews_count} reviews)</span>
            )}
          </div>
        </div>
      </div>

      {/* Pricing & Add to Cart */}
      <div className="p-4 pt-0 border-t border-[#F4F4F5]">
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-base font-bold text-[#18181B]">
            {formatPrice(product.effective_price)}
          </span>
          {product.discount_price && product.discount_price < product.price && (
            <span className="text-xs text-[#71717A] line-through">
              {formatPrice(product.price)}
            </span>
          )}
        </div>

        <button
          onClick={() => addToCart(product.id, 1)}
          disabled={!product.is_in_stock}
          className={`w-full py-2 px-3 text-sm font-medium rounded-md flex items-center justify-center gap-2 transition-colors ${
            product.is_in_stock
              ? "bg-[#059669] hover:bg-[#047857] text-white"
              : "bg-[#F4F4F5] text-[#A1A1AA] cursor-not-allowed"
          }`}
        >
          <ShoppingCart className="w-4 h-4" />
          <span>{product.is_in_stock ? "Add to Cart" : "Out of Stock"}</span>
        </button>
      </div>
    </div>
  );
};

