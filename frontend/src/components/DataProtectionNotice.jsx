import React from 'react';
import { ShieldCheck, Lock, EyeOff, Trash2, ArrowLeft } from 'lucide-react';

export default function DataProtectionNotice({ onBack }) {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-8 animate-fadeIn text-slate-800">
      {/* Back Button */}
      {onBack && (
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm transition-all"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </button>
      )}

      {/* Header */}
      <div className="border-b border-slate-200 pb-6 space-y-2">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Privacy Policy</h1>
            <p className="text-xs text-slate-500 font-medium">Last Updated: October 28, 2026</p>
          </div>
        </div>
      </div>

      {/* Summary Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600/10 text-blue-600 flex items-center justify-center">
            <Lock className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">Zero-Knowledge Storage</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            OAuth tokens are strictly encrypted at rest with Fernet/AES-256. Passwords are never collected.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-600/10 text-emerald-600 flex items-center justify-center">
            <EyeOff className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">No Selling or Ad Profiling</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Your email data is never sold, leased, or transferred to third parties or data brokers.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-purple-50/60 border border-purple-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-600/10 text-purple-600 flex items-center justify-center">
            <Trash2 className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">Full Revocation Rights</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Disconnecting immediately revokes credentials with Google and purges local mailbox records.
          </p>
        </div>
      </div>

      {/* Main Legal Sections */}
      <div className="space-y-6 text-sm text-slate-600 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Overview and Purpose</h2>
          <p>
            The <strong>AI Phishing Email Detection System</strong> (&ldquo;Service&rdquo;) is an open-source security intelligence tool developed to assist users and cybersecurity analysts in detecting phishing, brand spoofing, spear phishing, and Business Email Compromise (BEC) attacks within incoming email messages.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. Google API Services User Data Policy & Limited Use Disclosure</h2>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
            <p className="font-semibold text-slate-800">
              Compliance with Google API Services User Data Policy:
            </p>
            <p>
              The AI Phishing Email Detection System's use and transfer to any other app of information received from Google APIs will adhere to the{' '}
              <a 
                href="https://developers.google.com/terms/api-services-user-data-policy" 
                target="_blank" 
                rel="noreferrer" 
                className="text-blue-600 underline font-medium hover:text-blue-800"
              >
                Google API Services User Data Policy
              </a>
              , including the Limited Use requirements.
            </p>
          </div>
          <p className="pt-1">
            Specifically:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs">
            <li><strong>Minimal Scope Requested:</strong> We request only <code>https://www.googleapis.com/auth/gmail.readonly</code> and basic userinfo (email, profile identifier) strictly necessary to read and inspect recent inbox messages for phishing indicators.</li>
            <li><strong>No General AI Training on User Data:</strong> We do NOT use your personal email message content to train, retrain, or improve generalized or foundation artificial intelligence models.</li>
            <li><strong>Human Review:</strong> Human beings do not read your emails unless you explicitly provide affirmative consent for a specific message to troubleshoot a technical false positive, or as required by law.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. Data We Collect and Process</h2>
          <p>When you interact with the Service, we process:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs">
            <li><strong>Account Identity:</strong> Your authorized Google account email address and display name for multi-account tenant isolation.</li>
            <li><strong>Email Metadata:</strong> Subject line, sender address, date/time, and message identifier.</li>
            <li><strong>Email Content:</strong> Text body snippets and links extracted from scanned messages for algorithmic heuristic scoring and natural language feature extraction.</li>
            <li><strong>OAuth Access Tokens:</strong> Temporary authorization tokens granted by Google, encrypted before storage using AES-256.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. Data Storage and Security Controls</h2>
          <p>
            All persistent storage requires server-side identity validation. Client-supplied headers are not trusted; all operations require signed JWT bearer tokens. Passwords for external mailboxes are never collected.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">5. User Control and Account Deletion</h2>
          <p>
            You retain absolute ownership and control of your connected accounts. You may at any time:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs">
            <li>Click <strong>Disconnect</strong> in the Dashboard or Settings to delete the connected mailbox and immediately notify Google to revoke the active token.</li>
            <li>Use the <strong>Danger Zone &gt; Reset Data</strong> action to purge scanned email history and threat records.</li>
            <li>Manage or revoke third-party app permissions directly from your{' '}
              <a 
                href="https://myaccount.google.com/permissions" 
                target="_blank" 
                rel="noreferrer" 
                className="text-blue-600 underline font-medium hover:text-blue-800"
              >
                Google Security Settings
              </a>.
            </li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">6. Contact and Inquiries</h2>
          <p>
            For questions regarding this Privacy Policy or security practices, please contact the project repository maintainers via GitHub Issues.
          </p>
        </section>
      </div>
    </div>
  );
}
