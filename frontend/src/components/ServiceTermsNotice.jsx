import React from 'react';
import { FileText, AlertTriangle, ArrowLeft } from 'lucide-react';

export default function ServiceTermsNotice({ onBack }) {
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
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-md">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Terms of Service</h1>
            <p className="text-xs text-slate-500 font-medium">Last Updated: October 28, 2026</p>
          </div>
        </div>
      </div>

      {/* Main Legal Sections */}
      <div className="space-y-6 text-sm text-slate-600 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">1. Acceptance of Terms</h2>
          <p>
            By accessing or using the <strong>AI Phishing Email Detection System</strong> (&ldquo;Service&rdquo;), you agree to be bound by these Terms of Service. If you do not agree to these terms, do not access or use the application.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">2. Security Analysis & AI Advisory Disclaimer</h2>
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-2 text-xs text-amber-900">
            <div className="flex items-center space-x-2 font-bold">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Machine Learning & Heuristic Classification Notice</span>
            </div>
            <p>
              The Service provides automated threat classification based on statistical machine learning models and heuristic rules. While the model achieves high empirical accuracy, no automated tool can guarantee 100% detection of all zero-day phishing attacks or zero false positives.
            </p>
            <p>
              The classifications provided are informational security advisories. You remain solely responsible for validating critical communications before taking actions such as wire transfers, credential submissions, or software installation.
            </p>
          </div>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">3. Permitted and Acceptable Use</h2>
          <p>You agree to use the Service solely for lawful cybersecurity defense purposes. You agree not to:</p>
          <ul className="list-disc pl-5 space-y-1.5 text-xs">
            <li>Connect or monitor email mailboxes for which you lack explicit authorization.</li>
            <li>Attempt to reverse-engineer, exploit, or bypass server-side authentication or isolation boundaries.</li>
            <li>Use the service to distribute malicious payloads, conduct spam campaigns, or attack external infrastructure.</li>
            <li>Interfere with or disrupt the integrity or performance of the Service or its servers.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">4. Third-Party Integrations (Google API)</h2>
          <p>
            The Service connects to Google APIs solely upon your affirmative action. You must comply with all applicable Google Terms of Service and API policies. We do not assume responsibility for disruptions, quotas, or changes in third-party API availability.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">5. Limitation of Liability</h2>
          <p className="text-xs">
            TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE AUTHORS, CONTRIBUTORS, OR AFFILIATES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES ARISING IN ANY WAY OUT OF THE USE OR INABILITY TO USE THIS SERVICE, INCLUDING BUT NOT LIMITED TO DATA LOSS, UNAUTHORIZED ACCOUNT COMPROMISE, BUSINESS INTERRUPTION, OR PECUNIARY LOSS.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-bold text-slate-900">6. Termination & Modifications</h2>
          <p>
            We reserve the right to modify these terms at any time. Continued use of the Service following modifications constitutes your acceptance of the revised Terms of Service.
          </p>
        </section>
      </div>
    </div>
  );
}
