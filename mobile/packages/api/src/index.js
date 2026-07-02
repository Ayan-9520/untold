import axios from 'axios';

const DEFAULT_BASE = '/api/v1';

let apiBase = DEFAULT_BASE;
let getToken = async () => null;
let onUnauthorized = () => {};

export function configureApi({ baseUrl, tokenProvider, unauthorizedHandler } = {}) {
  if (baseUrl) apiBase = baseUrl.replace(/\/$/, '');
  if (tokenProvider) getToken = tokenProvider;
  if (unauthorizedHandler) onUnauthorized = unauthorizedHandler;
}

const client = axios.create({
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use(async (config) => {
  config.baseURL = apiBase;
  const token = await getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) onUnauthorized();
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email, password) => client.post('/login', { email, password }).then((r) => r.data),
  studioMe: () => client.get('/auth/studio/me').then((r) => r.data),
  originalsMe: () => client.get('/auth/me').then((r) => r.data),
};

export const mobileApi = {
  registerDevice: (body) => client.post('/mobile/devices/register', body).then((r) => r.data),
  unregisterDevice: (id) => client.delete(`/mobile/devices/${id}`),
  offlineManifest: (appType) =>
    client.get('/mobile/offline-manifest', { params: { app_type: appType } }).then((r) => r.data),

  studioOverview: () => client.get('/mobile/studio/overview').then((r) => r.data),
  studioApprovals: (limit = 50) =>
    client.get('/mobile/studio/approvals', { params: { limit } }).then((r) => r.data),
  studioApprovalAction: (id, action, notes) =>
    client.post(`/mobile/studio/approvals/${id}/action`, { action, notes }).then((r) => r.data),
  studioAiJobs: () => client.get('/mobile/studio/ai-jobs').then((r) => r.data),
  studioAnalytics: () => client.get('/mobile/studio/analytics').then((r) => r.data),
  studioUpload: async (file, projectId) => {
    const form = new FormData();
    form.append('file', file);
    if (projectId != null) form.append('project_id', String(projectId));
    const { data } = await client.post('/mobile/studio/assets/upload', form, {
      headers: { 'Content-Type': undefined },
      transformRequest: (d) => d,
    });
    return data;
  },

  originalsHome: () => client.get('/mobile/originals/home').then((r) => r.data),
};

export const originalsApi = {
  video: (id) => client.get(`/video/${id}`).then((r) => r.data),
  watchlist: () => client.get('/watchlist').then((r) => r.data),
  toggleWatchlist: (videoId) => client.post(`/watchlist/toggle/${videoId}`).then((r) => r.data),
  trackEvent: (payload) => client.post('/analytics/events', payload).catch(() => {}),
};

export { client, apiBase as API_BASE };
