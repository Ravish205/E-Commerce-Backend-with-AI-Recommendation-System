import api from "./api";
import { ApiResponse, DashboardMetrics, Product } from "../types";

export const adminService = {
  async getDashboard(): Promise<DashboardMetrics> {
    const res = await api.get<ApiResponse<DashboardMetrics>>("/admin/dashboard");
    return res.data.data;
  },

  async getProducts(params?: any): Promise<{ products: Product[]; meta: any }> {
    const res = await api.get<ApiResponse<Product[]>>("/admin/products", { params });
    return {
      products: res.data.data,
      meta: res.data.meta,
    };
  },

  async createProduct(data: any): Promise<Product> {
    const res = await api.post<ApiResponse<Product>>("/admin/products", data);
    return res.data.data;
  },

  async updateProduct(id: string, data: any): Promise<Product> {
    const res = await api.put<ApiResponse<Product>>(`/admin/products/${id}`, data);
    return res.data.data;
  },

  async deleteProduct(id: string): Promise<void> {
    await api.delete(`/admin/products/${id}`);
  },

  async createCategory(data: any) {
    const res = await api.post("/admin/categories", data);
    return res.data.data;
  },

  async getOrders(params?: any) {
    const res = await api.get("/admin/orders", { params });
    return res.data;
  },

  async updateOrderStatus(orderId: string, status: string, trackingNumber?: string, notes?: string) {
    const res = await api.put(`/admin/orders/${orderId}/status`, {
      status,
      tracking_number: trackingNumber,
      notes,
    });
    return res.data.data;
  },

  async adjustInventory(productId: string, quantityChange: number, notes: string) {
    const res = await api.post("/admin/inventory/adjust", {
      product_id: productId,
      quantity_change: quantityChange,
      notes,
    });
    return res.data.data;
  },

  async getReviews(params?: any) {
    const res = await api.get("/admin/reviews", { params });
    return res.data;
  },

  async moderateReview(reviewId: string, isApproved: boolean) {
    const res = await api.put(`/admin/reviews/${reviewId}/status`, { is_approved: isApproved });
    return res.data.data;
  },

  async getCustomers(params?: any) {
    const res = await api.get("/admin/customers", { params });
    return res.data;
  },
};
