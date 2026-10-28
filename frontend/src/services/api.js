import axios from 'axios';

// Base API URL configured from environment, falling back safely to local dev
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// =========================================================================
// TOKEN & SESSION MANAGEMENT
// =========================================================================

export const getStoredToken = () => {
  return localStorage.getItem('phish_auth_token') || '';
};

export const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem('phish_auth_token', token);
  } else {
    localStorage.removeItem('phish_auth_token');
  }
};

export const getCurrentUserId = () => {
  return localStorage.getItem('phish_user_id') || 'analyst_active';
};

export const setCurrentUserId = (userId) => {
  localStorage.setItem('phish_user_id', userId);
};

// Initialize or resume authenticated session with server
export const initSession = async () => {
  const existingToken = getStoredToken();
  if (existingToken) {
    try {
      const res = await api.get('/auth/me');
      if (res.data?.user_id) {
        setCurrentUserId(res.data.user_id);
        return res.data;
      }
    } catch (e) {
      console.warn('Existing session invalid or expired, establishing new session...');
      setStoredToken('');
    }
  }

  // Obtain freshly signed JWT session from backend
  try {
    const res = await api.post('/auth/session', {
      user_id: localStorage.getItem('phish_user_id') || undefined
    });
    if (res.data?.token) {
      setStoredToken(res.data.token);
      if (res.data.user?.user_id) {
        setCurrentUserId(res.data.user.user_id);
      }
    }
    return res.data;
  } catch (err) {
    console.error('Failed to initialize authenticated session:', err);
    throw err;
  }
};

// Attach cryptographically verified JWT Bearer token to every request
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Intercept 401s to automatically refresh expired sessions
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/auth/session')) {
      originalRequest._retry = true;
      try {
        setStoredToken('');
        const session = await initSession();
        if (session?.token) {
          originalRequest.headers['Authorization'] = `Bearer ${session.token}`;
          return api(originalRequest);
        }
      } catch (refreshErr) {
        console.error('Session recovery failed:', refreshErr);
      }
    }
    return Promise.reject(error);
  }
);

// Helper to construct Google OAuth authorization URL without hardcoded localhost
export const getGoogleLoginUrl = (prompt = 'select_account') => {
  const token = getStoredToken();
  const tokenQuery = token ? `&token=${encodeURIComponent(token)}` : '';
  return `${API_BASE_URL}/auth/google/login?prompt=${prompt}${tokenQuery}`;
};

// =========================================================================
// API ENDPOINTS
// =========================================================================

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
  if (res.data?.token) {
    setStoredToken(res.data.token);
  }
  setCurrentUserId(userId);
  return res.data;
};

export const resetDashboard = async () => {
  const res = await api.post('/dashboard/reset');
  return res.data;
};

export default api;
