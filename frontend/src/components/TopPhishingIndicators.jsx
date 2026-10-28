import React from 'react';

export default function TopPhishingIndicators({ indicators }) {
  const defaultIndicators = [
    { label: 'Suspicious Link', percentage: 75 },
    { label: 'Urgent Language', percentage: 62 },
    { label: 'Mismatched Domain', percentage: 48 },
    { label: 'Request for Credentials', percentage: 37 },
    { label: 'Suspicious Attachment', percentage: 25 },
  ];

  const list = indicators && indicators.length > 0 ? indicators : defaultIndicators;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between h-full">
      {/* Title */}
      <div className="pb-3 border-b border-slate-100">
        <h3 className="font-bold text-slate-900 text-base">
          Top Phishing Indicators
        </h3>
      </div>

      {/* Progress Bars */}
      <div className="space-y-4 py-2 my-auto">
        {list.map((item) => (
          <div key={item.label} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-slate-700">{item.label}</span>
              <span className="text-slate-500 font-mono font-medium">{item.percentage}%</span>
            </div>
            
            {/* Track & Filled Bar */}
            <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
              <div 
                className="h-full rounded-full bg-[#F87171] transition-all duration-700 ease-out"
                style={{ width: `${item.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
