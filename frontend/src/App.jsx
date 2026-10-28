import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import KPICards from './components/KPICards';
import EmailDetectionTrend from './components/EmailDetectionTrend';
import EmailClassificationDonut from './components/EmailClassificationDonut';
import TopPhishingIndicators from './components/TopPhishingIndicators';
import RecentEmailsTable from './components/RecentEmailsTable';
import LatestAnalysisCard from './components/LatestAnalysisCard';
import EmailHistoryView from './components/EmailHistoryView';
import ModelPerformanceView from './components/ModelPerformanceView';
import SettingsView from './components/SettingsView';
import SandboxScanner from './components/SandboxScanner';
import PhishingAlertModal from './components/PhishingAlertModal';
import EmailDetailModal from './components/EmailDetailModal';
import Footer from './components/Footer';

// Lazily loaded legal compliance views with ad-blocker immune component names
const DataProtectionNotice = React.lazy(() => import('./components/DataProtectionNotice'));
const ServiceTermsNotice = React.lazy(() => import('./components/ServiceTermsNotice'));
import { 
  getDashboardStats, 
  getEmails, 
  getRecentThreats, 
  syncEmails, 
  simulateBatch, 
  deleteEmail,
  resetDashboard,
  initSession,
  setStoredToken,
  setCurrentUserId
} from './services/api';
import { wsClient } from './services/websocket';
import { RefreshCw, Zap } from 'lucide-react';

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
  
  // Resolve initial view based on browser path (/privacy-policy or /terms)
  const getInitialTab = () => {
    if (typeof window !== 'undefined') {
      const path = window.location.pathname.toLowerCase();
      if (path.startsWith('/privacy')) return 'privacy';
      if (path.startsWith('/terms')) return 'terms';
    }
    return 'dashboard';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Sync tab with browser URL history
  const navigateToTab = useCallback((tab, path = null) => {
    setActiveTab(tab);
    setMobileOpen(false);
    if (path) {
      window.history.pushState({}, '', path);
    } else if (tab === 'privacy') {
      window.history.pushState({}, '', '/privacy-policy');
    } else if (tab === 'terms') {
      window.history.pushState({}, '', '/terms');
    } else if (tab === 'dashboard') {
      window.history.pushState({}, '', '/');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Listen for browser Back / Forward buttons
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname.toLowerCase();
      if (path.startsWith('/privacy')) {
        setActiveTab('privacy');
      } else if (path.startsWith('/terms')) {
        setActiveTab('terms');
      } else {
        setActiveTab('dashboard');
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

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
    const authToken = params.get('token');
    const authUserId = params.get('user_id');
    const authAccount = params.get('account') || params.get('email');

    if (authToken) {
      setStoredToken(authToken);
      if (authUserId) setCurrentUserId(authUserId);
    }

    if (authError) {
      if (authError === 'MissingClientID') {
        alert("Cannot connect to Google: You must first add your GOOGLE_CLIENT_ID to your environment.");
      } else {
        alert(`Google Authentication failed: ${authError}`);
      }
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authSuccess === 'success') {
      alert(`Successfully connected Google account: ${authAccount || 'Gmail Mailbox'}!`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Initialize authenticated server session and then fetch data
    const initializeData = async () => {
      try {
        await initSession();
        await fetchStats();
        await fetchEmails();
        await fetchThreats();
      } catch (err) {
        console.error("Session initialization error:", err);
      }
    };
    initializeData();

    // Start WebSocket
    wsClient.connect();
    const unsubStatus = wsClient.subscribeStatus((connected) => {
      setWsConnected(connected);
    });

    const unsubEvents = wsClient.subscribe((event) => {
      if (event.type === 'PHISHING_ALERT') {
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
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex">
      {/* 1. Left Dark Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        wsConnected={wsConnected}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* 2. Main Layout Area (Offset on desktop for sidebar) */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0 min-h-screen">
        {/* Top Header */}
        <TopHeader
          stats={stats}
          onSync={handleSync}
          syncing={syncing}
          onSimulate={handleSimulate}
          simulating={simulating}
          onRefresh={() => {
            fetchStats();
            fetchEmails();
            fetchThreats();
          }}
          onReset={handleReset}
          setMobileOpen={setMobileOpen}
        />

        {/* Content View Container */}
        <main className="p-4 sm:p-8 space-y-6 max-w-7xl w-full mx-auto">
          {activeTab === 'dashboard' && (
            <div className="space-y-6 animate-fadeIn">
              {/* Dashboard Title & Subtitle + Action Buttons */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight">
                    Dashboard
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">
                    Monitor and analyze email security with AI-powered phishing detection.
                  </p>
                </div>

                {/* Quick Action Buttons */}
                <div className="flex items-center space-x-2.5">
                  <button
                    onClick={handleSync}
                    disabled={syncing}
                    className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
                    <span>{syncing ? 'Syncing...' : 'Sync Gmail'}</span>
                  </button>

                  <button
                    onClick={handleSimulate}
                    disabled={simulating}
                    className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 shadow-sm transition-all disabled:opacity-50"
                  >
                    <Zap className="w-3.5 h-3.5 text-amber-500" />
                    <span>{simulating ? 'Simulating...' : 'Simulate Attack'}</span>
                  </button>
                </div>
              </div>

              {/* Row 1: 4 Top KPI Metric Cards */}
              <KPICards stats={stats} />

              {/* Row 2: 3 Analytics Cards (Line Chart, Donut Chart, Indicators) */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-5">
                {/* 1. Email Detection Trend (5 cols) */}
                <div className="lg:col-span-5">
                  <EmailDetectionTrend emails={emails} />
                </div>

                {/* 2. Email Classification Donut (3 cols) */}
                <div className="lg:col-span-3">
                  <EmailClassificationDonut stats={stats} />
                </div>

                {/* 3. Top Phishing Indicators (4 cols) */}
                <div className="lg:col-span-4 md:col-span-2 lg:col-span-4">
                  <TopPhishingIndicators />
                </div>
              </div>

              {/* Row 3: Recent Emails Table (~68%) + Latest Analysis (~32%) */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                {/* Recent Emails Table (8 cols) */}
                <div className="lg:col-span-8">
                  <RecentEmailsTable
                    emails={emails}
                    loading={loading}
                    onInspect={(email) => setSelectedEmail(email)}
                  />
                </div>

                {/* Latest Analysis Card (4 cols) */}
                <div className="lg:col-span-4">
                  <LatestAnalysisCard
                    latestThreat={bannerThreat || threats[0]}
                    onInspect={(threat) => setSelectedEmail(threat)}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'scan' && (
            <SandboxScanner
              onScanSaved={() => {
                fetchStats();
                fetchEmails();
                fetchThreats();
              }}
            />
          )}

          {activeTab === 'history' && (
            <EmailHistoryView
              emails={emails}
              loading={loading}
              currentFilter={currentFilter}
              onFilterChange={(f) => setCurrentFilter(f)}
              searchQuery={searchQuery}
              onSearchChange={(q) => setSearchQuery(q)}
              onInspect={(email) => setSelectedEmail(email)}
              onDelete={handleDeleteEmail}
              onRefresh={() => {
                fetchStats();
                fetchEmails();
                fetchThreats();
              }}
            />
          )}

          {activeTab === 'performance' && (
            <ModelPerformanceView stats={stats} />
          )}

          {activeTab === 'settings' && (
            <SettingsView
              stats={stats}
              wsConnected={wsConnected}
              onRefresh={() => {
                fetchStats();
                fetchEmails();
                fetchThreats();
              }}
              onReset={handleReset}
            />
          )}

          {activeTab === 'privacy' && (
            <React.Suspense fallback={<div className="p-8 text-center text-xs text-slate-500 font-medium">Loading Privacy Policy...</div>}>
              <DataProtectionNotice onBack={() => navigateToTab('dashboard', '/')} />
            </React.Suspense>
          )}

          {activeTab === 'terms' && (
            <React.Suspense fallback={<div className="p-8 text-center text-xs text-slate-500 font-medium">Loading Terms of Service...</div>}>
              <ServiceTermsNotice onBack={() => navigateToTab('dashboard', '/')} />
            </React.Suspense>
          )}
        </main>

        {/* Website Footer with Public Policy Links */}
        <Footer onNavigate={navigateToTab} />
      </div>

      {/* Real-Time WebSocket Phishing Alert Modal */}
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

      {/* Email Detailed Forensic Modal */}
      {selectedEmail && (
        <EmailDetailModal
          email={selectedEmail}
          onClose={() => setSelectedEmail(null)}
        />
      )}
    </div>
  );
}
