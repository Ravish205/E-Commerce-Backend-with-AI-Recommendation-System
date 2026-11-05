import React, { useEffect, useState } from "react";
import { Plus, Edit2, Trash2, Search, CheckCircle2, XCircle } from "lucide-react";
import { adminService } from "../../services/adminService";
import { catalogService } from "../../services/catalogService";
import { Product, Category } from "../../types";

export const AdminProductsPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  // Create Product Modal State
  const [showModal, setShowModal] = useState(false);
  const [editProductId, setEditProductId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [brand, setBrand] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [price, setPrice] = useState("");
  const [discountPrice, setDiscountPrice] = useState("");
  const [stock, setStock] = useState("");
  const [description, setDescription] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [modalSubmitting, setModalSubmitting] = useState(false);

  useEffect(() => {
    loadProducts();
    catalogService.getCategories().then(setCategories).catch(() => {});
  }, []);

  const loadProducts = () => {
    setLoading(true);
    adminService.getProducts({ limit: 50, search: searchTerm || undefined })
      .then((res) => setProducts(res.products))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleOpenCreate = () => {
    setEditProductId(null);
    setName("");
    setSku("");
    setBrand("");
    setCategoryId(categories[0]?.id || "");
    setPrice("");
    setDiscountPrice("");
    setStock("");
    setDescription("");
    setImageUrl("");
    setShowModal(true);
  };

  const handleOpenEdit = (p: Product) => {
    setEditProductId(p.id);
    setName(p.name);
    setSku(p.sku);
    setBrand(p.brand);
    setCategoryId(p.category_id);
    setPrice(p.price.toString());
    setDiscountPrice(p.discount_price ? p.discount_price.toString() : "");
    setStock(p.stock.toString());
    setDescription(p.description || "");
    setImageUrl(p.primary_image || "");
    setShowModal(true);
  };

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalSubmitting(true);
    try {
      const payload: any = {
        name,
        sku,
        brand,
        category_id: categoryId,
        price: parseFloat(price),
        discount_price: discountPrice ? parseFloat(discountPrice) : null,
        stock: parseInt(stock, 10),
        description,
      };

      if (imageUrl) {
        payload.images = [{ image_url: imageUrl, is_primary: true }];
      }

      if (editProductId) {
        await adminService.updateProduct(editProductId, payload);
      } else {
        await adminService.createProduct(payload);
      }
      setShowModal(false);
      loadProducts();
    } catch (err: any) {
      alert(err.response?.data?.message || "Failed to save product");
    } finally {
      setModalSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to deactivate this product?")) return;
    try {
      await adminService.deleteProduct(id);
      loadProducts();
    } catch {
      alert("Failed to delete product");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-[#18181B] tracking-tight">Product Catalog Management</h1>
          <p className="text-xs text-[#71717A] mt-1">Add, update, and manage hardware inventory & specifications</p>
        </div>

        <button
          onClick={handleOpenCreate}
          className="px-4 py-2 bg-[#059669] hover:bg-[#047857] text-white text-xs font-semibold rounded flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Product</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="flex gap-2 max-w-md">
        <input
          type="text"
          placeholder="Filter by product name, brand, or SKU..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full text-xs p-2 border border-[#E4E4E7] rounded bg-white focus:outline-none focus:border-[#059669]"
        />
        <button
          onClick={loadProducts}
          className="px-3 py-1.5 bg-[#18181B] text-white text-xs font-semibold rounded"
        >
          Filter
        </button>
      </div>

      {/* Products Table */}
      <div className="bg-white border border-[#E4E4E7] rounded-md overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#F9FAFB] border-b border-[#E4E4E7] text-[#71717A] uppercase tracking-wider font-semibold">
            <tr>
              <th className="py-3 px-4">Product Details</th>
              <th className="py-3 px-4">Brand</th>
              <th className="py-3 px-4">SKU</th>
              <th className="py-3 px-4">Price (INR)</th>
              <th className="py-3 px-4">Stock</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4E4E7]">
            {loading ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-[#71717A]">
                  Loading catalog...
                </td>
              </tr>
            ) : products.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-[#71717A]">
                  No products found.
                </td>
              </tr>
            ) : (
              products.map((p) => (
                <tr key={p.id} className="hover:bg-zinc-50">
                  <td className="py-3 px-4 flex items-center gap-3">
                    <img
                      src={p.primary_image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80"}
                      alt=""
                      className="w-10 h-10 object-cover rounded border border-[#E4E4E7]"
                    />
                    <div>
                      <span className="font-bold text-[#18181B] block truncate max-w-[200px]">{p.name}</span>
                      <span className="text-[#71717A] text-[11px]">{p.category_name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-medium">{p.brand}</td>
                  <td className="py-3 px-4 font-mono text-[11px]">{p.sku}</td>
                  <td className="py-3 px-4 font-bold">
                    {p.effective_price}
                    {p.discount_price && <span className="text-[11px] text-[#71717A] line-through block">{p.price}</span>}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`font-bold ${p.stock <= 5 ? "text-[#DC2626]" : "text-[#18181B]"}`}>
                      {p.stock}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {p.is_active ? (
                      <span className="text-[11px] font-semibold text-[#047857] bg-[#ECFDF5] px-2 py-0.5 rounded">Active</span>
                    ) : (
                      <span className="text-[11px] font-semibold text-zinc-500 bg-zinc-100 px-2 py-0.5 rounded">Disabled</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <button
                      onClick={() => handleOpenEdit(p)}
                      className="p-1 hover:text-[#059669] text-zinc-500"
                      title="Edit Product"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="p-1 hover:text-[#DC2626] text-zinc-500"
                      title="Deactivate Product"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-md max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-base font-bold text-[#18181B]">
              {editProductId ? "Edit Product" : "Add New Catalog Product"}
            </h2>

            <form onSubmit={handleSaveProduct} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold block mb-1">Product Title</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full p-2 border border-[#E4E4E7] rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold block mb-1">SKU</label>
                  <input
                    type="text"
                    required
                    value={sku}
                    onChange={(e) => setSku(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded font-mono"
                  />
                </div>
                <div>
                  <label className="font-semibold block mb-1">Brand</label>
                  <input
                    type="text"
                    required
                    value={brand}
                    onChange={(e) => setBrand(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold block mb-1">Category</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  className="w-full p-2 border border-[#E4E4E7] rounded bg-white"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="font-semibold block mb-1">Base Price (INR)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded"
                  />
                </div>
                <div>
                  <label className="font-semibold block mb-1">Discount Price</label>
                  <input
                    type="number"
                    min="0"
                    value={discountPrice}
                    onChange={(e) => setDiscountPrice(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded"
                  />
                </div>
                <div>
                  <label className="font-semibold block mb-1">Available Stock</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={stock}
                    onChange={(e) => setStock(e.target.value)}
                    className="w-full p-2 border border-[#E4E4E7] rounded"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold block mb-1">Primary Image URL</label>
                <input
                  type="url"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="https://images.unsplash.com/..."
                  className="w-full p-2 border border-[#E4E4E7] rounded"
                />
              </div>

              <div>
                <label className="font-semibold block mb-1">Description & Specs</label>
                <textarea
                  required
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full p-2 border border-[#E4E4E7] rounded"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[#E4E4E7]">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3.5 py-1.5 text-zinc-600 hover:text-black"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalSubmitting}
                  className="px-4 py-1.5 bg-[#059669] hover:bg-[#047857] text-white font-semibold rounded"
                >
                  {modalSubmitting ? "Saving..." : "Save Product"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

