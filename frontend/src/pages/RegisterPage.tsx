import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, User, Phone, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const RegisterPage: React.FC = () => {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register({
        first_name: firstName,
        last_name: lastName,
        email,
        phone_number: phone,
        password,
      });
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 bg-white border border-[#E4E4E7] rounded-md p-8 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Create an Account</h1>
        <p className="text-xs text-[#71717A] mt-1">Join ApexStore for personalized tech discovery & quick checkout</p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-[#DC2626] text-xs rounded border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-semibold text-[#18181B] block mb-1">First Name</label>
            <div className="relative">
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Rahul"
                className="w-full text-xs pl-8 pr-2 py-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
              />
              <User className="w-3.5 h-3.5 text-[#71717A] absolute left-2.5 top-2.5" />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-[#18181B] block mb-1">Last Name</label>
            <input
              type="text"
              required
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Sharma"
              className="w-full text-xs p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#18181B] block mb-1">Email Address</label>
          <div className="relative">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="rahul@example.com"
              className="w-full text-xs pl-8 pr-2 py-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
            />
            <Mail className="w-3.5 h-3.5 text-[#71717A] absolute left-2.5 top-2.5" />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#18181B] block mb-1">Phone Number</label>
          <div className="relative">
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91 9876543210"
              className="w-full text-xs pl-8 pr-2 py-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
            />
            <Phone className="w-3.5 h-3.5 text-[#71717A] absolute left-2.5 top-2.5" />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#18181B] block mb-1">Password</label>
          <div className="relative">
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="w-full text-xs pl-8 pr-2 py-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
            />
            <Lock className="w-3.5 h-3.5 text-[#71717A] absolute left-2.5 top-2.5" />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-[#059669] hover:bg-[#047857] text-white text-xs font-semibold rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <span>{loading ? "Creating Account..." : "Create Account"}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </form>

      <div className="text-center text-xs text-[#71717A] pt-2 border-t border-[#E4E4E7]">
        Already have an account?{" "}
        <Link to="/login" className="font-semibold text-[#059669] hover:underline">
          Log in
        </Link>
      </div>
    </div>
  );
};
