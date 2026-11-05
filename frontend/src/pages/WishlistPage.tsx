import React from "react";
import { Link } from "react-router-dom";
import { Heart, ShoppingCart, Trash2, ArrowRight } from "lucide-react";
import { useCart } from "../context/CartContext";
import { cartService } from "../services/cartService";

export const WishlistPage: React.FC = () => {
  const { wishlist, toggleWishlist, refreshCart } = useCart();

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  const handleMoveToCart = async (productId: string) => {
    try {
      await cartService.moveWishlistToCart(productId);
      await refreshCart();
    } catch (err: any) {
      alert(err.response?.data?.message || "Failed to move item to cart");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Your Wishlist</h1>
        <p className="text-xs text-[#71717A] mt-1">{wishlist.length} item{wishlist.length !== 1 ? "s" : ""} saved for later</p>
      </div>

      {wishlist.length === 0 ? (
        <div className="bg-white border border-[#E4E4E7] rounded-md p-16 text-center max-w-xl mx-auto my-12">
          <div className="w-16 h-16 rounded-full bg-[#F9FAFB] flex items-center justify-center mx-auto text-[#71717A] mb-4">
            <Heart className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-[#18181B] mb-2">Your wishlist is empty</h2>
          <p className="text-sm text-[#71717A] mb-6">Explore our catalog and click the heart icon on any device to save it here.</p>
          <Link
            to="/products"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#059669] hover:bg-[#047857] text-white text-sm font-semibold rounded-md transition-colors"
          >
            <span>Explore Catalog</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {wishlist.map((p) => (
            <div key={p.id} className="bg-white border border-[#E4E4E7] rounded-md overflow-hidden flex flex-col justify-between">
              <div>
                <div className="aspect-square bg-[#F9FAFB] relative">
                  <img
                    src={p.primary_image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80"}
                    alt={p.name}
                    className="w-full h-full object-cover"
                  />
                  <button
                    onClick={() => toggleWishlist(p)}
                    className="absolute top-2.5 right-2.5 p-1.5 bg-white rounded-md text-[#DC2626] border border-[#E4E4E7]"
                    title="Remove from wishlist"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="p-4">
                  <span className="text-[11px] font-bold text-[#71717A] uppercase">{p.brand}</span>
                  <Link to={`/products/${p.slug || p.id}`}>
                    <h3 className="text-sm font-semibold text-[#18181B] truncate hover:text-[#059669] mt-0.5">
                      {p.name}
                    </h3>
                  </Link>
                  <p className="text-sm font-bold text-[#18181B] mt-2">{formatPrice(p.effective_price)}</p>
                </div>
              </div>

              <div className="p-4 pt-0">
                <button
                  onClick={() => handleMoveToCart(p.id)}
                  disabled={!p.is_in_stock}
                  className={`w-full py-2 px-3 text-xs font-semibold rounded-md flex items-center justify-center gap-2 transition-colors ${
                    p.is_in_stock
                      ? "bg-[#059669] hover:bg-[#047857] text-white"
                      : "bg-zinc-100 text-zinc-400 cursor-not-allowed"
                  }`}
                >
                  <ShoppingCart className="w-3.5 h-3.5" />
                  <span>{p.is_in_stock ? "Move to Cart" : "Out of Stock"}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
