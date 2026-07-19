/* ============================================================
   CrimeLens AI — API Client
   Typed fetch wrapper with auth header injection and error handling.
   ============================================================ */

import Cookies from 'js-cookie';
import type { APIResponse } from './types';

let API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';
if (API_BASE.startsWith('http') && !API_BASE.endsWith('/api') && !API_BASE.includes('/api/')) {
  API_BASE = API_BASE.replace(/\/$/, '') + '/api';
}

/**
 * Get the stored JWT token from cookies.
 */
function getToken(): string | undefined {
  return Cookies.get('crimelens_token');
}

/**
 * Build request headers with auth token if available.
 */
function buildHeaders(extra?: Record<string, string>): HeadersInit {
  const headers: Record<string, string> = {
    ...extra,
  };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Make an API request and return typed JSON response.
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: buildHeaders(options.headers as Record<string, string>),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || `API Error: ${response.status}`);
  }

  return data;
}

/* ── Auth API ──────────────────────────────────────────────── */

export const authAPI = {
  register: (body: { email: string; password: string; full_name: string }) =>
    request('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  login: (body: { email: string; password: string }) =>
    request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  getProfile: () => request('/auth/me'),
  googleLogin: (token: string) =>
    request('/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    }),
  getConfig: () => request('/auth/config'),
};

/* ── Cases API ─────────────────────────────────────────────── */

export const casesAPI = {
  list: (page = 1, pageSize = 20, status?: string, priority?: string) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (status) params.set('status', status);
    if (priority) params.set('priority', priority);
    return request(`/cases?${params}`);
  },

  get: (id: string) => request(`/cases/${id}`),

  create: (body: { title: string; description: string; priority: string; tags: string[] }) =>
    request('/cases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  update: (id: string, body: Record<string, unknown>) =>
    request(`/cases/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  delete: (id: string) => request(`/cases/${id}`, { method: 'DELETE' }),

  getStats: () => request('/cases/stats'),
};

/* ── Evidence API ──────────────────────────────────────────── */

export const evidenceAPI = {
  upload: (caseId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`/evidence/cases/${caseId}/upload`, {
      method: 'POST',
      body: formData,
    });
  },

  uploadMultiple: (caseId: string, files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    return request(`/evidence/cases/${caseId}/upload-multiple`, {
      method: 'POST',
      body: formData,
    });
  },

  list: (caseId: string) => request(`/evidence/cases/${caseId}/list`),

  get: (id: string) => request(`/evidence/${id}`),

  getOCR: (id: string) => request(`/evidence/${id}/ocr`),

  getAnalysis: (id: string) => request(`/evidence/${id}/analysis`),

  analyzeCase: (caseId: string) =>
    request(`/evidence/cases/${caseId}/analyze`, { method: 'POST' }),

  getCaseAnalysis: (caseId: string) =>
    request(`/evidence/cases/${caseId}/analysis`),

  delete: (id: string) => request(`/evidence/${id}`, { method: 'DELETE' }),
};

/* ── Search API ────────────────────────────────────────────── */

export const searchAPI = {
  search: (caseId: string, query: string) =>
    request(`/search/cases/${caseId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    }),
};

/* ── Reports API ───────────────────────────────────────────── */

export const reportsAPI = {
  generate: (caseId: string) =>
    request(`/reports/cases/${caseId}/generate`, { method: 'POST' }),

  get: (caseId: string) => request(`/reports/cases/${caseId}`),
};

/* ── Analytics API ─────────────────────────────────────────── */

export const analyticsAPI = {
  getOverview: () => request('/analytics/overview'),
  getRiskDistribution: () => request('/analytics/risk-distribution'),
  getRecentActivity: () => request('/analytics/recent-activity'),
  getCrimeTypes: () => request('/analytics/crime-types'),
};

/* ── Admin API ─────────────────────────────────────────────── */

export const adminAPI = {
  listUsers: (page = 1) => request(`/admin/users?page=${page}`),
  updateUser: (id: string, body: Record<string, unknown>) =>
    request(`/admin/users/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),
  getLogs: (limit = 50) => request(`/admin/logs?limit=${limit}`),
  getStats: () => request('/admin/stats'),
};
