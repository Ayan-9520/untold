import axios from 'axios';
import { apiUrl, getApiBase } from '../../config/runtime';

const API_BASE = getApiBase();
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
  const orgId = localStorage.getItem('untold-org-id');
  if (orgId) config.headers['X-Organization-ID'] = orgId;
  const workspaceId = localStorage.getItem('untold-workspace-id');
  if (workspaceId) config.headers['X-Workspace-ID'] = workspaceId;
  return config;
});

let refreshPromise = null;

async function refreshAdminToken() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) throw new Error('No refresh token');
  const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refresh });
  localStorage.setItem(TOKEN_KEY, data.access_token);
  if (data.refresh_token) localStorage.setItem(REFRESH_KEY, data.refresh_token);
  return data.access_token;
}

adminApi.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      try {
        if (!refreshPromise) refreshPromise = refreshAdminToken().finally(() => { refreshPromise = null; });
        const token = await refreshPromise;
        original.headers.Authorization = `Bearer ${token}`;
        return adminApi(original);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem('untold-admin-user');
        localStorage.removeItem('untold-org-id');
        localStorage.removeItem('untold-workspace-id');
        if (!window.location.pathname.includes('/studio/login')) {
          window.location.href = '/studio/login';
        }
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
    const { data } = await adminApi.get('/auth/studio/me');
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
  listPlans: (params = {}) => adminApi.get('/plans', { params }).then((r) => r.data),
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

export const studioPlatform = {
  getDashboard: () => adminApi.get('/studio/platform/dashboard').then((r) => r.data),
  listProjects: (params) => adminApi.get('/studio/platform/projects', { params }).then((r) => r.data),
  getProject: (id) => adminApi.get(`/studio/platform/projects/${id}`).then((r) => r.data),
  createProject: (data) => adminApi.post('/studio/platform/projects', data).then((r) => r.data),
  updateProject: (id, data) => adminApi.patch(`/studio/platform/projects/${id}`, data).then((r) => r.data),
  deleteProject: (id) => adminApi.delete(`/studio/platform/projects/${id}`),
  publishProject: (id) => adminApi.post(`/studio/platform/projects/${id}/publish`).then((r) => r.data),
  assignMember: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/members`, data).then((r) => r.data),
  updateMember: (projectId, userId, data) => adminApi.patch(`/studio/platform/projects/${projectId}/members/${userId}`, data).then((r) => r.data),
  removeMember: (projectId, userId) => adminApi.delete(`/studio/platform/projects/${projectId}/members/${userId}`).then((r) => r.data),
  listComments: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/comments`).then((r) => r.data),
  addComment: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/comments`, data).then((r) => r.data),
  deleteComment: (projectId, commentId) => adminApi.delete(`/studio/platform/projects/${projectId}/comments/${commentId}`),
  listAttachments: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/attachments`).then((r) => r.data),
  addAttachment: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/attachments`, data).then((r) => r.data),
  deleteAttachment: (projectId, attachmentId) => adminApi.delete(`/studio/platform/projects/${projectId}/attachments/${attachmentId}`),
  getTimeline: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/timeline`).then((r) => r.data),
  listProjectTasks: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/tasks`).then((r) => r.data),
  getCalendar: (from, to) => adminApi.get('/studio/platform/calendar', { params: { from, to } }).then((r) => r.data),
  createTask: (data) => adminApi.post('/studio/platform/tasks', data).then((r) => r.data),

  getResearchWorkspace: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/research/workspace`).then((r) => r.data),
  getResearch: (researchId) => adminApi.get(`/studio/platform/research/${researchId}`).then((r) => r.data),
  autosaveResearch: (researchId, data) => adminApi.patch(`/studio/platform/research/${researchId}/autosave`, data).then((r) => r.data),
  createNote: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/notes`, data).then((r) => r.data),
  updateNote: (researchId, noteId, data) => adminApi.patch(`/studio/platform/research/${researchId}/notes/${noteId}`, data).then((r) => r.data),
  deleteNote: (researchId, noteId) => adminApi.delete(`/studio/platform/research/${researchId}/notes/${noteId}`),
  addSource: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/sources`, data).then((r) => r.data),
  updateSource: (researchId, id, data) => adminApi.patch(`/studio/platform/research/${researchId}/sources/${id}`, data).then((r) => r.data),
  deleteSource: (researchId, id) => adminApi.delete(`/studio/platform/research/${researchId}/sources/${id}`),
  addBookmark: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/bookmarks`, data).then((r) => r.data),
  deleteBookmark: (researchId, id) => adminApi.delete(`/studio/platform/research/${researchId}/bookmarks/${id}`),
  addFactCheck: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/fact-checks`, data).then((r) => r.data),
  updateFactCheck: (researchId, id, data) => adminApi.patch(`/studio/platform/research/${researchId}/fact-checks/${id}`, data).then((r) => r.data),
  addResearchComment: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/comments`, data).then((r) => r.data),
  addTimelineEvent: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/timeline`, data).then((r) => r.data),
  deleteTimelineEvent: (researchId, id) => adminApi.delete(`/studio/platform/research/${researchId}/timeline/${id}`),
  saveResearchVersion: (researchId) => adminApi.post(`/studio/platform/research/${researchId}/versions`).then((r) => r.data),
  restoreResearchVersion: (researchId, versionId) => adminApi.post(`/studio/platform/research/${researchId}/versions/${versionId}/restore`).then((r) => r.data),
  runResearchAI: (researchId, data) => adminApi.post(`/studio/platform/research/${researchId}/ai`, data).then((r) => r.data),
  exportResearchMarkdown: (researchId) => adminApi.get(`/studio/platform/research/${researchId}/export/markdown`, { responseType: 'text' }).then((r) => r.data),
  exportResearchWord: (researchId) => adminApi.get(`/studio/platform/research/${researchId}/export/word`, { responseType: 'blob' }).then((r) => r.data),
  updateResearchTopic: (researchId, topic) => adminApi.patch(`/studio/platform/research/${researchId}/topic`, { topic }).then((r) => r.data),
  requestResearchApproval: (researchId) => adminApi.post(`/studio/platform/research/${researchId}/approval/request`).then((r) => r.data),
  approveResearch: (researchId) => adminApi.post(`/studio/platform/research/${researchId}/approval/approve`).then((r) => r.data),
  rejectResearch: (researchId, notes) => adminApi.post(`/studio/platform/research/${researchId}/approval/reject`, notes ? { notes } : {}).then((r) => r.data),
  getResearchAIHistory: (researchId) => adminApi.get(`/studio/platform/research/${researchId}/ai/history`).then((r) => r.data),
  getResearchProviders: () => adminApi.get('/studio/platform/research/providers').then((r) => r.data),
  filterResearchSources: (researchId, params) => adminApi.get(`/studio/platform/research/${researchId}/sources`, { params }).then((r) => r.data),

  getScriptWorkspace: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/scripts/workspace`).then((r) => r.data),
  getScript: (scriptId) => adminApi.get(`/studio/platform/scripts/${scriptId}`).then((r) => r.data),
  autosaveScript: (scriptId, data) => adminApi.patch(`/studio/platform/scripts/${scriptId}/autosave`, data).then((r) => r.data),
  scriptHeartbeat: (scriptId) => adminApi.post(`/studio/platform/scripts/${scriptId}/heartbeat`).then((r) => r.data),
  saveScriptVersion: (scriptId, data) => adminApi.post(`/studio/platform/scripts/${scriptId}/versions`, data).then((r) => r.data),
  restoreScriptVersion: (scriptId, versionId) => adminApi.post(`/studio/platform/scripts/${scriptId}/versions/${versionId}/restore`).then((r) => r.data),
  addScriptComment: (scriptId, data) => adminApi.post(`/studio/platform/scripts/${scriptId}/comments`, data).then((r) => r.data),
  requestScriptApproval: (scriptId, data) => adminApi.post(`/studio/platform/scripts/${scriptId}/approval/request`, data).then((r) => r.data),
  approveScript: (scriptId, data) => adminApi.post(`/studio/platform/scripts/${scriptId}/approval/approve`, data || {}).then((r) => r.data),
  rejectScript: (scriptId, data) => adminApi.post(`/studio/platform/scripts/${scriptId}/approval/reject`, data || {}).then((r) => r.data),
  runScriptAI: (scriptId, data) => adminApi.post(`/studio/platform/scripts/${scriptId}/ai`, data).then((r) => r.data),
  getScriptAIHistory: (scriptId) => adminApi.get(`/studio/platform/scripts/${scriptId}/ai/history`).then((r) => r.data),
  getScriptProviders: () => adminApi.get('/studio/platform/scripts/providers').then((r) => r.data),
  exportScriptMarkdown: (scriptId) => adminApi.get(`/studio/platform/scripts/${scriptId}/export/markdown`, { responseType: 'text' }).then((r) => r.data),
  exportScriptWord: (scriptId) => adminApi.get(`/studio/platform/scripts/${scriptId}/export/word`, { responseType: 'blob' }).then((r) => r.data),

  getStoryboard: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/storyboard`).then((r) => r.data),
  importStoryboardFromScript: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/import-script`, data).then((r) => r.data),
  createStoryboardScene: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/scenes`, data).then((r) => r.data),
  updateStoryboardScene: (projectId, sceneId, data) => adminApi.patch(`/studio/platform/projects/${projectId}/storyboard/scenes/${sceneId}`, data).then((r) => r.data),
  deleteStoryboardScene: (projectId, sceneId) => adminApi.delete(`/studio/platform/projects/${projectId}/storyboard/scenes/${sceneId}`),
  reorderStoryboardScenes: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/reorder`, data).then((r) => r.data),
  saveStoryboardRevision: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/revisions`, data).then((r) => r.data),
  restoreStoryboardRevision: (projectId, revisionId) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/revisions/${revisionId}/restore`).then((r) => r.data),
  generateStoryboardAI: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/ai/generate`, data).then((r) => r.data),
  getStoryboardAIHistory: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/storyboard/ai/history`).then((r) => r.data),
  getStoryboardProviders: () => adminApi.get('/studio/platform/storyboard/providers').then((r) => r.data),
  requestStoryboardApproval: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/approval/request`, data).then((r) => r.data),
  approveStoryboard: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/approval/approve`, data || {}).then((r) => r.data),
  rejectStoryboard: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/storyboard/approval/reject`, data || {}).then((r) => r.data),

  getAIStudioOverview: () => adminApi.get('/studio/platform/ai-studio/overview').then((r) => r.data),
  createAIGeneration: (data) => adminApi.post('/studio/platform/ai-studio/generate', data).then((r) => r.data),
  getAIQueue: () => adminApi.get('/studio/platform/ai-studio/queue').then((r) => r.data),
  getAIHistory: ({ module, limit = 50, offset = 0 } = {}) =>
    adminApi.get('/studio/platform/ai-studio/history', { params: { module, limit, offset } }).then((r) => r.data),
  getAITelemetry: ({ module, limit = 100, offset = 0 } = {}) =>
    adminApi.get('/studio/platform/ai-studio/telemetry', { params: { module, limit, offset } }).then((r) => r.data),
  getAIJob: (id) => adminApi.get(`/studio/platform/ai-studio/jobs/${id}`).then((r) => r.data),
  retryAIJob: (id) => adminApi.post(`/studio/platform/ai-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelAIJob: (id) => adminApi.post(`/studio/platform/ai-studio/jobs/${id}/cancel`).then((r) => r.data),
  getAIPrompts: (module) => adminApi.get('/studio/platform/ai-studio/prompts', { params: module ? { module } : {} }).then((r) => r.data),
  createAIPrompt: (data) => adminApi.post('/studio/platform/ai-studio/prompts', data).then((r) => r.data),
  updateAIPrompt: (id, data) => adminApi.patch(`/studio/platform/ai-studio/prompts/${id}`, data).then((r) => r.data),
  deleteAIPrompt: (id) => adminApi.delete(`/studio/platform/ai-studio/prompts/${id}`),

  getImageStudioOverview: () => adminApi.get('/studio/platform/image-studio/overview').then((r) => r.data),
  createImageGeneration: (data) => adminApi.post('/studio/platform/image-studio/generate', data).then((r) => r.data),
  getImageQueue: () => adminApi.get('/studio/platform/image-studio/queue').then((r) => r.data),
  getImageHistory: (params) => adminApi.get('/studio/platform/image-studio/history', { params }).then((r) => r.data),
  getImageFavorites: () => adminApi.get('/studio/platform/image-studio/favorites').then((r) => r.data),
  toggleImageFavorite: (id) => adminApi.post(`/studio/platform/image-studio/jobs/${id}/favorite`).then((r) => r.data),
  upscaleImage: (id) => adminApi.post(`/studio/platform/image-studio/jobs/${id}/upscale`).then((r) => r.data),
  varyImage: (id, data) => adminApi.post(`/studio/platform/image-studio/jobs/${id}/variation`, data || {}).then((r) => r.data),
  getImageVersions: (id) => adminApi.get(`/studio/platform/image-studio/jobs/${id}/versions`).then((r) => r.data),
  saveImageToAsset: (id) => adminApi.post(`/studio/platform/image-studio/jobs/${id}/save-asset`).then((r) => r.data),
  getImageDownloadUrl: (id) => apiUrl(`/studio/platform/image-studio/jobs/${id}/download`),
  getImageCollections: () => adminApi.get('/studio/platform/image-studio/collections').then((r) => r.data),
  createImageCollection: (data) => adminApi.post('/studio/platform/image-studio/collections', data).then((r) => r.data),
  addImageToCollection: (collectionId, generationId) => adminApi.post(`/studio/platform/image-studio/collections/${collectionId}/items/${generationId}`),
  getImagePrompts: (imageType) => adminApi.get('/studio/platform/image-studio/prompts', { params: imageType ? { image_type: imageType } : {} }).then((r) => r.data),
  retryImageJob: (id) => adminApi.post(`/studio/platform/image-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelImageJob: (id) => adminApi.post(`/studio/platform/image-studio/jobs/${id}/cancel`).then((r) => r.data),

  getVideoStudioOverview: () => adminApi.get('/studio/platform/video-studio/overview').then((r) => r.data),
  createVideoGeneration: (data) => adminApi.post('/studio/platform/video-studio/generate', data).then((r) => r.data),
  getVideoQueue: () => adminApi.get('/studio/platform/video-studio/queue').then((r) => r.data),
  getVideoHistory: (params) => adminApi.get('/studio/platform/video-studio/history', { params }).then((r) => r.data),
  getVideoVersions: (id) => adminApi.get(`/studio/platform/video-studio/jobs/${id}/versions`).then((r) => r.data),
  saveVideoToAsset: (id) => adminApi.post(`/studio/platform/video-studio/jobs/${id}/save-asset`).then((r) => r.data),
  getVideoDownloadUrl: (id) => apiUrl(`/studio/platform/video-studio/jobs/${id}/download`),
  getVideoPrompts: (videoType) => adminApi.get('/studio/platform/video-studio/prompts', { params: videoType ? { video_type: videoType } : {} }).then((r) => r.data),
  retryVideoJob: (id) => adminApi.post(`/studio/platform/video-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelVideoJob: (id) => adminApi.post(`/studio/platform/video-studio/jobs/${id}/cancel`).then((r) => r.data),

  getVoiceStudioOverview: () => adminApi.get('/studio/platform/voice-studio/overview').then((r) => r.data),
  createVoiceGeneration: (data) => adminApi.post('/studio/platform/voice-studio/generate', data).then((r) => r.data),
  previewVoice: (data) => adminApi.post('/studio/platform/voice-studio/preview', data).then((r) => r.data),
  translateVoice: (data) => adminApi.post('/studio/platform/voice-studio/translate', data).then((r) => r.data),
  getVoiceQueue: () => adminApi.get('/studio/platform/voice-studio/queue').then((r) => r.data),
  getVoiceHistory: (params) => adminApi.get('/studio/platform/voice-studio/history', { params }).then((r) => r.data),
  getVoiceVersions: (id) => adminApi.get(`/studio/platform/voice-studio/jobs/${id}/versions`).then((r) => r.data),
  saveVoiceToAsset: (id) => adminApi.post(`/studio/platform/voice-studio/jobs/${id}/save-asset`).then((r) => r.data),
  getVoiceDownloadUrl: (id) => apiUrl(`/studio/platform/voice-studio/jobs/${id}/download`),
  getVoiceSubtitlesUrl: (id) => apiUrl(`/studio/platform/voice-studio/jobs/${id}/subtitles.srt`),
  getVoicePrompts: (language) => adminApi.get('/studio/platform/voice-studio/prompts', { params: language ? { language } : {} }).then((r) => r.data),
  retryVoiceJob: (id) => adminApi.post(`/studio/platform/voice-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelVoiceJob: (id) => adminApi.post(`/studio/platform/voice-studio/jobs/${id}/cancel`).then((r) => r.data),

  getMusicStudioOverview: () => adminApi.get('/studio/platform/music-studio/overview').then((r) => r.data),
  createMusicGeneration: (data) => adminApi.post('/studio/platform/music-studio/generate', data).then((r) => r.data),
  previewMusic: (data) => adminApi.post('/studio/platform/music-studio/preview', data).then((r) => r.data),
  getMusicQueue: () => adminApi.get('/studio/platform/music-studio/queue').then((r) => r.data),
  getMusicHistory: (params) => adminApi.get('/studio/platform/music-studio/history', { params }).then((r) => r.data),
  getMusicFavorites: () => adminApi.get('/studio/platform/music-studio/favorites').then((r) => r.data),
  toggleMusicFavorite: (id) => adminApi.post(`/studio/platform/music-studio/jobs/${id}/favorite`).then((r) => r.data),
  getMusicVersions: (id) => adminApi.get(`/studio/platform/music-studio/jobs/${id}/versions`).then((r) => r.data),
  saveMusicToAsset: (id) => adminApi.post(`/studio/platform/music-studio/jobs/${id}/save-asset`).then((r) => r.data),
  getMusicDownloadUrl: (id) => apiUrl(`/studio/platform/music-studio/jobs/${id}/download`),
  getMusicPrompts: (category) => adminApi.get('/studio/platform/music-studio/prompts', { params: category ? { category } : {} }).then((r) => r.data),
  retryMusicJob: (id) => adminApi.post(`/studio/platform/music-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelMusicJob: (id) => adminApi.post(`/studio/platform/music-studio/jobs/${id}/cancel`).then((r) => r.data),

  getShortsStudioOverview: () => adminApi.get('/studio/platform/shorts-studio/overview').then((r) => r.data),
  createShortsGeneration: (data) => adminApi.post('/studio/platform/shorts-studio/generate', data).then((r) => r.data),
  getShortsQueue: () => adminApi.get('/studio/platform/shorts-studio/queue').then((r) => r.data),
  getShortsHistory: (params) => adminApi.get('/studio/platform/shorts-studio/history', { params }).then((r) => r.data),
  queueShortsPublish: (id, data) => adminApi.post(`/studio/platform/shorts-studio/jobs/${id}/queue-publish`, data || {}).then((r) => r.data),
  saveShortsToAsset: (id) => adminApi.post(`/studio/platform/shorts-studio/jobs/${id}/save-asset`).then((r) => r.data),
  getShortsDownloadUrl: (id) => apiUrl(`/studio/platform/shorts-studio/jobs/${id}/download`),
  retryShortsJob: (id) => adminApi.post(`/studio/platform/shorts-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelShortsJob: (id) => adminApi.post(`/studio/platform/shorts-studio/jobs/${id}/cancel`).then((r) => r.data),

  getSEOStudioOverview: () => adminApi.get('/studio/platform/seo-studio/overview').then((r) => r.data),
  createSEOGeneration: (data) => adminApi.post('/studio/platform/seo-studio/generate', data).then((r) => r.data),
  getSEOQueue: () => adminApi.get('/studio/platform/seo-studio/queue').then((r) => r.data),
  getSEOHistory: (params) => adminApi.get('/studio/platform/seo-studio/history', { params }).then((r) => r.data),
  getSEOVariants: (id) => adminApi.get(`/studio/platform/seo-studio/jobs/${id}/variants`).then((r) => r.data),
  selectSEOVariant: (id, variantId) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/select-variant`, { variant_id: variantId }).then((r) => r.data),
  requestSEOApproval: (id, data) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/request-approval`, data || {}).then((r) => r.data),
  approveSEO: (id, data) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/approve`, data || {}).then((r) => r.data),
  rejectSEO: (id, data) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/reject`, data || {}).then((r) => r.data),
  exportSEOPack: (id, variantId) => adminApi.get(`/studio/platform/seo-studio/jobs/${id}/export`, { params: variantId ? { variant_id: variantId } : {} }).then((r) => r.data),
  applySEOToProject: (id, data) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/apply-project`, data || {}).then((r) => r.data),
  retrySEOJob: (id) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelSEOJob: (id) => adminApi.post(`/studio/platform/seo-studio/jobs/${id}/cancel`).then((r) => r.data),

  getTranslationStudioOverview: () => adminApi.get('/studio/platform/translation-studio/overview').then((r) => r.data),
  createTranslation: (data) => adminApi.post('/studio/platform/translation-studio/generate', data).then((r) => r.data),
  getTranslationQueue: () => adminApi.get('/studio/platform/translation-studio/queue').then((r) => r.data),
  getTranslationHistory: (params) => adminApi.get('/studio/platform/translation-studio/history', { params }).then((r) => r.data),
  getTranslationMemory: (params) => adminApi.get('/studio/platform/translation-studio/translation-memory', { params }).then((r) => r.data),
  deleteTranslationMemory: (id) => adminApi.delete(`/studio/platform/translation-studio/translation-memory/${id}`).then((r) => r.data),
  getTranslationVersions: (id) => adminApi.get(`/studio/platform/translation-studio/jobs/${id}/versions`).then((r) => r.data),
  requestTranslationApproval: (id, data) => adminApi.post(`/studio/platform/translation-studio/jobs/${id}/request-approval`, data || {}).then((r) => r.data),
  approveTranslation: (id, data) => adminApi.post(`/studio/platform/translation-studio/jobs/${id}/approve`, data || {}).then((r) => r.data),
  rejectTranslation: (id, data) => adminApi.post(`/studio/platform/translation-studio/jobs/${id}/reject`, data || {}).then((r) => r.data),
  getTranslationSrtUrl: (id) => apiUrl(`/studio/platform/translation-studio/jobs/${id}/subtitles.srt`),
  getTranslationVttUrl: (id) => apiUrl(`/studio/platform/translation-studio/jobs/${id}/subtitles.vtt`),
  retryTranslationJob: (id) => adminApi.post(`/studio/platform/translation-studio/jobs/${id}/retry`).then((r) => r.data),
  cancelTranslationJob: (id) => adminApi.post(`/studio/platform/translation-studio/jobs/${id}/cancel`).then((r) => r.data),

  getAssetsOverview: () => adminApi.get('/studio/platform/assets/overview').then((r) => r.data),
  listAssets: (params) => adminApi.get('/studio/platform/assets', { params }).then((r) => r.data),
  uploadAsset: (formData) => adminApi.post('/studio/platform/assets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data),
  updateAsset: (id, data) => adminApi.patch(`/studio/platform/assets/${id}`, data).then((r) => r.data),
  toggleAssetFavorite: (id) => adminApi.post(`/studio/platform/assets/${id}/favorite`).then((r) => r.data),
  deleteAsset: (id) => adminApi.delete(`/studio/platform/assets/${id}`),
  restoreAsset: (id) => adminApi.post(`/studio/platform/assets/${id}/restore`).then((r) => r.data),
  getAssetVersions: (id) => adminApi.get(`/studio/platform/assets/${id}/versions`).then((r) => r.data),
  restoreAssetVersion: (assetId, versionId) => adminApi.post(`/studio/platform/assets/${assetId}/versions/${versionId}/restore`).then((r) => r.data),
  listAssetCollections: () => adminApi.get('/studio/platform/assets/collections/list').then((r) => r.data),
  createAssetCollection: (data) => adminApi.post('/studio/platform/assets/collections', data).then((r) => r.data),
  getAssetPermissions: (id) => adminApi.get(`/studio/platform/assets/${id}/permissions`).then((r) => r.data),
  addAssetPermission: (id, data) => adminApi.post(`/studio/platform/assets/${id}/permissions`, data).then((r) => r.data),

  getTimelineWorkspace: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/timeline-editor`).then((r) => r.data),
  saveTimeline: (projectId, data) => adminApi.put(`/studio/platform/projects/${projectId}/timeline-editor`, data).then((r) => r.data),
  createTimelineSnapshot: (projectId, label) => adminApi.post(`/studio/platform/projects/${projectId}/timeline-editor/snapshots`, null, { params: label ? { label } : {} }).then((r) => r.data),
  listTimelineExports: (projectId) => adminApi.get(`/studio/platform/projects/${projectId}/timeline-editor/exports`).then((r) => r.data),
  createTimelineExport: (projectId, data) => adminApi.post(`/studio/platform/projects/${projectId}/timeline-editor/exports`, data).then((r) => r.data),

  getPublishingOverview: () => adminApi.get('/studio/platform/publishing/overview').then((r) => r.data),
  getPublishingQueue: (params) => adminApi.get('/studio/platform/publishing/queue', { params }).then((r) => r.data),
  getPublishingWorkspace: (projectId) => adminApi.get(`/studio/platform/publishing/projects/${projectId}`).then((r) => r.data),
  updatePublishingPackage: (projectId, data) => adminApi.put(`/studio/platform/publishing/projects/${projectId}`, data).then((r) => r.data),
  schedulePublish: (projectId, data) => adminApi.post(`/studio/platform/publishing/projects/${projectId}/schedule`, data).then((r) => r.data),
  approvePublishJob: (jobId, notes) => adminApi.post(`/studio/platform/publishing/jobs/${jobId}/approve`, notes ? { notes } : {}).then((r) => r.data),
  rejectPublishJob: (jobId, notes) => adminApi.post(`/studio/platform/publishing/jobs/${jobId}/reject`, notes ? { notes } : {}).then((r) => r.data),
  retryPublishJob: (jobId) => adminApi.post(`/studio/platform/publishing/jobs/${jobId}/retry`).then((r) => r.data),

  getPublishingAgentOverview: () => adminApi.get('/studio/platform/publishing-agent/overview').then((r) => r.data),
  dispatchPublishingAgent: (data) => adminApi.post('/studio/platform/publishing-agent/dispatch', data).then((r) => r.data),
  getPublishingAgentQueue: () => adminApi.get('/studio/platform/publishing-agent/queue').then((r) => r.data),
  getPublishingAgentHistory: (params) => adminApi.get('/studio/platform/publishing-agent/history', { params }).then((r) => r.data),
  getPublishingAgentAnalytics: (params) => adminApi.get('/studio/platform/publishing-agent/analytics', { params }).then((r) => r.data),
  approvePublishingRun: (id, notes) => adminApi.post(`/studio/platform/publishing-agent/runs/${id}/approve`, notes ? { notes } : {}).then((r) => r.data),
  rejectPublishingRun: (id, notes) => adminApi.post(`/studio/platform/publishing-agent/runs/${id}/reject`, notes ? { notes } : {}).then((r) => r.data),
  retryPublishingRun: (id, jobIds) => adminApi.post(`/studio/platform/publishing-agent/runs/${id}/retry`, jobIds ? { job_ids: jobIds } : {}).then((r) => r.data),
  listPublishingWebhooks: () => adminApi.get('/studio/platform/publishing-agent/webhooks').then((r) => r.data),
  createPublishingWebhook: (data) => adminApi.post('/studio/platform/publishing-agent/webhooks', data).then((r) => r.data),
  deletePublishingWebhook: (id) => adminApi.delete(`/studio/platform/publishing-agent/webhooks/${id}`).then((r) => r.data),

  getProductionPipelineOverview: () => adminApi.get('/studio/platform/workflow-engine/overview').then((r) => r.data),
  getWorkflowPrompts: () => adminApi.get('/studio/platform/workflow-engine/prompts').then((r) => r.data),
  startProductionPipeline: (data) => adminApi.post('/studio/platform/workflow-engine/runs', data).then((r) => r.data),
  getProductionPipelineRuns: () => adminApi.get('/studio/platform/workflow-engine/runs').then((r) => r.data),
  getProductionPipelineRun: (id) => adminApi.get(`/studio/platform/workflow-engine/runs/${id}`).then((r) => r.data),
  getWorkflowStatus: (id) => adminApi.get(`/studio/platform/workflow-engine/runs/${id}/status`).then((r) => r.data),
  getWorkflowLogs: (id) => adminApi.get(`/studio/platform/workflow-engine/runs/${id}/logs`).then((r) => r.data),
  getWorkflowHistory: (params) => adminApi.get('/studio/platform/workflow-engine/history', { params }).then((r) => r.data),
  runWorkflow: (id) => adminApi.post(`/studio/platform/workflow-engine/runs/${id}/run`).then((r) => r.data),
  cancelProductionPipelineRun: (id) => adminApi.post(`/studio/platform/workflow-engine/runs/${id}/cancel`).then((r) => r.data),
  retryWorkflow: (id) => adminApi.post(`/studio/platform/workflow-engine/runs/${id}/retry`).then((r) => r.data),
  approveWorkflow: (id, notes) => adminApi.post(`/studio/platform/workflow-engine/runs/${id}/approve`, notes ? { notes } : {}).then((r) => r.data),
  rejectWorkflow: (id, notes) => adminApi.post(`/studio/platform/workflow-engine/runs/${id}/reject`, notes ? { notes } : {}).then((r) => r.data),

  getWorkflowNodeCatalog: () => adminApi.get('/studio/platform/workflow-engine/catalog/nodes').then((r) => r.data),
  getWorkflowDashboard: () => adminApi.get('/studio/platform/workflow-engine/dashboard').then((r) => r.data),
  listWorkflowDefinitions: (params) => adminApi.get('/studio/platform/workflow-engine/definitions', { params }).then((r) => r.data),
  listWorkflowTemplates: () => adminApi.get('/studio/platform/workflow-engine/templates').then((r) => r.data),
  getWorkflowDefinition: (id) => adminApi.get(`/studio/platform/workflow-engine/definitions/${id}`).then((r) => r.data),
  createWorkflowDefinition: (data) => adminApi.post('/studio/platform/workflow-engine/definitions', data).then((r) => r.data),
  updateWorkflowDefinition: (id, data) => adminApi.patch(`/studio/platform/workflow-engine/definitions/${id}`, data).then((r) => r.data),
  deleteWorkflowDefinition: (id) => adminApi.delete(`/studio/platform/workflow-engine/definitions/${id}`),
  createWorkflowVersion: (definitionId, data) =>
    adminApi.post(`/studio/platform/workflow-engine/definitions/${definitionId}/versions`, data).then((r) => r.data),
  listWorkflowVersions: (definitionId) =>
    adminApi.get(`/studio/platform/workflow-engine/definitions/${definitionId}/versions`).then((r) => r.data),
  executeWorkflowDefinition: (definitionId, data) =>
    adminApi.post(`/studio/platform/workflow-engine/definitions/${definitionId}/execute`, data).then((r) => r.data),
  cloneWorkflowTemplate: (templateId, name) =>
    adminApi.post(`/studio/platform/workflow-engine/templates/${templateId}/clone`, null, { params: name ? { name } : {} }).then((r) => r.data),
  listWorkflowTriggers: (definitionId) =>
    adminApi.get(`/studio/platform/workflow-engine/definitions/${definitionId}/triggers`).then((r) => r.data),
  createWorkflowTrigger: (definitionId, data) =>
    adminApi.post(`/studio/platform/workflow-engine/definitions/${definitionId}/triggers`, data).then((r) => r.data),
  updateWorkflowTrigger: (definitionId, triggerId, data) =>
    adminApi.patch(`/studio/platform/workflow-engine/definitions/${definitionId}/triggers/${triggerId}`, data).then((r) => r.data),
  deleteWorkflowTrigger: (definitionId, triggerId) =>
    adminApi.delete(`/studio/platform/workflow-engine/definitions/${definitionId}/triggers/${triggerId}`),
  fireWorkflowTrigger: (definitionId, triggerId, data) =>
    adminApi.post(`/studio/platform/workflow-engine/definitions/${definitionId}/triggers/${triggerId}/fire`, data).then((r) => r.data),
  listWorkflowExecutionLogs: (runId, params) =>
    adminApi.get(`/studio/platform/workflow-engine/runs/${runId}/execution-logs`, { params }).then((r) => r.data),
  restoreWorkflowVersion: (definitionId, versionId) =>
    adminApi.post(`/studio/platform/workflow-engine/definitions/${definitionId}/versions/${versionId}/restore`).then((r) => r.data),

  getAgentMarketplaceOverview: () => adminApi.get('/studio/platform/agent-marketplace/overview').then((r) => r.data),
  listMarketplaceAgents: (params) => adminApi.get('/studio/platform/agent-marketplace/agents', { params }).then((r) => r.data),
  getMarketplaceAgent: (slug) => adminApi.get(`/studio/platform/agent-marketplace/agents/${slug}`).then((r) => r.data),
  listInstalledAgents: () => adminApi.get('/studio/platform/agent-marketplace/installed').then((r) => r.data),
  installAgent: (slug, data) => adminApi.post(`/studio/platform/agent-marketplace/agents/${slug}/install`, data || {}).then((r) => r.data),
  enableAgent: (id) => adminApi.post(`/studio/platform/agent-marketplace/installations/${id}/enable`).then((r) => r.data),
  disableAgent: (id) => adminApi.post(`/studio/platform/agent-marketplace/installations/${id}/disable`).then((r) => r.data),
  updateAgentConfig: (id, data) => adminApi.patch(`/studio/platform/agent-marketplace/installations/${id}/config`, data).then((r) => r.data),
  updateAgentPermissions: (id, data) => adminApi.patch(`/studio/platform/agent-marketplace/installations/${id}/permissions`, data).then((r) => r.data),
  updateAgentVersion: (id) => adminApi.post(`/studio/platform/agent-marketplace/installations/${id}/update`).then((r) => r.data),
  getAgentInstallationHistory: (id) => adminApi.get(`/studio/platform/agent-marketplace/installations/${id}/history`).then((r) => r.data),
  uninstallAgent: (id) => adminApi.delete(`/studio/platform/agent-marketplace/installations/${id}`),

  getAgentPlatformRegistry: () => adminApi.get('/studio/platform/agent-platform/registry').then((r) => r.data),
  getAgentSdkDocs: () => adminApi.get('/studio/platform/agent-platform/sdk').then((r) => r.data),
  getAgentMonitoring: () => adminApi.get('/studio/platform/agent-platform/monitoring').then((r) => r.data),
  getAgentExecutionLogs: (params) => adminApi.get('/studio/platform/agent-platform/logs', { params }).then((r) => r.data),
  getAgentInstallationAnalytics: (id) =>
    adminApi.get(`/studio/platform/agent-platform/installations/${id}/analytics`).then((r) => r.data),
  runAgent: (id, data) =>
    adminApi.post(`/studio/platform/agent-platform/installations/${id}/run`, data || {}).then((r) => r.data),
  listAgentMemory: (id, params) =>
    adminApi.get(`/studio/platform/agent-platform/installations/${id}/memory`, { params }).then((r) => r.data),
  upsertAgentMemory: (id, data) =>
    adminApi.put(`/studio/platform/agent-platform/installations/${id}/memory`, data).then((r) => r.data),
  deleteAgentMemory: (id, memoryId) =>
    adminApi.delete(`/studio/platform/agent-platform/installations/${id}/memory/${memoryId}`),
  listAgentSchedules: (id) =>
    adminApi.get(`/studio/platform/agent-platform/installations/${id}/schedules`).then((r) => r.data),
  createAgentSchedule: (id, data) =>
    adminApi.post(`/studio/platform/agent-platform/installations/${id}/schedules`, data).then((r) => r.data),
  deleteAgentSchedule: (id, scheduleId) =>
    adminApi.delete(`/studio/platform/agent-platform/installations/${id}/schedules/${scheduleId}`),
  listAgentMessages: (id, params) =>
    adminApi.get(`/studio/platform/agent-platform/installations/${id}/messages`, { params }).then((r) => r.data),
  sendAgentMessage: (id, data) =>
    adminApi.post(`/studio/platform/agent-platform/installations/${id}/messages`, data).then((r) => r.data),

  getBIExecutive: (params) => adminApi.get('/studio/platform/bi/executive', { params }).then((r) => r.data),
  getBIRevenue: (params) => adminApi.get('/studio/platform/bi/revenue', { params }).then((r) => r.data),
  getBIAICosts: (params) => adminApi.get('/studio/platform/bi/ai-costs', { params }).then((r) => r.data),
  getBIUsage: () => adminApi.get('/studio/platform/bi/usage').then((r) => r.data),
  getBIPerformance: (params) => adminApi.get('/studio/platform/bi/performance', { params }).then((r) => r.data),
  getBIProjects: () => adminApi.get('/studio/platform/bi/projects').then((r) => r.data),
  getBITeams: () => adminApi.get('/studio/platform/bi/teams').then((r) => r.data),
  getBIOrganizations: () => adminApi.get('/studio/platform/bi/organizations').then((r) => r.data),
  getBIRetention: (params) => adminApi.get('/studio/platform/bi/retention', { params }).then((r) => r.data),
  getBIGrowth: (params) => adminApi.get('/studio/platform/bi/growth', { params }).then((r) => r.data),
  getBICatalog: () => adminApi.get('/studio/platform/bi/catalog').then((r) => r.data),
  listBIReports: () => adminApi.get('/studio/platform/bi/reports').then((r) => r.data),
  createBIReport: (data) => adminApi.post('/studio/platform/bi/reports', data).then((r) => r.data),
  runBIReport: (id, params) => adminApi.post(`/studio/platform/bi/reports/${id}/run`, null, { params }).then((r) => r.data),
  exportBIReport: (id, format, params) =>
    adminApi.get(`/studio/platform/bi/reports/${id}/export`, { params: { format, ...params }, responseType: 'blob' }).then((r) => r.data),
  listBIScheduledReports: () => adminApi.get('/studio/platform/bi/scheduled-reports').then((r) => r.data),
  createBIScheduledReport: (data) => adminApi.post('/studio/platform/bi/scheduled-reports', data).then((r) => r.data),
  deleteBIScheduledReport: (id) => adminApi.delete(`/studio/platform/bi/scheduled-reports/${id}`),

  getPluginMarketplaceOverview: () => adminApi.get('/studio/platform/plugins/overview').then((r) => r.data),
  listMarketplacePlugins: (params) => adminApi.get('/studio/platform/plugins/catalog', { params }).then((r) => r.data),
  getMarketplacePlugin: (slug) => adminApi.get(`/studio/platform/plugins/catalog/${slug}`).then((r) => r.data),
  listInstalledPlugins: () => adminApi.get('/studio/platform/plugins/installed').then((r) => r.data),
  installPlugin: (slug, data) => adminApi.post(`/studio/platform/plugins/catalog/${slug}/install`, data || {}).then((r) => r.data),
  enablePlugin: (id) => adminApi.post(`/studio/platform/plugins/installations/${id}/enable`).then((r) => r.data),
  disablePlugin: (id) => adminApi.post(`/studio/platform/plugins/installations/${id}/disable`).then((r) => r.data),
  updatePluginSettings: (id, data) => adminApi.patch(`/studio/platform/plugins/installations/${id}/settings`, data).then((r) => r.data),
  updatePluginPermissions: (id, data) => adminApi.patch(`/studio/platform/plugins/installations/${id}/permissions`, data).then((r) => r.data),
  updatePluginVersion: (id) => adminApi.post(`/studio/platform/plugins/installations/${id}/update`).then((r) => r.data),
  getPluginInstallationHistory: (id) => adminApi.get(`/studio/platform/plugins/installations/${id}/history`).then((r) => r.data),
  uninstallPlugin: (id) => adminApi.delete(`/studio/platform/plugins/installations/${id}`),
  getPluginSdkDocs: () => adminApi.get('/studio/platform/plugins/docs').then((r) => r.data),
  getPluginRuntime: () => adminApi.get('/studio/platform/plugins/runtime').then((r) => r.data),
  getPluginEventLog: (params) => adminApi.get('/studio/platform/plugins/event-log', { params }).then((r) => r.data),
  testPluginEvent: (data) => adminApi.post('/studio/platform/plugins/test-event', data).then((r) => r.data),
  registerPlugin: (manifest) => adminApi.post('/studio/platform/plugins/register', { manifest }).then((r) => r.data),
  publishPluginVersion: (slug, data) =>
    adminApi.post(`/studio/platform/plugins/catalog/${slug}/publish-version`, data).then((r) => r.data),
  listPluginVersions: (slug) => adminApi.get(`/studio/platform/plugins/catalog/${slug}/versions`).then((r) => r.data),
  listPluginRatings: (slug, params) =>
    adminApi.get(`/studio/platform/plugins/catalog/${slug}/ratings`, { params }).then((r) => r.data),
  ratePlugin: (slug, data) =>
    adminApi.post(`/studio/platform/plugins/catalog/${slug}/ratings`, data).then((r) => r.data),
  getPluginHooksCatalog: () => adminApi.get('/studio/platform/plugins/hooks').then((r) => r.data),
  getPluginEventsCatalog: () => adminApi.get('/studio/platform/plugins/events').then((r) => r.data),

  getApiGatewayOverview: () => adminApi.get('/studio/platform/api-gateway/overview').then((r) => r.data),
  getApiGatewayUsageTimeseries: (params) => adminApi.get('/studio/platform/api-gateway/usage/timeseries', { params }).then((r) => r.data),
  getApiGatewayUsageEndpoints: (params) => adminApi.get('/studio/platform/api-gateway/usage/endpoints', { params }).then((r) => r.data),
  getApiGatewayDocs: () => adminApi.get('/studio/platform/api-gateway/docs').then((r) => r.data),
  listApiGatewayKeys: () => adminApi.get('/studio/platform/api-gateway/keys').then((r) => r.data),
  createApiGatewayKey: (data) => adminApi.post('/studio/platform/api-gateway/keys', data).then((r) => r.data),
  revokeApiGatewayKey: (id) => adminApi.delete(`/studio/platform/api-gateway/keys/${id}`),
  listApiGatewayWebhooks: () => adminApi.get('/studio/platform/api-gateway/webhooks').then((r) => r.data),
  createApiGatewayWebhook: (data) => adminApi.post('/studio/platform/api-gateway/webhooks', data).then((r) => r.data),
  deleteApiGatewayWebhook: (id) => adminApi.delete(`/studio/platform/api-gateway/webhooks/${id}`),
  getApiGatewayWebhookDeliveries: (id, params) => adminApi.get(`/studio/platform/api-gateway/webhooks/${id}/deliveries`, { params }).then((r) => r.data),
  testApiGatewayWebhook: (id) => adminApi.post(`/studio/platform/api-gateway/webhooks/${id}/test`).then((r) => r.data),

  getSecurityOverview: () => adminApi.get('/studio/platform/security/overview').then((r) => r.data),
  getSecurityCompliance: () => adminApi.get('/studio/platform/security/compliance').then((r) => r.data),
  getSecurityRbac: () => adminApi.get('/studio/platform/security/rbac').then((r) => r.data),
  getSecurityAudit: (params) => adminApi.get('/studio/platform/security/audit', { params }).then((r) => r.data),
  listIdpProviders: () => adminApi.get('/studio/platform/security/idp').then((r) => r.data),
  createIdpProvider: (data) => adminApi.post('/studio/platform/security/idp', data).then((r) => r.data),
  updateIdpProvider: (slug, data) => adminApi.patch(`/studio/platform/security/idp/${slug}`, data).then((r) => r.data),
  getMfaStatus: () => adminApi.get('/studio/platform/security/mfa/status').then((r) => r.data),
  setupMfa: () => adminApi.post('/studio/platform/security/mfa/setup').then((r) => r.data),
  verifyMfaSetup: (code) => adminApi.post('/studio/platform/security/mfa/verify', { code }).then((r) => r.data),
  disableMfa: (code) => adminApi.post('/studio/platform/security/mfa/disable', { code }),
  listSecuritySessions: () => adminApi.get('/studio/platform/security/sessions').then((r) => r.data),
  revokeSecuritySession: (id) => adminApi.delete(`/studio/platform/security/sessions/${id}`),
  listSecurityIpRules: () => adminApi.get('/studio/platform/security/ip-rules').then((r) => r.data),
  createSecurityIpRule: (data) => adminApi.post('/studio/platform/security/ip-rules', data).then((r) => r.data),
  deleteSecurityIpRule: (id) => adminApi.delete(`/studio/platform/security/ip-rules/${id}`),
  listSecuritySecrets: () => adminApi.get('/studio/platform/security/secrets').then((r) => r.data),
  createSecuritySecret: (data) => adminApi.post('/studio/platform/security/secrets', data).then((r) => r.data),
  deleteSecuritySecret: (id) => adminApi.delete(`/studio/platform/security/secrets/${id}`),

  getComplianceReport: () => adminApi.get('/studio/platform/compliance/report').then((r) => r.data),
  listCompliancePolicies: () => adminApi.get('/studio/platform/compliance/policies').then((r) => r.data),
  updateCompliancePolicy: (key, data) => adminApi.patch(`/studio/platform/compliance/policies/${key}`, data).then((r) => r.data),
  listComplianceConsents: (params) => adminApi.get('/studio/platform/compliance/consents', { params }).then((r) => r.data),
  listPrivacyRequests: (params) => adminApi.get('/studio/platform/compliance/privacy-requests', { params }).then((r) => r.data),
  updatePrivacyRequest: (id, data) => adminApi.patch(`/studio/platform/compliance/privacy-requests/${id}`, data).then((r) => r.data),
  processPrivacyErasure: (id) => adminApi.post(`/studio/platform/compliance/privacy-requests/${id}/erasure`).then((r) => r.data),
  exportPrivacyData: (id) => adminApi.post(`/studio/platform/compliance/privacy-requests/${id}/export`).then((r) => r.data),
  listComplianceAccessLogs: (params) => adminApi.get('/studio/platform/compliance/access-logs', { params }).then((r) => r.data),
  runComplianceRetention: () => adminApi.post('/studio/platform/compliance/retention/run').then((r) => r.data),

  getAICostDashboard: (params) => adminApi.get('/studio/platform/ai-cost/dashboard', { params }).then((r) => r.data),
  getAICostIntelligence: (params) => adminApi.get('/studio/platform/ai-cost/intelligence', { params }).then((r) => r.data),
  resolveAICostRouting: (data) => adminApi.post('/studio/platform/ai-cost/routing/resolve', data).then((r) => r.data),
  getAICostPricing: () => adminApi.get('/studio/platform/ai-cost/pricing').then((r) => r.data),
  getAICostCacheStats: () => adminApi.get('/studio/platform/ai-cost/cache-stats').then((r) => r.data),
  listAICostBudgets: () => adminApi.get('/studio/platform/ai-cost/budgets').then((r) => r.data),
  createAICostBudget: (data) => adminApi.post('/studio/platform/ai-cost/budgets', data).then((r) => r.data),
  updateAICostBudget: (id, data) => adminApi.patch(`/studio/platform/ai-cost/budgets/${id}`, data).then((r) => r.data),
  deleteAICostBudget: (id) => adminApi.delete(`/studio/platform/ai-cost/budgets/${id}`),
  listAICostPolicies: () => adminApi.get('/studio/platform/ai-cost/policies').then((r) => r.data),
  updateAICostPolicy: (module, data) => adminApi.patch(`/studio/platform/ai-cost/policies/${module}`, data).then((r) => r.data),
  listAICostAlerts: (params) => adminApi.get('/studio/platform/ai-cost/alerts', { params }).then((r) => r.data),
  acknowledgeAICostAlert: (id) => adminApi.post(`/studio/platform/ai-cost/alerts/${id}/acknowledge`).then((r) => r.data),
  listAICostReports: (params) => adminApi.get('/studio/platform/ai-cost/reports', { params }).then((r) => r.data),
  generateAICostReport: (params) => adminApi.post('/studio/platform/ai-cost/reports/generate', null, { params }).then((r) => r.data),

  getCollaborationOverview: (projectId) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/overview`).then((r) => r.data),
  getOrCreateCollabDocument: (projectId, params) => adminApi.post(`/studio/platform/collaboration/projects/${projectId}/documents`, null, { params }).then((r) => r.data),
  getCollabDocument: (id) => adminApi.get(`/studio/platform/collaboration/documents/${id}`).then((r) => r.data),
  saveCollabDocument: (id, data) => adminApi.put(`/studio/platform/collaboration/documents/${id}`, data).then((r) => r.data),
  resolveCollabConflict: (id, data) => adminApi.post(`/studio/platform/collaboration/conflicts/${id}/resolve`, data).then((r) => r.data),
  listCollabDocumentVersions: (id) => adminApi.get(`/studio/platform/collaboration/documents/${id}/versions`).then((r) => r.data),
  updateCollabPresence: (projectId, data) => adminApi.post(`/studio/platform/collaboration/projects/${projectId}/presence`, data).then((r) => r.data),
  listCollabPresence: (projectId) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/presence`).then((r) => r.data),
  listCollabComments: (projectId, params) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/comments`, { params }).then((r) => r.data),
  addCollabComment: (projectId, data) => adminApi.post(`/studio/platform/collaboration/projects/${projectId}/comments`, data).then((r) => r.data),
  listCollabFiles: (projectId) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/files`).then((r) => r.data),
  shareCollabFile: (projectId, data) => adminApi.post(`/studio/platform/collaboration/projects/${projectId}/files`, data).then((r) => r.data),
  listCollabTasks: (projectId) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/tasks`).then((r) => r.data),
  listCollabApprovals: (projectId) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/approvals`).then((r) => r.data),
  getCollabActivity: (projectId, params) => adminApi.get(`/studio/platform/collaboration/projects/${projectId}/activity`, { params }).then((r) => r.data),
  listCollabNotifications: (params) => adminApi.get('/studio/platform/collaboration/notifications', { params }).then((r) => r.data),
  markCollabNotificationRead: (id) => adminApi.post(`/studio/platform/collaboration/notifications/${id}/read`).then((r) => r.data),

  getAnalyticsOverview: () => adminApi.get('/studio/platform/analytics/overview').then((r) => r.data),
  getAnalyticsRealtime: () => adminApi.get('/studio/platform/analytics/realtime').then((r) => r.data),

  getAdminOverview: () => adminApi.get('/studio/platform/admin/overview').then((r) => r.data),
  getAdminRbac: () => adminApi.get('/studio/platform/admin/rbac').then((r) => r.data),
  getAdminUsers: () => adminApi.get('/studio/platform/admin/users').then((r) => r.data),
  getAdminAuditLogs: () => adminApi.get('/studio/platform/admin/audit-logs').then((r) => r.data),
  getAdminAIUsage: () => adminApi.get('/studio/platform/admin/ai-usage').then((r) => r.data),
  getAdminStorage: () => adminApi.get('/studio/platform/admin/storage').then((r) => r.data),
  getAdminBilling: () => adminApi.get('/studio/platform/admin/billing').then((r) => r.data),
  getAdminApiKeys: () => adminApi.get('/studio/platform/admin/api-keys').then((r) => r.data),
  createApiKey: (data) => adminApi.post('/studio/platform/admin/api-keys', data).then((r) => r.data),
  revokeApiKey: (id) => adminApi.delete(`/studio/platform/admin/api-keys/${id}`),
  getAdminHealth: () => adminApi.get('/studio/platform/admin/health').then((r) => r.data),
  getAdminSecurityLogs: () => adminApi.get('/studio/platform/admin/security-logs').then((r) => r.data),
  getAdminFeatureFlags: () => adminApi.get('/studio/platform/admin/feature-flags').then((r) => r.data),
  updateFeatureFlag: (id, data) => adminApi.patch(`/studio/platform/admin/feature-flags/${id}`, data).then((r) => r.data),
  getAdminSettings: () => adminApi.get('/studio/platform/admin/settings').then((r) => r.data),
  updateAdminSettings: (data) => adminApi.put('/studio/platform/admin/settings', data).then((r) => r.data),
  getAdminBackups: () => adminApi.get('/studio/platform/admin/backups').then((r) => r.data),
  createBackup: (label) => adminApi.post('/studio/platform/admin/backups', null, { params: label ? { label } : {} }).then((r) => r.data),

  listStudioNotifications: (params) => adminApi.get('/studio/platform/notifications', { params }).then((r) => r.data),
  markStudioNotificationRead: (id) => adminApi.post(`/studio/platform/notifications/${id}/read`).then((r) => r.data),
};

export const tenancy = {
  listOrganizations: () => adminApi.get('/studio/tenancy/organizations').then((r) => r.data),
  createOrganization: (data) => adminApi.post('/studio/tenancy/organizations', data).then((r) => r.data),
  getCurrentOrganization: () => adminApi.get('/studio/tenancy/organizations/current').then((r) => r.data),
  updateCurrentOrganization: (data) => adminApi.patch('/studio/tenancy/organizations/current', data).then((r) => r.data),
  getUsage: () => adminApi.get('/studio/tenancy/organizations/current/usage').then((r) => r.data),
  listMembers: () => adminApi.get('/studio/tenancy/organizations/current/members').then((r) => r.data),
  listTeams: () => adminApi.get('/studio/tenancy/teams').then((r) => r.data),
  listWorkspaces: () => adminApi.get('/studio/tenancy/workspaces').then((r) => r.data),
  setActiveOrg: (orgId) => {
    localStorage.setItem('untold-org-id', String(orgId));
    return Promise.resolve(orgId);
  },
};

export const enterpriseBilling = {
  listPlans: () => adminApi.get('/studio/billing/plans').then((r) => r.data),
  getSubscription: () => adminApi.get('/studio/billing/subscription').then((r) => r.data),
  subscribe: (data) => adminApi.post('/studio/billing/subscribe', data).then((r) => r.data),
  updateSubscription: (data) => adminApi.patch('/studio/billing/subscription', data).then((r) => r.data),
  listInvoices: () => adminApi.get('/studio/billing/invoices').then((r) => r.data),
  listPayments: () => adminApi.get('/studio/billing/payments').then((r) => r.data),
  getUsage: () => adminApi.get('/studio/billing/usage').then((r) => r.data),
  validateCoupon: (data) => adminApi.post('/studio/billing/coupons/validate', data).then((r) => r.data),
};

export const newsAdmin = {
  publish: (data) => adminApi.post('/admin/news/publish', data).then((r) => r.data),
  fetchExternal: (data) => adminApi.post('/admin/news/fetch', data).then((r) => r.data),
};

export default adminApi;
