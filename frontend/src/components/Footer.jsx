import React from 'react';
import { ShieldCheck, Lock, ExternalLink } from 'lucide-react';

export default function Footer({ onNavigate }) {
  const handleNav = (e, tab, path) => {
    // If modifier keys pressed, let browser handle normal new-tab behavior
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    if (onNavigate) {
      e.preventDefault();
      onNavigate(tab, path);
    }
  };

  return (
    <footer className="mt-auto border-t border-slate-200/80 bg-white/60 backdrop-blur-sm text-slate-500 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-6">
          {/* Column 1: Brand & Description (6 cols) */}
          <div className="md:col-span-6 space-y-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/20">
                <ShieldCheck className="w-4 h-4 stroke-[2.2]" />
              </div>
              <span className="font-bold text-slate-800 text-sm tracking-tight">
                AI Phishing Email Detection System
              </span>
            </div>
            <p className="text-slate-500 text-xs leading-relaxed max-w-md">
              AI-driven threat intelligence and email forensics platform. Combines Scikit-learn TF-IDF machine learning inference with heuristic rules to identify phishing, domain spoofing, and Business Email Compromise (BEC).
            </p>
            <div className="flex items-center space-x-2 text-[11px] text-slate-400">
              <Lock className="w-3.5 h-3.5 text-emerald-600" />
              <span>Encrypted at rest &bull; Read-only Gmail API integration &bull; No LLM training</span>
            </div>
          </div>

          {/* Column 2: Navigation Links (3 cols) */}
          <div className="md:col-span-3 space-y-2.5">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Navigation</h4>
            <ul className="space-y-1.5 text-xs">
              <li>
                <a 
                  href="/" 
                  onClick={(e) => handleNav(e, 'dashboard', '/')}
                  className="hover:text-blue-600 transition-colors"
                >
                  Dashboard
                </a>
              </li>
              <li>
                <a 
                  href="/" 
                  onClick={(e) => handleNav(e, 'scan', '/')}
                  className="hover:text-blue-600 transition-colors"
                >
                  Sandbox Scanner
                </a>
              </li>
              <li>
                <a 
                  href="/" 
                  onClick={(e) => handleNav(e, 'history', '/')}
                  className="hover:text-blue-600 transition-colors"
                >
                  Email History
                </a>
              </li>
              <li>
                <a 
                  href="/" 
                  onClick={(e) => handleNav(e, 'performance', '/')}
                  className="hover:text-blue-600 transition-colors"
                >
                  Model Metrics
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Legal & Policies (3 cols) */}
          <div className="md:col-span-3 space-y-2.5">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Compliance & Legal</h4>
            <ul className="space-y-1.5 text-xs">
              <li>
                <a 
                  href="/privacy-policy" 
                  onClick={(e) => handleNav(e, 'privacy', '/privacy-policy')}
                  className="text-slate-700 hover:text-blue-600 font-medium transition-colors flex items-center space-x-1"
                >
                  <span>Privacy Policy</span>
                </a>
              </li>
              <li>
                <a 
                  href="/terms" 
                  onClick={(e) => handleNav(e, 'terms', '/terms')}
                  className="text-slate-700 hover:text-blue-600 font-medium transition-colors flex items-center space-x-1"
                >
                  <span>Terms of Service</span>
                </a>
              </li>
              <li>
                <a 
                  href="https://developers.google.com/terms/api-services-user-data-policy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-500 hover:text-blue-600 transition-colors flex items-center space-x-1 text-[11px]"
                >
                  <span>Google Limited Use Policy</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
              <li>
                <a 
                  href="https://myaccount.google.com/permissions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-500 hover:text-blue-600 transition-colors flex items-center space-x-1 text-[11px]"
                >
                  <span>Google Permissions Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Copyright Bar */}
        <div className="pt-6 border-t border-slate-200/60 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-400">
          <p>
            &copy; {new Date().getFullYear()} AI Phishing Email Detection System. Open-Source Security Project.
          </p>
          <div className="flex items-center space-x-4">
            <a href="/privacy-policy" onClick={(e) => handleNav(e, 'privacy', '/privacy-policy')} className="hover:text-slate-600">
              Privacy
            </a>
            <span>&bull;</span>
            <a href="/terms" onClick={(e) => handleNav(e, 'terms', '/terms')} className="hover:text-slate-600">
              Terms
            </a>
            <span>&bull;</span>
            <span className="text-emerald-600 font-medium">SSL Encrypted</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
