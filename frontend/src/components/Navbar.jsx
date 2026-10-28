import React, { useState } from 'react';
import { 
  ShieldAlert, 
  RefreshCw, 
  Mail, 
  CheckCircle2, 
  XCircle, 
  Radio, 
  Zap, 
  ExternalLink,
  Lock,
  LogOut,
  Sparkles,
  AlertTriangle
} from 'lucide-react';
import { getGoogleLoginUrl, disconnectGmail, connectDemoMailbox } from '../services/api';

export default function Navbar({ 
  stats, 
  wsConnected, 
  onSync, 
  syncing, 
  onSimulate, 
  simulating, 
  activeTab, 
  setActiveTab,
  onRefresh
}) {
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [connectingDemo, setConnectingDemo] = useState(false);

  const handleConnectGoogle = () => {
    // Redirect directly to the backend login endpoint which initiates the Google OAuth flow
    window.location.href = getGoogleLoginUrl('select_account');
  };

  const handleConnectDemo = async () => {
    setConnectingDemo(true);
    try {
      await connectDemoMailbox();
      setShowConnectModal(false);
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setConnectingDemo(false);
    }
  };

  const handleDisconnect = async () => {
    if (confirm("Disconnect Gmail account?")) {
      await disconnectGmail();
      onRefresh();
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-[#0c101c]/90 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-lg shadow-sky-500/20">
              <ShieldAlert className="w-6 h-6 text-white" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  PhishShield AI
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold tracking-wider text-sky-400 bg-sky-950/80 border border-sky-800/60 rounded">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Real-Time ML Phishing Detection & Threat Shield
              </p>
            </div>
          </div>

          {/* Nav Tabs */}
          <div className="hidden md:flex items-center space-x-1 bg-slate-900/80 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-sky-500 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('sandbox')}
              className={`px-3.5 py-1.5 rounded-md text-xs font-medium transition-all flex items-center space-x-1.5 ${
                activeTab === 'sandbox'
                  ? 'bg-sky-500 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>AI Sandbox Scanner</span>
            </button>
          </div>

          {/* Action Buttons & Gmail Status */}
          <div className="flex items-center space-x-3">
            {/* Realtime WebSocket Status */}
            <div 
              title={wsConnected ? "WebSocket Connected: Real-time alerts active" : "WebSocket Disconnected: Reconnecting..."}
              className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-slate-900/80 border border-slate-800"
            >
              <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
              <span className="text-[11px] text-slate-300">
                {wsConnected ? 'LIVE FEED' : 'OFFLINE'}
              </span>
            </div>

            {/* Quick Simulate Attack */}
            <button
              onClick={onSimulate}
              disabled={simulating}
              title="Simulate incoming emails with threats"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 border border-rose-500/30 transition-all disabled:opacity-50"
            >
              <Zap className={`w-3.5 h-3.5 text-rose-400 ${simulating ? 'animate-bounce' : ''}`} />
              <span className="hidden sm:inline">Simulate Attack</span>
            </button>

            {/* Gmail Connection Status */}
            {stats?.is_gmail_connected ? (
              <div className="flex items-center space-x-2">
                <button
                  onClick={onSync}
                  disabled={syncing}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-sm shadow-sky-600/20 transition-all disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
                  <span>{syncing ? 'Scanning...' : 'Sync Gmail'}</span>
                </button>
                <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-300">
                  <Mail className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="truncate max-w-[140px]" title={stats.connected_email}>
                    {stats.connected_email}
                  </span>
                  <button 
                    onClick={handleDisconnect}
                    title="Disconnect Gmail"
                    className="text-slate-500 hover:text-rose-400 ml-1"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowConnectModal(true)}
                className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-md shadow-emerald-600/20 transition-all"
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Connect Gmail</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Gmail Connect Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-[#101726] border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 bg-sky-500/10 rounded-lg text-sky-400">
                  <Mail className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">Connect Gmail Account</h3>
              </div>
              <button 
                onClick={() => setShowConnectModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Connect your Gmail account via secure Google OAuth 2.0 to automatically inspect incoming emails for phishing lures, malicious URLs, and sender spoofing.
            </p>

            <div className="space-y-3 pt-1">
              <button
                onClick={handleConnectGoogle}
                className="w-full flex items-center justify-center space-x-2.5 py-2.5 px-4 bg-white text-slate-900 hover:bg-slate-100 font-semibold rounded-xl text-sm transition-all shadow-md"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                <span>Sign in with Google OAuth 2.0</span>
              </button>

              <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t border-slate-800"></div>
                <span className="flex-shrink mx-3 text-[11px] font-mono text-slate-500 uppercase">Or test immediately</span>
                <div className="flex-grow border-t border-slate-800"></div>
              </div>

              <button
                onClick={handleConnectDemo}
                disabled={connectingDemo}
                className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-sky-300 font-medium rounded-xl text-xs border border-slate-700 transition-all"
              >
                <Sparkles className="w-4 h-4 text-sky-400" />
                <span>{connectingDemo ? 'Connecting...' : 'Connect Instant Demo Mailbox'}</span>
              </button>
            </div>

            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div className="flex items-center space-x-1.5 text-slate-300 font-semibold">
                <Lock className="w-3.5 h-3.5 text-emerald-400" />
                <span>Zero Password Storage</span>
              </div>
              <p>
                We use official Google OAuth 2.0 read-only scopes. Your credentials and Gmail passwords are never seen or stored.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
