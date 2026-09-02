/**
 * RecoverAI API Client Service (Buildathon Track 3)
 * Communicates with the FastAPI backend under /api/*
 */
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchDashboardMetrics() {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/metrics`);
  if (!res.ok) throw new Error('Failed to load dashboard metrics');
  return res.json();
}

export async function fetchTransactions(params = {}) {
  const query = new URLSearchParams();
  if (params.status && params.status !== 'ALL') query.append('status', params.status);
  if (params.payment_method) query.append('payment_method', params.payment_method);
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);

  const res = await fetch(`${API_BASE_URL}/api/transactions?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to load transactions');
  return res.json();
}

export async function fetchTransactionDetail(transactionId) {
  const res = await fetch(`${API_BASE_URL}/api/transactions/${transactionId}`);
  if (!res.ok) throw new Error(`Failed to load transaction ${transactionId}`);
  return res.json();
}

export async function executeRecovery(transactionId) {
  const res = await fetch(`${API_BASE_URL}/api/recovery/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transaction_id: transactionId })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Recovery execution failed');
  }
  return res.json();
}

export async function fetchTransactionAudit(transactionId) {
  const res = await fetch(`${API_BASE_URL}/transactions/${transactionId}/audit`);
  if (!res.ok) throw new Error('Failed to fetch transaction audit trail');
  return res.json();
}

export async function fetchGlobalAudit(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);
  if (params.transaction_id) query.append('transaction_id', params.transaction_id);

  const res = await fetch(`${API_BASE_URL}/api/audit?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch global audit logs');
  return res.json();
}

export async function fetchRagEvaluation() {
  const res = await fetch(`${API_BASE_URL}/rag/evaluation`);
  if (!res.ok) throw new Error('Failed to fetch RAG evaluation');
  return res.json();
}
