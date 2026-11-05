from typing import Optional, List
from sqlalchemy.orm import joinedload
from backend.app.models.base import db
from backend.app.models.cart import Cart, CartItem, Wishlist, WishlistItem
from backend.app.models.catalog import Product

class CartRepository:
    @staticmethod
    def get_or_create_cart(user_id: Optional[str] = None, session_token: Optional[str] = None) -> Cart:
        cart = None
        if user_id:
            cart = Cart.query.options(
                joinedload(Cart.items).joinedload(CartItem.product).joinedload(Product.images)
            ).filter_by(user_id=user_id).first()
        elif session_token:
            cart = Cart.query.options(
                joinedload(Cart.items).joinedload(CartItem.product).joinedload(Product.images)
            ).filter_by(session_token=session_token).first()

        if not cart:
            cart = Cart(user_id=user_id, session_token=session_token if not user_id else None)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def get_cart_item(cart_id: str, product_id: str) -> Optional[CartItem]:
        return CartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first()

    @staticmethod
    def get_cart_item_by_id(item_id: str) -> Optional[CartItem]:
        return CartItem.query.filter_by(id=item_id).first()

    @staticmethod
    def add_or_update_item(cart_id: str, product_id: str, quantity: int) -> CartItem:
        item = CartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def set_item_quantity(item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        db.session.commit()
        return item

    @staticmethod
    def remove_item(item: CartItem) -> None:
        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def clear_cart(cart_id: str) -> None:
        CartItem.query.filter_by(cart_id=cart_id).delete()
        db.session.commit()

    # --- Wishlist Operations ---
    @staticmethod
    def get_or_create_wishlist(user_id: str) -> Wishlist:
        wishlist = Wishlist.query.options(
            joinedload(Wishlist.items).joinedload(WishlistItem.product).joinedload(Product.images)
        ).filter_by(user_id=user_id).first()
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            db.session.add(wishlist)
            db.session.commit()
        return wishlist

    @staticmethod
    def add_to_wishlist(wishlist_id: str, product_id: str) -> WishlistItem:
        item = WishlistItem.query.filter_by(wishlist_id=wishlist_id, product_id=product_id).first()
        if not item:
            item = WishlistItem(wishlist_id=wishlist_id, product_id=product_id)
            db.session.add(item)
            db.session.commit()
        return item

    @staticmethod
    def remove_from_wishlist(wishlist_id: str, product_id: str) -> bool:
        item = WishlistItem.query.filter_by(wishlist_id=wishlist_id, product_id=product_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
