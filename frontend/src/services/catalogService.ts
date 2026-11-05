import api from "./api";
import { ApiResponse, Category, Product } from "../types";

export interface ProductQueryParams {
  page?: number;
  limit?: number;
  category_id?: string;
  category_slug?: string;
  search?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
  sort_by?: "newest" | "price_asc" | "price_desc" | "rating" | "popularity";
}

export const catalogService = {
  async getCategories(): Promise<Category[]> {
    const res = await api.get<ApiResponse<Category[]>>("/categories");
    return res.data.data;
  },

  async getProducts(params?: ProductQueryParams): Promise<{ products: Product[]; meta: any }> {
    const res = await api.get<ApiResponse<Product[]>>("/products", { params });
    return {
      products: res.data.data,
      meta: res.data.meta,
    };
  },

  async getProductDetail(idOrSlug: string): Promise<Product> {
    const res = await api.get<ApiResponse<Product>>(`/products/${idOrSlug}`);
    return res.data.data;
  },

  async getProductReviews(productId: string, page = 1, limit = 10) {
    const res = await api.get(`/products/${productId}/reviews`, { params: { page, limit } });
    return res.data;
  },

  async submitReview(productId: string, rating: number, title: string, comment: string) {
    const res = await api.post("/reviews", {
      product_id: productId,
      rating,
      title,
      comment,
    });
    return res.data;
  },
};
