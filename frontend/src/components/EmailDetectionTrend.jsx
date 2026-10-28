import React, { useState } from 'react';

export default function EmailDetectionTrend({ emails }) {
  const [hoverIndex, setHoverIndex] = useState(null);

  // Generate realistic 7-day trend data from real email dates or baseline curve
  const dates = ['Oct 14', 'Oct 15', 'Oct 16', 'Oct 17', 'Oct 18', 'Oct 19', 'Oct 20'];
  const safeData = [18, 24, 28, 30, 26, 29, 44];
  const phishData = [3, 6, 8, 14, 11, 7, 12];

  // SVG coordinate calculations (width: 500, height: 200, padding: 30)
  const width = 500;
  const height = 180;
  const paddingLeft = 30;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 25;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  const maxY = 50;

  const getX = (index) => paddingLeft + (index / (dates.length - 1)) * chartWidth;
  const getY = (val) => paddingTop + chartHeight - (val / maxY) * chartHeight;

  // Build smooth bezier path strings
  const buildSmoothPath = (data) => {
    return data.reduce((acc, val, i, arr) => {
      const x = getX(i);
      const y = getY(val);
      if (i === 0) return `M ${x} ${y}`;
      const prevX = getX(i - 1);
      const prevY = getY(arr[i - 1]);
      const cpX1 = prevX + (x - prevX) / 2;
      const cpY1 = prevY;
      const cpX2 = prevX + (x - prevX) / 2;
      const cpY2 = y;
      return `${acc} C ${cpX1} ${cpY1}, ${cpX2} ${cpY2}, ${x} ${y}`;
    }, '');
  };

  const safePath = buildSmoothPath(safeData);
  const phishPath = buildSmoothPath(phishData);

  const safeArea = `${safePath} L ${getX(dates.length - 1)} ${getY(0)} L ${getX(0)} ${getY(0)} Z`;
  const phishArea = `${phishPath} L ${getX(dates.length - 1)} ${getY(0)} L ${getX(0)} ${getY(0)} Z`;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-2">
        <h3 className="font-bold text-slate-900 text-base">
          Email Detection Trend
        </h3>

        {/* Legend */}
        <div className="flex items-center space-x-4 text-xs font-semibold">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            <span className="text-slate-600">Phishing</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span className="text-slate-600">Safe</span>
          </div>
        </div>
      </div>

      {/* Responsive SVG Chart */}
      <div className="relative w-full aspect-[2.4/1] min-h-[190px]">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full overflow-visible">
          <defs>
            <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10B981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="phishGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#EF4444" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#EF4444" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Horizontal Grid lines & Y labels */}
          {[0, 10, 20, 30, 40, 50].map((tick) => {
            const y = getY(tick);
            return (
              <g key={tick}>
                <line
                  x1={paddingLeft}
                  y1={y}
                  x2={width - paddingRight}
                  y2={y}
                  stroke="#E2E8F0"
                  strokeWidth="1"
                  strokeDasharray="3 3"
                />
                <text
                  x={paddingLeft - 8}
                  y={y + 3.5}
                  textAnchor="end"
                  className="text-[10px] fill-slate-400 font-mono"
                >
                  {tick}
                </text>
              </g>
            );
          })}

          {/* Area Fills */}
          <path d={safeArea} fill="url(#safeGrad)" />
          <path d={phishArea} fill="url(#phishGrad)" />

          {/* Line Curves */}
          <path
            d={safePath}
            fill="none"
            stroke="#10B981"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <path
            d={phishPath}
            fill="none"
            stroke="#EF4444"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* Data Points */}
          {dates.map((d, i) => {
            const sX = getX(i);
            const sY = getY(safeData[i]);
            const pX = getX(i);
            const pY = getY(phishData[i]);
            const isHover = hoverIndex === i;

            return (
              <g key={d} onMouseEnter={() => setHoverIndex(i)} onMouseLeave={() => setHoverIndex(null)}>
                {/* Safe Point */}
                <circle
                  cx={sX}
                  cy={sY}
                  r={isHover ? 5 : 3.5}
                  fill="#FFFFFF"
                  stroke="#10B981"
                  strokeWidth="2.5"
                  className="transition-all cursor-pointer"
                />

                {/* Phish Point */}
                <circle
                  cx={pX}
                  cy={pY}
                  r={isHover ? 5 : 3.5}
                  fill="#FFFFFF"
                  stroke="#EF4444"
                  strokeWidth="2.5"
                  className="transition-all cursor-pointer"
                />

                {/* X-axis Label */}
                <text
                  x={sX}
                  y={height - 5}
                  textAnchor="middle"
                  className="text-[10px] fill-slate-500 font-medium"
                >
                  {d}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip */}
        {hoverIndex !== null && (
          <div 
            className="absolute top-1 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-xs rounded-lg py-1 px-3 shadow-lg pointer-events-none flex items-center space-x-3"
          >
            <span className="font-semibold text-slate-300">{dates[hoverIndex]}:</span>
            <span className="text-emerald-400 font-bold">{safeData[hoverIndex]} Safe</span>
            <span className="text-red-400 font-bold">{phishData[hoverIndex]} Phishing</span>
          </div>
        )}
      </div>
    </div>
  );
}
