import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  ShieldAlert, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Zap, 
  FileText, 
  RefreshCw, 
  AlertOctagon,
  AlertTriangle,
  Sliders,
  DollarSign,
  UserCheck,
  CreditCard,
  Scale
} from 'lucide-react';
import { fetchTransactionDetail, executeRecovery } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import ActionBadge from '../components/ActionBadge';

export default function TransactionDetails({ transactionId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [executionBanner, setExecutionBanner] = useState(null);
  const [error, setError] = useState(null);

  const loadDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchTransactionDetail(transactionId);
      setData(res);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to load transaction details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (transactionId) {
      loadDetail();
    }
  }, [transactionId]);

  const handleExecuteRecovery = async () => {
    setExecuting(true);
    setExecutionBanner(null);
    try {
      const res = await executeRecovery(transactionId);
      
      let bannerType = 'success';
      let bannerMsg = 'Payment recovered successfully';
      
      if (res.execution_result === 'ESCALATED') {
        bannerType = 'warning';
        bannerMsg = 'Transaction escalated for manual review';
      } else if (res.execution_result === 'STOPPED') {
        bannerType = 'neutral';
        bannerMsg = 'Recovery stopped per deterministic safety policy';
      } else if (res.execution_result === 'FAILED') {
        bannerType = 'danger';
        bannerMsg = 'Recovery attempt failed on payment gateway';
      }

      setExecutionBanner({
        type: bannerType,
        message: bannerMsg,
        reason: res.outcome_reason,
        recoveredAmount: res.transaction?.amount_recovered || res.transaction?.recovered_amount
      });

      await loadDetail();
    } catch (err) {
      console.error(err);
      setExecutionBanner({
        type: 'danger',
        message: 'Execution Error',
        reason: err.message || 'Failed to process recovery action'
      });
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <RefreshCw className="w-8 h-8 text-[#0C6BF5] animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-white rounded-xl border border-slate-200 card-shadow text-center space-y-4 max-w-xl mx-auto">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-[#0C2340]">Error Loading Transaction</h2>
        <p className="text-sm text-slate-500">{error || 'Transaction not found.'}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-[#0C6BF5] text-white text-xs font-semibold rounded-lg shadow-sm"
        >
          Back to Transactions
        </button>
      </div>
    );
  }

  const { transaction, preview_analysis, counterfactual_strategies, ai_decision, policy_decision, audit_logs } = data;
  const analysis = preview_analysis || {};
  const aiDec = ai_decision || analysis.ai_decision || {};
  const polDec = policy_decision || analysis.policy_decision || {};
  const strategies = counterfactual_strategies || analysis.counterfactual_strategies || [];
  const custHist = transaction.customer_history || {};

  // Compute Guardrail Safety States
  const duplicateDebitPass = transaction.status !== 'RECOVERED' && transaction.status !== 'SUCCESS';
  const fraudCheckPass = transaction.fraud_score <= 0.70;
  const retryLimitCheckPass = transaction.attempt_number < 2;
  const highValueCheckPass = transaction.amount <= 50000.0;
  const viabilityCheckPass = transaction.recovery_probability >= 0.30;

  return (
    <div className="space-y-6 pb-20 max-w-6xl mx-auto">
      {/* Back button & ID */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-[#0C6BF5] transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Transactions</span>
        </button>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Reference:</span>
          <span className="font-mono font-bold text-slate-800">{transaction.transaction_reference || transaction.transaction_id}</span>
        </div>
      </div>

      {/* Execution Feedback Alert Banner */}
      {executionBanner && (
        <div className={`p-4 rounded-xl border flex items-start space-x-3 transition-all ${
          executionBanner.type === 'success' 
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900' :
          executionBanner.type === 'warning'
            ? 'bg-amber-50 border-amber-300 text-amber-900' :
          executionBanner.type === 'danger'
            ? 'bg-rose-50 border-rose-300 text-rose-900' :
            'bg-slate-100 border-slate-300 text-slate-800'
        }`}>
          {executionBanner.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5" /> :
           executionBanner.type === 'warning' ? <AlertOctagon className="w-5 h-5 text-amber-600 mt-0.5" /> :
           executionBanner.type === 'danger' ? <XCircle className="w-5 h-5 text-rose-600 mt-0.5" /> :
           <ShieldAlert className="w-5 h-5 text-slate-600 mt-0.5" />}
          <div>
            <h4 className="text-sm font-bold">{executionBanner.message}</h4>
            <p className="text-xs mt-0.5 opacity-90">{executionBanner.reason}</p>
            {executionBanner.recoveredAmount > 0 && (
              <p className="text-xs font-bold text-emerald-700 mt-1">
                Recovered Revenue: ₹{Number(executionBanner.recoveredAmount).toLocaleString('en-IN')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Transaction & Customer Header Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 card-shadow">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-2xl font-black text-[#0C2340] font-mono">
                {transaction.transaction_reference || transaction.transaction_id}
              </h2>
              <StatusBadge status={transaction.status} />
            </div>
            <p className="text-xs text-slate-500 mt-1 flex items-center space-x-2">
              <span>Customer: <strong className="font-mono text-slate-700">{transaction.customer_reference || transaction.customer_id}</strong></span>
              <span>•</span>
              <span>Tier: <strong className="text-slate-700">{transaction.customer_value}</strong></span>
              <span>•</span>
              <span>History: <strong>{custHist.successful_transactions || 0} Successful</strong>, {custHist.failed_transactions || 0} Failed</span>
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <span className="text-xs text-slate-500 block">Transaction Value</span>
              <span className="text-2xl font-extrabold text-[#0C2340]">
                ₹{Number(transaction.amount).toLocaleString('en-IN')}
              </span>
            </div>

            <button
              onClick={handleExecuteRecovery}
              disabled={executing || transaction.status === 'RECOVERED'}
              className={`px-5 py-2.5 rounded-xl text-xs font-bold tracking-wide shadow-md transition flex items-center space-x-2 ${
                transaction.status === 'RECOVERED'
                  ? 'bg-emerald-100 text-emerald-700 cursor-not-allowed border border-emerald-200'
                  : executing
                  ? 'bg-blue-400 text-white cursor-wait'
                  : 'bg-[#0C6BF5] hover:bg-blue-700 text-white shadow-blue-500/25 active:scale-95'
              }`}
            >
              <Zap className={`w-4 h-4 ${executing ? 'animate-spin' : ''}`} />
              <span>
                {transaction.status === 'RECOVERED' ? 'Revenue Recovered' : executing ? 'Executing...' : 'Execute Recovery'}
              </span>
            </button>
          </div>
        </div>

        {/* Signals Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 pt-6 text-xs">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Payment Method</span>
            <span className="text-sm font-bold text-slate-800 uppercase mt-0.5 block">{transaction.payment_method}</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Failure Reason</span>
            <span className="text-sm font-bold text-slate-800 font-mono mt-0.5 block">{transaction.failure_reason}</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Failure Category</span>
            <span className="text-xs font-bold text-[#0C6BF5] mt-1 block">{transaction.failure_category}</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Attempt Count</span>
            <span className="text-sm font-bold text-slate-800 mt-0.5 block">{transaction.attempt_number} of 2</span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Fraud Risk</span>
            <span className={`text-sm font-bold mt-0.5 block ${transaction.fraud_score > 0.50 ? 'text-rose-600' : 'text-slate-800'}`}>
              {(transaction.fraud_score * 100).toFixed(1)}%
            </span>
          </div>

          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <span className="text-slate-500 block">Recovered Amount</span>
            <span className="text-sm font-bold text-emerald-600 mt-0.5 block">
              ₹{Number(transaction.amount_recovered || transaction.recovered_amount || 0).toLocaleString('en-IN')}
            </span>
          </div>
        </div>
      </div>

      {/* COUNTERFACTUAL STRATEGY MATRIX (KEY DIFFERENTIATOR) */}
      <div className="bg-white rounded-2xl border border-slate-200 card-shadow overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <Scale className="w-5 h-5 text-[#0C6BF5]" />
              <h3 className="text-base font-bold text-[#0C2340]">Counterfactual Recovery Strategy Evaluator</h3>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Simultaneously evaluates all 5 strategies to maximize safe expected recovered value while minimizing friction and cost
            </p>
          </div>
          <span className="text-xs font-mono font-bold bg-blue-50 text-[#0C6BF5] px-2.5 py-1 rounded border border-blue-200">
            Score = Expected Value − Cost − Risk − Friction
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Strategy</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Success Probability</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Expected Recovery</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Recovery Cost</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Risk Penalty</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Friction Penalty</th>
                <th className="px-6 py-3 font-semibold text-slate-500 uppercase">Recovery Score</th>
                <th className="px-6 py-3 text-right font-semibold text-slate-500 uppercase">Recommendation</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-100">
              {strategies.map((s, idx) => {
                const isSelected = s.is_recommended || s.strategy === polDec.enforced_action || s.strategy === aiDec.decision;
                return (
                  <tr key={idx} className={`${isSelected ? 'bg-blue-50/40 font-semibold' : 'hover:bg-slate-50'} transition`}>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <ActionBadge action={s.strategy} />
                      </div>
                      <span className="text-[11px] text-slate-500 font-normal block mt-1">{s.rationale}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-bold text-slate-800">
                        {(s.success_probability * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-900">
                      ₹{Number(s.expected_recovery).toLocaleString('en-IN')}
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      ₹{Number(s.recovery_cost).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-rose-600">
                      -₹{Number(s.risk_penalty).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-amber-600">
                      -₹{Number(s.friction_penalty).toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-sm font-extrabold ${s.recovery_score > 0 ? 'text-emerald-600' : 'text-slate-500'}`}>
                        ₹{Number(s.recovery_score).toLocaleString('en-IN')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {isSelected ? (
                        <span className="inline-flex items-center space-x-1 text-xs font-bold text-[#0C6BF5] bg-blue-100/80 px-2.5 py-1 rounded-full border border-blue-300">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Optimal Strategy</span>
                        </span>
                      ) : (
                        <span className="text-slate-400 text-[11px]">Suboptimal</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Decision & Deterministic Policy Check Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Decision Agent Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 card-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0C6BF5] flex items-center justify-center">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#0C2340]">AI Decision Agent</h3>
                  <p className="text-xs text-slate-500">Structured economic recovery recommendation</p>
                </div>
              </div>
              <ActionBadge action={aiDec.decision || transaction.recommended_strategy} />
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-slate-500 block">Recommended Decision:</span>
                  <span className="text-sm font-bold text-[#0C2340] mt-0.5 block">{aiDec.decision}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 block">Expected Recovery:</span>
                  <span className="text-sm font-bold text-emerald-600 mt-0.5 block">
                    ₹{Number(aiDec.expected_recovery || 0).toLocaleString('en-IN')}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block">Measurable Rationale:</span>
                <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200 mt-1 leading-relaxed">
                  {aiDec.reason}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2">
                <div>
                  <span className="text-slate-500 block">Next Action Directive:</span>
                  <span className="font-mono text-xs font-bold text-slate-800">
                    {aiDec.next_action}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 block">Agent Confidence:</span>
                  <span className="text-xs font-bold text-[#0C6BF5]">
                    {Math.round((aiDec.confidence || 0.85) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Deterministic Safety & Policy Engine Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 card-shadow flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-800 flex items-center justify-center">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#0C2340]">Deterministic Safety Engine</h3>
                  <p className="text-xs text-slate-500">Universal rules: Policy ALWAYS overrides AI</p>
                </div>
              </div>
              <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                polDec.policy_result === 'APPROVED' 
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}>
                {polDec.policy_result || 'APPROVED'}
              </span>
            </div>

            <div className="mt-4 space-y-2.5 text-xs">
              {/* Check 1: Duplicate Debit */}
              <div className="flex items-center justify-between p-2.5 rounded-lg border bg-slate-50/70 border-slate-200">
                <div className="flex items-center space-x-2">
                  {duplicateDebitPass ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
                  <span className="text-slate-700">Duplicate debit prevention (status != SUCCESS)</span>
                </div>
                <span className="font-mono font-bold text-slate-800">{duplicateDebitPass ? '✓ PASS' : '✕ BLOCKED'}</span>
              </div>

              {/* Check 2: Fraud Risk */}
              <div className="flex items-center justify-between p-2.5 rounded-lg border bg-slate-50/70 border-slate-200">
                <div className="flex items-center space-x-2">
                  {fraudCheckPass ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
                  <span className="text-slate-700">Fraud risk threshold (≤ 70%)</span>
                </div>
                <span className="font-mono font-bold text-slate-800">
                  {(transaction.fraud_score * 100).toFixed(1)}% {fraudCheckPass ? '✓' : '✕'}
                </span>
              </div>

              {/* Check 3: Retry Limit */}
              <div className="flex items-center justify-between p-2.5 rounded-lg border bg-slate-50/70 border-slate-200">
                <div className="flex items-center space-x-2">
                  {retryLimitCheckPass ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
                  <span className="text-slate-700">Excessive retry limit (&lt; 2 attempts)</span>
                </div>
                <span className="font-mono font-bold text-slate-800">
                  Attempt {transaction.attempt_number} {retryLimitCheckPass ? '✓' : '✕'}
                </span>
              </div>

              {/* Check 4: High Value Threshold */}
              <div className="flex items-center justify-between p-2.5 rounded-lg border bg-slate-50/70 border-slate-200">
                <div className="flex items-center space-x-2">
                  {highValueCheckPass ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
                  <span className="text-slate-700">High-value controls (≤ ₹50,000)</span>
                </div>
                <span className="font-mono font-bold text-slate-800">
                  ₹{Number(transaction.amount).toLocaleString('en-IN')} {highValueCheckPass ? '✓' : '✕'}
                </span>
              </div>

              {/* Check 5: Viability Threshold */}
              <div className="flex items-center justify-between p-2.5 rounded-lg border bg-slate-50/70 border-slate-200">
                <div className="flex items-center space-x-2">
                  {viabilityCheckPass ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <XCircle className="w-4 h-4 text-rose-600" />}
                  <span className="text-slate-700">Viability threshold (≥ 30%)</span>
                </div>
                <span className="font-mono font-bold text-slate-800">
                  {(transaction.recovery_probability * 100).toFixed(1)}% {viabilityCheckPass ? '✓' : '✕'}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600">
            <span className="font-bold text-slate-800">Enforced Action:</span>{' '}
            <strong className="text-[#0C6BF5] font-mono">{polDec.enforced_action || polDec.action || 'SMART_RETRY'}</strong>
            <span className="text-slate-400 ml-2">({polDec.rules_triggered || 'SAFETY_BOUNDS_SATISFIED'})</span>
          </div>
        </div>
      </div>

      {/* Chronological Audit Trail for this transaction */}
      <div className="bg-white rounded-2xl border border-slate-200 card-shadow overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-slate-600" />
            <div>
              <h3 className="text-base font-bold text-[#0C2340]">Immutable Audit Trail</h3>
              <p className="text-xs text-slate-500">Persistent ledger of risk evaluation, AI recommendations, policy decisions, and execution</p>
            </div>
          </div>
          <span className="text-xs font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full">
            {audit_logs?.length || 0} Events
          </span>
        </div>

        <div className="p-6">
          {(!audit_logs || audit_logs.length === 0) ? (
            <p className="text-xs text-slate-500">No audit events recorded yet.</p>
          ) : (
            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {audit_logs.map((log, idx) => (
                <div key={log.id || idx} className="relative">
                  <div className="absolute -left-6 top-1 w-3.5 h-3.5 rounded-full bg-white border-2 border-[#0C6BF5]" />
                  <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-[#0C2340]">{log.event || log.event_type}</span>
                        <ActionBadge action={log.action} />
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">
                        {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 mt-1.5">{log.reason}</p>
                    <div className="mt-2 flex items-center space-x-4 text-[11px] text-slate-500">
                      <span>Actor: <strong className="text-slate-700 font-mono">{log.actor || 'SYSTEM'}</strong></span>
                      <span>Decision: <strong className="text-slate-700">{log.decision}</strong></span>
                      {log.amount > 0 && (
                        <span>Amount: <strong className="text-[#0C2340]">₹{Number(log.amount).toLocaleString('en-IN')}</strong></span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
