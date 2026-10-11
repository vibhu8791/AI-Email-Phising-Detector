import React from 'react';
import { AlertOctagon, ArrowRight, ShieldAlert, X } from 'lucide-react';

export default function ThreatBanner({ threat, onInspect, onDismiss }) {
  if (!threat) return null;

  const isPhishing = threat.classification === 'PHISHING';

  return (
    <div className={`p-4 rounded-xl border animate-threat-flash transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-3 ${
      isPhishing 
        ? 'bg-rose-950/40 border-rose-500/60 text-rose-200' 
        : 'bg-amber-950/40 border-amber-500/60 text-amber-200'
    }`}>
      <div className="flex items-center space-x-3.5">
        <div className={`p-2.5 rounded-xl border animate-pulse ${
          isPhishing ? 'bg-rose-500/20 border-rose-500/40 text-rose-400' : 'bg-amber-500/20 border-amber-500/40 text-amber-400'
        }`}>
          <AlertOctagon className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 rounded text-[11px] font-extrabold uppercase tracking-wide ${
              isPhishing ? 'bg-rose-600 text-white' : 'bg-amber-500 text-slate-950'
            }`}>
              HIGH PRIORITY THREAT DETECTED
            </span>
            <span className="text-xs font-mono font-bold text-white">
              Risk Score: {threat.risk_score}/100
            </span>
          </div>
          <p className="text-sm font-semibold text-white mt-0.5 line-clamp-1">
            {threat.subject}
          </p>
          <p className="text-xs text-slate-400">
            From: <span className="text-slate-300 font-mono">{threat.sender}</span>
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2 self-end md:self-center">
        <button
          onClick={() => onInspect(threat)}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold bg-white text-slate-900 hover:bg-slate-200 transition-all shadow-md"
        >
          <span>Deep Inspect</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={onDismiss}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
