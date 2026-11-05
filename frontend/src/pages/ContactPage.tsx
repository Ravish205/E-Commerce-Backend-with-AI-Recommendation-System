import React, { useState } from "react";
import { Mail, Phone, MapPin, Send, CheckCircle2 } from "lucide-react";

export const ContactPage: React.FC = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="max-w-4xl mx-auto my-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-[#18181B] tracking-tight">Contact & Support</h1>
        <p className="text-xs text-[#71717A] mt-1">Our customer experience and engineering team is here to assist you</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Contact Info Card */}
        <div className="bg-white border border-[#E4E4E7] rounded-md p-6 space-y-6">
          <h2 className="text-sm font-bold text-[#18181B] pb-2 border-b border-[#E4E4E7]">Corporate Office</h2>

          <div className="space-y-4 text-xs">
            <div className="flex items-start gap-3">
              <MapPin className="w-4 h-4 text-[#059669] flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-[#18181B] block">Headquarters:</span>
                <p className="text-[#71717A]">ApexStore Technologies Pvt Ltd</p>
                <p className="text-[#71717A]">100ft Road, Indiranagar, Bengaluru, Karnataka 560038</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Mail className="w-4 h-4 text-[#059669] flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-[#18181B] block">Customer Support:</span>
                <p className="text-[#71717A]">support@apexstore.com</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Phone className="w-4 h-4 text-[#059669] flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-[#18181B] block">Telephone Helpline:</span>
                <p className="text-[#71717A]">+91 80 4912 3456</p>
                <p className="text-[11px] text-[#71717A]">(Mon - Sat, 9:00 AM - 6:00 PM IST)</p>
              </div>
            </div>
          </div>
        </div>

        {/* Message Form */}
        <div className="md:col-span-2 bg-white border border-[#E4E4E7] rounded-md p-6 space-y-4">
          <h2 className="text-sm font-bold text-[#18181B] pb-2 border-b border-[#E4E4E7]">Send Us a Message</h2>

          {submitted ? (
            <div className="p-8 text-center space-y-3">
              <CheckCircle2 className="w-10 h-10 text-[#059669] mx-auto" />
              <h3 className="text-base font-bold text-[#18181B]">Message Dispatched Successfully</h3>
              <p className="text-xs text-[#71717A]">Thank you for reaching out. Our support team will respond within 24 business hours.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold block mb-1">Your Full Name</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Rahul Sharma"
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
                <div>
                  <label className="font-semibold block mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="rahul@example.com"
                    className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold block mb-1">Subject / Order ID</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Inquiry regarding order ORD-..."
                  className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>

              <div>
                <label className="font-semibold block mb-1">Detailed Message</label>
                <textarea
                  required
                  rows={4}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Provide specific details so our agents can assist quickly..."
                  className="w-full p-2 border border-[#E4E4E7] rounded focus:outline-none focus:border-[#059669]"
                />
              </div>

              <button
                type="submit"
                className="px-5 py-2 bg-[#059669] hover:bg-[#047857] text-white font-semibold rounded flex items-center gap-2"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Submit Inquiry</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

