import api from "./api";
import { ApiResponse, Product } from "../types";

export const recommendationService = {
  async getTrending(limit = 8): Promise<Product[]> {
    const res = await api.get<ApiResponse<Product[]>>("/recommendations/trending", { params: { limit } });
    return res.data.data;
  },

  async getSimilar(productId: string, limit = 6): Promise<Product[]> {
    const res = await api.get<ApiResponse<Product[]>>(`/recommendations/similar/${productId}`, { params: { limit } });
    return res.data.data;
  },

  async getFrequentlyBoughtTogether(productId: string, limit = 4): Promise<Product[]> {
    const res = await api.get<ApiResponse<Product[]>>(`/recommendations/frequently-bought-together/${productId}`, { params: { limit } });
    return res.data.data;
  },

  async getPersonalized(limit = 8): Promise<Product[]> {
    const res = await api.get<ApiResponse<Product[]>>("/recommendations/personalized", { params: { limit } });
    return res.data.data;
  },

  async getRecentlyViewed(limit = 6): Promise<Product[]> {
    const res = await api.get<ApiResponse<Product[]>>("/recommendations/recently-viewed", { params: { limit } });
    return res.data.data;
  },

  async getPurchaseHistoryRecommendations(limit = 6): Promise<Product[]> {
    const res = await api.get<ApiResponse<Product[]>>("/recommendations/purchase-history", { params: { limit } });
    return res.data.data;
  },

  async trackInteraction(productId: string, interactionType: "view" | "search_click" | "wishlist_add" | "cart_add" | "purchase", dwellTime = 0) {
    try {
      await api.post("/recommendations/track-interaction", {
        product_id: productId,
        interaction_type: interactionType,
        dwell_time_seconds: dwellTime,
      });
    } catch {
      // Non-blocking interaction tracking
    }
  },
};
