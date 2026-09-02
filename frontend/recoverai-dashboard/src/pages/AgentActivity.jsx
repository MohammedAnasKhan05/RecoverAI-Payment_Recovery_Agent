import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  Search, 
  RefreshCw, 
  ArrowRight,
  Zap,
  Sliders,
  Database,
  Brain,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { fetchGlobalAudit, fetchTransactions, fetchTransactionDetail } from '../services/api';
import ActionBadge from '../components/ActionBadge';
import StatusBadge from '../components/StatusBadge';

export default function AgentActivity({ onSelectTransaction }) {
  const [selectedTxId, setSelectedTxId] = useState('TX001');
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [globalLogs, setGlobalLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async (txId = selectedTxId) => {
    setLoading(true);
    try {
      const [detailRes, logsRes] = await Promise.all([
        fetchTransactionDetail(txId).catch(() => null),
        fetchGlobalAudit({ limit: 25 })
      ]);
      setSelectedDetail(detailRes);
      setGlobalLogs(logsRes.audit_logs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedTxId);
  }, [selectedTxId]);

  const lifecycleStages = [
    { name: 'Failure detected', icon: Clock, desc: 'Transaction failure captured and queued for evaluation' },
    { name: 'Risk analysis completed', icon: Brain, desc: 'PaySim RandomForest ML fraud risk evaluation' },
    { name: 'Recovery probability calculated', icon: Sliders, desc: 'Viability computation based on customer tier & ticket size' },
    { name: 'Policy retrieved', icon: Database, desc: 'RAG vector similarity match against domain recovery policies' },
    { name: 'AI recommendation generated', icon: Zap, desc: 'Autonomous agent structured recommendation' },
    { name: 'Guardrail decision', icon: ShieldCheck, desc: 'Deterministic safety rules verification & override' },
    { name: 'Recovery executed', icon: RotateCcw, desc: 'Mock payment recovery execution dispatch' },
    { name: 'Recovery successful', altName: ['Recovery failed', 'Recovery escalated', 'Recovery stopped'], icon: CheckCircle2, desc: 'Final financial and operational outcome' },
  ];

  const audits = selectedDetail?.audit_logs || [];

  return (
    <div className="space-y-8 pb-16 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#0C2340]">Agent Activity & Telemetry</h1>
          <p className="text-sm text-slate-500">
            End-to-end execution trace from failure detection to resolution
          </p>
        </div>

        {/* Transaction Quick Switcher */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-medium">Inspect Flow:</span>
          {['TX001', 'TX002', 'TX003', 'TX004'].map((id) => (
            <button
              key={id}
              onClick={() => setSelectedTxId(id)}
              className={`px-3 py-1 rounded-lg text-xs font-mono font-bold border transition ${
                selectedTxId === id
                  ? 'bg-[#0C6BF5] text-white border-[#0C6BF5] shadow-sm'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      {/* 8-Stage Lifecycle Timeline */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 card-shadow">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-2">
          <div>
            <h2 className="text-lg font-bold text-[#0C2340]">
              Lifecycle Flow: <span className="font-mono text-[#0C6BF5]">{selectedTxId}</span>
            </h2>
            <p className="text-xs text-slate-500">
              Amount: ₹{selectedDetail?.transaction?.amount?.toLocaleString('en-IN') || '—'} • 
              Reason: {selectedDetail?.transaction?.failure_reason || '—'} • 
              Status: <span className="font-semibold">{selectedDetail?.transaction?.status || '—'}</span>
            </p>
          </div>
          {selectedDetail && (
            <button
              onClick={() => onSelectTransaction(selectedTxId)}
              className="text-xs font-semibold text-[#0C6BF5] hover:text-blue-700 inline-flex items-center space-x-1"
            >
              <span>Open Transaction Details</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Timeline Grid */}
        <div className="mt-8 relative pl-6 space-y-8 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
          {lifecycleStages.map((stage, idx) => {
            const Icon = stage.icon;
            // Check if matching audit log exists
            const matchedLog = audits.find((a) => 
              a.event.toLowerCase() === stage.name.toLowerCase() ||
              (stage.altName && stage.altName.some(an => an.toLowerCase() === a.event.toLowerCase()))
            );

            const isCompleted = !!matchedLog;

            return (
              <div key={idx} className="relative flex items-start space-x-4">
                {/* Node indicator */}
                <div className={`absolute -left-6 top-1 w-6 h-6 rounded-full flex items-center justify-center border-2 ${
                  isCompleted 
                    ? 'bg-blue-50 border-[#0C6BF5] text-[#0C6BF5]' 
                    : 'bg-white border-slate-300 text-slate-300'
                }`}>
                  <Icon className="w-3 h-3" />
                </div>

                <div className={`flex-1 p-4 rounded-xl border transition ${
                  isCompleted 
                    ? 'bg-white border-slate-200 shadow-sm' 
                    : 'bg-slate-50/60 border-slate-200/60 opacity-60'
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-[#0C2340]">
                        {matchedLog?.event || stage.name}
                      </span>
                      {matchedLog?.action && <ActionBadge action={matchedLog.action} />}
                    </div>
                    {matchedLog?.timestamp && (
                      <span className="text-[11px] font-mono text-slate-400">
                        {new Date(matchedLog.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-600 mt-1">
                    {matchedLog?.reason || stage.desc}
                  </p>

                  {matchedLog && (
                    <div className="mt-2 pt-2 border-t border-slate-100 flex items-center space-x-4 text-[11px] text-slate-500">
                      <span>Decision: <strong className="text-slate-700">{matchedLog.decision}</strong></span>
                      <span>Result: <strong className="text-slate-700">{matchedLog.result}</strong></span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Global Activity Stream */}
      <div className="bg-white rounded-2xl border border-slate-200 card-shadow overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#0C2340]">Live Multi-Transaction Event Stream</h3>
            <p className="text-xs text-slate-500 mt-0.5">Global audit stream across all pipeline transactions</p>
          </div>
          <button onClick={() => loadData(selectedTxId)} className="p-1.5 border rounded-lg text-slate-500 hover:bg-slate-50">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#0C6BF5]' : ''}`} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Timestamp</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Transaction</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Event</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Action</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Result</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {globalLogs.slice(0, 10).map((log) => (
                <tr 
                  key={log.id} 
                  onClick={() => onSelectTransaction(log.transaction_id)}
                  className="hover:bg-slate-50 cursor-pointer transition"
                >
                  <td className="px-6 py-3 font-mono text-slate-400 whitespace-nowrap">
                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                  </td>
                  <td className="px-6 py-3 font-mono font-bold text-[#0C6BF5]">
                    {log.transaction_id}
                  </td>
                  <td className="px-6 py-3 font-medium text-slate-800">
                    {log.event}
                  </td>
                  <td className="px-6 py-3">
                    <ActionBadge action={log.action} />
                  </td>
                  <td className="px-6 py-3">
                    <span className="font-semibold text-slate-700">{log.result}</span>
                  </td>
                  <td className="px-6 py-3 text-slate-600 max-w-xs truncate">
                    {log.reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
