import React from 'react';
import { ShieldCheck, Lock, EyeOff, Trash2, ArrowLeft, ExternalLink, AlertTriangle } from 'lucide-react';

export default function DataProtectionNotice({ onBack }) {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-8 animate-fadeIn text-slate-800">
      {/* Back Button */}
      {onBack && (
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm transition-all hover:bg-slate-50"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </button>
      )}

      {/* Header */}
      <div className="border-b border-slate-200 pb-6 space-y-2">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Privacy Policy</h1>
            <p className="text-xs text-slate-500 font-medium">
              AI Phishing Email Detection System &bull; Last Updated: October 28, 2026
            </p>
          </div>
        </div>
      </div>

      {/* Key Safeguard Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600/10 text-blue-600 flex items-center justify-center">
            <Lock className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">Encrypted Token Storage</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Google OAuth access and refresh tokens are encrypted at rest with Fernet (AES-128-CBC / SHA256 HMAC). Plaintext credentials never leave the backend.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-600/10 text-emerald-600 flex items-center justify-center">
            <EyeOff className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">No AI Model Retraining</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            User email data is strictly processed for transient security scoring. We never use your emails to train or fine-tune generalized foundation AI models.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-purple-50/70 border border-purple-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-600/10 text-purple-600 flex items-center justify-center">
            <Trash2 className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">Revocation & Deletion</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Disconnecting an account immediately sends an OAuth revocation call to Google and removes stored credentials from our database.
          </p>
        </div>
      </div>

      {/* Main Legal Sections */}
      <div className="space-y-6 text-sm text-slate-600 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Overview and Application Identity</h2>
          <p>
            The <strong>AI Phishing Email Detection System</strong> (&ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;the Service&rdquo;), accessible at{' '}
            <a href="https://ai-email-phising-detector.onrender.com" className="text-blue-600 underline font-medium">
              https://ai-email-phising-detector.onrender.com
            </a>
            , is a cybersecurity monitoring platform designed to inspect incoming email communications for phishing indicators, sender impersonation, suspicious links, and Business Email Compromise (BEC) patterns.
          </p>
          <div className="p-3 bg-amber-50/70 border-l-4 border-amber-500 rounded-r-lg text-xs text-amber-900 space-y-1">
            <p className="font-bold text-amber-800">[Configuration Notice &bull; User Input Required]:</p>
            <p>
              Please supply your legal name or organization name, official business jurisdiction, and dedicated support email (e.g. <code>privacy@your-domain.com</code>). Currently maintained as an open-source cybersecurity project on GitHub.
            </p>
          </div>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. Google API Services User Data Policy & Limited Use Disclosure</h2>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
            <p className="font-semibold text-slate-800">
              Compliance with Google API Services User Data Policy:
            </p>
            <p>
              The AI Phishing Email Detection System's use and transfer to any other app of information received from Google APIs adheres to the{' '}
              <a 
                href="https://developers.google.com/terms/api-services-user-data-policy" 
                target="_blank" 
                rel="noreferrer" 
                className="text-blue-600 underline font-medium hover:text-blue-800 inline-flex items-center space-x-0.5"
              >
                <span>Google API Services User Data Policy</span>
                <ExternalLink className="w-3 h-3 ml-0.5" />
              </a>
              , including the <strong>Limited Use</strong> requirements.
            </p>
          </div>
          <p className="pt-1 text-xs">Specifically:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Minimal Scope Requested:</strong> We request only <code>https://www.googleapis.com/auth/gmail.readonly</code> and basic user identity (<code>https://www.googleapis.com/auth/userinfo.email</code>) strictly necessary to read recent inbox messages for phishing classification. We cannot send messages, delete messages from your inbox, or alter your account.</li>
            <li><strong>No General AI/LLM Training:</strong> User email content retrieved via Google APIs is <strong>never</strong> transferred or utilized to train, retrain, or improve generalized, foundation, or commercial artificial intelligence or large language models.</li>
            <li><strong>No Commercial Data Reselling:</strong> We never sell, rent, or lease your email communications. Email data is never transferred to third-party data brokers, ad networks, or marketing platforms.</li>
            <li><strong>No Human Review:</strong> No human being reads your email contents unless you explicitly grant affirmative consent for technical troubleshooting of a false-positive detection, to comply with applicable laws, or when data is aggregated and anonymized for security auditing.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. Information We Collect and Process</h2>
          <p className="text-xs">The application collects only the data strictly necessary for security analysis:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Google Profile Identity:</strong> Your authorized email address, display name, and unique Google ID, collected during OAuth 2.0 authorization to bind your session to an isolated workspace.</li>
            <li><strong>Encrypted OAuth Tokens:</strong> Short-lived access tokens and offline refresh tokens provided by Google, encrypted before storage in MongoDB using Fernet (AES-128 in CBC mode with SHA-256 HMAC). Tokens are never exposed in browser storage or client-side code.</li>
            <li><strong>Email Metadata:</strong> Message ID, Subject line, Sender address (<code>From</code>), Recipient address (<code>To</code>), and Date/Time timestamps for the recent emails you choose to synchronize (default: 10 messages).</li>
            <li><strong>Email Body & Link Content:</strong> Plaintext message snippets and HTML body markup extracted for algorithmic scanning to identify suspicious URLs, IP-based links, deceptive display names, urgent wire transfer language, and credential-harvesting keywords.</li>
            <li><strong>Custom Sandbox Submissions:</strong> Any custom email subjects, senders, and body texts manually submitted into the Sandbox Scanner for on-demand analysis.</li>
            <li><strong>Session Identifiers:</strong> Server-signed JSON Web Tokens (HS256 JWT) stored in your browser's local storage to maintain your authenticated session.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. How Your Email Data is Processed</h2>
          <p className="text-xs">When you click <strong>Sync Gmail</strong> or submit text to the scanner, the following security pipeline runs:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Heuristic Security Analysis:</strong> Our engine scans extracted hyperlinks for raw IP addresses, homograph/punycode attacks, mismatched display vs destination domains, and suspicious top-level domains (.xyz, .top, .buzz, etc.). It scans body text for social engineering pressure tactics (&ldquo;urgent wire transfer&rdquo;, &ldquo;immediate account suspension&rdquo;).</li>
            <li><strong>Machine Learning Inference:</strong> A local Scikit-learn TF-IDF vectorizer and Logistic Regression classifier evaluates text features to compute a probabilistic phishing score (0% to 100%).</li>
            <li><strong>Composite Scoring:</strong> The system combines heuristic detections and ML probability into a Risk Score (0–100) and assigns an actionable status: <code>SAFE</code>, <code>SUSPICIOUS</code>, or <code>PHISHING</code>.</li>
            <li><strong>Real-Time Alerts:</strong> Detected threats are logged to your personal history and broadcast to your active dashboard via WebSocket.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">5. Data Storage and Tenant Isolation</h2>
          <p className="text-xs">
            In production, scanned email records, computed risk scores, and account metadata are persisted in a MongoDB database:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Strict Tenant Partitioning:</strong> All stored records are indexed and queried strictly by the authenticated <code>user_id</code>. No user can view, search, or access another user's email records.</li>
            <li><strong>Cryptographic Verification:</strong> All API endpoints enforce server-side JWT Bearer token authentication. Unauthenticated requests are rejected with HTTP 401 Unauthorized.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">6. Account Disconnection, Revocation & Data Deletion</h2>
          <p className="text-xs">You retain complete control over your accounts and data:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Disconnecting Accounts:</strong> You can disconnect any connected Gmail account at any time through the Settings or Header dropdown. Disconnecting immediately sends a formal revocation request to <code>https://oauth2.googleapis.com/revoke</code> and permanently purges the account credentials from the database.</li>
            <li><strong>Deleting Individual Records:</strong> Any scanned email record can be permanently deleted from the Email History view using the Delete button.</li>
            <li><strong>Full Data Purge:</strong> You can clear all scanned email records and threat history at any time using the <strong>Danger Zone &gt; Reset Data</strong> action in Settings.</li>
            <li><strong>Google Account Revocation:</strong> You can independently revoke access at any time directly through your <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Account Security Settings</a>.</li>
          </ul>
          <div className="p-3 bg-amber-50/70 border-l-4 border-amber-500 rounded-r-lg text-xs text-amber-900">
            <span className="font-bold">[Configuration Notice &bull; Retention Timeframe]:</span> By default, scanned email records remain until manually deleted or reset by the user. If an automated retention schedule is desired (e.g. rolling 30-day purge), update this notice accordingly.
          </div>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">7. Third Parties and Sub-processors</h2>
          <p className="text-xs">
            We do not sell user data. Data is communicated only to technical infrastructure providers necessary to host the application:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Google APIs:</strong> For OAuth 2.0 identity verification and read-only inbox message synchronization upon user command.</li>
            <li><strong>Render:</strong> Cloud hosting infrastructure provider for the web application and backend API, operating under TLS encryption.</li>
            <li><strong>MongoDB:</strong> Database infrastructure for persistent storage of user records and threat detections.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">8. Inquiries and Contact Information</h2>
          <p className="text-xs">
            For questions or requests concerning this Privacy Policy, please contact the repository maintainers:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Project Repository:</strong> <a href="https://github.com/vibhu8791/AI-Email-Phising-Detector" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">GitHub: vibhu8791/AI-Email-Phising-Detector</a></li>
            <li><strong>Issue Tracker:</strong> <a href="https://github.com/vibhu8791/AI-Email-Phising-Detector/issues" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Submit a Privacy Inquiry</a></li>
            <li><strong>Support Email:</strong> <em>[Missing Information: Insert maintainer contact email, e.g. support@your-domain.com]</em></li>
          </ul>
        </section>
      </div>
    </div>
  );
}
