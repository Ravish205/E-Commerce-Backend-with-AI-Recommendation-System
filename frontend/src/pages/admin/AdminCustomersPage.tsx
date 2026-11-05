import React, { useEffect, useState } from "react";
import { Users, Mail, Phone } from "lucide-react";
import { adminService } from "../../services/adminService";

export const AdminCustomersPage: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.getCustomers({ limit: 50 })
      .then((res) => setCustomers(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#18181B] tracking-tight">Customer Directory</h1>
        <p className="text-xs text-[#71717A] mt-1">Registered customer accounts, orders counts, and account activity</p>
      </div>

      <div className="bg-white border border-[#E4E4E7] rounded-md overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#F9FAFB] border-b border-[#E4E4E7] text-[#71717A] uppercase tracking-wider font-semibold">
            <tr>
              <th className="py-3 px-4">Customer Name</th>
              <th className="py-3 px-4">Email</th>
              <th className="py-3 px-4">Phone</th>
              <th className="py-3 px-4">Lifetime Orders</th>
              <th className="py-3 px-4">Account Status</th>
              <th className="py-3 px-4">Registered Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4E4E7]">
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-[#71717A]">Loading customers...</td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-[#71717A]">No registered customers found.</td>
              </tr>
            ) : (
              customers.map((c) => (
                <tr key={c.id} className="hover:bg-zinc-50">
                  <td className="py-3 px-4 font-bold text-[#18181B]">
                    {c.first_name} {c.last_name}
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-[#71717A]">{c.email}</td>
                  <td className="py-3 px-4 text-[#71717A]">{c.phone_number || "—"}</td>
                  <td className="py-3 px-4 font-semibold">{c.orders_count} orders</td>
                  <td className="py-3 px-4">
                    {c.is_active ? (
                      <span className="text-[11px] font-semibold text-[#047857] bg-[#ECFDF5] px-2 py-0.5 rounded">Active</span>
                    ) : (
                      <span className="text-[11px] font-semibold text-[#DC2626] bg-red-50 px-2 py-0.5 rounded">Suspended</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-[#71717A]">
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : ""}
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

