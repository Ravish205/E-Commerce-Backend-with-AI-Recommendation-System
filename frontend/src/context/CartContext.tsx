import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { cartService } from "../services/cartService";
import { recommendationService } from "../services/recommendationService";
import { CartSummary, Product } from "../types";
import { useAuth } from "./AuthContext";

interface CartContextType {
  cart: CartSummary | null;
  loading: boolean;
  wishlist: Product[];
  refreshCart: () => Promise<void>;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  toggleWishlist: (product: Product) => Promise<void>;
  isInWishlist: (productId: string) => boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<CartSummary | null>(null);
  const [wishlist, setWishlist] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { isAuthenticated } = useAuth();

  const refreshCart = useCallback(async () => {
    try {
      const summary = await cartService.getCart();
      setCart(summary);
    } catch {
      // Ignore initial guest fetch errors
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshWishlist = useCallback(async () => {
    if (isAuthenticated) {
      try {
        const items = await cartService.getWishlist();
        setWishlist(items);
      } catch {
        setWishlist([]);
      }
    } else {
      setWishlist([]);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshCart();
    refreshWishlist();
  }, [refreshCart, refreshWishlist]);

  const addToCart = async (productId: string, quantity = 1) => {
    const updated = await cartService.addToCart(productId, quantity);
    setCart(updated);
    recommendationService.trackInteraction(productId, "cart_add");
  };

  const updateQuantity = async (itemId: string, quantity: number) => {
    const updated = await cartService.updateQuantity(itemId, quantity);
    setCart(updated);
  };

  const removeItem = async (itemId: string) => {
    const updated = await cartService.removeItem(itemId);
    setCart(updated);
  };

  const clearCart = async () => {
    await cartService.clearCart();
    await refreshCart();
  };

  const toggleWishlist = async (product: Product) => {
    const exists = wishlist.some((item) => item.id === product.id);
    if (exists) {
      await cartService.removeFromWishlist(product.id);
      setWishlist((prev) => prev.filter((item) => item.id !== product.id));
    } else {
      await cartService.addToWishlist(product.id);
      setWishlist((prev) => [...prev, product]);
      recommendationService.trackInteraction(product.id, "wishlist_add");
    }
  };

  const isInWishlist = (productId: string) => {
    return wishlist.some((item) => item.id === productId);
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        wishlist,
        refreshCart,
        addToCart,
        updateQuantity,
        removeItem,
        clearCart,
        toggleWishlist,
        isInWishlist,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};
