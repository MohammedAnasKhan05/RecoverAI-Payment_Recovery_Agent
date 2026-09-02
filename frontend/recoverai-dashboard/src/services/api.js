/**
 * RecoverAI API Client Service (Buildathon Track 3)
 * Communicates with the FastAPI backend under /api/*
 */

function getApiBaseUrl() {
  let envUrl = (import.meta.env.VITE_API_URL || '').trim();

  // If no environment variable is provided, default to localhost for local dev
  if (!envUrl) {
    if (typeof window !== 'undefined') {
      const host = window.location.hostname;
      if (host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000';
      }
    }
    return '';
  }

  // Automatically prepend https:// if protocol was omitted (e.g. Render property: host)
  if (!envUrl.startsWith('http://') && !envUrl.startsWith('https://')) {
    envUrl = `https://${envUrl}`;
  }

  return envUrl.replace(/\/+$/, '');
}

const API_BASE_URL = getApiBaseUrl();

async function handleResponse(res, fallbackMessage) {
  const contentType = res.headers.get('content-type') || '';
  
  if (!res.ok) {
    let detail = '';
    if (contentType.includes('application/json')) {
      try {
        const errData = await res.json();
        detail = errData.detail || errData.message || '';
      } catch {}
    }
    throw new Error(detail || fallbackMessage || `Request failed with status ${res.status}`);
  }

  if (!contentType.includes('application/json')) {
    throw new Error(`Server returned HTML instead of JSON from ${res.url}. Please verify that VITE_API_URL points to your backend URL (e.g. https://recoverai-backend.onrender.com).`);
  }

  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return handleResponse(res, 'Health check failed');
}

export async function fetchDashboardMetrics() {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/metrics`);
  return handleResponse(res, 'Failed to load dashboard metrics');
}

export async function fetchTransactions(params = {}) {
  const query = new URLSearchParams();
  if (params.status && params.status !== 'ALL') query.append('status', params.status);
  if (params.payment_method) query.append('payment_method', params.payment_method);
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);

  const res = await fetch(`${API_BASE_URL}/api/transactions?${query.toString()}`);
  return handleResponse(res, 'Failed to load transactions');
}

export async function fetchTransactionDetail(transactionId) {
  const res = await fetch(`${API_BASE_URL}/api/transactions/${transactionId}`);
  return handleResponse(res, `Failed to load transaction ${transactionId}`);
}

export async function executeRecovery(transactionId) {
  const res = await fetch(`${API_BASE_URL}/api/recovery/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transaction_id: transactionId })
  });
  return handleResponse(res, 'Recovery execution failed');
}

export async function fetchTransactionAudit(transactionId) {
  const res = await fetch(`${API_BASE_URL}/transactions/${transactionId}/audit`);
  return handleResponse(res, 'Failed to fetch transaction audit trail');
}

export async function fetchGlobalAudit(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);
  if (params.transaction_id) query.append('transaction_id', params.transaction_id);

  const res = await fetch(`${API_BASE_URL}/api/audit?${query.toString()}`);
  return handleResponse(res, 'Failed to fetch global audit logs');
}

export async function fetchRagEvaluation() {
  const res = await fetch(`${API_BASE_URL}/rag/evaluation`);
  return handleResponse(res, 'Failed to fetch RAG evaluation');
}
