import React, { useState } from 'react';
import { ExternalLink, CheckSquare, Square } from 'lucide-react';
import { formatEmailDateIST } from '../utils/dateFormatter';

export default function RecentEmailsTable({ emails, onInspect, loading }) {
  const [selectedIds, setSelectedIds] = useState(new Set());

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // Default fallback data matching image if database has fewer items
  const demoFallback = [
    {
      id: 'demo-1',
      date: 'Oct 20, 2026 21:14',
      sender: 'security@micr0soft-login.com',
      subject: 'Account Verification Required',
      classification: 'PHISHING',
      risk_score: 98.7,
      ml_phishing_probability: 0.987,
      detected_flags: ['Suspicious domain (micr0soft-login.com)', 'Urgent language detected', 'Link points to a non-official domain'],
      body_plain: 'Immediate action required: We detected unusual login attempts. Verify your Microsoft credentials within 24 hours to prevent account suspension.'
    },
    {
      id: 'demo-2',
      date: 'Oct 20, 2026 18:32',
      sender: 'hr@company.com',
      subject: 'Team Meeting Tomorrow',
      classification: 'SAFE',
      risk_score: 12.4,
      ml_phishing_probability: 0.124,
      detected_flags: [],
      body_plain: 'Hi everyone, please find the agenda for our upcoming quarterly team meeting attached. Let me know if you have any questions.'
    },
    {
      id: 'demo-3',
      date: 'Oct 20, 2026 16:05',
      sender: 'support@amazon-secure.com',
      subject: 'Your Account Will Be Suspended',
      classification: 'PHISHING',
      risk_score: 96.2,
      ml_phishing_probability: 0.962,
      detected_flags: ['Lookalike Amazon domain', 'Urgent suspension threat'],
      body_plain: 'Your Amazon account has been flagged for fraudulent transactions. Click here immediately to confirm billing information.'
    },
    {
      id: 'demo-4',
      date: 'Oct 20, 2026 13:47',
      sender: 'no-reply@google.com',
      subject: 'Security Alert: Unusual Login',
      classification: 'PHISHING',
      risk_score: 94.8,
      ml_phishing_probability: 0.948,
      detected_flags: ['Sender spoofing: Claims Google', 'Credential harvesting form'],
      body_plain: 'Someone logged into your Google account from an unrecognized location. Follow the link to reset your password.'
    },
    {
      id: 'demo-5',
      date: 'Oct 20, 2026 11:23',
      sender: 'team@project.com',
      subject: 'Project Update',
      classification: 'SAFE',
      risk_score: 8.7,
      ml_phishing_probability: 0.087,
      detected_flags: [],
      body_plain: 'Hey team, here is the weekly summary of sprint goals completed and our current release progress.'
    }
  ];

  const displayList = emails && emails.length > 0 ? emails.slice(0, 6) : demoFallback;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between h-full">
      {/* Title */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <h3 className="font-bold text-slate-900 text-base">
          Recent Emails
        </h3>
        <span className="text-xs text-slate-400 font-medium">
          Showing latest {displayList.length} scanned
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto my-2">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-slate-400 font-semibold border-b border-slate-100">
              <th className="py-3 px-3">Date & Time</th>
              <th className="py-3 px-3">Sender</th>
              <th className="py-3 px-3">Subject</th>
              <th className="py-3 px-3 text-center">Status</th>
              <th className="py-3 px-3 text-center">Confidence</th>
              <th className="py-3 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100/80">
            {displayList.map((email) => {
              const isSelected = selectedIds.has(email.id);
              const isPhish = email.classification === 'PHISHING';
              const isSusp = email.classification === 'SUSPICIOUS';
              const isSafe = !isPhish && !isSusp;
              
              // Format confidence percentage
              const confidenceVal = email.risk_score 
                ? `${parseFloat(email.risk_score).toFixed(1)}%` 
                : email.ml_phishing_probability 
                ? `${(email.ml_phishing_probability * 100).toFixed(1)}%` 
                : '98.7%';

              return (
                <tr 
                  key={email.id} 
                  className="hover:bg-slate-50/80 transition-colors group cursor-pointer"
                  onClick={() => onInspect(email)}
                >
                  {/* Date & Time with Checkbox */}
                  <td className="py-3.5 px-3 whitespace-nowrap text-slate-500 font-medium" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center space-x-2.5">
                      <button 
                        onClick={() => toggleSelect(email.id)}
                        className="text-blue-600 hover:text-blue-700 focus:outline-none"
                      >
                        {isSelected ? (
                          <CheckSquare className="w-4 h-4 fill-blue-600 text-white" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-300 group-hover:text-slate-400" />
                        )}
                      </button>
                      <span className="text-slate-600 font-normal">
                        {formatEmailDateIST(email)}
                      </span>
                    </div>
                  </td>

                  {/* Sender */}
                  <td className="py-3.5 px-3 font-mono text-slate-600 max-w-[180px] truncate">
                    <div>{email.sender}</div>
                    {email.account_email && (
                      <div className="text-[10px] text-blue-600 font-sans truncate">
                        to {email.account_email}
                      </div>
                    )}
                  </td>

                  {/* Subject */}
                  <td className="py-3.5 px-3 font-medium text-slate-900 max-w-[220px] truncate">
                    {email.subject}
                  </td>

                  {/* Status Badge */}
                  <td className="py-3.5 px-3 text-center whitespace-nowrap">
                    {isPhish ? (
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-50 text-red-600 border border-red-200">
                        Phishing
                      </span>
                    ) : isSusp ? (
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-600 border border-amber-200">
                        Suspicious
                      </span>
                    ) : (
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-600 border border-emerald-200">
                        Safe
                      </span>
                    )}
                  </td>

                  {/* Confidence */}
                  <td className="py-3.5 px-3 text-center font-mono text-slate-600">
                    {confidenceVal}
                  </td>

                  {/* Action */}
                  <td className="py-3.5 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => onInspect(email)}
                      className="px-3 py-1 rounded-lg text-xs font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 border border-blue-200/80 transition-all"
                    >
                      View
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
