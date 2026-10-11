import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import StatsOverview from './components/StatsOverview';
import ThreatBanner from './components/ThreatBanner';
import PhishingAlertModal from './components/PhishingAlertModal';
import LiveThreatFeed from './components/LiveThreatFeed';
import EmailList from './components/EmailList';
import EmailDetailModal from './components/EmailDetailModal';
import SandboxScanner from './components/SandboxScanner';
import { 
  getDashboardStats, 
  getEmails, 
  getRecentThreats, 
  syncEmails, 
  simulateBatch, 
  deleteEmail,
  resetDashboard 
} from './services/api';
import { wsClient } from './services/websocket';
import { RotateCcw, Database } from 'lucide-react';

export default function App() {
  const [stats, setStats] = useState(null);
  const [emails, setEmails] = useState([]);
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [currentFilter, setCurrentFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activePhishingAlert, setActivePhishingAlert] = useState(null);
  const [bannerThreat, setBannerThreat] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Load stats
  const fetchStats = useCallback(async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (e) {
      console.error('Error fetching stats:', e);
    }
  }, []);

  // Load emails
  const fetchEmails = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getEmails({
        skip: 0,
        limit: 100,
        classification: currentFilter,
        search: searchQuery || undefined
      });
      setEmails(res.items || []);
    } catch (e) {
      console.error('Error fetching emails:', e);
    } finally {
      setLoading(false);
    }
  }, [currentFilter, searchQuery]);

  // Load recent threats
  const fetchThreats = useCallback(async () => {
    try {
      const res = await getRecentThreats(10);
      setThreats(res || []);
      if (res && res.length > 0 && !bannerThreat) {
        setBannerThreat(res[0]);
      }
    } catch (e) {
      console.error('Error fetching threats:', e);
    }
  }, [bannerThreat]);

  // Initial load and WebSocket listener registration
  useEffect(() => {
    // Check URL for OAuth responses
    const params = new URLSearchParams(window.location.search);
    const authError = params.get('auth_error');
    const authSuccess = params.get('auth');
    if (authError) {
      if (authError === 'MissingClientID') {
        alert("Cannot connect to Google: You must first add your GOOGLE_CLIENT_ID to the backend/.env file.");
      } else {
        alert(`Google Authentication failed: ${authError}`);
      }
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authSuccess === 'success') {
      alert("Successfully connected to Google account!");
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    fetchStats();
    fetchEmails();
    fetchThreats();

    // Start WebSocket
    wsClient.connect();
    const unsubStatus = wsClient.subscribeStatus((connected) => {
      setWsConnected(connected);
    });

    const unsubEvents = wsClient.subscribe((event) => {
      if (event.type === 'PHISHING_ALERT') {
        // High-priority threat alert event
        setActivePhishingAlert(event);
        setBannerThreat(event);
        fetchStats();
        fetchEmails();
        fetchThreats();
      } else if (event.type === 'STATS_UPDATED') {
        fetchStats();
        fetchEmails();
        fetchThreats();
      }
    });

    return () => {
      unsubStatus();
      unsubEvents();
    };
  }, [fetchStats, fetchEmails, fetchThreats]);

  // Handle Sync Gmail
  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncEmails(10);
      await fetchStats();
      await fetchEmails();
      await fetchThreats();
    } catch (e) {
      console.error('Sync failed:', e);
      alert('Gmail sync failed. Please check connection status.');
    } finally {
      setSyncing(false);
    }
  };

  // Handle Simulate Attack Batch
  const handleSimulate = async () => {
    setSimulating(true);
    try {
      await simulateBatch();
      await fetchStats();
      await fetchEmails();
      await fetchThreats();
    } catch (e) {
      console.error('Simulation failed:', e);
    } finally {
      setSimulating(false);
    }
  };

  // Handle Delete email
  const handleDeleteEmail = async (id) => {
    try {
      await deleteEmail(id);
      setEmails((prev) => prev.filter((e) => e.id !== id));
      await fetchStats();
      await fetchThreats();
    } catch (e) {
      console.error('Failed to delete email:', e);
    }
  };

  // Handle Reset data
  const handleReset = async () => {
    if (confirm('Clear all scanned emails and reset dashboard metrics?')) {
      await resetDashboard();
      setBannerThreat(null);
      await fetchStats();
      await fetchEmails();
      await fetchThreats();
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0d14] text-slate-100 flex flex-col selection:bg-sky-500/30 selection:text-sky-200">
      {/* Top Navbar */}
      <Navbar
        stats={stats}
        wsConnected={wsConnected}
        onSync={handleSync}
        syncing={syncing}
        onSimulate={handleSimulate}
        simulating={simulating}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRefresh={() => {
          fetchStats();
          fetchEmails();
          fetchThreats();
        }}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Urgent Threat Banner (if active) */}
        {bannerThreat && (
          <ThreatBanner
            threat={bannerThreat}
            onInspect={(t) => setSelectedEmail(t)}
            onDismiss={() => setBannerThreat(null)}
          />
        )}

        {/* Tab Routing */}
        {activeTab === 'dashboard' ? (
          <div className="space-y-6">
            {/* Stats Metrics Cards */}
            <StatsOverview stats={stats} />

            {/* Two Column Section: Live Threat Feed & Email History Table */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Scan History (Table) */}
              <div className="lg:col-span-8 space-y-4">
                <EmailList
                  emails={emails}
                  loading={loading}
                  onInspect={(email) => setSelectedEmail(email)}
                  onDelete={handleDeleteEmail}
                  currentFilter={currentFilter}
                  onFilterChange={(filter) => setCurrentFilter(filter)}
                  searchQuery={searchQuery}
                  onSearchChange={(q) => setSearchQuery(q)}
                />
              </div>

              {/* Sidebar: Live Threat Feed & Info */}
              <div className="lg:col-span-4 space-y-4">
                <LiveThreatFeed
                  threats={threats}
                  onInspect={(t) => setSelectedEmail(t)}
                />

                {/* Storage & System Status Box */}
                <div className="glass-panel p-4 rounded-2xl text-xs space-y-2.5">
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="flex items-center space-x-1.5">
                      <Database className="w-3.5 h-3.5 text-sky-400" />
                      <span>Data Persistence</span>
                    </span>
                    <span className="font-mono text-emerald-400 font-semibold">
                      {stats?.database_mode || 'Active'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Gmail API Mode</span>
                    <span className="font-mono text-slate-300">
                      {stats?.is_gmail_connected ? (stats?.connected_email ? 'Live Ingest' : 'Connected') : 'Disconnected'}
                    </span>
                  </div>
                  <div className="pt-2 border-t border-slate-800 flex justify-end">
                    <button
                      onClick={handleReset}
                      className="text-[11px] text-slate-500 hover:text-rose-400 flex items-center space-x-1 transition-colors"
                    >
                      <RotateCcw className="w-3 h-3" />
                      <span>Reset Dashboard Data</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Sandbox Interactive Scanner */
          <SandboxScanner
            onScanSaved={() => {
              fetchStats();
              fetchEmails();
              fetchThreats();
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#0c101c] py-4 text-center text-xs text-slate-500">
        AI Phishing Detection System &bull; Powered by Scikit-Learn (TF-IDF + Logistic Regression), FastAPI, WebSockets &amp; React
      </footer>

      {/* High-Priority Real-Time Phishing Alert Modal */}
      {activePhishingAlert && (
        <PhishingAlertModal
          alert={activePhishingAlert}
          onClose={() => setActivePhishingAlert(null)}
          onInspect={(threat) => {
            setSelectedEmail(threat);
            setActivePhishingAlert(null);
          }}
        />
      )}

      {/* Email Detail Inspection Modal */}
      {selectedEmail && (
        <EmailDetailModal
          email={selectedEmail}
          onClose={() => setSelectedEmail(null)}
        />
      )}
    </div>
  );
}
