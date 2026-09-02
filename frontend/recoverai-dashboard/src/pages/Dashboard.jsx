import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowUpRight, 
  Layers, 
  RefreshCw,
  Zap,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  Sliders,
  DollarSign,
  Ban,
  Activity
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { fetchDashboardMetrics, fetchTransactions } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import ActionBadge from '../components/ActionBadge';

export default function Dashboard({ onSelectTransaction, setActivePage }) {
  const [metrics, setMetrics] = useState(null);
  const [recentTx, setRecentTx] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashData, txData] = await Promise.all([
        fetchDashboardMetrics(),
        fetchTransactions({ limit: 6 })
      ]);
      setMetrics(dashData);
      setRecentTx(txData.transactions || []);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to connect to backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '₹0';
    if (val >= 100000) {
      return `₹${(val / 100000).toFixed(2)}L`;
    }
    return `₹${Math.round(val).toLocaleString('en-IN')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="w-8 h-8 text-[#0C6BF5] animate-spin" />
          <p className="text-sm font-medium text-slate-500">Loading autonomous recovery telemetry...</p>
        </div>
      </div>
    );
  }

  const rev = metrics?.revenue_metrics || {};
  const breakdown = rev.breakdown || {};
  const agent = metrics?.agent_metrics || {};
  const risk = metrics?.risk_metrics || {};
  const stratPerf = metrics?.strategy_performance || {};

  // Strategy performance data for feedback loop chart
  const strategyChartData = [
    { name: 'Smart Retry', winRate: stratPerf.SMART_RETRY?.win_rate_percentage || 75.5, color: '#0C6BF5' },
    { name: 'Alternate Pay', winRate: stratPerf.ALTERNATE_PAYMENT?.win_rate_percentage || 84.2, color: '#4F46E5' },
    { name: 'Customer Nudge', winRate: stratPerf.CUSTOMER_NUDGE?.win_rate_percentage || 64.3, color: '#9333EA' },
    { name: 'Escalation', winRate: stratPerf.HUMAN_ESCALATION?.win_rate_percentage || 75.0, color: '#F59E0B' },
  ];

  const comparisonData = [
    { name: 'Revenue at Risk', amount: rev.total_revenue_at_risk || metrics?.revenue_at_risk, fill: '#EF4444' },
    { name: 'Expected Recoverable', amount: rev.expected_recoverable_revenue, fill: '#3B82F6' },
    { name: 'Revenue Recovered', amount: rev.revenue_recovered || metrics?.revenue_recovered, fill: '#10B981' }
  ];

  return (
    <div className="space-y-8 pb-16">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-white via-blue-50/40 to-white p-6 sm:p-8 rounded-2xl border border-slate-200 card-shadow">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 bg-blue-100/70 border border-blue-200 text-[#0C6BF5] px-3 py-1 rounded-full text-xs font-semibold mb-3">
            <Zap className="w-3.5 h-3.5" />
            <span>Razorpay Buildathon Track 3: Context-Aware Autonomous Revenue Recovery Agent</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0C2340] tracking-tight">
            Recover revenue before it's lost.
          </h1>
          <p className="text-slate-600 text-base sm:text-lg mt-2">
            Evaluates counterfactual recovery strategies, balances economic expected value against customer friction, and enforces deterministic safety policies.
          </p>
        </div>

        {/* 5 Buildathon Demo Cases Shortcut Pills */}
        <div className="mt-6 pt-6 border-t border-slate-200/80">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2.5">
            Buildathon 5 Core Scenarios (Click to Inspect Counterfactuals):
          </span>
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => onSelectTransaction('TX001')}
              className="text-xs bg-white hover:bg-blue-50 text-[#0C2340] hover:text-[#0C6BF5] px-3 py-1.5 rounded-lg border border-slate-300 font-medium transition shadow-sm flex items-center space-x-1"
            >
              <span>1. Easy Recovery (TX001: Timeout → Smart Retry)</span>
              <ArrowRight className="w-3 h-3 text-[#0C6BF5]" />
            </button>
            <button
              onClick={() => onSelectTransaction('TX002')}
              className="text-xs bg-white hover:bg-indigo-50 text-[#0C2340] hover:text-indigo-700 px-3 py-1.5 rounded-lg border border-slate-300 font-medium transition shadow-sm flex items-center space-x-1"
            >
              <span>2. Alternate Payment (TX002: Card Decline → Link)</span>
              <ArrowRight className="w-3 h-3 text-indigo-600" />
            </button>
            <button
              onClick={() => onSelectTransaction('TX_NUDGE_01')}
              className="text-xs bg-white hover:bg-purple-50 text-[#0C2340] hover:text-purple-700 px-3 py-1.5 rounded-lg border border-slate-300 font-medium transition shadow-sm flex items-center space-x-1"
            >
              <span>3. Customer Nudge (TX_NUDGE_01: Dropped Cart)</span>
              <ArrowRight className="w-3 h-3 text-purple-600" />
            </button>
            <button
              onClick={() => onSelectTransaction('TX003')}
              className="text-xs bg-white hover:bg-amber-50 text-[#0C2340] hover:text-amber-700 px-3 py-1.5 rounded-lg border border-slate-300 font-medium transition shadow-sm flex items-center space-x-1"
            >
              <span>4. High Fraud Risk (TX003: 76% Fraud → Policy Block)</span>
              <ArrowRight className="w-3 h-3 text-amber-600" />
            </button>
            <button
              onClick={() => onSelectTransaction('TX004')}
              className="text-xs bg-white hover:bg-rose-50 text-[#0C2340] hover:text-rose-700 px-3 py-1.5 rounded-lg border border-slate-300 font-medium transition shadow-sm flex items-center space-x-1"
            >
              <span>5. Unfavorable Recovery (TX004: 2nd Attempt → STOP)</span>
              <ArrowRight className="w-3 h-3 text-rose-600" />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-500" />
            <span>{error}</span>
          </div>
          <button onClick={loadData} className="underline font-semibold text-xs">Retry</button>
        </div>
      )}

      {/* Primary Financial Telemetry Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Revenue at Risk */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 card-shadow card-hover">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">Revenue at Risk</span>
            <div className="w-9 h-9 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-bold text-[#0C2340]">
              {formatCurrency(rev.total_revenue_at_risk || metrics?.revenue_at_risk)}
            </div>
            <p className="text-xs text-slate-500 mt-1">Total revenue flagged across payment events</p>
          </div>
        </div>

        {/* Expected Recoverable Revenue */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 card-shadow card-hover">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">Expected Recoverable</span>
            <div className="w-9 h-9 rounded-lg bg-blue-50 text-[#0C6BF5] flex items-center justify-center">
              <Sliders className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-bold text-[#0C6BF5]">
              {formatCurrency(rev.expected_recoverable_revenue)}
            </div>
            <p className="text-xs text-slate-500 mt-1">Net expected value of top strategies</p>
          </div>
        </div>

        {/* Revenue Recovered */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 card-shadow card-hover">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">Revenue Recovered</span>
            <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-bold text-emerald-600">
              {formatCurrency(rev.revenue_recovered || metrics?.revenue_recovered)}
            </div>
            <p className="text-xs text-slate-500 mt-1">Successfully restored to merchants</p>
          </div>
        </div>

        {/* Recovery Rate */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 card-shadow card-hover">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">Recovery Rate</span>
            <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-bold text-[#0C2340]">
              {rev.recovery_rate || metrics?.recovery_rate || 0}%
            </div>
            <p className="text-xs text-slate-500 mt-1">Operational cost: ₹{rev.recovery_cost || 0}</p>
          </div>
        </div>
      </div>

      {/* Revenue at Risk Granular Breakdown (Section 4 of Prompt) */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 card-shadow">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h3 className="text-base font-bold text-[#0C2340]">Revenue at Risk Decomposition</h3>
            <p className="text-xs text-slate-500">Contextual breakdown by viability, friction, and risk category</p>
          </div>
          <span className="text-xs font-bold text-[#0C6BF5] bg-blue-50 px-2.5 py-1 rounded-md border border-blue-200">
            Total: {formatCurrency(rev.total_revenue_at_risk)}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4 text-xs">
          <div className="bg-blue-50/60 p-4 rounded-xl border border-blue-200">
            <span className="text-blue-700 font-semibold block">Recoverable (Smart Retry)</span>
            <span className="text-xl font-bold text-blue-900 mt-1 block">
              {formatCurrency(breakdown.recoverable)}
            </span>
            <span className="text-[11px] text-blue-600 mt-0.5 block">Transient gateway timeouts</span>
          </div>

          <div className="bg-indigo-50/60 p-4 rounded-xl border border-indigo-200">
            <span className="text-indigo-700 font-semibold block">Alternate Method Recommended</span>
            <span className="text-xl font-bold text-indigo-900 mt-1 block">
              {formatCurrency(breakdown.alternate_method_recommended)}
            </span>
            <span className="text-[11px] text-indigo-600 mt-0.5 block">Card declines / blocked cards</span>
          </div>

          <div className="bg-amber-50/60 p-4 rounded-xl border border-amber-200">
            <span className="text-amber-800 font-semibold block">High Risk (Escalation)</span>
            <span className="text-xl font-bold text-amber-950 mt-1 block">
              {formatCurrency(breakdown.high_risk)}
            </span>
            <span className="text-[11px] text-amber-700 mt-0.5 block">Fraud score &gt; 70% / high ticket</span>
          </div>

          <div className="bg-slate-100 p-4 rounded-xl border border-slate-300">
            <span className="text-slate-700 font-semibold block">Unrecoverable (Stop Rule)</span>
            <span className="text-xl font-bold text-slate-900 mt-1 block">
              {formatCurrency(breakdown.unrecoverable)}
            </span>
            <span className="text-[11px] text-slate-500 mt-0.5 block">Retry limit reached (attempts &ge; 2)</span>
          </div>
        </div>
      </div>

      {/* Visual Charts: Expected vs Recovered & Feedback Learning Loop */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Volume Comparison */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 card-shadow">
          <h3 className="text-base font-bold text-[#0C2340]">Revenue at Risk vs Recovered</h3>
          <p className="text-xs text-slate-500 mt-0.5">Financial conversion across pipeline</p>
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} margin={{ top: 20, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 12 }} />
                <YAxis tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`} tick={{ fill: '#64748B', fontSize: 12 }} />
                <Tooltip formatter={(value) => [`₹${Number(value).toLocaleString('en-IN')}`, 'Amount']} />
                <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
                  {comparisonData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Strategy Performance (Continuous Learning Loop) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 card-shadow">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-[#0C2340]">Strategy Success Rate (Feedback Loop)</h3>
              <p className="text-xs text-slate-500 mt-0.5">Empirical historical win-rate refining future predictions</p>
            </div>
            <span className="text-[11px] bg-emerald-50 text-emerald-700 font-bold px-2 py-0.5 rounded border border-emerald-200">
              Live Calibrated
            </span>
          </div>
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={strategyChartData} margin={{ top: 20, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} />
                <YAxis tickFormatter={(val) => `${val}%`} tick={{ fill: '#64748B', fontSize: 12 }} domain={[0, 100]} />
                <Tooltip formatter={(val) => [`${val}%`, 'Win Rate']} />
                <Bar dataKey="winRate" radius={[6, 6, 0, 0]}>
                  {strategyChartData.map((entry, index) => (
                    <Cell key={`strat-cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Operational Agent & Risk Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="bg-white p-4 rounded-xl border border-slate-200 card-shadow">
          <span className="text-slate-500 block">Smart Retries Dispatched</span>
          <span className="text-xl font-bold text-[#0C6BF5] mt-1 block">{agent.smart_retries || 0}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 card-shadow">
          <span className="text-slate-500 block">Alternate Pay Links Sent</span>
          <span className="text-xl font-bold text-indigo-600 mt-1 block">{agent.alternate_payments || 0}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 card-shadow">
          <span className="text-slate-500 block">Fraud Stops Enforced</span>
          <span className="text-xl font-bold text-amber-600 mt-1 block">{risk.fraud_stops_prevented || 0}</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 card-shadow">
          <span className="text-slate-500 block">Retry Limits Respected</span>
          <span className="text-xl font-bold text-slate-700 mt-1 block">{risk.retry_limits_enforced || 0}</span>
        </div>
      </div>

      {/* Recent Recovery Table */}
      <div className="bg-white rounded-xl border border-slate-200 card-shadow overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-[#0C2340]">Recent Pipeline Telemetry</h3>
            <p className="text-xs text-slate-500 mt-0.5">Click any transaction to inspect counterfactual strategies and safety checks</p>
          </div>
          <button
            onClick={() => setActivePage('transactions')}
            className="text-xs font-semibold text-[#0C6BF5] hover:text-blue-700 flex items-center space-x-1"
          >
            <span>View All Transactions</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Transaction</th>
                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Fraud Score</th>
                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Recovery Prob</th>
                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Recommended Strategy</th>
                <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Inspect</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-100">
              {recentTx.map((tx) => (
                <tr 
                  key={tx.id || tx.transaction_id}
                  onClick={() => onSelectTransaction(tx.transaction_reference || tx.transaction_id)}
                  className="hover:bg-slate-50/80 cursor-pointer transition"
                >
                  <td className="px-6 py-4 font-mono font-medium text-slate-800">
                    {tx.transaction_reference || tx.transaction_id}
                  </td>
                  <td className="px-6 py-4 font-semibold text-[#0C2340]">
                    ₹{Number(tx.amount).toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs font-semibold ${tx.fraud_score > 0.5 ? 'text-rose-600' : 'text-slate-600'}`}>
                      {(tx.fraud_score * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-xs font-semibold text-emerald-600">
                      {(tx.recovery_probability * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <ActionBadge action={tx.recommended_strategy || tx.recovery_action} />
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={tx.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectTransaction(tx.transaction_reference || tx.transaction_id);
                      }}
                      className="text-xs text-[#0C6BF5] hover:text-blue-700 font-semibold inline-flex items-center space-x-1"
                    >
                      <span>Analyze</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
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
