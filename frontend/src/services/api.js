import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach authenticated user ID to every request for strict multi-user isolation
api.interceptors.request.use((config) => {
  const currentUserId = localStorage.getItem('phish_user_id') || 'default_user';
  config.headers['X-User-ID'] = currentUserId;
  return config;
});

export const getCurrentUserId = () => {
  return localStorage.getItem('phish_user_id') || 'default_user';
};

export const setCurrentUserId = (userId) => {
  localStorage.setItem('phish_user_id', userId);
};

export const getDashboardStats = async () => {
  const res = await api.get('/dashboard/stats');
  return res.data;
};

export const getRecentThreats = async (limit = 10) => {
  const res = await api.get(`/dashboard/threats?limit=${limit}`);
  return res.data;
};

export const getEmails = async (params = {}) => {
  const res = await api.get('/emails', { params });
  return res.data;
};

export const getEmailById = async (id) => {
  const res = await api.get(`/emails/${id}`);
  return res.data;
};

export const deleteEmail = async (id) => {
  const res = await api.delete(`/emails/${id}`);
  return res.data;
};

export const syncEmails = async (maxCount = 10, accountId = null) => {
  const url = accountId 
    ? `/emails/sync?max_count=${maxCount}&account_id=${encodeURIComponent(accountId)}`
    : `/emails/sync?max_count=${maxCount}`;
  const res = await api.post(url);
  return res.data;
};

export const simulateBatch = async (accountId = null) => {
  const url = accountId
    ? `/emails/simulate-batch?account_id=${encodeURIComponent(accountId)}`
    : '/emails/simulate-batch';
  const res = await api.post(url);
  return res.data;
};

export const analyzeCustomEmail = async (payload) => {
  const res = await api.post('/emails/analyze-custom', payload);
  return res.data;
};

export const getAccounts = async () => {
  const res = await api.get('/auth/accounts');
  return res.data;
};

export const selectAccount = async (accountId) => {
  const res = await api.post(`/auth/accounts/${accountId}/select`);
  return res.data;
};

export const disconnectAccount = async (accountId) => {
  const res = await api.post(`/auth/accounts/${accountId}/disconnect`);
  return res.data;
};

export const getAuthStatus = async () => {
  const res = await api.get('/auth/status');
  return res.data;
};

export const disconnectGmail = async () => {
  const res = await api.post('/auth/disconnect');
  return res.data;
};

export const connectDemoMailbox = async (email = null, displayName = null) => {
  const res = await api.post('/auth/accounts/demo-connect', {
    email: email || undefined,
    display_name: displayName || undefined
  });
  return res.data;
};

export const switchUser = async (userId) => {
  const res = await api.post('/auth/switch-user', { user_id: userId });
  setCurrentUserId(userId);
  return res.data;
};

export const resetDashboard = async () => {
  const res = await api.post('/dashboard/reset');
  return res.data;
};

export default api;

