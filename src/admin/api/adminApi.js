import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const TOKEN_KEY = 'untold-admin-token';
const REFRESH_KEY = 'untold-admin-refresh';

const adminApi = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

adminApi.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_KEY);
      localStorage.removeItem('untold-admin-user');
      if (!window.location.pathname.includes('/studio/login')) {
        window.location.href = '/studio/login';
      }
    }
    return Promise.reject(error);
  }
);

export const auth = {
  async login(email, password) {
    const { data } = await adminApi.post('/login', { email, password });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_KEY, data.refresh_token);
    const profile = await auth.getMe();
    return profile;
  },

  async getMe() {
    const { data } = await adminApi.get('/auth/me');
    localStorage.setItem('untold-admin-user', JSON.stringify(data));
    return data;
  },

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem('untold-admin-user');
  },

  getStoredUser() {
    const raw = localStorage.getItem('untold-admin-user');
    return raw ? JSON.parse(raw) : null;
  },

  isAuthenticated() {
    return !!localStorage.getItem(TOKEN_KEY);
  },
};

export const dashboard = {
  getStats: () => adminApi.get('/admin/dashboard').then((r) => r.data),
  getAnalytics: () => adminApi.get('/analytics').then((r) => r.data),
  getRevenue: () => adminApi.get('/admin/revenue').then((r) => r.data),
};

export const users = {
  list: (params = {}) => adminApi.get('/admin/users', { params }).then((r) => r.data),
  deactivate: (id) => adminApi.post(`/admin/users/${id}/deactivate`).then((r) => r.data),
};

export const videos = {
  list: (params = {}) => adminApi.get('/videos', { params }).then((r) => r.data),
  get: (id) => adminApi.get(`/videos/${id}`).then((r) => r.data),
  create: (data) => adminApi.post('/admin/videos', data).then((r) => r.data),
  update: (id, data) => adminApi.patch(`/videos/${id}`, data).then((r) => r.data),
  delete: (id) => adminApi.delete(`/videos/${id}`),
};

export const categories = {
  list: () => adminApi.get('/categories').then((r) => r.data),
  create: (data) => adminApi.post('/admin/categories', data).then((r) => r.data),
};

export const notifications = {
  listEvents: (limit = 50) =>
    adminApi.get('/analytics/events', { params: { limit } }).then((r) => r.data),
};

export const aiPipeline = {
  listJobs: (params = {}) => adminApi.get('/admin/ai/jobs', { params }).then((r) => r.data),
  getJob: (id) => adminApi.get(`/admin/ai/jobs/${id}`).then((r) => r.data),
  createJob: (data) => adminApi.post('/admin/ai/jobs', data).then((r) => r.data),
  processJob: (id) => adminApi.post(`/admin/ai/jobs/${id}/process`).then((r) => r.data),
};

export const membership = {
  getStats: () => adminApi.get('/admin/membership/stats').then((r) => r.data),
  listSubscriptions: (params = {}) => adminApi.get('/admin/membership/subscriptions', { params }).then((r) => r.data),
  updateSubscription: (id, data) => adminApi.patch(`/admin/membership/subscriptions/${id}`, data).then((r) => r.data),
};

export const magazine = {
  listJobs: () => adminApi.get('/magazine/admin/jobs').then((r) => r.data),
  generateIssue: (data) => adminApi.post('/magazine/admin/generate', data).then((r) => r.data),
  advanceJob: (id) => adminApi.post(`/magazine/admin/jobs/${id}/advance`).then((r) => r.data),
  approveIssue: (id) => adminApi.post(`/magazine/admin/jobs/${id}/approve`).then((r) => r.data),
  listIssues: () => adminApi.get('/magazine/issues').then((r) => r.data),
};

export const studio = {
  listProductions: (params = {}) => adminApi.get('/admin/studio/productions', { params }).then((r) => r.data),
  getProduction: (id) => adminApi.get(`/admin/studio/productions/${id}`).then((r) => r.data),
  updateProduction: (id, data) => adminApi.patch(`/admin/studio/productions/${id}`, data).then((r) => r.data),
  getAgents: () => adminApi.get('/admin/studio/agents').then((r) => r.data),
  getAssets: () => adminApi.get('/admin/studio/assets').then((r) => r.data),
  getScriptsSummary: () => adminApi.get('/admin/studio/scripts/summary').then((r) => r.data),
};

export default adminApi;
