import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  LogOut, 
  ExternalLink, 
  Database, 
  RotateCcw,
  Key,
  Plus,
  Mail,
  Zap,
  User,
  RefreshCw,
  Lock
} from 'lucide-react';
import { 
  getAccounts, 
  selectAccount, 
  disconnectAccount, 
  connectDemoMailbox,
  getCurrentUserId,
  setCurrentUserId,
  switchUser
} from '../services/api';
import { formatEmailDateIST } from '../utils/dateFormatter';

export default function SettingsView({ stats, wsConnected, onRefresh, onReset }) {
  const [accounts, setAccounts] = useState([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [userProfile, setUserProfile] = useState(getCurrentUserId());
  const [switchingUser, setSwitchingUser] = useState(false);

  const fetchConnectedAccounts = async () => {
    setLoadingAccounts(true);
    try {
      const res = await getAccounts();
      setAccounts(res.accounts || []);
    } catch (e) {
      console.error('Failed to load connected accounts:', e);
    } finally {
      setLoadingAccounts(false);
    }
  };

  useEffect(() => {
    fetchConnectedAccounts();
  }, []);

  const handleConnectGoogle = () => {
    const currentUserId = getCurrentUserId();
    // Pass user_id and prompt=select_account so Google presents the account chooser
    window.location.href = `http://localhost:8000/api/auth/google/login?user_id=${encodeURIComponent(currentUserId)}&prompt=select_account`;
  };

  const handleSelectActive = async (accountId) => {
    try {
      await selectAccount(accountId);
      await fetchConnectedAccounts();
      onRefresh();
    } catch (e) {
      alert("Failed to activate account: " + (e.response?.data?.detail || e.message));
    }
  };

  const handleDisconnect = async (accountId, email) => {
    if (confirm(`Are you sure you want to disconnect ${email}? Tokens will be revoked and removed.`)) {
      try {
        await disconnectAccount(accountId);
        await fetchConnectedAccounts();
        onRefresh();
      } catch (e) {
        alert("Failed to disconnect account: " + (e.response?.data?.detail || e.message));
      }
    }
  };

  const handleConnectDemo = async () => {
    try {
      await connectDemoMailbox();
      await fetchConnectedAccounts();
      onRefresh();
    } catch (e) {
      alert("Failed to connect demo mailbox: " + (e.response?.data?.detail || e.message));
    }
  };

  const handleSwitchUserSession = async (newUserId) => {
    if (!newUserId.trim()) return;
    setSwitchingUser(true);
    try {
      await switchUser(newUserId.trim());
      setUserProfile(newUserId.trim());
      await fetchConnectedAccounts();
      onRefresh();
    } catch (e) {
      alert("Failed to switch user: " + (e.response?.data?.detail || e.message));
    } finally {
      setSwitchingUser(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">System Settings & Accounts</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Manage multiple connected Google accounts, user isolation workspaces, and storage telemetry.
        </p>
      </div>

      {/* 1. Multi-User Workspace Isolation */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">User Workspace Isolation</h3>
              <p className="text-xs text-slate-500">Each user workspace completely isolates connected Gmail accounts, scans, and alerts.</p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-violet-50 text-violet-700 border border-violet-200">
            Tenant Isolated
          </span>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
          <div>
            <span className="text-slate-500 font-medium">Active Workspace User:</span>
            <div className="font-mono font-bold text-slate-900 text-sm mt-0.5 flex items-center space-x-2">
              <span>{userProfile}</span>
              <span className="text-[11px] text-slate-400 font-normal">({accounts.length} linked accounts)</span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleSwitchUserSession('default_user')}
              disabled={userProfile === 'default_user' || switchingUser}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                userProfile === 'default_user' 
                  ? 'bg-violet-600 text-white border-violet-600' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              Default User
            </button>
            <button
              onClick={() => handleSwitchUserSession('analyst_alpha')}
              disabled={userProfile === 'analyst_alpha' || switchingUser}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                userProfile === 'analyst_alpha' 
                  ? 'bg-violet-600 text-white border-violet-600' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              User Alpha
            </button>
            <button
              onClick={() => handleSwitchUserSession('analyst_beta')}
              disabled={userProfile === 'analyst_beta' || switchingUser}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                userProfile === 'analyst_beta' 
                  ? 'bg-violet-600 text-white border-violet-600' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              User Beta
            </button>
          </div>
        </div>
      </div>

      {/* 2. Connected Google Accounts (Multi-Account Support) */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Connected Gmail Accounts</h3>
              <p className="text-xs text-slate-500">Authorize multiple Gmail mailboxes. Passwords are never collected or stored.</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={fetchConnectedAccounts}
              disabled={loadingAccounts}
              title="Refresh accounts list"
              className="p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loadingAccounts ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Account Cards List */}
        <div className="space-y-3">
          {accounts.length === 0 ? (
            <div className="p-8 text-center rounded-xl border border-dashed border-slate-300 bg-slate-50/50 space-y-3">
              <div className="w-12 h-12 mx-auto rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                <Mail className="w-6 h-6" />
              </div>
              <div>
                <p className="font-bold text-slate-800 text-sm">No Gmail Accounts Connected</p>
                <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                  Connect your Google account using read-only OAuth 2.0 to begin scanning for advanced phishing threats.
                </p>
              </div>
              <div className="pt-2 flex items-center justify-center space-x-3">
                <button
                  onClick={handleConnectGoogle}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition-colors flex items-center space-x-1.5"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Connect Gmail</span>
                </button>
                <button
                  onClick={handleConnectDemo}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 shadow-sm transition-colors flex items-center space-x-1.5"
                >
                  <Zap className="w-3.5 h-3.5 text-amber-500" />
                  <span>Connect Demo Mailbox</span>
                </button>
              </div>
            </div>
          ) : (
            accounts.map((acc) => {
              const isDefault = acc.is_default;
              const isActiveStatus = acc.status === 'active';
              const isRevoked = acc.status === 'revoked' || acc.status === 'expired';

              return (
                <div 
                  key={acc.id}
                  className={`p-4 rounded-xl border transition-all ${
                    isDefault 
                      ? 'bg-blue-50/40 border-blue-200 ring-1 ring-blue-300/40' 
                      : 'bg-slate-50/70 border-slate-200/80 hover:border-slate-300'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-slate-900 text-sm">{acc.email}</span>
                        {isDefault && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-600 text-white">
                            Active Scanner
                          </span>
                        )}
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium border ${
                          acc.mode === 'live' 
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                            : 'bg-amber-50 text-amber-700 border-amber-200'
                        }`}>
                          {acc.mode === 'live' ? 'Live OAuth' : 'Demo Mode'}
                        </span>
                      </div>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-500">
                        <span className="flex items-center space-x-1">
                          <span>Status:</span>
                          {isActiveStatus ? (
                            <span className="text-emerald-600 font-semibold flex items-center space-x-0.5">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Connected</span>
                            </span>
                          ) : (
                            <span className="text-rose-600 font-semibold flex items-center space-x-0.5">
                              <AlertCircle className="w-3 h-3" />
                              <span>{isRevoked ? 'Re-auth Required' : 'Disconnected'}</span>
                            </span>
                          )}
                        </span>

                        {acc.last_synced_at && (
                          <span>Last Synced: <strong className="text-slate-700 font-normal">{acc.last_synced_at}</strong></span>
                        )}
                      </div>

                      {acc.error_message && (
                        <p className="text-[11px] text-rose-600 font-medium">{acc.error_message}</p>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2 pt-2 sm:pt-0">
                      {!isDefault && (
                        <button
                          onClick={() => handleSelectActive(acc.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 shadow-sm transition-colors"
                        >
                          Set as Active
                        </button>
                      )}

                      {isRevoked ? (
                        <button
                          onClick={handleConnectGoogle}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-amber-600 hover:bg-amber-700 shadow-sm transition-colors flex items-center space-x-1"
                        >
                          <RefreshCw className="w-3 h-3" />
                          <span>Reconnect</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleDisconnect(acc.id, acc.email)}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium text-rose-600 bg-white border border-rose-200 hover:bg-rose-50 shadow-sm transition-colors flex items-center space-x-1"
                        >
                          <LogOut className="w-3 h-3" />
                          <span>Disconnect</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Add Account Buttons (Requirement 1) */}
        {accounts.length > 0 && (
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={handleConnectGoogle}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition-colors flex items-center space-x-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add another Gmail account</span>
            </button>
            <button
              onClick={handleConnectDemo}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 shadow-sm transition-colors flex items-center space-x-1.5"
            >
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              <span>Add Demo Mailbox</span>
            </button>
          </div>
        )}
      </div>

      {/* Security & Scopes Information */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm space-y-3">
        <div className="flex items-center space-x-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm">OAuth 2.0 Security & Minimal Scopes</h3>
            <p className="text-xs text-slate-500">Security guarantees and cryptographic storage standards.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="font-bold text-slate-800">Minimum Gmail Scope:</span>
            <p className="font-mono text-[11px] text-blue-600">gmail.readonly</p>
            <p className="text-[11px] text-slate-500">Strictly read-only access. Cannot delete, modify, or send emails.</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="font-bold text-slate-800">AES/Fernet Token Encryption:</span>
            <p className="text-[11px] text-emerald-600 font-medium">Encrypted At Rest</p>
            <p className="text-[11px] text-slate-500">Access and refresh tokens are encrypted in DB and never exposed to the frontend.</p>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="font-bold text-slate-800">Safe Disconnect / Revocation:</span>
            <p className="text-[11px] text-purple-600 font-medium">Google Revoke API</p>
            <p className="text-[11px] text-slate-500">Disconnecting purges local records and revokes permissions with Google.</p>
          </div>
        </div>
      </div>

      {/* Database & Telemetry */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-sm space-y-4">
        <div className="flex items-center space-x-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm">Storage & Telemetry Service</h3>
            <p className="text-xs text-slate-500">Database persistence engine and live event broadcast stream.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="text-slate-500 font-medium">Database Persistence:</span>
            <div className="font-bold text-slate-900 font-mono">
              {stats?.database_mode || 'Local Storage JSON (database/local_storage.json)'}
            </div>
            <p className="text-[11px] text-slate-500">Zero data loss with automatic MongoDB/JSON fallbacks.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
            <span className="text-slate-500 font-medium">WebSocket Alert Stream:</span>
            <div className="flex items-center space-x-2 mt-0.5">
              <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              <span className="font-bold text-slate-900 font-mono">
                {wsConnected ? 'Connected (ws://127.0.0.1:8000/ws/alerts)' : 'Reconnecting...'}
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Pushes real-time alerts the second threats are ingested.</p>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-2xl p-6 border border-rose-200 shadow-sm space-y-3">
        <h3 className="font-bold text-rose-600 text-sm">Danger Zone</h3>
        <p className="text-xs text-slate-500">
          Reset scanned email history and threat logs for current workspace user (<strong className="font-mono text-slate-700">{userProfile}</strong>).
        </p>

        <div className="pt-1">
          <button
            onClick={onReset}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-rose-600 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition-colors flex items-center space-x-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Scanned Data for {userProfile}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

