import React from "react";
import { Link, Outlet, useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Package,
  Layers,
  ShoppingCart,
  Boxes,
  MessageSquare,
  Users,
  LogOut,
  Store,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const AdminLayout: React.FC = () => {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (!isAdmin) {
    navigate("/login");
    return null;
  }

  const navItems = [
    { label: "Dashboard", path: "/admin/dashboard", icon: LayoutDashboard },
    { label: "Products", path: "/admin/products", icon: Package },
    { label: "Orders", path: "/admin/orders", icon: ShoppingCart },
    { label: "Inventory", path: "/admin/inventory", icon: Boxes },
    { label: "Reviews", path: "/admin/reviews", icon: MessageSquare },
    { label: "Customers", path: "/admin/customers", icon: Users },
  ];

  return (
    <div className="min-h-screen flex bg-[#F9FAFB]">
      {/* Sidebar */}
      <aside className="w-64 bg-[#18181B] text-white flex flex-col justify-between flex-shrink-0">
        <div>
          {/* Brand header */}
          <div className="h-16 flex items-center px-6 border-b border-zinc-800">
            <Link to="/admin/dashboard" className="text-lg font-bold tracking-tight">
              Apex<span className="text-[#059669]">Admin</span>
            </Link>
          </div>

          {/* Navigation links */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-3.5 py-2.5 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? "bg-[#059669] text-white"
                      : "text-zinc-400 hover:text-white hover:bg-zinc-800"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User profile & exit */}
        <div className="p-4 border-t border-zinc-800 space-y-2">
          <Link
            to="/"
            className="flex items-center gap-3 px-3.5 py-2 text-xs font-medium text-zinc-400 hover:text-white rounded-md transition-colors"
          >
            <Store className="w-4 h-4" />
            <span>View Public Store</span>
          </Link>

          <div className="pt-2 flex items-center justify-between text-xs text-zinc-400">
            <span className="truncate">{user?.email}</span>
            <button
              onClick={logout}
              className="p-1 hover:text-[#DC2626] transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-x-hidden">
        <header className="h-16 bg-white border-b border-[#E4E4E7] px-8 flex items-center justify-between">
          <h1 className="text-base font-semibold text-[#18181B]">Administration Workspace</h1>
          <span className="text-xs bg-[#ECFDF5] text-[#047857] px-2.5 py-1 rounded font-medium">
            Active Store Database
          </span>
        </header>

        <main className="p-8 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
