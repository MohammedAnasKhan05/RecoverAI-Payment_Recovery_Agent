import React, { useState, useEffect } from 'react';
import { FileText, Search, RefreshCw, ArrowRight, Filter } from 'lucide-react';
import { fetchGlobalAudit } from '../services/api';
import ActionBadge from '../components/ActionBadge';

export default function AuditLogs({ onSelectTransaction }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchGlobalAudit({ limit: 100 });
      setLogs(data.audit_logs || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      log.transaction_id.toLowerCase().includes(term) ||
      log.event.toLowerCase().includes(term) ||
      log.action.toLowerCase().includes(term) ||
      (log.reason && log.reason.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-6 pb-16 w-full max-w-[1500px] mx-auto ">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#0C2340]">Audit Logs & Compliance Ledger</h1>
          <p className="text-sm text-slate-500">
            Immutable trace of all automated risk scoring, AI recommendations, guardrail decisions, and recovery executions
          </p>
        </div>

        <button
          onClick={loadLogs}
          className="p-2 border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-600 transition self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#0C6BF5]' : ''}`} />
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 card-shadow flex items-center justify-between">
        <div className="relative w-full max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by transaction ID, event, action..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-[#0C6BF5] focus:bg-white transition"
          />
        </div>
        <span className="text-xs font-semibold text-slate-500">
          Showing {filteredLogs.length} events
        </span>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white rounded-2xl border border-slate-200 card-shadow overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center justify-center space-y-2">
            <RefreshCw className="w-6 h-6 text-[#0C6BF5] animate-spin" />
            <span className="text-sm">Loading audit events...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <p className="text-sm">No audit logs found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Transaction ID</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Event</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Action</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Decision</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Result</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Amount</th>
                  <th className="px-6 py-3.5 font-semibold text-slate-500 uppercase">Reason / Context</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100">
                {filteredLogs.map((log) => (
                  <tr
                    key={log.id}
                    onClick={() => onSelectTransaction(log.transaction_id)}
                    className="hover:bg-blue-50/50 cursor-pointer transition"
                  >
                    <td className="px-6 py-3.5 font-mono text-slate-400 whitespace-nowrap">
                      {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                    </td>
                    <td className="px-6 py-3.5 font-mono font-bold text-[#0C6BF5] whitespace-nowrap">
                      {log.transaction_id}
                    </td>
                    <td className="px-6 py-3.5 font-semibold text-[#0C2340] whitespace-nowrap">
                      {log.event}
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <ActionBadge action={log.action} />
                    </td>
                    <td className="px-6 py-3.5 font-medium text-slate-700 whitespace-nowrap">
                      {log.decision}
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <span className={`font-semibold ${log.result === 'SUCCESS' ? 'text-emerald-600' :
                        log.result === 'FAILED' ? 'text-rose-600' :
                          log.result === 'ESCALATED' ? 'text-amber-600' : 'text-slate-600'
                        }`}>
                        {log.result}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 font-semibold text-slate-900 whitespace-nowrap">
                      {log.amount > 0 ? `₹${Number(log.amount).toLocaleString('en-IN')}` : '—'}
                    </td>
                    <td className="px-6 py-3.5 text-slate-600 max-w-sm truncate" title={log.reason}>
                      {log.reason}
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
