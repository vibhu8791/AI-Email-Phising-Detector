import React from 'react';
import { ShieldCheck, Lock, EyeOff, Trash2, ArrowLeft, ExternalLink, AlertTriangle, Database, Server, UserCheck } from 'lucide-react';

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
          <div className="w-11 h-11 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
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
            Google OAuth access and refresh tokens are encrypted at rest with Fernet (AES-128-CBC / SHA-256 HMAC). Plaintext credentials never leave the backend or enter client storage.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-600/10 text-emerald-600 flex items-center justify-center">
            <EyeOff className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">No AI Foundation Training</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            User email data is processed strictly for security heuristic analysis and Scikit-learn inference. We never use your emails to train or fine-tune generalized foundation AI models.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-purple-50/70 border border-purple-100 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-600/10 text-purple-600 flex items-center justify-center">
            <Trash2 className="w-4 h-4" />
          </div>
          <h3 className="font-bold text-xs text-slate-900">Revocation &amp; Deletion</h3>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Disconnecting an account immediately invokes Google's OAuth revocation endpoint and deletes stored credentials from MongoDB. Users can purge scan history at any time.
          </p>
        </div>
      </div>

      {/* Main Legal Sections */}
      <div className="space-y-6 text-sm text-slate-600 leading-relaxed">
        {/* Section 1 */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Overview and Application Identity</h2>
          <p>
            The <strong>AI Phishing Email Detection System</strong> (&ldquo;we&rdquo;, &ldquo;our&rdquo;, or &ldquo;the Service&rdquo;), hosted at{' '}
            <a href="https://ai-email-phising-detector.onrender.com" className="text-blue-600 underline font-medium">
              https://ai-email-phising-detector.onrender.com
            </a>
            , is a cybersecurity monitoring platform that assists users and security analysts in identifying phishing attacks, spoofed sender domains, credential-harvesting links, and Business Email Compromise (BEC) fraud.
          </p>
          <div className="p-3 bg-amber-50/70 border-l-4 border-amber-500 rounded-r-lg text-xs text-amber-900 space-y-1">
            <p className="font-bold text-amber-800">[Configuration Notice &bull; User Input Required]:</p>
            <p>
              Please specify your legal name or organization name, official business/physical jurisdiction, and dedicated privacy inquiry email address (e.g., <code>privacy@your-domain.com</code>). Currently maintained as an open-source cybersecurity project on GitHub.
            </p>
          </div>
        </section>

        {/* Section 2: Google Limited Use */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. Google API Services User Data Policy &amp; Limited Use Disclosure</h2>
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
                className="text-blue-600 underline font-medium hover:text-blue-800 inline-flex items-center space-x-0.5"
              >
                <span>Google API Services User Data Policy</span>
                <ExternalLink className="w-3 h-3 ml-0.5" />
              </a>
              , including the <strong>Limited Use</strong> requirements.
            </p>
          </div>
          <p className="pt-1 text-xs">In strict compliance with Google's Limited Use standards:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>No Generalized AI/LLM Training:</strong> User email content obtained via Google APIs is <strong>never</strong> transferred, exported, or used to develop, train, retrain, or fine-tune generalized artificial intelligence, machine learning, or commercial foundation models (including Large Language Models).</li>
            <li><strong>No Commercial Reselling or Advertising:</strong> Google user data is never sold, leased, rented, or transferred to third-party data brokers, advertising networks, or marketing aggregators.</li>
            <li><strong>Strict Purpose Limitation:</strong> Information received via Google APIs is used solely to provide and improve user-facing email phishing analysis, threat detection, and forensic scoring.</li>
            <li><strong>No Human Review:</strong> No human being reads your email communications unless:
              <ol className="list-decimal pl-5 mt-1 space-y-1">
                <li>You provide explicit affirmative consent for a specific message to troubleshoot a false-positive detection;</li>
                <li>Necessary for security purposes (such as investigating system abuse); or</li>
                <li>Required to comply with applicable statutory laws or judicial processes.</li>
              </ol>
            </li>
          </ul>
        </section>

        {/* Section 3: Scopes Table */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. Google OAuth Scopes &amp; Purpose of Access</h2>
          <p className="text-xs">
            The Service connects to Google APIs solely upon your voluntary affirmative action. We request only the minimum necessary permissions under the principle of least privilege:
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200 rounded-lg overflow-hidden">
              <thead className="bg-slate-100 text-slate-700 font-semibold">
                <tr>
                  <th className="p-2.5 border-b border-slate-200">OAuth 2.0 Scope</th>
                  <th className="p-2.5 border-b border-slate-200">Access Level</th>
                  <th className="p-2.5 border-b border-slate-200">Specific Purpose</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr>
                  <td className="p-2.5 font-mono text-[11px] text-blue-700">https://www.googleapis.com/auth/gmail.readonly</td>
                  <td className="p-2.5 font-medium text-slate-700">Read-Only</td>
                  <td className="p-2.5 text-slate-600">Retrieves recent inbox messages (default 10, max 50) when you click &ldquo;Sync Gmail&rdquo; to inspect headers, body text, and links for phishing indicators. <strong>The app CANNOT send emails, delete messages, modify inbox contents, or create drafts.</strong></td>
                </tr>
                <tr>
                  <td className="p-2.5 font-mono text-[11px] text-blue-700">https://www.googleapis.com/auth/userinfo.email</td>
                  <td className="p-2.5 font-medium text-slate-700">Read-Only</td>
                  <td className="p-2.5 text-slate-600">Retrieves your Google email address to authenticate your session and isolate your scanned emails in your personal dashboard workspace.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 4: Data Collected & Stored */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. Information Collected, Processed &amp; Stored</h2>
          <p className="text-xs">The application processes only the data strictly required for threat detection:</p>

          <h3 className="text-xs font-bold text-slate-800 pt-2">A. User Identity &amp; Profile Data</h3>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Google Account Email:</strong> Used as your unique tenant identifier.</li>
            <li><strong>Profile Display Name:</strong> Displayed in the top navigation header.</li>
            <li><strong>Google User ID:</strong> Internal alphanumeric ID used to enforce cross-user data isolation.</li>
          </ul>

          <h3 className="text-xs font-bold text-slate-800 pt-2">B. Google OAuth Credentials</h3>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Access &amp; Refresh Tokens:</strong> Received from Google's token endpoint upon successful OAuth consent.</li>
            <li><strong>Storage &amp; Encryption:</strong> Both access and refresh tokens are encrypted at rest using symmetric Fernet encryption (AES-128-CBC with SHA-256 HMAC). Plaintext tokens are never stored in the database and are never sent to browser storage.</li>
          </ul>

          <h3 className="text-xs font-bold text-slate-800 pt-2">C. Email Message Metadata &amp; Content</h3>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Header Metadata:</strong> Message ID, Subject, Sender address (<code>From</code>), Recipient address (<code>To</code>), and Date/Time timestamp.</li>
            <li><strong>Message Body Snippets:</strong> Plaintext body text and HTML markup extracted to scan embedded URLs, domain reputations, urgency patterns, and suspicious formatting.</li>
          </ul>

          <h3 className="text-xs font-bold text-slate-800 pt-2">D. Forensic Security Artifacts &amp; Risk Scores</h3>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Extracted URLs:</strong> Hyperlinks found within scanned emails, inspected for raw IP addresses, typosquatting, and suspicious top-level domains (.xyz, .top, .buzz, etc.).</li>
            <li><strong>Machine Learning Probability:</strong> A statistical probability score (0.0 to 1.0) generated by our local Scikit-learn TF-IDF vectorizer and Logistic Regression classifier.</li>
            <li><strong>Heuristic Scores &amp; Flags:</strong> Specific detected threat indicators (e.g., &ldquo;Urgency tactics detected&rdquo;, &ldquo;Sender domain mismatch&rdquo;, &ldquo;Credential harvesting link&rdquo;).</li>
            <li><strong>Composite Risk Score:</strong> An aggregated score from 0 to 100 categorizing messages as <code>SAFE</code> (0–39), <code>SUSPICIOUS</code> (40–69), or <code>PHISHING</code> (70–100).</li>
          </ul>

          <h3 className="text-xs font-bold text-slate-800 pt-2">E. Manual Sandbox Submissions</h3>
          <p className="text-xs text-slate-600">
            Any custom email subjects, senders, and body texts manually submitted into the Sandbox Scanner for on-demand analysis.
          </p>

          <h3 className="text-xs font-bold text-slate-800 pt-2">F. Session &amp; Authentication Tokens</h3>
          <p className="text-xs text-slate-600">
            Cryptographically signed JSON Web Tokens (HS256 JWT) stored in browser local storage (<code>phish_auth_token</code>, <code>phish_user_id</code>) to maintain authenticated sessions across page reloads.
          </p>
        </section>

        {/* Section 5: Storage & Retention */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">5. Storage Location, Retention Schedule &amp; Data Deletion</h2>
          <h3 className="text-xs font-bold text-slate-800">A. Storage Location</h3>
          <p className="text-xs text-slate-600">
            In production, all account credentials (encrypted), email scan records, threat notifications, and forensic analysis results are stored in a persistent MongoDB database hosted in the cloud. In local development mode, a resilient local JSON storage file is utilized.
          </p>

          <h3 className="text-xs font-bold text-slate-800 pt-2">B. Cross-User Data Isolation</h3>
          <p className="text-xs text-slate-600">
            All stored records are partitioned and indexed strictly by the authenticated <code>user_id</code>. Every database query enforces user ownership verification. No user can view, search, modify, or delete another user's email records.
          </p>

          <h3 className="text-xs font-bold text-slate-800 pt-2">C. Retention Period</h3>
          <p className="text-xs text-slate-600">
            Scanned email records and threat logs remain stored in the user's isolated workspace until manually deleted by the user or until account disconnection.
          </p>
          <div className="p-3 bg-amber-50/70 border-l-4 border-amber-500 rounded-r-lg text-xs text-amber-900">
            <span className="font-bold">[Configuration Notice &bull; Retention Timeframe]:</span> If you enforce an automated rolling retention window (e.g., automatic deletion of scanned records after 30, 60, or 90 days), specify that exact period here. Currently, data remains until user-initiated deletion.
          </div>

          <h3 className="text-xs font-bold text-slate-800 pt-2">D. User Data Deletion &amp; Account Disconnection Rights</h3>
          <p className="text-xs text-slate-600">You have continuous, unilateral control over your stored records:</p>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Disconnecting Your Gmail Account:</strong> Clicking &ldquo;Disconnect&rdquo; in Settings or the Header menu immediately triggers two actions:
              <ol className="list-decimal pl-5 mt-1 space-y-0.5">
                <li>The backend sends a token revocation request to Google's OAuth 2.0 revocation endpoint (<code>https://oauth2.googleapis.com/revoke</code>), terminating the authorization with Google; and</li>
                <li>Your account record and encrypted access/refresh tokens are permanently erased from our database.</li>
              </ol>
            </li>
            <li><strong>Deleting Individual Email Records:</strong> You can delete any individual scanned email from the Email History table at any time using the Delete action.</li>
            <li><strong>Full Data Purge (&ldquo;Reset Data&rdquo;):</strong> You can instantly purge all scanned email records, metrics, and threat alerts from your workspace by using the <strong>Danger Zone &gt; Reset Data</strong> action in Settings.</li>
            <li><strong>Independent Revocation in Google:</strong> You may unilaterally revoke the application's access at any time via your <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Account Third-Party Access Portal</a>.</li>
          </ul>
        </section>

        {/* Section 6: Third Parties */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">6. Third-Party Sharing &amp; Service Providers</h2>
          <p className="text-xs text-slate-600">
            We do <strong>not</strong> sell, rent, commercialize, or share your personal information. Data is communicated only with technical service providers essential to hosting and operating the platform:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Google APIs:</strong> For OAuth 2.0 authentication and read-only inbox message synchronization upon user command.</li>
            <li><strong>Render (Render Services Inc.):</strong> Cloud infrastructure provider hosting the web application frontend and backend API under TLS encryption.</li>
            <li><strong>MongoDB (MongoDB Inc.):</strong> Cloud database provider storing encrypted account tokens and isolated email scan records.</li>
          </ul>
        </section>

        {/* Section 7: Security Controls */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">7. Security Controls &amp; Inherent Limitations</h2>
          <h3 className="text-xs font-bold text-slate-800">A. Technical Safeguards</h3>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Encryption in Transit:</strong> All HTTP traffic, API endpoints, and real-time WebSocket streams (<code>wss://</code>) are enforced over SSL/TLS (HTTPS).</li>
            <li><strong>Encryption at Rest:</strong> OAuth credentials are encrypted at rest with Fernet symmetric cryptography (AES-128-CBC / SHA-256 HMAC).</li>
            <li><strong>Server-Side Identity Verification:</strong> Client-supplied user headers are never trusted. Every protected API endpoint verifies a server-signed JWT Bearer token.</li>
            <li><strong>CORS Hardening:</strong> Production environments enforce strict Cross-Origin Resource Sharing (CORS) origin whitelisting.</li>
          </ul>

          <h3 className="text-xs font-bold text-slate-800 pt-2">B. Limitations &amp; Security Disclaimer</h3>
          <p className="text-xs text-slate-600">
            While we implement industry-standard administrative and cryptographic safeguards, no method of transmission over the Internet or electronic storage is 100% secure. The Service operates as an informational security advisory tool; users remain responsible for maintaining general account security (e.g., multi-factor authentication on Google accounts).
          </p>
        </section>

        {/* Section 8: Children's Privacy */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">8. Children's Privacy</h2>
          <p className="text-xs text-slate-600">
            The Service is not intended for or directed toward children under 13 years of age (or 16 years of age in the European Union). We do not knowingly collect personal data from children.
          </p>
        </section>

        {/* Section 9: Modifications */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">9. Modifications to this Privacy Policy</h2>
          <p className="text-xs text-slate-600">
            We may update this Privacy Policy from time to time to reflect operational, architectural, or legal updates. Material updates will be indicated by the &ldquo;Last Updated&rdquo; date at the top of this document. Continued use of the Service following revisions constitutes your acknowledgment of the updated policy.
          </p>
        </section>

        {/* Section 10: Contact Information */}
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">10. Inquiries and Contact Information</h2>
          <p className="text-xs text-slate-600">
            For inquiries, data deletion requests, or questions regarding this Privacy Policy and our data handling practices, please contact:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-xs text-slate-600">
            <li><strong>Project Repository:</strong> <a href="https://github.com/vibhu8791/AI-Email-Phising-Detector" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">github.com/vibhu8791/AI-Email-Phising-Detector</a></li>
            <li><strong>Issue Tracker:</strong> <a href="https://github.com/vibhu8791/AI-Email-Phising-Detector/issues" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Submit a Privacy Request / Issue</a></li>
            <li><strong>Contact Email:</strong> <em>[Missing Information: Insert maintainer/support email, e.g., privacy@your-domain.com]</em></li>
            <li><strong>Developer / Entity Name:</strong> <em>[Missing Information: Insert full legal name or organization name]</em></li>
            <li><strong>Mailing Address / Jurisdiction:</strong> <em>[Missing Information: Insert business city/state/country]</em></li>
          </ul>
        </section>
      </div>
    </div>
  );
}
