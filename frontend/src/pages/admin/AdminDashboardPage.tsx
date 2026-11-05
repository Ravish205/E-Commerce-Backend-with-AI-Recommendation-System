import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  Package,
  ShoppingCart,
  IndianRupee,
  AlertTriangle,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { adminService } from "../../services/adminService";
import { DashboardMetrics } from "../../types";

export const AdminDashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.getDashboard()
      .then(setMetrics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const formatPrice = (amount: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);

  if (loading) {
    return <div className="py-20 text-center text-sm text-[#71717A]">Calculating real store analytics...</div>;
  }

  if (!metrics) {
    return <div className="py-20 text-center text-sm text-[#DC2626]">Failed to load admin metrics</div>;
  }

  const statCards = [
    { label: "Total Revenue", value: formatPrice(metrics.total_revenue), icon: IndianRupee, color: "text-[#059669]", bg: "bg-[#ECFDF5]" },
    { label: "Completed Orders", value: metrics.total_orders.toString(), icon: ShoppingCart, color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Active Products", value: metrics.total_products.toString(), icon: Package, color: "text-purple-600", bg: "bg-purple-50" },
    { label: "Registered Customers", value: metrics.total_customers.toString(), icon: Users, color: "text-indigo-600", bg: "bg-indigo-50" },
    { label: "Pending Orders", value: metrics.pending_orders.toString(), icon: Clock, color: "text-[#D97706]", bg: "bg-amber-50" },
    { label: "Low Stock Alerts", value: metrics.low_stock_count.toString(), icon: AlertTriangle, color: "text-[#DC2626]", bg: "bg-red-50" },
  ];

  return (
    <div className="space-y-8">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="bg-white border border-[#E4E4E7] rounded-md p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-[#71717A] uppercase">{card.label}</span>
                <div className={`p-1.5 rounded ${card.bg} ${card.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <p className="text-xl font-bold text-[#18181B] tracking-tight">{card.value}</p>
            </div>
          );
        })}
      </div>

      {/* Analytics Chart */}
      <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-[#E4E4E7]">
          <div>
            <h2 className="text-sm font-bold text-[#18181B]">14-Day Sales Velocity & Revenue</h2>
            <p className="text-xs text-[#71717A]">Calculated directly from captured orders and settlements</p>
          </div>
          <span className="text-xs text-[#059669] font-semibold bg-[#ECFDF5] px-2 py-0.5 rounded">
            Live Database Feed
          </span>
        </div>

        <div className="h-64 w-full pt-4">
          {metrics.sales_time_series.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics.sales_time_series}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F4F4F5" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#71717A" }} />
                <YAxis tick={{ fontSize: 11, fill: "#71717A" }} />
                <Tooltip
                  formatter={(val: any) => [formatPrice(Number(val)), "Revenue"]}
                  contentStyle={{ backgroundColor: "#18181B", color: "#FFF", borderRadius: 4, fontSize: 12 }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#059669" fill="#ECFDF5" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-[#71717A]">
              No sales time series recorded in the past 14 days. Place orders to populate real data.
            </div>
          )}
        </div>
      </div>

      {/* Tables Row: Recent Orders & Low Stock */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Orders */}
        <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#E4E4E7]">
            <h3 className="text-sm font-bold text-[#18181B]">Recent Store Orders</h3>
            <Link to="/admin/orders" className="text-xs font-semibold text-[#059669] hover:underline flex items-center gap-1">
              <span>View all orders</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-[#E4E4E7] text-xs">
            {metrics.recent_orders.map((o) => (
              <div key={o.id} className="py-2.5 flex items-center justify-between">
                <div>
                  <span className="font-bold text-[#18181B] block">{o.order_number}</span>
                  <span className="text-[#71717A]">{o.customer_name}</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-[#18181B] block">{formatPrice(o.total_amount)}</span>
                  <span className="text-[11px] font-semibold text-[#059669] uppercase">{o.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#E4E4E7]">
            <h3 className="text-sm font-bold text-[#18181B]">Low Inventory Warnings</h3>
            <Link to="/admin/inventory" className="text-xs font-semibold text-[#059669] hover:underline flex items-center gap-1">
              <span>Manage stock</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-[#E4E4E7] text-xs">
            {metrics.low_stock_products.length === 0 ? (
              <p className="text-[#71717A] py-4 text-center">All active products meet inventory thresholds.</p>
            ) : (
              metrics.low_stock_products.map((p) => (
                <div key={p.id} className="py-2.5 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-[#18181B] block truncate max-w-[200px]">{p.name}</span>
                    <span className="text-[#71717A]">SKU: {p.sku}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-[#DC2626] block">{p.stock} units left</span>
                    <span className="text-[11px] text-[#71717A]">Threshold: {p.low_stock_threshold}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
