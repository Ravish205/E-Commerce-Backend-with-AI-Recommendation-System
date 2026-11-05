import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { CheckCircle2, ArrowRight, FileText, ShoppingBag } from "lucide-react";
import { orderService } from "../services/orderService";
import { Order } from "../types";

export const OrderSuccessPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId) {
      orderService.getOrderDetail(orderId)
        .then(setOrder)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [orderId]);

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  const handleDownloadInvoice = async () => {
    if (!orderId) return;
    try {
      const invoiceData = await orderService.getInvoice(orderId);
      const blob = new Blob([JSON.stringify(invoiceData, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Invoice-${order?.order_number || orderId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert("Failed to download invoice");
    }
  };

  if (loading) {
    return <div className="py-20 text-center text-sm text-[#71717A]">Verifying completed payment...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto my-8 bg-white border border-[#E4E4E7] rounded-md p-8 text-center space-y-6">
      <div className="w-16 h-16 rounded-full bg-[#ECFDF5] text-[#059669] flex items-center justify-center mx-auto">
        <CheckCircle2 className="w-10 h-10" />
      </div>

      <div>
        <span className="text-xs font-semibold text-[#059669] uppercase tracking-wider">Payment Confirmed</span>
        <h1 className="text-2xl font-bold text-[#18181B] mt-1">Thank you for your order!</h1>
        <p className="text-sm text-[#71717A] mt-2">
          Your order has been placed successfully and is now being processed for delivery.
        </p>
      </div>

      {order && (
        <div className="bg-[#F9FAFB] border border-[#E4E4E7] rounded-md p-5 text-left text-xs space-y-3">
          <div className="flex justify-between border-b border-[#E4E4E7] pb-2">
            <span className="text-[#71717A]">Order Number:</span>
            <span className="font-bold text-[#18181B]">{order.order_number}</span>
          </div>
          <div className="flex justify-between border-b border-[#E4E4E7] pb-2">
            <span className="text-[#71717A]">Order Status:</span>
            <span className="font-bold text-[#059669] uppercase">{order.status}</span>
          </div>
          <div className="flex justify-between border-b border-[#E4E4E7] pb-2">
            <span className="text-[#71717A]">Total Amount Paid:</span>
            <span className="font-bold text-[#18181B]">{formatPrice(order.total_amount)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-[#71717A]">Shipping To:</span>
            <span className="font-medium text-[#18181B] text-right">
              {order.shipping_address?.recipient_name}, {order.shipping_address?.city}
            </span>
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
        <button
          onClick={handleDownloadInvoice}
          className="px-4 py-2 text-xs font-semibold border border-[#E4E4E7] rounded-md text-[#18181B] hover:bg-zinc-50 flex items-center gap-1.5 transition-colors"
        >
          <FileText className="w-4 h-4 text-[#059669]" />
          <span>Download Invoice</span>
        </button>

        <Link
          to="/orders"
          className="px-4 py-2 text-xs font-semibold border border-[#E4E4E7] rounded-md text-[#18181B] hover:bg-zinc-50 transition-colors"
        >
          View Order History
        </Link>

        <Link
          to="/products"
          className="px-5 py-2 text-xs font-semibold bg-[#059669] hover:bg-[#047857] text-white rounded-md flex items-center gap-1.5 transition-colors"
        >
          <span>Continue Shopping</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
};

