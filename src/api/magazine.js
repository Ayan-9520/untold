import client from './client';

const DEFAULT_COVER = 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=1200&q=80';

export function normalizeIssue(issue) {
  if (!issue) return null;
  return {
    ...issue,
    id: issue.id || issue.issue_slug,
    coverImage: issue.coverImage || issue.cover_image_url || DEFAULT_COVER,
    pageCount: issue.pageCount ?? issue.page_count ?? 48,
    sections: issue.sections || [],
    sample: issue.sample ?? issue.access === 'free',
  };
}

export const magazineApi = {
  async listIssues() {
    const { data } = await client.get('/magazine/issues');
    const items = (data.items || data).map(normalizeIssue);
    return { data: items };
  },

  async getIssue(id) {
    const { data } = await client.get(`/magazine/issues/${id}`);
    return { data: normalizeIssue(data) };
  },

  async getFeatured() {
    const { data } = await client.get('/magazine/featured');
    return { data: normalizeIssue(data) };
  },

  async getFreeSample() {
    const { data } = await client.get('/magazine/free-sample');
    return { data: normalizeIssue(data) };
  },
};

export default magazineApi;
