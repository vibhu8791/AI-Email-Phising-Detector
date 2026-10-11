import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert, Inbox, TrendingUp, Activity } from 'lucide-react';

export default function StatsOverview({ stats }) {
  const total = stats?.total_scanned || 0;
  const safe = stats?.safe_count || 0;
  const suspicious = stats?.suspicious_count || 0;
  const phishing = stats?.phishing_count || 0;
  const avgRisk = stats?.avg_risk_score || 0;

  const safePct = total > 0 ? Math.round((safe / total) * 100) : 0;
  const suspPct = total > 0 ? Math.round((suspicious / total) * 100) : 0;
  const phishPct = total > 0 ? Math.round((phishing / total) * 100) : 0;

  return (
    <div className="space-y-4">
      {/* 4 Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Scanned */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Inbox className="w-16 h-16 text-sky-400" />
          </div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2.5 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Inbox className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Scanned
            </span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {total}
            </span>
            <span className="text-xs text-slate-400">emails</span>
          </div>
          <div className="mt-3 flex items-center text-[11px] text-sky-400">
            <Activity className="w-3.5 h-3.5 mr-1" />
            <span>Real-time ingestion active</span>
          </div>
        </div>

        {/* Safe Emails */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-900/50 transition-all">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <ShieldCheck className="w-16 h-16 text-emerald-400" />
          </div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Safe Emails
            </span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-emerald-400 font-mono tracking-tight">
              {safe}
            </span>
            <span className="text-xs text-slate-400">({safePct}%)</span>
          </div>
          <div className="mt-3 w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${safePct}%` }}
            />
          </div>
        </div>

        {/* Suspicious Emails */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-amber-900/50 transition-all">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <AlertTriangle className="w-16 h-16 text-amber-400" />
          </div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Suspicious
            </span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-amber-400 font-mono tracking-tight">
              {suspicious}
            </span>
            <span className="text-xs text-slate-400">({suspPct}%)</span>
          </div>
          <div className="mt-3 w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-amber-500 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${suspPct}%` }}
            />
          </div>
        </div>

        {/* Phishing Threats */}
        <div className="glass-card p-5 rounded-2xl relative overflow-hidden border-rose-900/30 group hover:border-rose-700/60 transition-all">
          <div className="absolute top-0 right-0 p-4 opacity-15 group-hover:opacity-25 transition-opacity">
            <ShieldAlert className="w-16 h-16 text-rose-500" />
          </div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2.5 rounded-xl bg-rose-500/15 text-rose-400 border border-rose-500/30 animate-pulse">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <span className="text-xs font-semibold text-rose-300 uppercase tracking-wider">
              Phishing Threats
            </span>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-rose-400 font-mono tracking-tight">
              {phishing}
            </span>
            <span className="text-xs text-rose-300/80">({phishPct}%)</span>
          </div>
          <div className="mt-3 w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-rose-500 to-red-600 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${phishPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Average Risk Meter Banner */}
      <div className="glass-panel p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 text-sky-400">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-medium text-slate-300">
              Fleet Average Phishing Risk Score
            </div>
            <div className="text-[11px] text-slate-500">
              Calibrated combination of Scikit-Learn TF-IDF classification and heuristic URL/header features
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4 w-full sm:w-auto">
          <div className="w-full sm:w-48 bg-slate-900 rounded-full h-2.5 p-0.5 border border-slate-800">
            <div 
              className={`h-1.5 rounded-full transition-all duration-500 ${
                avgRisk >= 70 ? 'bg-rose-500' : avgRisk >= 36 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(5, avgRisk))}%` }}
            />
          </div>
          <span className="font-mono text-sm font-bold text-white min-w-[50px] text-right">
            {avgRisk}/100
          </span>
        </div>
      </div>
    </div>
  );
}
