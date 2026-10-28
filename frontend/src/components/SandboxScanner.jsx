import React, { useState } from 'react';
import { Sparkles, ShieldAlert, ShieldCheck, AlertTriangle, Send, RefreshCw, Cpu, Link2 } from 'lucide-react';
import { analyzeCustomEmail } from '../services/api';

const PRESETS = [
  {
    name: 'PayPal Account Locked (Phishing)',
    subject: 'URGENT: Your PayPal Account Has Been Suspended',
    sender: 'security-alert@paypa1-support.com',
    body: 'Dear Customer, We have detected unauthorized activity on your PayPal account. Your account has been temporarily suspended for your security. Please click here to verify your identity immediately: http://192.168.1.100/verify-paypal. Failure to do so within 24 hours will result in permanent account termination.'
  },
  {
    name: 'CEO Urgent Wire Transfer (Phishing)',
    subject: 'Immediate Action Required: Wire Transfer Verification',
    sender: 'cfo-office@executive-funds.top',
    body: 'Greetings, I am currently in a closed-door board meeting and need an urgent wire transfer of $45,200 processed to our new supplier before 3 PM today. Please find the wire details here: http://bit.ly/wire-transfer-doc2026. Do not call me as I cannot take calls right now.'
  },
  {
    name: 'Google Cloud Invoice (Safe)',
    subject: 'Google Cloud Platform: Monthly invoice available',
    sender: 'cloud-noreply@google.com',
    body: 'Hello, Your Google Cloud Platform invoice for last month is now ready to view. Total amount billed: $14.20. You can download your PDF invoice from the Google Cloud Console billing section: https://console.cloud.google.com/billing.'
  },
  {
    name: 'Microsoft 365 Compromise (Phishing)',
    subject: 'Alert: Unusual sign-in attempt detected on your Microsoft 365',
    sender: 'support@m1crosoft-office365-verify.com',
    body: 'Security Alert: We blocked a suspicious login attempt to your Microsoft 365 account from IP address 185.220.101.5 in Moscow, Russia. If this was not you, confirm your credentials immediately to avoid mailbox lockout: http://login-microsoft365-secure.xyz/auth.'
  },
  {
    name: 'Zoom Meeting Invitation (Safe)',
    subject: 'Your Zoom meeting link for Client Onboarding',
    sender: 'meetings@zoom.us',
    body: 'Hi David, Your Zoom meeting Client Onboarding is scheduled for today at 4:30 PM. Join Zoom Meeting: https://zoom.us/j/98127391823. Meeting ID: 981 2739 1823. Passcode: 482910.'
  }
];

export default function SandboxScanner({ onScanSaved }) {
  const [subject, setSubject] = useState(PRESETS[0].subject);
  const [sender, setSender] = useState(PRESETS[0].sender);
  const [body, setBody] = useState(PRESETS[0].body);
  const [saveResult, setSaveResult] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleApplyPreset = (preset) => {
    setSubject(preset.subject);
    setSender(preset.sender);
    setBody(preset.body);
    setResult(null);
  };

  const handleScan = async (e) => {
    e.preventDefault();
    if (!subject.trim() && !body.trim()) return;

    setLoading(true);
    try {
      const res = await analyzeCustomEmail({
        subject,
        sender,
        body,
        save_result: saveResult
      });
      setResult(res);
      if (saveResult && onScanSaved) {
        onScanSaved();
      }
    } catch (err) {
      console.error('Custom scan failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Interactive Email Sandbox Scanner</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Scan arbitrary email subjects, senders, and body text on-demand using the trained Scikit-learn AI model.
        </p>
      </div>

      {/* Preset Selection Strip */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <span className="text-xs font-semibold text-slate-600 flex items-center space-x-1.5">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <span>Quick Sample Presets:</span>
        </span>

        <div className="flex flex-wrap gap-1.5">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyPreset(p)}
              className="px-2.5 py-1.5 rounded-xl text-xs font-medium bg-slate-50 border border-slate-200 hover:border-blue-500 hover:text-blue-600 text-slate-700 transition-all"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form */}
        <form onSubmit={handleScan} className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5">
              Email Subject Line
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="e.g. Action Required: Please verify your account"
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5">
              Sender Email Address / Display Name
            </label>
            <input
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="e.g. security-team@support-security-alert.top"
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-mono"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1.5">
              Email Body Content (Includes links and text)
            </label>
            <textarea
              rows={6}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Paste email text with URLs here..."
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-mono leading-relaxed"
              required
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <label className="flex items-center space-x-2 text-xs text-slate-600 cursor-pointer">
              <input
                type="checkbox"
                checked={saveResult}
                onChange={(e) => setSaveResult(e.target.checked)}
                className="w-4 h-4 rounded text-blue-600 border-slate-300 focus:ring-blue-500"
              />
              <span>Save result to history & alert dashboard</span>
            </label>

            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Analyze with AI</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Live Analysis Output */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Detection Telemetry
              </span>
              <span className="text-[11px] font-mono text-slate-400 font-semibold">
                {result ? 'SCAN COMPLETED' : 'AWAITING INPUT'}
              </span>
            </div>

            {result ? (
              <div className="space-y-4">
                {/* Classification Banner */}
                <div className={`p-4 rounded-xl border flex items-center justify-between ${
                  result.classification === 'PHISHING' ? 'bg-red-50 border-red-200 text-red-700' :
                  result.classification === 'SUSPICIOUS' ? 'bg-amber-50 border-amber-200 text-amber-700' :
                  'bg-emerald-50 border-emerald-200 text-emerald-700'
                }`}>
                  <div>
                    <div className="text-[10px] uppercase font-bold tracking-wider opacity-80">Classification Verdict</div>
                    <div className="text-xl font-extrabold">{result.classification}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-mono opacity-80">RISK SCORE</div>
                    <div className="text-3xl font-black font-mono">{result.risk_score}<span className="text-sm opacity-60">/100</span></div>
                  </div>
                </div>

                {/* Score Meters */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">ML Model Prob</div>
                    <div className="text-lg font-bold font-mono text-blue-600 mt-0.5">
                      {Math.round((result.ml_phishing_probability || 0) * 100)}%
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">Heuristic Threat</div>
                    <div className="text-lg font-bold font-mono text-amber-600 mt-0.5">
                      {Math.round(result.heuristic_score || 0)}/100
                    </div>
                  </div>
                </div>

                {/* Identified Flags */}
                <div className="space-y-1.5">
                  <div className="text-xs font-bold text-slate-700 uppercase">Triggered Security Rules</div>
                  {result.detected_flags && result.detected_flags.length > 0 ? (
                    <div className="space-y-1 max-h-40 overflow-y-auto pr-1">
                      {result.detected_flags.map((flag, i) => (
                        <div key={i} className="text-xs p-2 bg-red-50/60 rounded-lg border border-red-100 flex items-start space-x-2 text-red-800">
                          <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                          <span>{flag}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-emerald-700 p-2 bg-emerald-50 rounded-lg border border-emerald-100 flex items-center space-x-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      <span>Zero high-risk indicators identified.</span>
                    </div>
                  )}
                </div>

                {/* Extracted URLs preview */}
                {result.extracted_urls && result.extracted_urls.length > 0 && (
                  <div className="space-y-1">
                    <div className="text-xs font-bold text-slate-700 uppercase">
                      Embedded Links ({result.extracted_urls.length})
                    </div>
                    <div className="space-y-1 max-h-28 overflow-y-auto">
                      {result.extracted_urls.map((u, i) => (
                        <div key={i} className="text-[11px] font-mono text-blue-600 truncate bg-slate-50 p-1.5 rounded border border-slate-100">
                          {u}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center space-y-2 text-slate-400">
                <Cpu className="w-12 h-12 stroke-1 text-slate-300" />
                <p className="text-xs max-w-xs text-slate-500">
                  Fill in the email fields on the left or choose a sample preset, then click "Analyze with AI" to inspect real-time detection telemetry.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
