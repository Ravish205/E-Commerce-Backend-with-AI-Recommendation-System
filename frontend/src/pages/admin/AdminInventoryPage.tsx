import React, { useEffect, useState } from "react";
import { Boxes, AlertTriangle, Plus, Minus } from "lucide-react";
import { adminService } from "../../services/adminService";
import { Product } from "../../types";

export const AdminInventoryPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  // Adjustment form modal
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantityChange, setQuantityChange] = useState<number>(10);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadProducts = () => {
    setLoading(true);
    adminService.getProducts({ limit: 100 })
      .then((res) => setProducts(res.products))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleAdjustInventory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProduct || !notes.trim()) return;
    setSubmitting(true);
    try {
      await adminService.adjustInventory(selectedProduct.id, quantityChange, notes.trim());
      setSelectedProduct(null);
      setNotes("");
      loadProducts();
    } catch (err: any) {
      alert(err.response?.data?.message || "Failed to adjust stock");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#18181B] tracking-tight">Warehouse & Stock Inventory</h1>
        <p className="text-xs text-[#71717A] mt-1">
          Double-entry audited inventory movements. Every manual stock change requires a documented audit note.
        </p>
      </div>

      <div className="bg-white border border-[#E4E4E7] rounded-md overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#F9FAFB] border-b border-[#E4E4E7] text-[#71717A] uppercase tracking-wider font-semibold">
            <tr>
              <th className="py-3 px-4">Device</th>
              <th className="py-3 px-4">SKU</th>
              <th className="py-3 px-4">Current Stock</th>
              <th className="py-3 px-4">Alert Threshold</th>
              <th className="py-3 px-4">Inventory Health</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4E4E7]">
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-[#71717A]">Loading stock levels...</td>
              </tr>
            ) : (
              products.map((p) => (
                <tr key={p.id} className="hover:bg-zinc-50">
                  <td className="py-3 px-4 font-bold text-[#18181B]">{p.name}</td>
                  <td className="py-3 px-4 font-mono">{p.sku}</td>
                  <td className="py-3 px-4 font-bold text-sm">{p.stock} units</td>
                  <td className="py-3 px-4 text-[#71717A]">{p.stock <= 5 ? "5 units (Low Alert)" : "5 units"}</td>
                  <td className="py-3 px-4">
                    {p.stock === 0 ? (
                      <span className="text-[11px] font-bold text-[#DC2626] bg-red-50 px-2 py-0.5 rounded">Depleted (0)</span>
                    ) : p.stock <= 5 ? (
                      <span className="text-[11px] font-bold text-[#D97706] bg-amber-50 px-2 py-0.5 rounded">Low Inventory</span>
                    ) : (
                      <span className="text-[11px] font-bold text-[#047857] bg-[#ECFDF5] px-2 py-0.5 rounded">Healthy</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setSelectedProduct(p)}
                      className="px-3 py-1 text-xs font-semibold bg-[#18181B] hover:bg-black text-white rounded"
                    >
                      Audit / Adjust Stock
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Adjust Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-md max-w-md w-full p-6 space-y-4">
            <h2 className="text-base font-bold text-[#18181B]">
              Stock Adjustment: {selectedProduct.name}
            </h2>
            <p className="text-xs text-[#71717A]">
              Current stock: <strong className="text-[#18181B]">{selectedProduct.stock} units</strong>
            </p>

            <form onSubmit={handleAdjustInventory} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold block mb-1">Quantity Adjustment (+ for restock, - for deduction)</label>
                <input
                  type="number"
                  required
                  value={quantityChange}
                  onChange={(e) => setQuantityChange(parseInt(e.target.value, 10))}
                  className="w-full p-2 border border-[#E4E4E7] rounded"
                />
                <span className="text-[11px] text-[#71717A] mt-1 block">
                  New resulting stock balance will be: <strong>{selectedProduct.stock + (quantityChange || 0)} units</strong>
                </span>
              </div>

              <div>
                <label className="font-semibold block mb-1">Mandatory Audit Note / Reason</label>
                <textarea
                  required
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Received shipment container #BGL-409 from distributor."
                  className="w-full p-2 border border-[#E4E4E7] rounded"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[#E4E4E7]">
                <button
                  type="button"
                  onClick={() => setSelectedProduct(null)}
                  className="px-3.5 py-1.5 text-zinc-600 hover:text-black"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-1.5 bg-[#059669] hover:bg-[#047857] text-white font-semibold rounded"
                >
                  {submitting ? "Logging Transaction..." : "Save Adjustment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

