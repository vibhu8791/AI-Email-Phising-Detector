import React, { useState } from 'react';
import { 
  Menu, 
  Mail, 
  ChevronDown, 
  RefreshCw, 
  LogOut, 
  CheckCircle2, 
  AlertCircle,
  Zap,
  RotateCcw,
  Plus,
  UserCheck
} from 'lucide-react';
import { disconnectGmail, selectAccount, getCurrentUserId } from '../services/api';

export default function TopHeader({ 
  stats, 
  onSync, 
  syncing, 
  onSimulate, 
  simulating, 
  onRefresh,
  onReset,
  setMobileOpen 
}) {
  const [profileOpen, setProfileOpen] = useState(false);

  const currentUserId = getCurrentUserId();
  const isConnected = stats?.is_gmail_connected;
  const connectedEmail = stats?.connected_email || "No active account";
  const connectedAccounts = stats?.connected_accounts || [];

  const handleConnectGoogle = () => {
    window.location.href = `http://localhost:8000/api/auth/google/login?user_id=${encodeURIComponent(currentUserId)}&prompt=select_account`;
  };

  const handleDisconnect = async () => {
    if (confirm("Disconnect active Gmail account?")) {
      await disconnectGmail();
      setProfileOpen(false);
      onRefresh();
    }
  };

  const handleSelectAccount = async (accountId) => {
    try {
      await selectAccount(accountId);
      onRefresh();
    } catch (e) {
      console.error("Failed to select account:", e);
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-8 py-3.5 flex items-center justify-between">
      {/* Mobile Hamburger Button */}
      <div className="flex items-center space-x-3 lg:hidden">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100"
        >
          <Menu className="w-5 h-5" />
        </button>
        <span className="font-bold text-slate-900 text-base">PhishShield AI</span>
      </div>

      <div className="hidden lg:block">
        {/* Workspace Pill */}
        <div className="flex items-center space-x-2 text-xs text-slate-500 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200/80">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Workspace: <strong className="text-slate-800 font-mono">{currentUserId}</strong></span>
          {connectedAccounts.length > 0 && (
            <span className="text-slate-400">({connectedAccounts.length} mailboxes)</span>
          )}
        </div>
      </div>

      {/* Right User & Actions Controls */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        {/* Sync Gmail Quick Button with spinner */}
        <button
          onClick={onSync}
          disabled={syncing}
          title="Sync Gmail inbox for new threats"
          className="relative p-2 rounded-xl text-slate-600 hover:text-blue-600 hover:bg-blue-50 border border-slate-200 transition-colors flex items-center space-x-1.5 text-xs font-medium"
        >
          <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin text-blue-600' : ''}`} />
          <span className="hidden md:inline">{syncing ? 'Scanning...' : 'Scan Inbox'}</span>
          {syncing && (
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-600"></span>
            </span>
          )}
        </button>

        {/* User Profile & Mailbox Dropdown Pill */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center space-x-3 p-1.5 sm:pr-3 rounded-full hover:bg-slate-100 border border-transparent hover:border-slate-200 transition-all"
          >
            {/* Avatar circle */}
            <div className="w-8 h-8 rounded-full bg-[#0F172A] text-white flex items-center justify-center font-bold text-xs tracking-wider">
              {currentUserId.slice(0, 2).toUpperCase()}
            </div>
            
            <div className="hidden sm:block text-left max-w-[140px]">
              <div className="text-xs font-bold text-slate-900 leading-tight truncate">{currentUserId}</div>
              <div className="text-[11px] text-slate-500 font-medium truncate">
                {isConnected ? connectedEmail : 'No account'}
              </div>
            </div>

            <ChevronDown className="w-4 h-4 text-slate-400 hidden sm:block" />
          </button>

          {/* Profile Dropdown Menu */}
          {profileOpen && (
            <>
              <div 
                className="fixed inset-0 z-30" 
                onClick={() => setProfileOpen(false)}
              />
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 z-40 text-xs text-slate-700 animate-fadeIn">
                <div className="p-3 border-b border-slate-100">
                  <p className="font-semibold text-slate-900 text-sm">{currentUserId}</p>
                  <p className="text-slate-500 truncate text-[11px] font-mono mt-0.5">{connectedEmail}</p>
                  
                  <div className="mt-2.5 flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
                    <span className="text-[11px] text-slate-600 font-medium">Active Scanner:</span>
                    {isConnected ? (
                      <span className="flex items-center space-x-1 text-emerald-600 font-semibold text-[11px]">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Ready</span>
                      </span>
                    ) : (
                      <span className="flex items-center space-x-1 text-amber-600 font-semibold text-[11px]">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>Not Linked</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Connected Mailboxes Quick Switcher */}
                {connectedAccounts.length > 0 && (
                  <div className="p-2 border-b border-slate-100 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider px-1">
                      Switch Mailbox:
                    </span>
                    <div className="space-y-1 max-h-36 overflow-y-auto">
                      {connectedAccounts.map((acc) => (
                        <button
                          key={acc.id}
                          onClick={() => handleSelectAccount(acc.id)}
                          className={`w-full flex items-center justify-between p-2 rounded-lg text-left transition-colors text-[11px] ${
                            acc.is_default 
                              ? 'bg-blue-50 text-blue-700 font-semibold border border-blue-200' 
                              : 'hover:bg-slate-50 text-slate-600'
                          }`}
                        >
                          <span className="truncate max-w-[190px]">{acc.email}</span>
                          {acc.is_default && (
                            <span className="text-[9px] bg-blue-600 text-white px-1.5 py-0.5 rounded-full font-bold">
                              ACTIVE
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="p-1.5 space-y-1">
                  {/* Connect / Add Another Account Button */}
                  <button
                    onClick={handleConnectGoogle}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-blue-600 hover:bg-blue-50 font-medium transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>{connectedAccounts.length > 0 ? 'Add another Gmail account' : 'Connect Gmail Account'}</span>
                  </button>

                  {isConnected && (
                    <button
                      onClick={handleDisconnect}
                      className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-rose-600 hover:bg-rose-50 font-medium transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Disconnect Active Mailbox</span>
                    </button>
                  )}

                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      onSimulate();
                    }}
                    disabled={simulating}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 font-medium transition-colors"
                  >
                    <Zap className="w-4 h-4 text-amber-500" />
                    <span>{simulating ? 'Simulating...' : 'Simulate Attack Batch'}</span>
                  </button>

                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      onReset();
                    }}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50/50 font-medium transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Reset Workspace Data</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

