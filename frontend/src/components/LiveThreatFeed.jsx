import React from 'react';
import { ShieldAlert, AlertTriangle, Clock, ArrowRight } from 'lucide-react';

export default function LiveThreatFeed({ threats, onInspect }) {
  if (!threats || threats.length === 0) {
    return (
      <div className="glass-panel p-5 rounded-2xl">
        <div className="flex items-center space-x-2.5 mb-3">
          <ShieldAlert className="w-5 h-5 text-sky-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Live Threat Alerts</h3>
        </div>
        <div className="text-center py-6 text-slate-500 text-xs">
          No security threats detected recently. Your mailbox is clean!
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel p-5 rounded-2xl space-y-3.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
          </span>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Live Threat Stream ({threats.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">Auto-Refreshed via WebSocket</span>
      </div>

      <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
        {threats.map((threat, idx) => {
          const isPhish = threat.classification === 'PHISHING';
          return (
            <div
              key={threat.id || idx}
              onClick={() => onInspect(threat)}
              className={`p-3 rounded-xl border transition-all cursor-pointer group flex items-center justify-between ${
                isPhish 
                  ? 'bg-rose-950/20 hover:bg-rose-950/40 border-rose-900/40 hover:border-rose-700/60' 
                  : 'bg-amber-950/20 hover:bg-amber-950/40 border-amber-900/40 hover:border-amber-700/60'
              }`}
            >
              <div className="space-y-1 min-w-0 pr-3">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wide ${
                    isPhish ? 'bg-rose-600/80 text-white' : 'bg-amber-500/80 text-slate-950'
                  }`}>
                    {threat.classification}
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-300">
                    Risk: {threat.risk_score}/100
                  </span>
                </div>
                <p className="text-xs font-semibold text-white truncate group-hover:text-sky-300 transition-colors">
                  {threat.subject}
                </p>
                <p className="text-[11px] text-slate-400 truncate">
                  {threat.sender}
                </p>
              </div>

              <div className="text-slate-500 group-hover:text-sky-400 transition-colors shrink-0">
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
