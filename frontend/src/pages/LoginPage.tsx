import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Lock, Mail, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirect = searchParams.get("redirect") || "/";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const user = await login(email, password);
      if (user.role === "admin") {
        navigate("/admin/dashboard");
      } else {
        navigate(redirect);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 bg-white border border-[#E4E4E7] rounded-md p-8 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Log In to Your Account</h1>
        <p className="text-xs text-[#71717A] mt-1">Enter your credentials to access your orders and recommendations</p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-[#DC2626] text-xs rounded border border-red-200">
          {error}
        </div>
      )}

      {/* Quick Demo Credentials Box */}
      <div className="p-3 bg-[#F9FAFB] border border-[#E4E4E7] rounded text-xs space-y-1">
        <span className="font-semibold text-[#18181B]">Demo Test Credentials:</span>
        <div className="flex justify-between text-[#71717A]">
          <span>Customer: <code className="text-[#059669]">rahul.sharma@example.com</code></span>
          <span>Pass: <code className="text-[#059669]">CustomerPass123!</code></span>
        </div>
        <div className="flex justify-between text-[#71717A]">
          <span>Admin: <code className="text-[#059669]">admin@ecommerce.com</code></span>
          <span>Pass: <code className="text-[#059669]">AdminPass123!</code></span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs font-semibold text-[#18181B] block mb-1">Email Address</label>
          <div className="relative">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full text-xs pl-9 pr-3 py-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
            />
            <Mail className="w-4 h-4 text-[#71717A] absolute left-2.5 top-2.5" />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#18181B] block mb-1">Password</label>
          <div className="relative">
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full text-xs pl-9 pr-3 py-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
            />
            <Lock className="w-4 h-4 text-[#71717A] absolute left-2.5 top-2.5" />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-[#059669] hover:bg-[#047857] text-white text-xs font-semibold rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <span>{loading ? "Authenticating..." : "Log In"}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </form>

      <div className="text-center text-xs text-[#71717A] pt-2 border-t border-[#E4E4E7]">
        Don't have an account yet?{" "}
        <Link to="/register" className="font-semibold text-[#059669] hover:underline">
          Sign up here
        </Link>
      </div>
    </div>
  );
};

