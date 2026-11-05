import React, { useState, useEffect } from "react";
import { User, Lock, MapPin, Plus, Trash2, Check } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import { Address } from "../types";

export const ProfilePage: React.FC = () => {
  const { user, setUser } = useAuth();

  // Profile Form
  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [phone, setPhone] = useState(user?.phone_number || "");
  const [profileMsg, setProfileMsg] = useState("");

  // Change Password Form
  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");
  const [pwdError, setPwdError] = useState("");

  // Addresses
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [showAddAddr, setShowAddAddr] = useState(false);
  const [recipient, setRecipient] = useState("");
  const [addrPhone, setAddrPhone] = useState("");
  const [street, setStreet] = useState("");
  const [city, setCity] = useState("Bengaluru");
  const [state, setState] = useState("Karnataka");
  const [postal, setPostal] = useState("");

  useEffect(() => {
    api.get("/users/addresses")
      .then((res) => setAddresses(res.data.data || []))
      .catch(() => {});
  }, []);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMsg("");
    try {
      const res = await api.put("/users/profile", {
        first_name: firstName,
        last_name: lastName,
        phone_number: phone,
      });
      setUser(res.data.data);
      setProfileMsg("Profile updated successfully!");
    } catch {
      setProfileMsg("Failed to update profile.");
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdMsg("");
    setPwdError("");
    try {
      await api.put("/users/change-password", {
        current_password: currentPwd,
        new_password: newPwd,
      });
      setPwdMsg("Password changed successfully!");
      setCurrentPwd("");
      setNewPwd("");
    } catch (err: any) {
      setPwdError(err.response?.data?.message || "Failed to change password.");
    }
  };

  const handleAddAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post("/users/addresses", {
        recipient_name: recipient,
        phone: addrPhone,
        street_address: street,
        city,
        state,
        postal_code: postal,
        country: "India",
      });
      setAddresses([...addresses, res.data.data]);
      setShowAddAddr(false);
      setRecipient("");
      setAddrPhone("");
      setStreet("");
      setPostal("");
    } catch {
      alert("Failed to add address");
    }
  };

  const handleDeleteAddress = async (id: string) => {
    try {
      await api.delete(`/users/addresses/${id}`);
      setAddresses(addresses.filter((a) => a.id !== id));
    } catch {
      alert("Failed to delete address");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Your Account & Settings</h1>
        <p className="text-xs text-[#71717A] mt-1">Manage personal details, saved shipping addresses, and account security</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Profile Details Form */}
        <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-[#E4E4E7]">
            <User className="w-4 h-4 text-[#059669]" />
            <h2 className="text-sm font-bold text-[#18181B]">Personal Information</h2>
          </div>

          {profileMsg && <p className="text-xs text-[#059669] font-medium">{profileMsg}</p>}

          <form onSubmit={handleUpdateProfile} className="space-y-3 text-xs">
            <div>
              <label className="font-semibold text-[#18181B] block mb-1">Email (Read Only)</label>
              <input
                type="text"
                disabled
                value={user?.email || ""}
                className="w-full p-2 bg-zinc-100 border border-[#E4E4E7] rounded text-zinc-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-[#18181B] block mb-1">First Name</label>
                <input
                  type="text"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>
              <div>
                <label className="font-semibold text-[#18181B] block mb-1">Last Name</label>
                <input
                  type="text"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>
            </div>
            <div>
              <label className="font-semibold text-[#18181B] block mb-1">Phone Number</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-[#059669] hover:bg-[#047857] text-white font-semibold rounded"
            >
              Update Profile
            </button>
          </form>
        </div>

        {/* Change Password Form */}
        <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-[#E4E4E7]">
            <Lock className="w-4 h-4 text-[#059669]" />
            <h2 className="text-sm font-bold text-[#18181B]">Security & Password</h2>
          </div>

          {pwdMsg && <p className="text-xs text-[#059669] font-medium">{pwdMsg}</p>}
          {pwdError && <p className="text-xs text-[#DC2626] font-medium">{pwdError}</p>}

          <form onSubmit={handleChangePassword} className="space-y-3 text-xs">
            <div>
              <label className="font-semibold text-[#18181B] block mb-1">Current Password</label>
              <input
                type="password"
                required
                value={currentPwd}
                onChange={(e) => setCurrentPwd(e.target.value)}
                className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
              />
            </div>
            <div>
              <label className="font-semibold text-[#18181B] block mb-1">New Password (min 8 chars)</label>
              <input
                type="password"
                required
                minLength={8}
                value={newPwd}
                onChange={(e) => setNewPwd(e.target.value)}
                className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 bg-[#18181B] hover:bg-black text-white font-semibold rounded"
            >
              Update Password
            </button>
          </form>
        </div>
      </div>

      {/* Saved Addresses Section */}
      <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#E4E4E7]">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-[#059669]" />
            <h2 className="text-sm font-bold text-[#18181B]">Saved Shipping Addresses</h2>
          </div>
          <button
            onClick={() => setShowAddAddr(!showAddAddr)}
            className="text-xs font-semibold px-3 py-1.5 bg-[#ECFDF5] text-[#047857] hover:bg-emerald-100 rounded flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            Add Address
          </button>
        </div>

        {/* Add Address Form Modal / Inline */}
        {showAddAddr && (
          <form onSubmit={handleAddAddress} className="p-4 bg-[#F9FAFB] rounded border border-[#E4E4E7] grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="font-semibold block mb-1">Recipient Name</label>
              <input
                type="text"
                required
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                className="w-full p-1.5 border rounded"
              />
            </div>
            <div>
              <label className="font-semibold block mb-1">Phone Number</label>
              <input
                type="text"
                required
                value={addrPhone}
                onChange={(e) => setAddrPhone(e.target.value)}
                className="w-full p-1.5 border rounded"
              />
            </div>
            <div className="col-span-2">
              <label className="font-semibold block mb-1">Street Address</label>
              <input
                type="text"
                required
                value={street}
                onChange={(e) => setStreet(e.target.value)}
                className="w-full p-1.5 border rounded"
              />
            </div>
            <div>
              <label className="font-semibold block mb-1">City</label>
              <input
                type="text"
                required
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full p-1.5 border rounded"
              />
            </div>
            <div>
              <label className="font-semibold block mb-1">PIN / Postal Code</label>
              <input
                type="text"
                required
                value={postal}
                onChange={(e) => setPostal(e.target.value)}
                className="w-full p-1.5 border rounded"
              />
            </div>
            <div className="col-span-2 flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddAddr(false)}
                className="px-3 py-1 text-zinc-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1 bg-[#059669] text-white font-semibold rounded"
              >
                Save Address
              </button>
            </div>
          </form>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {addresses.map((a) => (
            <div key={a.id} className="p-4 bg-[#F9FAFB] border border-[#E4E4E7] rounded text-xs flex justify-between items-start">
              <div className="space-y-1">
                <span className="font-bold text-[#18181B] block">{a.recipient_name}</span>
                <p className="text-[#71717A]">{a.street_address}, {a.city}, {a.state} {a.postal_code}</p>
                <p className="text-[#71717A]">Phone: {a.phone}</p>
              </div>
              <button
                onClick={() => handleDeleteAddress(a.id)}
                className="text-[#DC2626] p-1 hover:bg-red-50 rounded"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

