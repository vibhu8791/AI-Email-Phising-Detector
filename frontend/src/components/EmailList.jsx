import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Search, 
  Trash2, 
  Eye, 
  Link2, 
  ExternalLink,
  ChevronRight,
  Filter
} from 'lucide-react';
import { formatEmailDateIST } from '../utils/dateFormatter';

export default function EmailList({ emails, loading, onInspect, onDelete, onFilterChange, currentFilter, searchQuery, onSearchChange }) {
  const filterOptions = [
    { label: 'All Emails', value: 'ALL' },
    { label: 'Phishing', value: 'PHISHING' },
    { label: 'Suspicious', value: 'SUSPICIOUS' },
    { label: 'Safe', value: 'SAFE' },
  ];

  return (
    <div className="glass-panel rounded-2xl p-5 space-y-4">
      {/* Top Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by subject, sender, or content..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900/90 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0">
          {filterOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onFilterChange(opt.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                currentFilter === opt.value
                  ? 'bg-sky-500 text-white shadow-sm'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-900/80 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <th className="py-3 px-4">Verdict</th>
              <th className="py-3 px-4">Threat Score</th>
              <th className="py-3 px-4">Subject</th>
              <th className="py-3 px-4">Sender</th>
              <th className="py-3 px-4 text-center">URLs</th>
              <th className="py-3 px-4">Scanned Date</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {loading ? (
              <tr>
                <td colSpan="7" className="py-8 text-center text-slate-500">
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
                    <span>Loading scan records...</span>
                  </div>
                </td>
              </tr>
            ) : emails.length === 0 ? (
              <tr>
                <td colSpan="7" className="py-10 text-center text-slate-500">
                  No scanned emails found matching your filters. Click "Sync Gmail" or "Simulate Attack" to begin scanning!
                </td>
              </tr>
            ) : (
              emails.map((email) => {
                const isPhish = email.classification === 'PHISHING';
                const isSusp = email.classification === 'SUSPICIOUS';
                const isSafe = email.classification === 'SAFE';

                return (
                  <tr 
                    key={email.id} 
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => onInspect(email)}
                  >
                    {/* Verdict */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {isPhish && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-500/15 text-rose-400 border border-rose-500/30">
                          <ShieldAlert className="w-3 h-3 mr-1" />
                          PHISHING
                        </span>
                      )}
                      {isSusp && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          SUSPICIOUS
                        </span>
                      )}
                      {isSafe && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                          <ShieldCheck className="w-3 h-3 mr-1" />
                          SAFE
                        </span>
                      )}
                    </td>

                    {/* Threat Score Bar */}
                    <td className="py-3.5 px-4 whitespace-nowrap font-mono">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-1.5 rounded-full ${
                              isPhish ? 'bg-rose-500' : isSusp ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${Math.min(100, Math.max(8, email.risk_score))}%` }}
                          />
                        </div>
                        <span className={`text-xs font-bold ${
                          isPhish ? 'text-rose-400' : isSusp ? 'text-amber-400' : 'text-emerald-400'
                        }`}>
                          {email.risk_score}
                        </span>
                      </div>
                    </td>

                    {/* Subject */}
                    <td className="py-3.5 px-4 max-w-[280px]">
                      <div className="font-semibold text-white truncate group-hover:text-sky-300 transition-colors">
                        {email.subject}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate">
                        {email.snippet || email.body_plain?.slice(0, 70)}
                      </div>
                    </td>

                    {/* Sender */}
                    <td className="py-3.5 px-4 max-w-[200px] truncate text-slate-300 font-mono text-[11px]">
                      {email.sender}
                    </td>

                    {/* URLs Count */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      {email.extracted_urls && email.extracted_urls.length > 0 ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-sky-400 border border-slate-700">
                          <Link2 className="w-3 h-3 mr-1" />
                          {email.extracted_urls.length}
                        </span>
                      ) : (
                        <span className="text-slate-600 font-mono">0</span>
                      )}
                    </td>

                    {/* Date */}
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-400 text-[11px]">
                      {formatEmailDateIST(email)}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end space-x-1.5">
                        <button
                          onClick={() => onInspect(email)}
                          title="Inspect Details"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDelete(email.id)}
                          title="Delete Record"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
