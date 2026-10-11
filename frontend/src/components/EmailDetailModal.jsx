import React, { useState } from 'react';
import { 
  X, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Link2, 
  Mail, 
  Calendar, 
  User, 
  FileText, 
  Code, 
  ExternalLink,
  Cpu,
  Sliders
} from 'lucide-react';

export default function EmailDetailModal({ email, onClose }) {
  const [viewTab, setViewTab] = useState('text'); // 'text' | 'html' | 'urls'

  if (!email) return null;

  const isPhish = email.classification === 'PHISHING';
  const isSusp = email.classification === 'SUSPICIOUS';
  const isSafe = email.classification === 'SAFE';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#101726] border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-900/60">
          <div className="space-y-1.5 pr-4">
            <div className="flex items-center space-x-2">
              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold tracking-wide uppercase ${
                isPhish ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' :
                isSusp ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}>
                {email.classification}
              </span>
              <span className="text-xs font-mono font-bold text-slate-300">
                Threat Score: <span className={isPhish ? 'text-rose-400 font-extrabold' : isSusp ? 'text-amber-400' : 'text-emerald-400'}>{email.risk_score}</span>/100
              </span>
            </div>
            <h2 className="text-lg font-bold text-white leading-snug">
              {email.subject}
            </h2>
            <div className="flex flex-wrap gap-y-1 gap-x-4 text-xs text-slate-400">
              <div className="flex items-center space-x-1">
                <User className="w-3.5 h-3.5 text-slate-500" />
                <span>From: <strong className="text-slate-200 font-mono">{email.sender}</strong></span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                <span>Date: <span className="text-slate-300">{email.date}</span></span>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* AI / ML & Heuristic Scoring Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* ML Probability */}
            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 mb-1">
                <Cpu className="w-4 h-4 text-sky-400" />
                <span>Scikit-Learn ML Model</span>
              </div>
              <div className="text-2xl font-bold font-mono text-sky-400">
                {Math.round((email.ml_phishing_probability || 0) * 100)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                TF-IDF + Logistic Regression linguistic probability
              </p>
            </div>

            {/* Heuristic Score */}
            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 mb-1">
                <Sliders className="w-4 h-4 text-amber-400" />
                <span>Heuristic Signals</span>
              </div>
              <div className="text-2xl font-bold font-mono text-amber-400">
                {Math.round(email.heuristic_score || 0)}/100
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Domain spoofing, urgency triggers, suspicious URLs
              </p>
            </div>

            {/* Final Calibrated Score */}
            <div className={`p-3.5 rounded-xl border ${
              isPhish ? 'bg-rose-950/20 border-rose-900/50 text-rose-300' :
              isSusp ? 'bg-amber-950/20 border-amber-900/50 text-amber-300' :
              'bg-emerald-950/20 border-emerald-900/50 text-emerald-300'
            }`}>
              <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider mb-1">
                <ShieldAlert className="w-4 h-4" />
                <span>Calibrated Risk Score</span>
              </div>
              <div className="text-2xl font-bold font-mono">
                {email.risk_score}/100
              </div>
              <p className="text-[11px] opacity-80 mt-1">
                Verdict: <strong>{email.classification}</strong>
              </p>
            </div>
          </div>

          {/* Detected Attack Indicators */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Identified Threat Signals ({email.detected_flags?.length || 0})
            </h4>
            <div className="space-y-1.5">
              {email.detected_flags && email.detected_flags.length > 0 ? (
                email.detected_flags.map((flag, idx) => (
                  <div key={idx} className="flex items-start space-x-2 p-2.5 bg-slate-900/70 border border-slate-800 rounded-xl text-xs text-slate-200">
                    <AlertTriangle className={`w-4 h-4 shrink-0 mt-0.5 ${isPhish ? 'text-rose-400' : 'text-amber-400'}`} />
                    <span>{flag}</span>
                  </div>
                ))
              ) : (
                <div className="p-3 bg-emerald-950/20 border border-emerald-900/40 rounded-xl text-xs text-emerald-300 flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4" />
                  <span>No security anomalies or deceptive tactics found in this message.</span>
                </div>
              )}
            </div>
          </div>

          {/* Tabs: Plain Text, HTML Preview, URLs */}
          <div className="space-y-3 pt-2">
            <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setViewTab('text')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  viewTab === 'text' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Plain Text Body</span>
              </button>
              {email.body_html && (
                <button
                  onClick={() => setViewTab('html')}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    viewTab === 'html' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Code className="w-3.5 h-3.5" />
                  <span>HTML Email Preview</span>
                </button>
              )}
              <button
                onClick={() => setViewTab('urls')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  viewTab === 'urls' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Link2 className="w-3.5 h-3.5" />
                <span>Extracted URLs ({email.extracted_urls?.length || 0})</span>
              </button>
            </div>

            {/* Tab: Plain Text */}
            {viewTab === 'text' && (
              <div className="p-4 bg-slate-900/90 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto">
                {email.body_plain || email.snippet || '(Empty body)'}
              </div>
            )}

            {/* Tab: HTML Preview */}
            {viewTab === 'html' && email.body_html && (
              <div className="p-4 bg-white rounded-xl text-slate-900 text-sm max-h-60 overflow-y-auto">
                <div dangerouslySetInnerHTML={{ __html: email.body_html }} />
              </div>
            )}

            {/* Tab: URLs Inspection */}
            {viewTab === 'urls' && (
              <div className="space-y-2">
                {(!email.extracted_urls || email.extracted_urls.length === 0) ? (
                  <div className="text-xs text-slate-500 p-4 text-center">
                    No hyperlinks found in this email.
                  </div>
                ) : (
                  email.url_details && email.url_details.length > 0 ? (
                    email.url_details.map((u, i) => (
                      <div key={i} className={`p-3 rounded-xl border text-xs space-y-1 ${
                        u.is_suspicious ? 'bg-rose-950/20 border-rose-900/50' : 'bg-slate-900 border-slate-800'
                      }`}>
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-sky-400 font-semibold truncate max-w-sm">
                            {u.url}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            u.is_suspicious ? 'bg-rose-500 text-white' : 'bg-emerald-500/20 text-emerald-400'
                          }`}>
                            {u.is_suspicious ? 'SUSPICIOUS LINK' : 'BENIGN'}
                          </span>
                        </div>
                        {u.indicators && u.indicators.length > 0 && (
                          <div className="text-[11px] text-rose-300 space-y-0.5 pt-1">
                            {u.indicators.map((ind, j) => (
                              <div key={j} className="flex items-center space-x-1">
                                <AlertTriangle className="w-3 h-3 text-rose-400 shrink-0" />
                                <span>{ind}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    email.extracted_urls.map((url, i) => (
                      <div key={i} className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 text-xs font-mono text-sky-400 break-all">
                        {url}
                      </div>
                    ))
                  )
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl transition-all"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
