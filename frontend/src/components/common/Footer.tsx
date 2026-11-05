import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Truck, RefreshCw, Headphones } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-[#E4E4E7] mt-16">
      {/* Trust Badges */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-b border-[#E4E4E7]">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="flex items-center gap-3">
            <Truck className="w-5 h-5 text-[#059669] flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-[#18181B]">Free Express Delivery</h4>
              <p className="text-xs text-[#71717A]">On orders over INR 1,000</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-[#059669] flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-[#18181B]">Authentic Products</h4>
              <p className="text-xs text-[#71717A]">100% manufacturer warranty</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <RefreshCw className="w-5 h-5 text-[#059669] flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-[#18181B]">7-Day Return Policy</h4>
              <p className="text-xs text-[#71717A]">Hassle-free verified returns</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Headphones className="w-5 h-5 text-[#059669] flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-[#18181B]">Dedicated Support</h4>
              <p className="text-xs text-[#71717A]">Direct customer assistance</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-sm font-semibold text-[#18181B] tracking-wider uppercase mb-3">
              Shop Categories
            </h3>
            <ul className="space-y-2 text-sm text-[#71717A]">
              <li><Link to="/products?category_slug=audio-headphones" className="hover:text-[#18181B]">Audio & Headphones</Link></li>
              <li><Link to="/products?category_slug=laptops-computing" className="hover:text-[#18181B]">Laptops & Computing</Link></li>
              <li><Link to="/products?category_slug=smartphones-tablets" className="hover:text-[#18181B]">Smartphones & Tablets</Link></li>
              <li><Link to="/products?category_slug=smart-home-wearables" className="hover:text-[#18181B]">Smart Home & Wearables</Link></li>
              <li><Link to="/products?category_slug=photography-video" className="hover:text-[#18181B]">Photography & Video</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#18181B] tracking-wider uppercase mb-3">
              Customer Account
            </h3>
            <ul className="space-y-2 text-sm text-[#71717A]">
              <li><Link to="/profile" className="hover:text-[#18181B]">My Profile</Link></li>
              <li><Link to="/orders" className="hover:text-[#18181B]">Track Orders</Link></li>
              <li><Link to="/wishlist" className="hover:text-[#18181B]">Saved Wishlist</Link></li>
              <li><Link to="/recommendations" className="hover:text-[#18181B]">Personalized Feed</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#18181B] tracking-wider uppercase mb-3">
              Legal & Compliance
            </h3>
            <ul className="space-y-2 text-sm text-[#71717A]">
              <li><Link to="/privacy-policy" className="hover:text-[#18181B]">Privacy Policy</Link></li>
              <li><Link to="/terms-and-conditions" className="hover:text-[#18181B]">Terms & Conditions</Link></li>
              <li><Link to="/contact" className="hover:text-[#18181B]">Contact & Support</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-[#18181B] tracking-wider uppercase mb-3">
              About ApexStore
            </h3>
            <p className="text-sm text-[#71717A] leading-relaxed">
              Enterprise e-commerce platform offering genuine consumer technology, transparent pricing, and personalized machine-learning product discovery.
            </p>
          </div>
        </div>

        <div className="border-t border-[#E4E4E7] mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-[#71717A] gap-4">
          <p>&copy; {new Date().getFullYear()} ApexStore Inc. All rights reserved.</p>
          <div className="flex gap-4">
            <Link to="/privacy-policy" className="hover:underline">Privacy</Link>
            <Link to="/terms-and-conditions" className="hover:underline">Terms</Link>
            <Link to="/contact" className="hover:underline">Contact</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

