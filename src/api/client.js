import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('untold-token') || localStorage.getItem('untold-admin-token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default client;

export const api = {
  auth: {
    register: (data) => client.post('/register', data).then((r) => r.data),
    login: (data) => client.post('/login', data).then((r) => r.data),
    me: () => client.get('/auth/me').then((r) => r.data),
  },
  videos: {
    list: (params) => client.get('/videos', { params }).then((r) => r.data),
    get: (id) => client.get(`/video/${id}`).then((r) => r.data),
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
  analytics: {
    track: (data) => client.post('/analytics/events', data).catch(() => {}),
  },
};

export { API_BASE };
