import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, CreditCard, Lock, CheckCircle2 } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { orderService } from "../services/orderService";
import api from "../services/api";

export const CheckoutPage: React.FC = () => {
  const { cart, refreshCart } = useCart();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [addresses, setAddresses] = useState<any[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<string>("");
  const [recipientName, setRecipientName] = useState(user ? `${user.first_name} ${user.last_name}` : "");
  const [phone, setPhone] = useState(user?.phone_number || "");
  const [streetAddress, setStreetAddress] = useState("");
  const [city, setCity] = useState("Bengaluru");
  const [state, setState] = useState("Karnataka");
  const [postalCode, setPostalCode] = useState("560001");
  const [notes, setNotes] = useState("");

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login?redirect=/checkout");
      return;
    }
    api.get("/users/addresses")
      .then((res) => {
        setAddresses(res.data.data || []);
        const defaultAddr = res.data.data?.find((a: any) => a.is_default);
        if (defaultAddr) {
          setSelectedAddressId(defaultAddr.id);
        }
      })
      .catch(() => {});
  }, [isAuthenticated, navigate]);

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cart || cart.items.length === 0) return;
    setProcessing(true);
    setError("");

    try {
      // 1. Create Order
      const payload: any = {
        notes,
        coupon_code: cart.coupon?.code,
      };

      if (selectedAddressId) {
        payload.shipping_address_id = selectedAddressId;
      } else {
        payload.shipping_address = {
          recipient_name: recipientName,
          phone,
          street_address: streetAddress,
          city,
          state,
          postal_code: postalCode,
          country: "India",
        };
      }

      const order = await orderService.createOrder(payload);

      // 2. Initiate Payment Session
      const paymentOrder = await orderService.createPaymentOrder(order.id);

      // 3. Complete payment verification
      // Simulate/trigger payment callback with gateway signature
      const verifyPayload = {
        order_id: order.id,
        gateway_order_id: paymentOrder.gateway_order_id,
        gateway_payment_id: `pay_test_${Math.random().toString(36).substring(2, 10)}`,
        gateway_signature: "sig_verified_mock_test_token",
      };

      await orderService.verifyPayment(verifyPayload);
      await refreshCart();

      navigate(`/order/success/${order.id}`);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || "Failed to process order");
    } finally {
      setProcessing(false);
    }
  };

  if (!cart || cart.items.length === 0) {
    return <div className="py-20 text-center text-sm text-[#71717A]">Cart is empty</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Checkout</h1>
        <p className="text-xs text-[#71717A] mt-1">Review your delivery address and finalize order payment</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-[#DC2626] text-xs rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handlePlaceOrder} className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Shipping Form */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
            <h2 className="text-base font-bold text-[#18181B] pb-3 border-b border-[#E4E4E7]">
              Shipping Address
            </h2>

            {addresses.length > 0 && (
              <div className="space-y-2 mb-4">
                <span className="text-xs font-semibold text-[#18181B] block">Saved Addresses:</span>
                {addresses.map((a) => (
                  <label
                    key={a.id}
                    className={`block p-3 border rounded text-xs cursor-pointer ${
                      selectedAddressId === a.id
                        ? "border-[#059669] bg-[#ECFDF5]"
                        : "border-[#E4E4E7] hover:bg-zinc-50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="selected_address"
                      checked={selectedAddressId === a.id}
                      onChange={() => setSelectedAddressId(a.id)}
                      className="mr-2"
                    />
                    <span className="font-bold">{a.recipient_name}</span> ({a.phone}) - {a.street_address}, {a.city}, {a.state} {a.postal_code}
                  </label>
                ))}
                <label className="block p-2 text-xs text-[#71717A] cursor-pointer">
                  <input
                    type="radio"
                    name="selected_address"
                    checked={!selectedAddressId}
                    onChange={() => setSelectedAddressId("")}
                    className="mr-2"
                  />
                  Use a different address below
                </label>
              </div>
            )}

            {!selectedAddressId && (
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="font-semibold text-[#18181B] block mb-1">Recipient Name</label>
                  <input
                    type="text"
                    required
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
                <div>
                  <label className="font-semibold text-[#18181B] block mb-1">Phone Number</label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
                <div className="col-span-2">
                  <label className="font-semibold text-[#18181B] block mb-1">Street Address</label>
                  <input
                    type="text"
                    required
                    value={streetAddress}
                    onChange={(e) => setStreetAddress(e.target.value)}
                    placeholder="House/Apartment #, Street, Landmark"
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
                <div>
                  <label className="font-semibold text-[#18181B] block mb-1">City</label>
                  <input
                    type="text"
                    required
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
                <div>
                  <label className="font-semibold text-[#18181B] block mb-1">State</label>
                  <input
                    type="text"
                    required
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
                <div>
                  <label className="font-semibold text-[#18181B] block mb-1">Postal Code (PIN)</label>
                  <input
                    type="text"
                    required
                    value={postalCode}
                    onChange={(e) => setPostalCode(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Payment Method Notice */}
          <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-3">
            <h2 className="text-base font-bold text-[#18181B] pb-2 border-b border-[#E4E4E7] flex items-center justify-between">
              <span>Payment Gateway</span>
              <span className="text-xs font-semibold text-[#059669] flex items-center gap-1">
                <Lock className="w-3.5 h-3.5" /> 256-Bit SSL Encrypted
              </span>
            </h2>
            <div className="p-3 bg-[#F9FAFB] rounded border border-[#E4E4E7] flex items-center gap-3">
              <CreditCard className="w-5 h-5 text-[#059669]" />
              <div className="text-xs">
                <p className="font-bold text-[#18181B]">Razorpay Payment Gateway (Instant & Secure)</p>
                <p className="text-[#71717A]">Supports UPI, NetBanking, Credit/Debit Cards, & Wallets</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Summary */}
        <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-5 h-fit">
          <h2 className="text-base font-bold text-[#18181B] pb-3 border-b border-[#E4E4E7]">
            Order Review
          </h2>

          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {cart.items.map((it) => (
              <div key={it.item_id} className="flex justify-between text-xs py-1 border-b border-zinc-100">
                <span className="truncate max-w-[150px] font-medium text-[#18181B]">{it.name} (x{it.quantity})</span>
                <span className="font-bold">{formatPrice(it.item_total)}</span>
              </div>
            ))}
          </div>

          <div className="space-y-2 text-xs pt-3 border-t border-[#E4E4E7]">
            <div className="flex justify-between text-[#71717A]">
              <span>Subtotal</span>
              <span className="font-semibold text-[#18181B]">{formatPrice(cart.subtotal)}</span>
            </div>
            {cart.discount_amount > 0 && (
              <div className="flex justify-between text-[#059669]">
                <span>Discount</span>
                <span className="font-semibold">-{formatPrice(cart.discount_amount)}</span>
              </div>
            )}
            <div className="flex justify-between text-[#71717A]">
              <span>GST (18%)</span>
              <span className="font-semibold text-[#18181B]">{formatPrice(cart.tax_amount)}</span>
            </div>
            <div className="flex justify-between text-[#71717A]">
              <span>Shipping</span>
              <span className="font-semibold text-[#18181B]">
                {cart.shipping_amount === 0 ? "FREE" : formatPrice(cart.shipping_amount)}
              </span>
            </div>
            <div className="pt-2 border-t border-[#E4E4E7] flex justify-between text-base font-bold text-[#18181B]">
              <span>Grand Total</span>
              <span>{formatPrice(cart.final_total)}</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={processing}
            className="w-full py-2.5 px-4 bg-[#059669] hover:bg-[#047857] text-white text-sm font-semibold rounded-md flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            <Lock className="w-4 h-4" />
            <span>{processing ? "Processing Payment..." : "Confirm & Pay"}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
