import React from "react";
import { Shield } from "lucide-react";

export const PrivacyPolicyPage: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto my-8 bg-white border border-[#E4E4E7] rounded-md p-8 md:p-12 space-y-8">
      <div className="border-b border-[#E4E4E7] pb-4">
        <div className="flex items-center gap-2 text-[#059669] text-xs font-semibold uppercase tracking-wider mb-1">
          <Shield className="w-4 h-4" />
          <span>Compliance & Data Protection</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-[#18181B]">Privacy Policy</h1>
        <p className="text-xs text-[#71717A] mt-1">Last Updated: November 5, 2026</p>
      </div>

      <div className="space-y-6 text-sm text-[#71717A] leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">1. Overview & Scope</h2>
          <p>
            ApexStore is committed to safeguarding your personal information. This Privacy Policy discloses the data collection, machine learning processing, and security practices of our e-commerce platform and AI recommendation services.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">2. Information We Collect</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li><strong>Account Information:</strong> Name, verified email address, hashed credentials, and contact phone numbers.</li>
            <li><strong>Shipping & Billing:</strong> Delivery addresses, recipient contact numbers, and postal codes.</li>
            <li><strong>Behavioral Interaction Data:</strong> Browsing impressions, search clicks, category views, wishlist additions, and cart actions recorded to generate personalized product recommendations.</li>
            <li><strong>Transactional Records:</strong> Order line items, payment identifiers from Razorpay/Stripe, and historical pricing snapshots.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">3. Payment Gateway Security</h2>
          <p>
            We do not collect, process, or store credit card numbers, CVVs, or bank login credentials on our servers. All financial transactions are securely handed off and tokenized through certified PCI-DSS compliant payment gateways (Razorpay/Stripe) using HMAC-SHA256 signature verification.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">4. AI Recommendations & Data Controls</h2>
          <p>
            Our hybrid recommendation engine computes mathematical similarity vectors based strictly on product metadata and interaction logs. You have the right to request deletion of your interaction history or account at any time through our support desk.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-[#18181B]">5. Contact Us</h2>
          <p>
            For privacy inquiries or data rights requests, contact our Data Protection Officer at <code className="text-[#059669]">privacy@apexstore.com</code>.
          </p>
        </section>
      </div>
    </div>
  );
};

