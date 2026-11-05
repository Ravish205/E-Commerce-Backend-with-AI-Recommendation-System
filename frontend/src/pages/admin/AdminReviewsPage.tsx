import React, { useEffect, useState } from "react";
import { Star, ShieldCheck, Check, X } from "lucide-react";
import { adminService } from "../../services/adminService";

export const AdminReviewsPage: React.FC = () => {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadReviews = () => {
    setLoading(true);
    adminService.getReviews({ limit: 50 })
      .then((res) => setReviews(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadReviews();
  }, []);

  const handleModerate = async (id: string, isApproved: boolean) => {
    try {
      await adminService.moderateReview(id, isApproved);
      loadReviews();
    } catch {
      alert("Failed to moderate review");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#18181B] tracking-tight">Review Moderation Queue</h1>
        <p className="text-xs text-[#71717A] mt-1">
          Maintain review integrity. Approve or reject reviews submitted by verified and public customers.
        </p>
      </div>

      <div className="bg-white border border-[#E4E4E7] rounded-md overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#F9FAFB] border-b border-[#E4E4E7] text-[#71717A] uppercase tracking-wider font-semibold">
            <tr>
              <th className="py-3 px-4">Product</th>
              <th className="py-3 px-4">Author</th>
              <th className="py-3 px-4">Rating</th>
              <th className="py-3 px-4">Feedback Content</th>
              <th className="py-3 px-4">Verified Proof</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Moderation Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E4E4E7]">
            {loading ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-[#71717A]">Loading reviews queue...</td>
              </tr>
            ) : reviews.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-[#71717A]">No reviews pending moderation.</td>
              </tr>
            ) : (
              reviews.map((r) => (
                <tr key={r.id} className="hover:bg-zinc-50">
                  <td className="py-3 px-4 font-bold max-w-[150px] truncate">{r.product_name}</td>
                  <td className="py-3 px-4">{r.user_name}</td>
                  <td className="py-3 px-4">
                    <span className="font-bold flex items-center gap-1 text-[#D97706]">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      {r.rating}/5
                    </span>
                  </td>
                  <td className="py-3 px-4 max-w-xs">
                    <span className="font-bold block text-[#18181B]">{r.title}</span>
                    <p className="text-[#71717A] truncate">{r.comment}</p>
                  </td>
                  <td className="py-3 px-4">
                    {r.is_verified_purchase ? (
                      <span className="text-[11px] font-semibold text-[#047857] bg-[#ECFDF5] px-2 py-0.5 rounded flex items-center gap-1 w-fit">
                        <ShieldCheck className="w-3 h-3" /> Verified Order
                      </span>
                    ) : (
                      <span className="text-[11px] text-[#71717A]">Unverified</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {r.is_approved ? (
                      <span className="text-[11px] font-semibold text-[#047857] bg-[#ECFDF5] px-2 py-0.5 rounded">Approved</span>
                    ) : (
                      <span className="text-[11px] font-semibold text-[#DC2626] bg-red-50 px-2 py-0.5 rounded">Rejected</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <button
                      onClick={() => handleModerate(r.id, true)}
                      className="px-2.5 py-1 text-xs font-semibold bg-[#059669] text-white rounded hover:bg-[#047857]"
                      title="Approve Review"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleModerate(r.id, false)}
                      className="px-2.5 py-1 text-xs font-semibold bg-[#DC2626] text-white rounded hover:bg-red-700"
                      title="Reject Review"
                    >
                      Reject
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

