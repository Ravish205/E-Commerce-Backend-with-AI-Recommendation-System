# REST API Specification

## 1. Global Standards & Conventions

- **Base URL**: `/api/v1`
- **Content Type**: `application/json`
- **Authentication**: Bearer JWT in `Authorization: Bearer <access_token>` or via secure HTTP-only cookies.
- **Status Codes**:
  - `200 OK`: Request succeeded.
  - `201 Created`: Resource created.
  - `400 Bad Request`: Validation failure or business logic violation.
  - `401 Unauthorized`: Authentication missing, expired, or invalid.
  - `403 Forbidden`: Insufficient role permissions (e.g. non-admin accessing admin routes).
  - `404 Not Found`: Requested resource does not exist.
  - `409 Conflict`: Conflict with current state (e.g., email already registered, concurrent stock deduction).
  - `422 Unprocessable Entity`: Request body syntax valid, but semantic validation failed.
  - `429 Too Many Requests`: Rate limit exceeded.
  - `500 Internal Server Error`: Unhandled server exception.

All responses use the standard JSON envelope:
```json
{
  "success": true,
  "message": "Human readable status message",
  "data": { ... },
  "meta": { "page": 1, "limit": 20, "total": 100, "pages": 5 }
}
```

---

## 2. API Endpoints Catalog

### A. Authentication & User Profile (`/api/auth`, `/api/users`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Public | Register new customer account |
| `POST` | `/api/auth/login` | Public | Authenticate user & return JWT tokens |
| `POST` | `/api/auth/refresh` | Auth (Refresh) | Issue new access token using refresh token |
| `POST` | `/api/auth/logout` | Auth | Revoke active tokens |
| `POST` | `/api/auth/forgot-password` | Public | Request password reset email |
| `POST` | `/api/auth/reset-password` | Public | Complete password reset with token |
| `POST` | `/api/auth/verify-email` | Public | Verify email address with token |
| `GET` | `/api/auth/me` | Auth | Get current authenticated user profile |
| `PUT` | `/api/users/profile` | Auth | Update name, phone, preferences |
| `PUT` | `/api/users/change-password` | Auth | Change password with current password confirmation |
| `GET` | `/api/users/addresses` | Auth | List saved shipping/billing addresses |
| `POST` | `/api/users/addresses` | Auth | Create a new address |
| `PUT` | `/api/users/addresses/{id}` | Auth | Update address |
| `DELETE` | `/api/users/addresses/{id}` | Auth | Delete address |

### B. Catalog & Products (`/api/categories`, `/api/products`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/categories` | Public | List active category tree |
| `GET` | `/api/categories/{slug}` | Public | Get category details and subcategories |
| `GET` | `/api/products` | Public | List products with pagination, search, filters (`category`, `brand`, `min_price`, `max_price`, `min_rating`, `sort_by`: `price_asc`, `price_desc`, `newest`, `popularity`, `rating`) |
| `GET` | `/api/products/{id_or_slug}` | Public | Get full product detail with gallery, attributes, stock status, verified review summaries |
| `GET` | `/api/products/{id}/reviews` | Public | Paginated list of approved reviews for product |

### C. Shopping Cart (`/api/cart`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/cart` | Public/Auth | Retrieve active cart with line items, subtotal, tax, shipping, discount, final total |
| `POST` | `/api/cart/items` | Public/Auth | Add product to cart with quantity (validates stock) |
| `PUT` | `/api/cart/items/{item_id}` | Public/Auth | Update quantity of a line item |
| `DELETE` | `/api/cart/items/{item_id}` | Public/Auth | Remove item from cart |
| `DELETE` | `/api/cart` | Public/Auth | Clear entire cart |
| `POST` | `/api/cart/apply-coupon` | Public/Auth | Validate and apply promo code |
| `DELETE` | `/api/cart/remove-coupon` | Public/Auth | Remove applied promo code |

### D. Wishlist (`/api/wishlist`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/wishlist` | Auth | List user's saved wishlist products |
| `POST` | `/api/wishlist/{product_id}` | Auth | Add product to wishlist |
| `DELETE` | `/api/wishlist/{product_id}` | Auth | Remove product from wishlist |
| `POST` | `/api/wishlist/{product_id}/move-to-cart`| Auth | Move item from wishlist to active cart |

### E. Orders & Checkout (`/api/orders`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/orders` | Auth | Create order from cart items; locks inventory and generates order record with status `pending` |
| `GET` | `/api/orders` | Auth | Paginated order history for authenticated customer |
| `GET` | `/api/orders/{id_or_number}` | Auth | Get order breakdown, tracking timeline, item snapshot |
| `POST` | `/api/orders/{id}/cancel` | Auth | Cancel order (eligible only before shipment); triggers stock restitution |
| `GET` | `/api/orders/{id}/invoice` | Auth | Download structured PDF/HTML invoice |

### F. Payments (`/api/payments`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/payments/create-order` | Auth | Create gateway order with Razorpay/Stripe for given `order_id` |
| `POST` | `/api/payments/verify` | Auth | Verify payment signature (`razorpay_signature` or Stripe confirmation) and transition order to `confirmed` |
| `POST` | `/api/payments/webhook` | Public (Signed) | Process asynchronous webhooks from payment gateway |
| `POST` | `/api/payments/refund` | Admin | Initiate partial or full refund for an order |

### G. Reviews & Ratings (`/api/reviews`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/reviews` | Auth | Submit rating and review (enforces verified purchase check) |
| `PUT` | `/api/reviews/{id}` | Auth | Edit submitted review |
| `DELETE` | `/api/reviews/{id}` | Auth | Delete own review |
| `POST` | `/api/reviews/{id}/report` | Auth | Report inappropriate review |

### H. AI Recommendations & Behavior Tracking (`/api/recommendations`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/recommendations/personalized` | Auth/Public | Personalized recommendations based on hybrid model (falls back to trending for cold start) |
| `GET` | `/api/recommendations/similar/{product_id}` | Public | Content-based recommendations using TF-IDF and attribute cosine similarity |
| `GET` | `/api/recommendations/trending` | Public | Top performing products based on weighted views, carts, and purchases over last 30 days |
| `GET` | `/api/recommendations/frequently-bought-together/{product_id}` | Public | Collaborative item-item basket co-occurrence recommendations |
| `GET` | `/api/recommendations/recently-viewed` | Auth/Public | Retrieve customer's recently viewed products from interaction feed |
| `GET` | `/api/recommendations/purchase-history` | Auth | Recommendations derived from past verified purchase categories and brands |
| `POST` | `/api/recommendations/track-interaction` | Public/Auth | Ingest user behavior events (`view`, `search_click`, `cart_add`, `wishlist_add`) with session metadata |

### I. Administration (`/api/admin`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/admin/dashboard` | Admin | Real metrics: total registered customers, total catalog products, total orders, real completed revenue, low stock alerts, 30-day sales time series |
| `GET` | `/api/admin/products` | Admin | Full product list with inventory balances and management flags |
| `POST` | `/api/admin/products` | Admin | Create product with images and attributes |
| `PUT` | `/api/admin/products/{id}` | Admin | Update product information, price, inventory |
| `DELETE` | `/api/admin/products/{id}` | Admin | Deactivate / delete product |
| `POST` | `/api/admin/categories` | Admin | Create category |
| `PUT` | `/api/admin/categories/{id}` | Admin | Update category |
| `DELETE` | `/api/admin/categories/{id}` | Admin | Delete category |
| `GET` | `/api/admin/orders` | Admin | View all system orders with status filter |
| `PUT` | `/api/admin/orders/{id}/status` | Admin | Update order status (`confirmed`, `processing`, `shipped`, `delivered`, `cancelled`) |
| `GET` | `/api/admin/inventory/transactions` | Admin | Audit log of all stock movements |
| `POST` | `/api/admin/inventory/adjust` | Admin | Manual inventory adjustment with mandatory audit note |
| `GET` | `/api/admin/customers` | Admin | Customer directory with order counts and lifetime value |
| `PUT` | `/api/admin/customers/{id}/status` | Admin | Activate or suspend customer account |
| `GET` | `/api/admin/reviews` | Admin | Review moderation queue |
| `PUT` | `/api/admin/reviews/{id}/status` | Admin | Approve or reject customer review |
| `GET` | `/api/admin/coupons` | Admin | List promotional coupons |
| `POST` | `/api/admin/coupons` | Admin | Create promo coupon |
| `PUT` | `/api/admin/coupons/{id}` | Admin | Edit or toggle coupon status |

