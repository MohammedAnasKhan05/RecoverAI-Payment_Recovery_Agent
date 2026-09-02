import React from 'react';
import { ShieldCheck, Activity, Database, FileText, ArrowRightLeft, LayoutDashboard } from 'lucide-react';

export default function Navbar({ activePage, setActivePage, isOnline = true }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', icon: ArrowRightLeft },
    { id: 'agent-activity', label: 'Agent Activity', icon: Activity },
    { id: 'rag-evaluation', label: 'RAG Evaluation', icon: Database },
    { id: 'audit-logs', label: 'Audit Logs', icon: FileText },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Tagline */}
          <div className="flex items-center space-x-4 cursor-pointer" onClick={() => setActivePage('dashboard')}>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-blue-700 to-blue-500 flex items-center justify-center shadow-md shadow-blue-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-[#0C2340]">RecoverAI</span>
                <span className="bg-blue-50 text-[#0C6BF5] text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border border-blue-200">
                  Agent
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Recover revenue before it's lost.
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActivePage(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-[#0C6BF5] font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#0C6BF5]' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Health Status Pill */}
          <div className="hidden md:flex items-center space-x-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full text-xs">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-slate-600 font-medium">{isOnline ? 'Live Engine' : 'Backend Offline'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
