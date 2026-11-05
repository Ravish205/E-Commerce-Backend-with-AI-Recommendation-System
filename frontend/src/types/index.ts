export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: "customer" | "admin";
  phone_number?: string | null;
  is_active: boolean;
  is_email_verified: boolean;
  created_at?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
}

export interface Address {
  id: string;
  address_type: "shipping" | "billing";
  recipient_name: string;
  phone: string;
  street_address: string;
  landmark?: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface Category {
  id: string;
  parent_id?: string | null;
  name: string;
  slug: string;
  description?: string | null;
  image_url?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface ProductAttribute {
  id?: string;
  attribute_name: string;
  attribute_value: string;
}

export interface ProductImage {
  id?: string;
  image_url: string;
  alt_text?: string | null;
  display_order: number;
  is_primary: boolean;
}

export interface Product {
  id: string;
  category_id: string;
  category_name?: string | null;
  category_slug?: string | null;
  name: string;
  slug: string;
  sku: string;
  brand: string;
  short_description?: string | null;
  description?: string;
  price: number;
  discount_price?: number | null;
  effective_price: number;
  stock: number;
  is_in_stock: boolean;
  average_rating: number;
  reviews_count: number;
  is_active: boolean;
  is_featured: boolean;
  primary_image?: string | null;
  images?: ProductImage[];
  attributes?: ProductAttribute[];
  created_at?: string;
  recommendation_score?: number;
  recommendation_reason?: string;
}

export interface CartLineItem {
  item_id: string;
  product_id: string;
  name: string;
  slug: string;
  sku: string;
  brand: string;
  unit_price: number;
  original_price: number;
  quantity: number;
  item_total: number;
  stock: number;
  is_in_stock: boolean;
  primary_image?: string | null;
}

export interface CartSummary {
  cart_id: string;
  items: CartLineItem[];
  items_count: number;
  subtotal: number;
  discount_amount: number;
  coupon?: {
    code: string;
    discount_type: "percentage" | "fixed_amount";
    discount_value: number;
    discount_amount: number;
  } | null;
  tax_amount: number;
  shipping_amount: number;
  final_total: number;
  free_shipping_threshold: number;
  is_checkout_ready: boolean;
  warnings: string[];
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  sku: string;
  unit_price: number;
  quantity: number;
  total_price: number;
  primary_image?: string | null;
}

export interface Order {
  id: string;
  order_number: string;
  user_id: string;
  status: "pending" | "confirmed" | "processing" | "shipped" | "delivered" | "cancelled" | "refunded";
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  shipping_amount: number;
  total_amount: number;
  coupon_code?: string | null;
  shipping_address: Record<string, any>;
  billing_address?: Record<string, any>;
  tracking_number?: string | null;
  notes?: string | null;
  created_at?: string;
  cancelled_at?: string | null;
  cancellation_reason?: string | null;
  items?: OrderItem[];
  payments?: any[];
}

export interface Review {
  id: string;
  product_id: string;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  is_verified_purchase: boolean;
  created_at: string;
}

export interface DashboardMetrics {
  total_customers: number;
  total_products: number;
  total_orders: number;
  total_revenue: number;
  pending_orders: number;
  low_stock_count: number;
  low_stock_products: Array<{
    id: string;
    name: string;
    sku: string;
    stock: number;
    low_stock_threshold: number;
  }>;
  recent_orders: Array<{
    id: string;
    order_number: string;
    customer_name: string;
    status: string;
    total_amount: number;
    created_at: string;
  }>;
  sales_time_series: Array<{
    date: string;
    revenue: number;
    orders: number;
  }>;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  meta?: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
  errors?: any;
}
