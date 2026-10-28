import React from 'react';
import { Search, Trash2, ExternalLink, RefreshCw } from 'lucide-react';
import { formatEmailDateIST } from '../utils/dateFormatter';

export default function EmailHistoryView({
  emails,
  loading,
  currentFilter,
  onFilterChange,
  searchQuery,
  onSearchChange,
  onInspect,
  onDelete,
  onRefresh
}) {
  const filterOptions = [
    { id: 'ALL', label: 'All Emails' },
    { id: 'PHISHING', label: 'Phishing Only' },
    { id: 'SUSPICIOUS', label: 'Suspicious' },
    { id: 'SAFE', label: 'Safe Only' },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Email History</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Full audit log of scanned inbound emails and threats.
          </p>
        </div>

        <button
          onClick={onRefresh}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by subject, sender, or content..."
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:border-blue-500 text-slate-900 placeholder-slate-400"
          />
        </div>

        {/* Filter Badges */}
        <div className="flex items-center space-x-1 overflow-x-auto w-full md:w-auto">
          {filterOptions.map((opt) => (
            <button
              key={opt.id}
              onClick={() => onFilterChange(opt.id)}
              className={`px-3 py-1.5 text-xs font-medium rounded-xl transition-all whitespace-nowrap ${
                currentFilter === opt.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-2" />
            <span>Loading email history...</span>
          </div>
        ) : emails.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            <span>No emails match your search or filter.</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3.5 px-4">Classification</th>
                  <th className="py-3.5 px-4">Date & Time</th>
                  <th className="py-3.5 px-4">Sender</th>
                  <th className="py-3.5 px-4">Subject</th>
                  <th className="py-3.5 px-4 text-center">Threat Score</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {emails.map((email) => {
                  const isPhish = email.classification === 'PHISHING';
                  const isSusp = email.classification === 'SUSPICIOUS';
                  return (
                    <tr 
                      key={email.id} 
                      className="hover:bg-slate-50 transition-colors cursor-pointer"
                      onClick={() => onInspect(email)}
                    >
                      <td className="py-3.5 px-4 whitespace-nowrap">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                          isPhish ? 'bg-red-50 text-red-600 border border-red-200' :
                          isSusp ? 'bg-amber-50 text-amber-600 border border-amber-200' :
                          'bg-emerald-50 text-emerald-600 border border-emerald-200'
                        }`}>
                          {email.classification}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-slate-500 font-mono whitespace-nowrap">
                        {formatEmailDateIST(email)}
                      </td>

                      <td className="py-3.5 px-4 font-mono text-slate-700 max-w-[200px] truncate">
                        <div>{email.sender}</div>
                        {email.account_email && (
                          <div className="text-[10px] text-blue-600 font-sans truncate">
                            to {email.account_email}
                          </div>
                        )}
                      </td>

                      <td className="py-3.5 px-4 font-medium text-slate-900 max-w-[260px] truncate">
                        {email.subject}
                      </td>

                      <td className="py-3.5 px-4 text-center font-mono font-bold">
                        <span className={isPhish ? 'text-red-500' : isSusp ? 'text-amber-500' : 'text-emerald-600'}>
                          {email.risk_score}/100
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => onInspect(email)}
                            className="px-2.5 py-1 rounded-lg text-xs font-semibold text-blue-600 hover:bg-blue-50 border border-blue-200 transition-colors"
                          >
                            View
                          </button>
                          <button
                            onClick={() => onDelete(email.id)}
                            className="p-1 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                            title="Delete record"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
