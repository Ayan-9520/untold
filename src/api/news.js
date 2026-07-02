import client from './client';

/** Normalize API article to frontend shape */
export function normalizeArticle(item) {
  if (!item) return null;
  return {
    id: item.id,
    slug: item.slug,
    title: item.title,
    excerpt: item.excerpt || item.summary || '',
    sport: item.sport,
    publishedAt: item.published_at || item.publishedAt,
    thumbnail: item.thumbnail_url || item.thumbnail,
    author: item.author || 'UNTOLD Editorial',
    trending: item.is_trending ?? item.trending ?? false,
    breaking: item.is_breaking ?? item.breaking ?? false,
    category: item.news_type || item.category || 'news',
    content: item.rewritten_content || item.content,
    summary: item.summary,
    seoTitle: item.seo_title,
    seoDescription: item.seo_description,
    tags: item.tags || [],
  };
}

function normalizeList(items = []) {
  return items.map(normalizeArticle).filter(Boolean);
}

export const newsApi = {
  async list(params = {}) {
    const { data } = await client.get('/news', { params });
    return { items: normalizeList(data.items), total: data.total, source: 'api' };
  },

  async get(id) {
    const { data } = await client.get(`/news/${id}`);
    return { data: normalizeArticle(data), source: 'api' };
  },

  async trending(limit = 10) {
    const { data } = await client.get('/news/trending', { params: { limit } });
    return { items: normalizeList(data), source: 'api' };
  },

  async bySport(sport, limit = 20) {
    const { data } = await client.get(`/news/category/${encodeURIComponent(sport)}`, { params: { limit } });
    return { items: normalizeList(data), source: 'api' };
  },

  async latest(limit = 10) {
    return newsApi.list({ page: 1, page_size: limit });
  },
};

export default newsApi;
