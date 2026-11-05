import api from "./api";
import { ApiResponse, CartSummary, Product } from "../types";

export const cartService = {
  async getCart(couponCode?: string): Promise<CartSummary> {
    const res = await api.get<ApiResponse<CartSummary>>("/cart", {
      params: couponCode ? { coupon_code: couponCode } : {},
    });
    return res.data.data;
  },

  async addToCart(productId: string, quantity = 1): Promise<CartSummary> {
    const res = await api.post<ApiResponse<CartSummary>>("/cart/items", {
      product_id: productId,
      quantity,
    });
    return res.data.data;
  },

  async updateQuantity(itemId: string, quantity: number): Promise<CartSummary> {
    const res = await api.put<ApiResponse<CartSummary>>(`/cart/items/${itemId}`, { quantity });
    return res.data.data;
  },

  async removeItem(itemId: string): Promise<CartSummary> {
    const res = await api.delete<ApiResponse<CartSummary>>(`/cart/items/${itemId}`);
    return res.data.data;
  },

  async clearCart(): Promise<void> {
    await api.delete("/cart");
  },

  // Wishlist
  async getWishlist(): Promise<Product[]> {
    const res = await api.get<ApiResponse<{ items: Product[] }>>("/wishlist");
    return res.data.data.items;
  },

  async addToWishlist(productId: string): Promise<void> {
    await api.post(`/wishlist/${productId}`);
  },

  async removeFromWishlist(productId: string): Promise<void> {
    await api.delete(`/wishlist/${productId}`);
  },

  async moveWishlistToCart(productId: string): Promise<CartSummary> {
    const res = await api.post<ApiResponse<CartSummary>>(`/wishlist/${productId}/move-to-cart`);
    return res.data.data;
  },
};
