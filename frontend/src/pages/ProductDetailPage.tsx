import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Star, ShieldCheck, Truck, RefreshCw, ShoppingCart, Heart, Sparkles, MessageSquarePlus } from "lucide-react";
import { catalogService } from "../services/catalogService";
import { recommendationService } from "../services/recommendationService";
import { Product, Review } from "../types";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { RecommendationSection } from "../components/product/RecommendationSection";

export const ProductDetailPage: React.FC = () => {
  const { idOrSlug } = useParams<{ idOrSlug: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedImage, setSelectedImage] = useState<string>("");
  const [quantity, setQuantity] = useState(1);
  const [similar, setSimilar] = useState<Product[]>([]);
  const [frequentlyBought, setFrequentlyBought] = useState<Product[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  // Review modal state
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewComment, setReviewComment] = useState("");
  const [reviewSubmitting, setReviewSubmitting] = useState(false);
  const [reviewError, setReviewError] = useState("");

  const { addToCart, toggleWishlist, isInWishlist } = useCart();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    async function loadData() {
      if (!idOrSlug) return;
      setLoading(true);
      try {
        const prod = await catalogService.getProductDetail(idOrSlug);
        setProduct(prod);
        setSelectedImage(prod.primary_image || "");

        // Track interaction
        recommendationService.trackInteraction(prod.id, "view");

        // Load reviews and recommendations in parallel
        const [sim, freq, revRes] = await Promise.all([
          recommendationService.getSimilar(prod.id, 4),
          recommendationService.getFrequentlyBoughtTogether(prod.id, 4),
          catalogService.getProductReviews(prod.id),
        ]);
        setSimilar(sim);
        setFrequentlyBought(freq);
        setReviews(revRes.data || []);
      } catch (err) {
        console.error("Failed to load product", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [idOrSlug]);

  if (loading) {
    return <div className="py-24 text-center text-sm text-[#71717A]">Loading product specifications...</div>;
  }

  if (!product) {
    return (
      <div className="py-24 text-center">
        <h2 className="text-xl font-bold text-[#18181B] mb-2">Product Not Found</h2>
        <p className="text-sm text-[#71717A] mb-4">The product you requested might have been discontinued or moved.</p>
        <Link to="/products" className="text-sm font-semibold text-[#059669] hover:underline">
          Return to Catalog
        </Link>
      </div>
    );
  }

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setReviewSubmitting(true);
    setReviewError("");
    try {
      await catalogService.submitReview(product.id, reviewRating, reviewTitle, reviewComment);
      setShowReviewModal(false);
      // Reload reviews
      const revRes = await catalogService.getProductReviews(product.id);
      setReviews(revRes.data || []);
    } catch (err: any) {
      setReviewError(err.response?.data?.message || "Failed to submit review");
    } finally {
      setReviewSubmitting(false);
    }
  };

  const isWishlisted = isInWishlist(product.id);
  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  return (
    <div className="space-y-12">
      {/* Product Overview Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10 bg-white border border-[#E4E4E7] rounded-md p-6 md:p-8">
        {/* Left: Product Images */}
        <div className="space-y-4">
          <div className="aspect-square bg-[#F9FAFB] rounded-md overflow-hidden border border-[#E4E4E7]">
            <img
              src={selectedImage || product.primary_image || ""}
              alt={product.name}
              className="w-full h-full object-cover object-center"
            />
          </div>

          {/* Gallery Thumbnails */}
          {product.images && product.images.length > 1 && (
            <div className="flex gap-3 overflow-x-auto pb-2">
              {product.images.map((img) => (
                <button
                  key={img.id || img.image_url}
                  onClick={() => setSelectedImage(img.image_url)}
                  className={`w-16 h-16 rounded border overflow-hidden flex-shrink-0 ${
                    selectedImage === img.image_url ? "border-[#059669] ring-2 ring-[#ECFDF5]" : "border-[#E4E4E7]"
                  }`}
                >
                  <img src={img.image_url} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: Product Details & Actions */}
        <div className="space-y-5">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[#71717A] uppercase tracking-wider">
                {product.brand}
              </span>
              <span className="text-xs text-[#71717A]">SKU: {product.sku}</span>
            </div>
            <h1 className="text-2xl font-bold text-[#18181B] mt-1 tracking-tight">{product.name}</h1>
          </div>

          {/* Rating summary */}
          <div className="flex items-center gap-3 text-sm">
            <div className="flex items-center text-[#D97706]">
              <Star className="w-4 h-4 fill-current" />
              <span className="ml-1 font-bold text-[#18181B]">
                {product.average_rating > 0 ? product.average_rating.toFixed(1) : "New"}
              </span>
            </div>
            <span className="text-[#E4E4E7]">|</span>
            <span className="text-[#71717A] text-xs">
              {product.reviews_count} verified customer review{product.reviews_count !== 1 ? "s" : ""}
            </span>
          </div>

          {/* Pricing */}
          <div className="p-4 bg-[#F9FAFB] border border-[#E4E4E7] rounded-md flex items-baseline gap-3">
            <span className="text-2xl font-bold text-[#18181B]">
              {formatPrice(product.effective_price)}
            </span>
            {product.discount_price && product.discount_price < product.price && (
              <>
                <span className="text-sm text-[#71717A] line-through">
                  {formatPrice(product.price)}
                </span>
                <span className="text-xs font-semibold text-[#059669] bg-[#ECFDF5] px-2 py-0.5 rounded">
                  Save {Math.round(((product.price - product.discount_price) / product.price) * 100)}%
                </span>
              </>
            )}
          </div>

          {/* Stock Status */}
          <div className="flex items-center gap-2 text-xs">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                product.stock > 0 ? "bg-[#059669]" : "bg-[#DC2626]"
              }`}
            />
            <span className="font-medium text-[#18181B]">
              {product.stock > 0
                ? `In Stock (${product.stock} units available)`
                : "Currently Out of Stock"}
            </span>
          </div>

          {/* Actions: Quantity + Add to Cart + Wishlist */}
          <div className="flex items-center gap-3 pt-2">
            <div className="flex items-center border border-[#E4E4E7] rounded-md">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="px-3 py-2 text-xs font-semibold hover:bg-zinc-100"
              >
                -
              </button>
              <span className="px-3 text-xs font-bold text-[#18181B]">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                disabled={quantity >= product.stock}
                className="px-3 py-2 text-xs font-semibold hover:bg-zinc-100 disabled:opacity-40"
              >
                +
              </button>
            </div>

            <button
              onClick={() => addToCart(product.id, quantity)}
              disabled={product.stock <= 0}
              className={`flex-1 py-2.5 px-4 rounded-md text-sm font-semibold flex items-center justify-center gap-2 transition-colors ${
                product.stock > 0
                  ? "bg-[#059669] hover:bg-[#047857] text-white"
                  : "bg-zinc-200 text-zinc-400 cursor-not-allowed"
              }`}
            >
              <ShoppingCart className="w-4 h-4" />
              <span>{product.stock > 0 ? "Add to Cart" : "Out of Stock"}</span>
            </button>

            <button
              onClick={() => toggleWishlist(product)}
              className={`p-2.5 rounded-md border border-[#E4E4E7] hover:border-[#18181B] transition-colors ${
                isWishlisted ? "text-[#DC2626]" : "text-[#71717A]"
              }`}
            >
              <Heart className={`w-5 h-5 ${isWishlisted ? "fill-current" : ""}`} />
            </button>
          </div>

          {/* Short description */}
          <p className="text-sm text-[#71717A] leading-relaxed pt-2">
            {product.short_description || product.description}
          </p>
        </div>
      </div>

      {/* Attributes & Full Description */}
      <div className="bg-white border border-[#E4E4E7] rounded-md p-6 md:p-8 space-y-6">
        <h2 className="text-lg font-bold text-[#18181B]">Technical Specifications</h2>
        {product.attributes && product.attributes.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {product.attributes.map((attr) => (
              <div key={attr.id || attr.attribute_name} className="flex justify-between py-2 border-b border-[#E4E4E7] text-xs">
                <span className="font-semibold text-[#71717A]">{attr.attribute_name}</span>
                <span className="text-[#18181B] font-medium">{attr.attribute_value}</span>
              </div>
            ))}
          </div>
        )}
        <div className="pt-4 border-t border-[#E4E4E7]">
          <h3 className="text-sm font-bold text-[#18181B] mb-2">Detailed Overview</h3>
          <p className="text-sm text-[#71717A] leading-relaxed whitespace-pre-line">{product.description}</p>
        </div>
      </div>

      {/* Frequently Bought Together (Co-occurrence basket recommendations) */}
      <RecommendationSection
        title="Frequently Bought Together"
        subtitle="Popular items often checked out alongside this device"
        products={frequentlyBought}
      />

      {/* Similar Products (Content-based recommendations) */}
      <RecommendationSection
        title="Similar Products"
        subtitle="Devices sharing high attribute and acoustic/hardware similarity"
        products={similar}
      />

      {/* Verified Reviews Section */}
      <section className="bg-white border border-[#E4E4E7] rounded-md p-6 md:p-8 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-[#E4E4E7]">
          <div>
            <h2 className="text-lg font-bold text-[#18181B]">Verified Customer Reviews</h2>
            <p className="text-xs text-[#71717A]">Honest reviews submitted strictly by verified purchasers</p>
          </div>

          {isAuthenticated ? (
            <button
              onClick={() => setShowReviewModal(true)}
              className="text-xs font-semibold px-3.5 py-2 bg-[#059669] hover:bg-[#047857] text-white rounded-md flex items-center gap-1.5"
            >
              <MessageSquarePlus className="w-3.5 h-3.5" />
              Write a Review
            </button>
          ) : (
            <Link to="/login" className="text-xs text-[#059669] font-medium hover:underline">
              Log in to review
            </Link>
          )}
        </div>

        {reviews.length === 0 ? (
          <p className="text-xs text-[#71717A] italic py-4">
            No reviews yet for this product. Be the first verified customer to leave your feedback!
          </p>
        ) : (
          <div className="space-y-4">
            {reviews.map((rev) => (
              <div key={rev.id} className="p-4 bg-[#F9FAFB] rounded-md border border-[#E4E4E7] space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-[#18181B]">{rev.user_name}</span>
                    {rev.is_verified_purchase && (
                      <span className="text-[11px] bg-[#ECFDF5] text-[#047857] font-semibold px-2 py-0.5 rounded flex items-center gap-1">
                        <ShieldCheck className="w-3 h-3" />
                        Verified Purchase
                      </span>
                    )}
                  </div>
                  <div className="flex items-center text-[#D97706]">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-3.5 h-3.5 ${
                          i < rev.rating ? "fill-current" : "text-zinc-300"
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <h4 className="text-xs font-bold text-[#18181B]">{rev.title}</h4>
                <p className="text-xs text-[#71717A] leading-relaxed">{rev.comment}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Review Submission Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-md max-w-md w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-[#18181B]">Write a Verified Review</h3>
            {reviewError && (
              <div className="p-3 bg-red-50 text-[#DC2626] text-xs rounded border border-red-200">
                {reviewError}
              </div>
            )}
            <form onSubmit={handleReviewSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-[#18181B] block mb-1">Rating</label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button
                      type="button"
                      key={s}
                      onClick={() => setReviewRating(s)}
                      className="p-1 text-[#D97706]"
                    >
                      <Star className={`w-5 h-5 ${s <= reviewRating ? "fill-current" : "text-zinc-300"}`} />
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-[#18181B] block mb-1">Review Title</label>
                <input
                  type="text"
                  required
                  value={reviewTitle}
                  onChange={(e) => setReviewTitle(e.target.value)}
                  placeholder="e.g. Excellent build quality and acoustic clarity"
                  className="w-full text-xs p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-[#18181B] block mb-1">Your Detailed Review</label>
                <textarea
                  required
                  rows={4}
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="Explain what you liked or disliked about the device..."
                  className="w-full text-xs p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReviewModal(false)}
                  className="px-3.5 py-1.5 text-xs text-[#71717A] hover:text-[#18181B]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={reviewSubmitting}
                  className="px-4 py-1.5 text-xs font-semibold bg-[#059669] hover:bg-[#047857] text-white rounded"
                >
                  {reviewSubmitting ? "Submitting..." : "Submit Review"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
