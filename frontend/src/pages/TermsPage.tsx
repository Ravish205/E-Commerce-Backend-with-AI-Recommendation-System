import React from "react";
import { FileText } from "lucide-react";

export const TermsPage: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto my-8 bg-white border border-[#E4E4E7] rounded-md p-8 md:p-12 space-y-8">
      <div className="border-b border-[#E4E4E7] pb-4">
        <div className="flex items-center gap-2 text-[#059669] text-xs font-semibold uppercase tracking-wider mb-1">
          <FileText className="w-4 h-4" />
          <span>Legal Agreement</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-[#18181B]">Terms and Conditions</h1>
        <p className="text-xs text-[#71717A] mt-1">Last Updated: November 5, 2026</p>
      </div>

      <div className="space-y-6 text-sm text-[#71717A] leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">1. Acceptance of Terms</h2>
          <p>
            By accessing or ordering from ApexStore, you agree to be bound by these Terms and Conditions. All purchases constitute a binding contract under Indian consumer protection and commercial law.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">2. Product Catalog, Stock & Pricing</h2>
          <p>
            All listed prices are displayed in Indian Rupees (INR) and are inclusive of statutory GST (18%) where specified. We strive for exact inventory synchronization; however, in the event of concurrent inventory stockouts, affected customers will be notified immediately and full refunds processed.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">3. Order Cancellation & Returns Policy</h2>
          <p>
            Customers may cancel unfulfilled orders in "pending" or "processing" states directly from the customer order dashboard. Eligible hardware items may be returned within 7 days of verified delivery in original manufacturer packaging with all serial numbers intact.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">4. Authentic Reviews & Content Integrity</h2>
          <p>
            Only customers with verified delivered purchases may submit review ratings and written feedback. We strictly forbid artificial, incentivized, or fabricated product reviews.
          </p>
        </section>
      </div>
    </div>
  );
};
