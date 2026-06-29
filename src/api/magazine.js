import { api } from './client';
import {
  magazineCatalog,
  getMagazineIssues,
  getIssueById,
  getFeaturedIssue,
  getFreeSampleIssue,
  MOCK_WORKFLOW_JOBS,
} from '../data/magazineCatalog';

export const magazineApi = {
  async listIssues() {
    try {
      const { data } = await api.get('/magazine/issues');
      return { data: data.items || data };
    } catch {
      return { data: getMagazineIssues(), source: 'mock' };
    }
  },

  async getIssue(id) {
    try {
      const { data } = await api.get(`/magazine/issues/${id}`);
      return { data };
    } catch {
      return { data: getIssueById(id), source: 'mock' };
    }
  },

  async getFeatured() {
    try {
      const { data } = await api.get('/magazine/featured');
      return { data };
    } catch {
      return { data: getFeaturedIssue(), source: 'mock' };
    }
  },

  async getFreeSample() {
    return { data: getFreeSampleIssue(), source: 'mock' };
  },
};

export const magazineAdminApi = {
  listJobs: () =>
    import('./adminApi').then((m) => m.magazine?.listJobs?.() || Promise.resolve({ items: MOCK_WORKFLOW_JOBS })),
  generateIssue: (payload) =>
    import('./adminApi').then((m) => m.magazine?.generateIssue?.(payload)),
  approveIssue: (jobId) =>
    import('./adminApi').then((m) => m.magazine?.approveIssue?.(jobId)),
  publishIssue: (jobId) =>
    import('./adminApi').then((m) => m.magazine?.publishIssue?.(jobId)),
};

export default magazineApi;
