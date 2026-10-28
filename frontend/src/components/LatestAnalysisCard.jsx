import React from 'react';
import { ShieldAlert, AlertTriangle, ArrowRight } from 'lucide-react';

export default function LatestAnalysisCard({ latestThreat, onInspect }) {
  // Use latest real threat from backend if available, or fall back to sample threat
  const threat = latestThreat || {
    id: 'sample-analysis',
    subject: 'Account Verification Required',
    sender: 'security@micr0soft-login.com',
    risk_score: 98.7,
    classification: 'PHISHING',
    detected_flags: [
      'Suspicious domain (micr0soft-login.com)',
      'Urgent language detected',
      'Link points to a non-official domain'
    ],
    snippet: 'The email contains a suspicious link, uses urgent language and tries to collect your credentials.',
    body_plain: 'Immediate action required: We detected unusual login attempts. Verify your Microsoft credentials within 24 hours to prevent account suspension.'
  };

  const findings = threat.detected_flags && threat.detected_flags.length > 0
    ? threat.detected_flags.slice(0, 3)
    : [
        'Suspicious domain (micr0soft-login.com)',
        'Urgent language detected',
        'Link points to a non-official domain'
      ];

  const confidenceScore = threat.risk_score ? `${parseFloat(threat.risk_score).toFixed(1)}%` : '98.7%';

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm flex flex-col justify-between h-full">
      {/* Title */}
      <div className="flex items-center space-x-2 pb-4 border-b border-slate-100">
        <ShieldAlert className="w-5 h-5 text-blue-600" />
        <h3 className="font-bold text-slate-900 text-base">
          Latest Analysis
        </h3>
      </div>

      <div className="space-y-4 my-2">
        {/* Threat Alert Box matching the image */}
        <div className="bg-[#FFF1F2] border border-red-200/90 rounded-xl p-4 text-xs space-y-3">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">
              !
            </div>
            <div className="space-y-1">
              <h4 className="font-bold text-red-600 text-sm leading-tight">
                This email is likely a phishing attempt!
              </h4>
              <p className="text-[11px] font-semibold text-slate-600">
                Confidence Score: <span className="text-red-500 font-bold">{confidenceScore}</span>
              </p>
            </div>
          </div>

          <p className="text-slate-600 text-[11px] leading-relaxed">
            {threat.snippet || "The email contains a suspicious link, uses urgent language and tries to collect your credentials."}
          </p>

          <button
            onClick={() => onInspect(threat)}
            className="w-full py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center justify-center space-x-1.5 shadow-sm transition-all"
          >
            <span>View Full Analysis</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Key Findings List matching image */}
        <div className="space-y-2 pt-1">
          <p className="text-xs font-bold text-slate-700">
            Key Findings
          </p>
          <ul className="space-y-1.5 text-xs text-slate-600">
            {findings.map((f, i) => (
              <li key={i} className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 flex-shrink-0"></span>
                <span className="leading-tight">{f}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
