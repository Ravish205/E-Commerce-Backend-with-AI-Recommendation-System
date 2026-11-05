import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Trash2, ArrowRight, ShieldCheck, Tag, ShoppingCart } from "lucide-react";
import { useCart } from "../context/CartContext";
import { cartService } from "../services/cartService";

export const CartPage: React.FC = () => {
  const { cart, updateQuantity, removeItem, refreshCart } = useCart();
  const [couponCode, setCouponCode] = useState("");
  const [couponLoading, setCouponLoading] = useState(false);
  const [couponError, setCouponError] = useState("");
  const navigate = useNavigate();

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  const handleApplyCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    setCouponError("");
    try {
      const summary = await cartService.getCart(couponCode.trim());
      if (summary.coupon) {
        // Updated with applied coupon
        await refreshCart();
      } else if (summary.warnings && summary.warnings.length > 0) {
        setCouponError(summary.warnings[0]);
      }
    } catch (err: any) {
      setCouponError(err.response?.data?.message || "Failed to apply coupon");
    } finally {
      setCouponLoading(false);
    }
  };

  if (!cart || cart.items.length === 0) {
    return (
      <div className="bg-white border border-[#E4E4E7] rounded-md p-16 text-center max-w-xl mx-auto my-12">
        <div className="w-16 h-16 rounded-full bg-[#F9FAFB] flex items-center justify-center mx-auto text-[#71717A] mb-4">
          <ShoppingCart className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-[#18181B] mb-2">Your shopping cart is empty</h2>
        <p className="text-sm text-[#71717A] mb-6">Explore our curated catalog to find items you love.</p>
        <Link
          to="/products"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#059669] hover:bg-[#047857] text-white text-sm font-semibold rounded-md transition-colors"
        >
          <span>Continue Shopping</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Shopping Cart</h1>
        <p className="text-xs text-[#71717A] mt-1">{cart.items_count} item{cart.items_count !== 1 ? "s" : ""} in your bag</p>
      </div>

      {cart.warnings && cart.warnings.length > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-200 text-[#D97706] text-xs rounded-md space-y-1">
          {cart.warnings.map((w, idx) => (
            <p key={idx}>• {w}</p>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Line Items Table */}
        <div className="lg:col-span-2 bg-white border border-[#E4E4E7] rounded-md divide-y divide-[#E4E4E7]">
          {cart.items.map((item) => (
            <div key={item.item_id} className="p-5 flex items-center gap-4">
              <img
                src={item.primary_image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80"}
                alt={item.name}
                className="w-20 h-20 object-cover rounded border border-[#E4E4E7] flex-shrink-0"
              />

              <div className="flex-1 min-w-0">
                <span className="text-[11px] font-bold text-[#71717A] uppercase">{item.brand}</span>
                <Link to={`/products/${item.slug || item.product_id}`}>
                  <h3 className="text-sm font-semibold text-[#18181B] truncate hover:text-[#059669] transition-colors">
                    {item.name}
                  </h3>
                </Link>
                <p className="text-xs text-[#71717A] mt-0.5">Unit price: {formatPrice(item.unit_price)}</p>

                {/* Mobile controls */}
                <div className="flex items-center gap-4 mt-3 sm:hidden">
                  <span className="text-sm font-bold text-[#18181B]">{formatPrice(item.item_total)}</span>
                  <button
                    onClick={() => removeItem(item.item_id)}
                    className="text-xs text-[#DC2626] flex items-center gap-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" /> Remove
                  </button>
                </div>
              </div>

              {/* Quantity Controls */}
              <div className="hidden sm:flex items-center border border-[#E4E4E7] rounded-md">
                <button
                  onClick={() => updateQuantity(item.item_id, Math.max(1, item.quantity - 1))}
                  className="px-2.5 py-1 text-xs hover:bg-zinc-100 font-semibold"
                >
                  -
                </button>
                <span className="px-3 text-xs font-bold text-[#18181B]">{item.quantity}</span>
                <button
                  onClick={() => updateQuantity(item.item_id, item.quantity + 1)}
                  disabled={item.quantity >= item.stock}
                  className="px-2.5 py-1 text-xs hover:bg-zinc-100 font-semibold disabled:opacity-30"
                >
                  +
                </button>
              </div>

              {/* Item Total & Remove */}
              <div className="hidden sm:flex flex-col items-end gap-2 text-right">
                <span className="text-sm font-bold text-[#18181B]">{formatPrice(item.item_total)}</span>
                <button
                  onClick={() => removeItem(item.item_id)}
                  className="text-xs text-[#71717A] hover:text-[#DC2626] transition-colors"
                  title="Remove item"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary & Coupon Box */}
        <div className="space-y-4">
          <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-5">
            <h2 className="text-base font-bold text-[#18181B] pb-3 border-b border-[#E4E4E7]">
              Order Summary
            </h2>

            {/* Calculations Breakdown */}
            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between text-[#71717A]">
                <span>Items Subtotal</span>
                <span className="font-semibold text-[#18181B]">{formatPrice(cart.subtotal)}</span>
              </div>

              {cart.discount_amount > 0 && (
                <div className="flex justify-between text-[#059669]">
                  <span>Discount Applied ({cart.coupon?.code})</span>
                  <span className="font-semibold">-{formatPrice(cart.discount_amount)}</span>
                </div>
              )}

              <div className="flex justify-between text-[#71717A]">
                <span>GST / Taxes (18%)</span>
                <span className="font-semibold text-[#18181B]">{formatPrice(cart.tax_amount)}</span>
              </div>

              <div className="flex justify-between text-[#71717A]">
                <span>Shipping</span>
                <span className="font-semibold text-[#18181B]">
                  {cart.shipping_amount === 0 ? "FREE" : formatPrice(cart.shipping_amount)}
                </span>
              </div>

              <div className="pt-3 border-t border-[#E4E4E7] flex justify-between text-sm font-bold text-[#18181B]">
                <span>Total Amount</span>
                <span>{formatPrice(cart.final_total)}</span>
              </div>
            </div>

            {/* Checkout Button */}
            <button
              onClick={() => navigate("/checkout")}
              disabled={!cart.is_checkout_ready}
              className={`w-full py-2.5 px-4 text-sm font-semibold rounded-md flex items-center justify-center gap-2 transition-colors ${
                cart.is_checkout_ready
                  ? "bg-[#059669] hover:bg-[#047857] text-white"
                  : "bg-zinc-200 text-zinc-400 cursor-not-allowed"
              }`}
            >
              <span>Proceed to Checkout</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Coupon Code Input */}
          <div className="bg-white border border-[#E4E4E7] rounded-md p-4 space-y-2">
            <span className="text-xs font-semibold text-[#18181B] flex items-center gap-1.5">
              <Tag className="w-3.5 h-3.5 text-[#059669]" /> Have a promo coupon?
            </span>
            <form onSubmit={handleApplyCoupon} className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. WELCOME10"
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                className="flex-1 text-xs p-2 uppercase border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
              />
              <button
                type="submit"
                disabled={couponLoading}
                className="px-3 py-1.5 text-xs font-semibold bg-[#18181B] hover:bg-black text-white rounded"
              >
                Apply
              </button>
            </form>
            {couponError && <p className="text-[11px] text-[#DC2626]">{couponError}</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

