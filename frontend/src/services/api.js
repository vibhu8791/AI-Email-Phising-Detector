import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export const syncEmails = async (maxCount = 10) => {
  const res = await api.post(`/emails/sync?max_count=${maxCount}`);
  return res.data;
};

export const simulateBatch = async () => {
  const res = await api.post('/emails/simulate-batch');
  return res.data;
};

export const analyzeCustomEmail = async (payload) => {
  const res = await api.post('/emails/analyze-custom', payload);
  return res.data;
};

export const getGoogleAuthUrl = async () => {
  const res = await api.get('/auth/google/url');
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

export const connectDemoMailbox = async () => {
  const res = await api.post('/auth/demo-connect');
  return res.data;
};

export const resetDashboard = async () => {
  const res = await api.post('/dashboard/reset');
  return res.data;
};

export default api;
