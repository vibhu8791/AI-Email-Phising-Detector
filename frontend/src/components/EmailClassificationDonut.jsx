import React from 'react';

export default function EmailClassificationDonut({ stats }) {
  const total = stats?.total_scanned ?? 200;
  const phish = stats?.threat_count ?? 12;
  const safe = stats?.safe_count ?? (total >= phish ? total - phish : 188);

  const phishPct = total > 0 ? ((phish / total) * 100).toFixed(1) : '6.0';
  const safePct = total > 0 ? ((safe / total) * 100).toFixed(1) : '94.0';

  // SVG Donut calculations (radius: 65, circumference: 2 * pi * 65 ≈ 408.4)
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  
  // Safe stroke covers safePct % of circumference, phish stroke covers the rest
  const safeStroke = (parseFloat(safePct) / 100) * circumference;
  const phishStroke = circumference - safeStroke;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between h-full">
      {/* Title */}
      <div className="pb-2">
        <h3 className="font-bold text-slate-900 text-base">
          Email Classification
        </h3>
      </div>

      {/* SVG Donut Chart */}
      <div className="flex flex-col items-center justify-center my-auto py-2">
        <div className="relative w-44 h-44 flex items-center justify-center">
          <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
            {/* Background track */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke="#F1F5F9"
              strokeWidth="20"
            />
            {/* Safe arc (Green) */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke="#059669"
              strokeWidth="20"
              strokeDasharray={`${safeStroke} ${circumference}`}
              strokeDashoffset="0"
              className="transition-all duration-700 ease-out"
            />
            {/* Phishing arc (Red) */}
            <circle
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke="#EF4444"
              strokeWidth="20"
              strokeDasharray={`${phishStroke} ${circumference}`}
              strokeDashoffset={-safeStroke}
              className="transition-all duration-700 ease-out"
            />
          </svg>

          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
            <span className="text-2xl font-black text-slate-900 tracking-tight leading-none">
              {total}
            </span>
            <span className="text-[11px] font-semibold text-slate-400 mt-1 uppercase tracking-wider">
              Total Emails
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center space-x-6 mt-4 text-xs font-semibold">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 flex-shrink-0"></span>
            <span className="text-slate-700">Phishing</span>
            <span className="text-slate-400 font-mono font-medium">{phish} ({phishPct}%)</span>
          </div>

          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 flex-shrink-0"></span>
            <span className="text-slate-700">Safe</span>
            <span className="text-slate-400 font-mono font-medium">{safe} ({safePct}%)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
