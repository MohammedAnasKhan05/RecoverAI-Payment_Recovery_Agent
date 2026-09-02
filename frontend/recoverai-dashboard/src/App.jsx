import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import TransactionDetails from './pages/TransactionDetails';
import AgentActivity from './pages/AgentActivity';
import RagEvaluation from './pages/RagEvaluation';
import AuditLogs from './pages/AuditLogs';
import { fetchHealth } from './services/api';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedTxId, setSelectedTxId] = useState(null);
  const [isOnline, setIsOnline] = useState(true);

  // Check health periodically
  useEffect(() => {
    const check = async () => {
      try {
        await fetchHealth();
        setIsOnline(true);
      } catch (err) {
        setIsOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectTransaction = (txId) => {
    setSelectedTxId(txId);
    setActivePage('transaction-detail');
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0C2340] flex flex-col font-sans">
      <Navbar
        activePage={activePage}
        setActivePage={(page) => {
          setActivePage(page);
          if (page !== 'transaction-detail') setSelectedTxId(null);
        }}
        isOnline={isOnline}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activePage === 'dashboard' && (
          <Dashboard
            onSelectTransaction={handleSelectTransaction}
            setActivePage={setActivePage}
          />
        )}

        {activePage === 'transactions' && (
          <Transactions
            onSelectTransaction={handleSelectTransaction}
          />
        )}

        {activePage === 'transaction-detail' && (
          <TransactionDetails
            transactionId={selectedTxId || 'TX001'}
            onBack={() => setActivePage('transactions')}
          />
        )}

        {activePage === 'agent-activity' && (
          <AgentActivity
            onSelectTransaction={handleSelectTransaction}
          />
        )}

        {activePage === 'rag-evaluation' && (
          <RagEvaluation />
        )}

        {activePage === 'audit-logs' && (
          <AuditLogs
            onSelectTransaction={handleSelectTransaction}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-[#0C2340]">RecoverAI</span>
            <span>—</span>
            <span>Autonomous Revenue Recovery Agent</span>
          </div>
          <div className="text-slate-400">
            Local Mock Execution Sandbox • No Real Payments Processed •<b>Created by <a href="https://www.linkedin.com/in/mohammedanaskhan05/" target="_blank" rel="noopener noreferrer">Mohammed Anas Khan</a></b>
          </div>
        </div>
      </footer>
    </div>
  );
}
