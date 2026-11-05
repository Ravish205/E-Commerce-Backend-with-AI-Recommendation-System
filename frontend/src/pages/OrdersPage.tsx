import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Package, Clock, CheckCircle2, XCircle, FileText, ChevronRight } from "lucide-react";
import { orderService } from "../services/orderService";
import { Order } from "../types";

export const OrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    orderService.listOrders()
      .then((res) => setOrders(res.orders))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "delivered":
        return <span className="text-[11px] font-semibold bg-[#ECFDF5] text-[#047857] px-2.5 py-0.5 rounded">Delivered</span>;
      case "cancelled":
        return <span className="text-[11px] font-semibold bg-red-50 text-[#DC2626] px-2.5 py-0.5 rounded">Cancelled</span>;
      case "confirmed":
      case "processing":
        return <span className="text-[11px] font-semibold bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded capitalize">{status}</span>;
      default:
        return <span className="text-[11px] font-semibold bg-zinc-100 text-zinc-700 px-2.5 py-0.5 rounded capitalize">{status}</span>;
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (!window.confirm("Are you sure you want to cancel this order? Items will be returned to inventory.")) return;
    try {
      await orderService.cancelOrder(orderId, "Customer requested cancellation via portal");
      const updated = await orderService.listOrders();
      setOrders(updated.orders);
    } catch (err: any) {
      alert(err.response?.data?.message || "Failed to cancel order");
    }
  };

  if (loading) {
    return <div className="py-20 text-center text-sm text-[#71717A]">Loading your orders...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Your Order History</h1>
        <p className="text-xs text-[#71717A] mt-1">Review past purchases, download invoices, and check shipment statuses</p>
      </div>

      {orders.length === 0 ? (
        <div className="bg-white border border-[#E4E4E7] rounded-md p-12 text-center">
          <Package className="w-10 h-10 text-[#71717A] mx-auto mb-3" />
          <h2 className="text-base font-bold text-[#18181B] mb-1">No orders placed yet</h2>
          <p className="text-xs text-[#71717A] mb-4">When you purchase items, your order details and invoices will appear here.</p>
          <Link to="/products" className="text-xs font-semibold text-[#059669] hover:underline">
            Start browsing catalog
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((o) => (
            <div key={o.id} className="bg-white border border-[#E4E4E7] rounded-md overflow-hidden">
              {/* Order Header */}
              <div className="p-4 bg-[#F9FAFB] border-b border-[#E4E4E7] flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-6">
                  <div>
                    <span className="text-[#71717A] block">Order Number</span>
                    <span className="font-bold text-[#18181B]">{o.order_number}</span>
                  </div>
                  <div>
                    <span className="text-[#71717A] block">Date Placed</span>
                    <span className="font-medium text-[#18181B]">
                      {o.created_at ? new Date(o.created_at).toLocaleDateString() : ""}
                    </span>
                  </div>
                  <div>
                    <span className="text-[#71717A] block">Total Amount</span>
                    <span className="font-bold text-[#18181B]">{formatPrice(o.total_amount)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {getStatusBadge(o.status)}
                  {["pending", "confirmed", "processing"].includes(o.status) && (
                    <button
                      onClick={() => handleCancelOrder(o.id)}
                      className="text-xs text-[#DC2626] font-semibold hover:underline"
                    >
                      Cancel Order
                    </button>
                  )}
                </div>
              </div>

              {/* Order Items List */}
              <div className="p-4 divide-y divide-zinc-100">
                {o.items?.map((item) => (
                  <div key={item.id} className="py-3 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <img
                        src={item.primary_image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80"}
                        alt=""
                        className="w-12 h-12 object-cover rounded border border-[#E4E4E7]"
                      />
                      <div>
                        <h4 className="font-bold text-[#18181B]">{item.product_name}</h4>
                        <span className="text-[#71717A]">
                          Qty: {item.quantity} × {formatPrice(item.unit_price)}
                        </span>
                      </div>
                    </div>
                    <span className="font-bold text-[#18181B]">{formatPrice(item.total_price)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
