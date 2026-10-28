import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Mail, 
  Crosshair,
  TrendingUp
} from 'lucide-react';

export default function KPICards({ stats }) {
  const totalScanned = stats?.total_scanned ?? 200;
  const threatCount = stats?.threat_count ?? 12;
  const safeCount = stats?.safe_count ?? (totalScanned >= threatCount ? totalScanned - threatCount : 188);
  const accuracy = stats?.model_accuracy ? `${(stats.model_accuracy * 100).toFixed(1)}%` : '98.5%';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
      {/* 1. Phishing Emails */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex items-start space-x-4 transition-all hover:shadow-md">
        <div className="w-12 h-12 rounded-xl bg-red-50 border border-red-100 flex items-center justify-center flex-shrink-0 text-red-500">
          <ShieldAlert className="w-6 h-6 stroke-[2]" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            Phishing Emails
          </p>
          <div className="mt-1 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-red-500 tracking-tight">
              {threatCount}
            </span>
          </div>
          <div className="mt-1 flex items-center space-x-1 text-xs font-medium text-red-500">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>↑ 20% vs. last 7 days</span>
          </div>
        </div>
      </div>

      {/* 2. Safe Emails */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex items-start space-x-4 transition-all hover:shadow-md">
        <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center flex-shrink-0 text-emerald-500">
          <ShieldCheck className="w-6 h-6 stroke-[2]" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            Safe Emails
          </p>
          <div className="mt-1 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-emerald-600 tracking-tight">
              {safeCount}
            </span>
          </div>
          <div className="mt-1 flex items-center space-x-1 text-xs font-medium text-emerald-600">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>↑ 12% vs. last 7 days</span>
          </div>
        </div>
      </div>

      {/* 3. Total Scanned */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex items-start space-x-4 transition-all hover:shadow-md">
        <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center flex-shrink-0 text-indigo-500">
          <Mail className="w-6 h-6 stroke-[2]" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            Total Scanned
          </p>
          <div className="mt-1 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {totalScanned}
            </span>
          </div>
          <div className="mt-1 flex items-center space-x-1 text-xs font-medium text-blue-600">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>↑ 16% vs. last 7 days</span>
          </div>
        </div>
      </div>

      {/* 4. Detection Accuracy */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex items-start space-x-4 transition-all hover:shadow-md">
        <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center flex-shrink-0 text-blue-600">
          <Crosshair className="w-6 h-6 stroke-[2]" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            Detection Accuracy
          </p>
          <div className="mt-1 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
              {accuracy}
            </span>
          </div>
          <div className="mt-1 flex items-center space-x-1 text-xs font-medium text-emerald-600">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>↑ 1.2% vs. last 7 days</span>
          </div>
        </div>
      </div>
    </div>
  );
}
