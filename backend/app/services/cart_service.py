from typing import Optional, Dict, Any, Tuple
from backend.app.models.cart import Cart, CartItem
from backend.app.repositories.cart_repo import CartRepository
from backend.app.repositories.catalog_repo import CatalogRepository
from backend.app.repositories.order_repo import OrderRepository

TAX_RATE = 0.18  # 18% GST
FREE_SHIPPING_THRESHOLD = 1000.00
STANDARD_SHIPPING_FEE = 100.00

class CartService:
    @staticmethod
    def calculate_cart_summary(cart: Cart, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        """Calculates accurate cart totals strictly from server-side database records."""
        subtotal = 0.0
        line_items = []
        is_checkout_ready = True
        warnings = []

        for item in cart.items:
            product = item.product
            if not product or not product.is_active:
                warnings.append(f"Product '{item.product_id}' is no longer available.")
                is_checkout_ready = False
                continue

            unit_price = product.effective_price
            item_total = round(unit_price * item.quantity, 2)
            subtotal += item_total

            stock_available = product.stock
            is_in_stock = stock_available >= item.quantity

            if not is_in_stock:
                is_checkout_ready = False
                if stock_available <= 0:
                    warnings.append(f"'{product.name}' is out of stock.")
                else:
                    warnings.append(f"Only {stock_available} units of '{product.name}' are available (you requested {item.quantity}).")

            line_items.append({
                "item_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "slug": product.slug,
                "sku": product.sku,
                "brand": product.brand,
                "unit_price": unit_price,
                "original_price": float(product.price),
                "quantity": item.quantity,
                "item_total": item_total,
                "stock": stock_available,
                "is_in_stock": is_in_stock,
                "primary_image": product.primary_image,
            })

        subtotal = round(subtotal, 2)

        # Coupon Discount calculation
        discount_amount = 0.0
        applied_coupon = None

        if coupon_code and subtotal > 0:
            coupon = OrderRepository.get_coupon_by_code(coupon_code)
            if coupon:
                if subtotal >= float(coupon.min_order_amount):
                    if coupon.discount_type == "percentage":
                        raw_discount = subtotal * (float(coupon.discount_value) / 100.0)
                        if coupon.max_discount:
                            discount_amount = min(raw_discount, float(coupon.max_discount))
                        else:
                            discount_amount = raw_discount
                    else:  # fixed_amount
                        discount_amount = min(float(coupon.discount_value), subtotal)

                    discount_amount = round(discount_amount, 2)
                    applied_coupon = {
                        "code": coupon.code,
                        "discount_type": coupon.discount_type,
                        "discount_value": float(coupon.discount_value),
                        "discount_amount": discount_amount,
                    }
                else:
                    warnings.append(f"Coupon '{coupon_code}' requires a minimum order of INR {coupon.min_order_amount}.")
            else:
                warnings.append(f"Coupon '{coupon_code}' is invalid or expired.")

        # Tax calculation
        taxable_amount = max(0.0, subtotal - discount_amount)
        tax_amount = round(taxable_amount * TAX_RATE, 2)

        # Shipping calculation
        shipping_amount = 0.00 if (taxable_amount >= FREE_SHIPPING_THRESHOLD or subtotal == 0) else STANDARD_SHIPPING_FEE

        final_total = round(taxable_amount + tax_amount + shipping_amount, 2)

        return {
            "cart_id": cart.id,
            "items": line_items,
            "items_count": sum(item["quantity"] for item in line_items),
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "coupon": applied_coupon,
            "tax_amount": tax_amount,
            "shipping_amount": shipping_amount,
            "final_total": final_total,
            "free_shipping_threshold": FREE_SHIPPING_THRESHOLD,
            "is_checkout_ready": is_checkout_ready and len(line_items) > 0,
            "warnings": warnings,
        }

    @staticmethod
    def get_cart(user_id: Optional[str] = None, session_token: Optional[str] = None, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        cart = CartRepository.get_or_create_cart(user_id=user_id, session_token=session_token)
        return CartService.calculate_cart_summary(cart, coupon_code=coupon_code)

    @staticmethod
    def add_to_cart(product_id: str, quantity: int = 1, user_id: Optional[str] = None, session_token: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        product = CatalogRepository.get_product_by_id(product_id, active_only=True)
        if not product:
            return False, "Product not found or unavailable", None

        cart = CartRepository.get_or_create_cart(user_id=user_id, session_token=session_token)
        existing_item = CartRepository.get_cart_item(cart.id, product_id)
        current_qty = existing_item.quantity if existing_item else 0

        if current_qty + quantity > product.stock:
            return False, f"Cannot add {quantity} units. Only {product.stock} units are currently in stock (you have {current_qty} in cart).", None

        CartRepository.add_or_update_item(cart.id, product_id, quantity)
        return True, f"Added {quantity} unit(s) of '{product.name}' to cart", CartService.calculate_cart_summary(cart)

    @staticmethod
    def update_cart_item_quantity(item_id: str, quantity: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        item = CartRepository.get_cart_item_by_id(item_id)
        if not item:
            return False, "Cart item not found", None

        product = item.product
        if not product or not product.is_active:
            CartRepository.remove_item(item)
            return False, "Product is no longer available and was removed from your cart", None

        if quantity > product.stock:
            return False, f"Only {product.stock} units are available in stock", None

        CartRepository.set_item_quantity(item, quantity)
        cart = Cart.query.filter_by(id=item.cart_id).first()
        return True, "Cart updated", CartService.calculate_cart_summary(cart)

    @staticmethod
    def remove_cart_item(item_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        item = CartRepository.get_cart_item_by_id(item_id)
        if not item:
            return False, "Cart item not found", None

        cart_id = item.cart_id
        CartRepository.remove_item(item)
        cart = Cart.query.filter_by(id=cart_id).first()
        return True, "Item removed from cart", CartService.calculate_cart_summary(cart)

    @staticmethod
    def clear_cart(user_id: Optional[str] = None, session_token: Optional[str] = None) -> Tuple[bool, str]:
        cart = CartRepository.get_or_create_cart(user_id=user_id, session_token=session_token)
        CartRepository.clear_cart(cart.id)
        return True, "Cart cleared"
