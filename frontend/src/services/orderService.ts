import api from "./api";
import { ApiResponse, Order } from "../types";

export const orderService = {
  async createOrder(payload: {
    shipping_address?: any;
    shipping_address_id?: string;
    coupon_code?: string;
    notes?: string;
  }): Promise<Order> {
    const res = await api.post<ApiResponse<Order>>("/orders", payload);
    return res.data.data;
  },

  async listOrders(page = 1, limit = 10): Promise<{ orders: Order[]; meta: any }> {
    const res = await api.get<ApiResponse<Order[]>>("/orders", { params: { page, limit } });
    return {
      orders: res.data.data,
      meta: res.data.meta,
    };
  },

  async getOrderDetail(idOrNumber: string): Promise<Order> {
    const res = await api.get<ApiResponse<Order>>(`/orders/${idOrNumber}`);
    return res.data.data;
  },

  async cancelOrder(orderId: string, reason?: string): Promise<Order> {
    const res = await api.post<ApiResponse<Order>>(`/orders/${orderId}/cancel`, { reason });
    return res.data.data;
  },

  async getInvoice(orderId: string): Promise<any> {
    const res = await api.get(`/orders/${orderId}/invoice`);
    return res.data.data;
  },

  // Payment
  async createPaymentOrder(orderId: string) {
    const res = await api.post("/payments/create-order", { order_id: orderId });
    return res.data.data;
  },

  async verifyPayment(payload: {
    order_id: string;
    gateway_order_id: string;
    gateway_payment_id: string;
    gateway_signature: string;
  }) {
    const res = await api.post("/payments/verify", payload);
    return res.data.data;
  },
};
