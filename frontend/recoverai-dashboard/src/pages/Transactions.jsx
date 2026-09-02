import React, { useState, useEffect } from 'react';
import { Search, Filter, RefreshCw, ArrowRight, ArrowUpDown } from 'lucide-react';
import { fetchTransactions } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import ActionBadge from '../components/ActionBadge';

export default function Transactions({ onSelectTransaction }) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  const filters = [
    { id: 'ALL', label: 'All' },
    { id: 'AT_RISK', label: 'Recoverable' },
    { id: 'RECOVERED', label: 'Recovered' },
    { id: 'ESCALATED', label: 'Escalated' },
    { id: 'STOPPED', label: 'Stopped' },
  ];

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const data = await fetchTransactions({
        status: filterStatus,
        limit: 100
      });
      setTransactions(data.transactions || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [filterStatus]);

  const filtered = transactions.filter((tx) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      tx.transaction_id.toLowerCase().includes(term) ||
      tx.customer_id.toLowerCase().includes(term) ||
      tx.payment_method.toLowerCase().includes(term) ||
      tx.failure_reason.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#0C2340]">Transactions</h1>
          <p className="text-sm text-slate-500">
            Real-time pipeline of failed, at-risk, and recovered revenue transactions
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadTransactions}
            className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-600 transition"
            title="Refresh list"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#0C6BF5]' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 card-shadow flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Status Pills */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setFilterStatus(f.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                filterStatus === f.id
                  ? 'bg-[#0C6BF5] text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search TX ID, customer, method..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-[#0C6BF5] focus:bg-white transition"
          />
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-xl border border-slate-200 card-shadow overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center space-y-2">
            <RefreshCw className="w-6 h-6 text-[#0C6BF5] animate-spin" />
            <span className="text-sm">Fetching transactions...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <p className="text-sm">No transactions match your search criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Transaction ID</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Amount</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Method</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Failure Reason</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Fraud Risk</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Recovery Prob</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Recommended Action</th>
                  <th className="px-6 py-3.5 text-xs font-semibold text-slate-500 uppercase">Status</th>
                  <th className="px-6 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100 text-sm">
                {filtered.map((tx) => (
                  <tr
                    key={tx.transaction_id}
                    onClick={() => onSelectTransaction(tx.transaction_id)}
                    className="hover:bg-blue-50/40 cursor-pointer transition"
                  >
                    <td className="px-6 py-4 font-mono font-medium text-slate-900">
                      {tx.transaction_id}
                    </td>
                    <td className="px-6 py-4 font-semibold text-[#0C2340]">
                      ₹{Number(tx.amount).toLocaleString('en-IN')}
                    </td>
                    <td className="px-6 py-4 uppercase text-xs font-semibold text-slate-600">
                      {tx.payment_method}
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-slate-600">
                      <span className="bg-slate-100 px-2 py-0.5 rounded border border-slate-200 font-mono">
                        {tx.failure_reason}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs font-bold ${tx.fraud_probability > 0.50 ? 'text-rose-600' : 'text-slate-700'}`}>
                        {(tx.fraud_probability * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-bold text-emerald-600">
                        {(tx.recovery_probability * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <ActionBadge action={tx.recovery_action} />
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={tx.status} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectTransaction(tx.transaction_id);
                        }}
                        className="text-xs bg-slate-100 hover:bg-blue-50 text-[#0C6BF5] px-2.5 py-1 rounded font-semibold border border-slate-200 transition inline-flex items-center space-x-1"
                      >
                        <span>Details</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
