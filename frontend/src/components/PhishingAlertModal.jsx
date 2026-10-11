import React, { useEffect } from 'react';
import { ShieldAlert, AlertTriangle, ExternalLink, X, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function PhishingAlertModal({ alert, onClose, onInspect }) {
  if (!alert) return null;

  // Synthesize a warning tone via Web Audio API
  useEffect(() => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
      }
    } catch (e) {
      // Audio context blocked or not permitted, safe ignore
    }
  }, [alert]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative max-w-lg w-full bg-[#121829] border-2 border-rose-600/80 rounded-2xl shadow-2xl overflow-hidden animate-bounce-short">
        {/* Glowing Top Banner */}
        <div className="bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 px-6 py-4 flex items-center justify-between text-white">
          <div className="flex items-center space-x-2.5">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
            <span className="font-extrabold text-sm tracking-wider uppercase">
              High-Priority Phishing Threat Intercepted
            </span>
          </div>
          <button 
            onClick={onClose}
            className="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {/* Risk Score Gauge */}
          <div className="flex items-center justify-between p-3.5 bg-rose-950/30 border border-rose-900/50 rounded-xl">
            <div>
              <div className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">
                Risk Classification Verdict
              </div>
              <div className="text-xl font-bold text-rose-300">
                {alert.classification || 'PHISHING'}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] font-mono text-slate-400">THREAT SCORE</div>
              <div className="text-3xl font-black font-mono text-rose-400">
                {alert.risk_score}<span className="text-sm text-slate-500">/100</span>
              </div>
            </div>
          </div>

          {/* Email Subject & Sender */}
          <div className="space-y-1.5">
            <div className="text-xs font-semibold text-slate-400 uppercase">Targeted Message</div>
            <div className="text-base font-bold text-white leading-snug">
              {alert.subject}
            </div>
            <div className="text-xs text-slate-300 font-mono bg-slate-900/80 p-2 rounded-lg border border-slate-800 break-all">
              From: <span className="text-rose-300">{alert.sender}</span>
            </div>
          </div>

          {/* Detected Red Flags */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-400 uppercase">Identified Attack Indicators</div>
            <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
              {alert.detected_flags && alert.detected_flags.length > 0 ? (
                alert.detected_flags.map((flag, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-xs text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-slate-800/80">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <span>{flag}</span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-400 italic">
                  Suspicious language, urgent deadline pressure, or deceptive link patterns detected by Scikit-learn model.
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3 pt-2">
            <button
              onClick={() => {
                onInspect(alert);
                onClose();
              }}
              className="flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-xl font-bold text-xs bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-600/30 transition-all"
            >
              <span>Inspect Threat Details</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="py-3 px-4 rounded-xl font-medium text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all"
            >
              Dismiss Alert
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
