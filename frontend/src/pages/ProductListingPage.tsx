import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Filter, SlidersHorizontal, ChevronLeft, ChevronRight, X } from "lucide-react";
import { catalogService, ProductQueryParams } from "../services/catalogService";
import { Category, Product } from "../types";
import { ProductCard } from "../components/product/ProductCard";

export const ProductListingPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [meta, setMeta] = useState<any>({ page: 1, limit: 12, total: 0, pages: 1 });
  const [loading, setLoading] = useState(true);

  // Filter state
  const currentCategory = searchParams.get("category_slug") || "";
  const currentSearch = searchParams.get("search") || "";
  const currentSort = searchParams.get("sort_by") || "newest";
  const minPrice = searchParams.get("min_price") || "";
  const maxPrice = searchParams.get("max_price") || "";
  const minRating = searchParams.get("min_rating") || "";
  const currentPage = parseInt(searchParams.get("page") || "1", 10);

  useEffect(() => {
    catalogService.getCategories().then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    async function loadProducts() {
      setLoading(true);
      try {
        const query: ProductQueryParams = {
          page: currentPage,
          limit: 12,
          category_slug: currentCategory || undefined,
          search: currentSearch || undefined,
          sort_by: currentSort as any,
          min_price: minPrice ? parseFloat(minPrice) : undefined,
          max_price: maxPrice ? parseFloat(maxPrice) : undefined,
          min_rating: minRating ? parseFloat(minRating) : undefined,
        };
        const res = await catalogService.getProducts(query);
        setProducts(res.products);
        setMeta(res.meta);
      } catch (err) {
        console.error("Error loading products", err);
      } finally {
        setLoading(false);
      }
    }
    loadProducts();
  }, [currentCategory, currentSearch, currentSort, minPrice, maxPrice, minRating, currentPage]);

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    next.set("page", "1");
    setSearchParams(next);
  };

  const clearFilters = () => {
    setSearchParams({});
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#E4E4E7]">
        <div>
          <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">
            {currentCategory
              ? categories.find((c) => c.slug === currentCategory)?.name || "Category Products"
              : currentSearch
              ? `Search Results for "${currentSearch}"`
              : "All Products"}
          </h1>
          <p className="text-xs text-[#71717A] mt-1">
            Showing {products.length} of {meta.total} available items
          </p>
        </div>

        {/* Sort Select */}
        <div className="flex items-center gap-3">
          <label className="text-xs font-medium text-[#71717A]">Sort By:</label>
          <select
            value={currentSort}
            onChange={(e) => updateParam("sort_by", e.target.value)}
            className="text-xs bg-white border border-[#E4E4E7] rounded-md px-3 py-1.5 focus:outline-none focus:border-[#059669]"
          >
            <option value="newest">Newest Arrivals</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="rating">Highest Rated</option>
            <option value="popularity">Most Popular</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filter Sidebar */}
        <aside className="space-y-6">
          <div className="bg-white border border-[#E4E4E7] rounded-md p-5 space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-[#E4E4E7]">
              <span className="text-sm font-bold text-[#18181B] flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4 text-[#059669]" />
                Filters
              </span>
              {(currentCategory || minPrice || maxPrice || minRating || currentSearch) && (
                <button
                  onClick={clearFilters}
                  className="text-xs font-semibold text-[#DC2626] hover:underline"
                >
                  Reset all
                </button>
              )}
            </div>

            {/* Category Filter */}
            <div>
              <h3 className="text-xs font-semibold text-[#18181B] uppercase tracking-wider mb-2">Category</h3>
              <div className="space-y-1.5">
                <button
                  onClick={() => updateParam("category_slug", "")}
                  className={`block text-xs w-full text-left py-1 px-2 rounded ${
                    !currentCategory ? "bg-[#ECFDF5] text-[#047857] font-semibold" : "text-[#71717A] hover:bg-zinc-50"
                  }`}
                >
                  All Categories
                </button>
                {categories.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => updateParam("category_slug", c.slug)}
                    className={`block text-xs w-full text-left py-1 px-2 rounded ${
                      currentCategory === c.slug
                        ? "bg-[#ECFDF5] text-[#047857] font-semibold"
                        : "text-[#71717A] hover:bg-zinc-50"
                    }`}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Price Filter */}
            <div>
              <h3 className="text-xs font-semibold text-[#18181B] uppercase tracking-wider mb-2">Price (INR)</h3>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={minPrice}
                  onChange={(e) => updateParam("min_price", e.target.value)}
                  className="text-xs p-1.5 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
                <input
                  type="number"
                  placeholder="Max"
                  value={maxPrice}
                  onChange={(e) => updateParam("max_price", e.target.value)}
                  className="text-xs p-1.5 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>
            </div>

            {/* Rating Filter */}
            <div>
              <h3 className="text-xs font-semibold text-[#18181B] uppercase tracking-wider mb-2">Customer Rating</h3>
              <div className="space-y-1 text-xs">
                {[4, 3, 2].map((stars) => (
                  <button
                    key={stars}
                    onClick={() => updateParam("min_rating", minRating === stars.toString() ? "" : stars.toString())}
                    className={`block w-full text-left py-1 px-2 rounded ${
                      minRating === stars.toString()
                        ? "bg-[#ECFDF5] text-[#047857] font-semibold"
                        : "text-[#71717A] hover:bg-zinc-50"
                    }`}
                  >
                    {stars} Stars & above
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Product Grid Area */}
        <div className="lg:col-span-3 space-y-6">
          {loading ? (
            <div className="py-20 text-center text-sm text-[#71717A]">Loading catalog products...</div>
          ) : products.length === 0 ? (
            <div className="bg-white border border-[#E4E4E7] rounded-md p-12 text-center">
              <h3 className="text-base font-semibold text-[#18181B] mb-2">No products matched your criteria</h3>
              <p className="text-xs text-[#71717A] mb-4">Try clearing filters or checking for typos in your search query.</p>
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-xs font-semibold bg-[#059669] text-white rounded-md hover:bg-[#047857]"
              >
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
              {products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          {meta.pages > 1 && (
            <div className="flex items-center justify-between pt-6 border-t border-[#E4E4E7]">
              <button
                onClick={() => updateParam("page", Math.max(1, currentPage - 1).toString())}
                disabled={currentPage <= 1}
                className="flex items-center gap-1 text-xs font-medium px-3 py-1.5 border border-[#E4E4E7] rounded bg-white disabled:opacity-40"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                Previous
              </button>

              <span className="text-xs text-[#71717A]">
                Page {currentPage} of {meta.pages}
              </span>

              <button
                onClick={() => updateParam("page", Math.min(meta.pages, currentPage + 1).toString())}
                disabled={currentPage >= meta.pages}
                className="flex items-center gap-1 text-xs font-medium px-3 py-1.5 border border-[#E4E4E7] rounded bg-white disabled:opacity-40"
              >
                Next
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

