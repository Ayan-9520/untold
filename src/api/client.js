import axios from 'axios';
import { getApiBase } from '../config/runtime';

const API_BASE = getApiBase();
const TOKEN_KEY = 'untold-token';
const REFRESH_KEY = 'untold-refresh';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

let refreshPromise = null;

async function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) throw new Error('No refresh token');
  const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refresh });
  localStorage.setItem(TOKEN_KEY, data.access_token);
  if (data.refresh_token) localStorage.setItem(REFRESH_KEY, data.refresh_token);
  return data.access_token;
}

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem('untold-admin-token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        if (!refreshPromise) refreshPromise = refreshAccessToken().finally(() => { refreshPromise = null; });
        const token = await refreshPromise;
        original.headers.Authorization = `Bearer ${token}`;
        return client(original);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
      }
    }
    return Promise.reject(error);
  }
);

export default client;

export const api = {
  auth: {
    register: (data) => client.post('/register', data).then((r) => r.data),
    login: (data) => client.post('/login', data).then((r) => r.data),
    refresh: (refresh_token) => client.post('/auth/refresh', { refresh_token }).then((r) => r.data),
    google: (id_token) => client.post('/auth/google', { id_token }).then((r) => r.data),
    me: () => client.get('/auth/me').then((r) => r.data),
    forgotPassword: (email) => client.post('/auth/forgot-password', { email }).then((r) => r.data),
    resetPassword: (data) => client.post('/auth/reset-password', data).then((r) => r.data),
  },
  videos: {
    list: (params) => client.get('/videos', { params }).then((r) => r.data),
    get: (id) => client.get(`/videos/${id}`).then((r) => r.data),
    search: (q) => client.get('/videos', { params: { search: q, page_size: 20 } }).then((r) => r.data),
  },
  categories: {
    list: () => client.get('/categories').then((r) => r.data),
  },
  watchlist: {
    list: () => client.get('/watchlist').then((r) => r.data),
    add: (video_id) => client.post('/watchlist', { video_id }).then((r) => r.data),
    remove: (video_id) => client.delete(`/watchlist/${video_id}`).then((r) => r.data),
    toggle: (video_id) => client.post(`/watchlist/toggle/${video_id}`).then((r) => r.data),
  },
  subscriptions: {
    me: () => client.get('/membership/me').then((r) => r.data),
  },
  contact: {
    submit: (data) => client.post('/contact', data).then((r) => r.data),
  },
  analytics: {
    track: (data) => client.post('/analytics/events', data).catch(() => {}),
  },
};

export { API_BASE, TOKEN_KEY, REFRESH_KEY };
