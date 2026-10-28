import React from 'react';
import { 
  ShieldCheck, 
  LayoutDashboard, 
  MailSearch, 
  History, 
  BarChart3, 
  Settings,
  X
} from 'lucide-react';

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  wsConnected,
  mobileOpen,
  setMobileOpen 
}) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'scan', label: 'Scan Email', icon: MailSearch },
    { id: 'history', label: 'Email History', icon: History },
    { id: 'performance', label: 'Model Performance', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#0F172A] text-slate-300 flex flex-col justify-between border-r border-slate-800 transition-transform duration-300 ease-in-out
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Top Branding */}
        <div>
          <div className="p-6 flex items-center justify-between border-b border-slate-800/80">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                <ShieldCheck className="w-6 h-6 stroke-[2.2]" />
              </div>
              <div>
                <h1 className="font-bold text-white text-base tracking-tight leading-tight">
                  AI Phishing Email
                </h1>
                <p className="text-xs text-slate-400 font-medium">Detection System</p>
              </div>
            </div>

            {/* Mobile Close Button */}
            <button 
              onClick={() => setMobileOpen(false)}
              className="lg:hidden text-slate-400 hover:text-white p-1 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setMobileOpen(false);
                  }}
                  className={`
                    w-full flex items-center space-x-3.5 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-150
                    ${isActive 
                      ? 'bg-[#2563EB] text-white shadow-md shadow-blue-600/30' 
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/70'
                    }
                  `}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom System Status */}
        <div className="p-5 border-t border-slate-800/80 space-y-1 bg-[#090D1A]">
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-300">
            <span className="relative flex h-2.5 w-2.5">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${wsConnected ? 'bg-emerald-400' : 'bg-amber-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${wsConnected ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
            </span>
            <span className="text-emerald-400 font-semibold">System Online</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono">AI Model v1.0 &bull; 99.4% Acc</p>
        </div>
      </aside>
    </>
  );
}
