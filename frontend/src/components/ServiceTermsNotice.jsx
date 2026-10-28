import React from 'react';
import { FileText, AlertTriangle, ArrowLeft, ShieldAlert, CheckCircle, ExternalLink } from 'lucide-react';

export default function ServiceTermsNotice({ onBack }) {
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
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-md">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Terms of Service</h1>
            <p className="text-xs text-slate-500 font-medium">
              AI Phishing Email Detection System &bull; Last Updated: October 28, 2026
            </p>
          </div>
        </div>
      </div>

      {/* Prominent Warning Callout */}
      <div className="p-4 rounded-xl bg-amber-50 border border-amber-200/80 space-y-2 text-xs text-amber-900">
        <div className="flex items-center space-x-2 font-bold text-amber-800">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>Important Security Notice &amp; Machine Learning Advisory Disclaimer</span>
        </div>
        <p className="leading-relaxed">
          The Service provides automated threat classification based on statistical machine learning models (Scikit-learn TF-IDF + Logistic Regression) and heuristic rules. While the model achieves high accuracy on benchmark datasets, <strong>no automated security tool can guarantee 100% detection of all zero-day phishing attacks or zero false-positive classifications</strong>.
        </p>
        <p className="leading-relaxed">
          Classifications are provided strictly as informational security advisories. The Service is not a certified forensics tool, and users remain solely responsible for performing due diligence before executing financial transactions, transferring funds, clicking external links, or submitting credentials.
        </p>
      </div>

      {/* Main Legal Sections */}
      <div className="space-y-6 text-sm text-slate-600 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Acceptance of Terms</h2>
          <p>
            By accessing or using the <strong>AI Phishing Email Detection System</strong> (&ldquo;Service&rdquo;), hosted at{' '}
            <a href="https://ai-email-phising-detector.onrender.com" className="text-blue-600 underline font-medium">
              https://ai-email-phising-detector.onrender.com
            </a>
            , you confirm that you have read, understood, and agreed to be bound by these Terms of Service. If you do not agree to these terms, you must discontinue using the application immediately.
          </p>
          <div className="p-3 bg-amber-50/70 border-l-4 border-amber-500 rounded-r-lg text-xs text-amber-900 space-y-1">
            <p className="font-bold text-amber-800">[Configuration Notice &bull; User Input Required]:</p>
            <p>
              Please specify your legal entity or maintainer name, official contact email, and governing jurisdiction.
            </p>
          </div>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. Nature and Purpose of the Service</h2>
          <p className="text-xs">
            The Service is an open-source cybersecurity threat intelligence and phishing analysis application. It enables users to:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li>Connect authorized Google Gmail accounts via Google OAuth 2.0 to scan recent incoming messages for deceptive patterns.</li>
            <li>Manually paste and analyze raw email subjects, senders, and body texts in an isolated Sandbox Scanner.</li>
            <li>Review detailed forensic indicators including sender domain mismatches, suspicious URL parameters, urgent language, and machine-learning phishing probabilities.</li>
            <li>Receive real-time WebSocket alerts upon detection of high-risk phishing attempts.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. User Authorization and Lawful Authority</h2>
          <p className="text-xs">You expressly represent and warrant that:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li>You own or have explicit, documented legal authorization to monitor and scan any email mailbox connected to the Service.</li>
            <li>You will not connect any Google account belonging to third parties without their affirmative legal consent.</li>
            <li>You are solely responsible for ensuring that your use of this Service complies with all local, corporate, and organizational privacy policies applicable to your communications.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. Prohibited and Unlawful Uses</h2>
          <p className="text-xs">You agree not to use the Service for any unauthorized or harmful purpose, including but not limited to:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>Malicious Campaign Testing:</strong> Utilizing the detection engine to optimize, test, or evade security filters for weaponized phishing attacks, social engineering, or malware campaigns.</li>
            <li><strong>Unauthorized Access Attempts:</strong> Attempting to tamper with, bypass, or exploit server-side JWT authentication, cross-user isolation barriers, or database controls.</li>
            <li><strong>Infrastructure Disruption:</strong> Launching denial-of-service (DoS) attacks, automated scraping, or disproportionately heavy API requests that degrade platform performance.</li>
            <li><strong>Credential Interception:</strong> Attempting to extract or intercept another user's encrypted Google OAuth tokens or scan history.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">5. Third-Party Integrations &amp; Google API Compliance</h2>
          <p className="text-xs">
            The Service integrates with Google OAuth 2.0 and the Gmail API to facilitate read-only message inspection upon your affirmative action:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li>Your use of Google APIs through our Service is subject to Google's <a href="https://policies.google.com/terms" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Terms of Service</a> and the <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google API Services User Data Policy</a>.</li>
            <li>We are not responsible for downtime, rate-limiting, quota suspensions, or service alterations instituted by Google or other third-party cloud infrastructure providers.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">6. Disclaimer of Warranties</h2>
          <p className="text-xs uppercase text-slate-500 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
            THE SERVICE IS PROVIDED ON AN &ldquo;AS IS&rdquo; AND &ldquo;AS AVAILABLE&rdquo; BASIS WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY, TITLE, OR NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR COMPLETELY FREE FROM VULNERABILITIES, OR THAT ALL PHISHING COMMUNICATIONS WILL BE IDENTIFIED.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">7. Limitation of Liability</h2>
          <p className="text-xs uppercase text-slate-500 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
            TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE AUTHORS, MAINTAINERS, CONTRIBUTORS, OR HOSTING PROVIDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING BUT NOT LIMITED TO LOSS OF DATA, COMPROMISE OF BUSINESS OR PERSONAL ACCOUNTS, LOSS OF PROFITS, BUSINESS INTERRUPTION, OR FINANCIAL LOSS RESULTING FROM BUSINESS EMAIL COMPROMISE) ARISING OUT OF OR IN CONNECTION WITH THE USE OR INABILITY TO USE THIS SERVICE.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">8. User Account Termination &amp; Data Deletion</h2>
          <p className="text-xs">
            You may terminate your usage of the Service at any time by:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li>Disconnecting your active Gmail account via the Dashboard or Settings menu (which immediately revokes authorization with Google and deletes credentials).</li>
            <li>Purging all stored email scan history via the &ldquo;Reset Data&rdquo; function.</li>
            <li>Revoking permissions directly in your <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Security Portal</a>.</li>
          </ul>
          <p className="text-xs">
            We reserve the right to suspend or terminate access to any user who violates these Terms or engages in unauthorized activity.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">9. Modifications to Terms</h2>
          <p className="text-xs">
            We reserve the right to update or modify these Terms of Service at any time. Any changes will be published directly on this page with an updated &ldquo;Last Updated&rdquo; date. Continued access or use of the Service following modifications constitutes your acceptance of the updated Terms.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">10. Inquiries and Contact Information</h2>
          <p className="text-xs">
            For inquiries regarding these Terms of Service, please reach out via our project repository:
          </p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600">
            <li><strong>GitHub Repository:</strong> <a href="https://github.com/vibhu8791/AI-Email-Phising-Detector" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">github.com/vibhu8791/AI-Email-Phising-Detector</a></li>
            <li><strong>Support Email:</strong> <em>[Missing Information: Insert maintainer email, e.g. support@your-domain.com]</em></li>
          </ul>
        </section>
      </div>
    </div>
  );
}
