import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, Heart, Search, User as UserIcon, LogOut, Shield, Sparkles } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useCart } from "../../context/CartContext";

export const Navbar: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const { cart, wishlist } = useCart();
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  const cartCount = cart?.items_count || 0;
  const wishlistCount = wishlist.length;

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-[#E4E4E7]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2 flex-shrink-0">
            <span className="text-xl font-bold tracking-tight text-[#18181B]">
              Apex<span className="text-[#059669]">Store</span>
            </span>
          </Link>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="flex-1 max-w-lg hidden md:block">
            <div className="relative">
              <input
                type="text"
                placeholder="Search products, brands, categories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm bg-[#F9FAFB] border border-[#E4E4E7] rounded-md focus:outline-none focus:border-[#059669] focus:bg-white transition-colors"
              />
              <Search className="w-4 h-4 text-[#71717A] absolute left-3 top-2.5" />
            </div>
          </form>

          {/* Navigation Links & Actions */}
          <nav className="flex items-center gap-5 text-sm font-medium text-[#71717A]">
            <Link to="/products" className="hover:text-[#18181B] transition-colors">
              Catalog
            </Link>
            <Link to="/recommendations" className="hover:text-[#059669] flex items-center gap-1.5 transition-colors text-[#059669]">
              <Sparkles className="w-4 h-4" />
              <span>For You</span>
            </Link>

            {/* Wishlist */}
            <Link to="/wishlist" className="relative p-1.5 hover:text-[#18181B] transition-colors" title="Wishlist">
              <Heart className="w-5 h-5" />
              {wishlistCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#059669] text-white text-[11px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                  {wishlistCount}
                </span>
              )}
            </Link>

            {/* Cart */}
            <Link to="/cart" className="relative p-1.5 hover:text-[#18181B] transition-colors" title="Shopping Cart">
              <ShoppingCart className="w-5 h-5" />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#059669] text-white text-[11px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>

            {/* Auth Dropdown / Buttons */}
            {isAuthenticated ? (
              <div className="flex items-center gap-3 pl-2 border-l border-[#E4E4E7]">
                {isAdmin && (
                  <Link
                    to="/admin/dashboard"
                    className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1.5 bg-[#18181B] text-white rounded-md hover:bg-black transition-colors"
                  >
                    <Shield className="w-3.5 h-3.5" />
                    <span>Admin</span>
                  </Link>
                )}
                <Link to="/profile" className="flex items-center gap-1.5 hover:text-[#18181B] transition-colors">
                  <UserIcon className="w-4 h-4" />
                  <span className="hidden sm:inline">{user?.first_name}</span>
                </Link>
                <button
                  onClick={logout}
                  className="p-1.5 hover:text-[#DC2626] transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 pl-2 border-l border-[#E4E4E7]">
                <Link
                  to="/login"
                  className="px-3 py-1.5 text-sm font-medium text-[#18181B] hover:text-[#059669] transition-colors"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="px-3.5 py-1.5 text-sm font-medium text-white bg-[#059669] hover:bg-[#047857] rounded-md transition-colors"
                >
                  Sign up
                </Link>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

