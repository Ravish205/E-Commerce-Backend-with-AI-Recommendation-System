import React, { useEffect, useState } from "react";
import { adminService } from "../../services/adminService";

export const AdminOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const loadOrders = () => {
    setLoading(true);
    adminService.getOrders({ status: statusFilter || undefined, limit: 50 })
      .then((res) => setOrders(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOrders();
  }, [statusFilter]);

  const handleStatusChange = async (orderId: string, newStatus: string) => {
    try {
      await adminService.updateOrderStatus(orderId, newStatus);
      loadOrders();
    } catch {
      alert("Failed to update status");
    }
  };

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-[#18181B] tracking-tight">Customer Orders Queue</h1>
          <p className="text-xs text-[#71717A] mt-1">Fulfill orders, track shipping timelines, and update dispatch status</p>
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-xs p-2 border border-[#E4E4E7] rounded bg-white"
        >
          <option value="">All Order Statuses</option>
          <option value="pending">Pending</option>
          <option value="confirmed">Confirmed</option>
          <option value="processing">Processing</option>
          <option value="shipped">Shipped</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <div className="bg-white border border-[#E4E4E7] rounded-md overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#F9FAFB] border-b border-[#E4E4E7] text-[#71717A] uppercase tracking-wider font-semibold">
            <tr>
              <th className="py-3 px-4">Order #</th>
              <th className="py-3 px-4">Customer</th>
              <th className="py-3 px-4">Items</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Date</th>
              <th className="py-3 px-4">Status & Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4E4E7]">
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-[#71717A]">Loading orders...</td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-[#71717A]">No orders found for this filter.</td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.id} className="hover:bg-zinc-50">
                  <td className="py-3 px-4 font-mono font-bold">{o.order_number}</td>
                  <td className="py-3 px-4">
                    <span className="font-semibold block">{o.customer_name}</span>
                    <span className="text-[#71717A] text-[11px]">{o.customer_email}</span>
                  </td>
                  <td className="py-3 px-4">{o.items_count} units</td>
                  <td className="py-3 px-4 font-bold">{formatPrice(o.total_amount)}</td>
                  <td className="py-3 px-4 text-[#71717A]">
                    {o.created_at ? new Date(o.created_at).toLocaleDateString() : ""}
                  </td>
                  <td className="py-3 px-4">
                    <select
                      value={o.status}
                      onChange={(e) => handleStatusChange(o.id, e.target.value)}
                      className="text-xs p-1 border border-[#E4E4E7] rounded bg-white font-medium"
                    >
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="processing">Processing</option>
                      <option value="shipped">Shipped</option>
                      <option value="delivered">Delivered</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
