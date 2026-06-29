import client from './client';
import {
  newsCatalog,
  getLatestNews,
  getTrendingNews,
  getNewsBySport,
  searchNews,
} from '../data/newsCatalog';

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
    try {
      const { data } = await client.get('/news', { params });
      return { items: normalizeList(data.items), total: data.total, source: 'api' };
    } catch {
      let items = newsCatalog;
      if (params.sport) items = getNewsBySport(params.sport);
      if (params.search) items = searchNews(params.search);
      if (params.trending) items = items.filter((n) => n.trending);
      if (params.breaking) items = items.filter((n) => n.breaking);
      return { items, total: items.length, source: 'mock' };
    }
  },

  async get(id) {
    try {
      const { data } = await client.get(`/news/${id}`);
      return { data: normalizeArticle(data), source: 'api' };
    } catch {
      const found = newsCatalog.find((n) => String(n.id) === String(id));
      return { data: found || null, source: 'mock' };
    }
  },

  async trending(limit = 10) {
    try {
      const { data } = await client.get('/news/trending', { params: { limit } });
      return { items: normalizeList(data), source: 'api' };
    } catch {
      return { items: getTrendingNews(limit), source: 'mock' };
    }
  },

  async bySport(sport, limit = 20) {
    try {
      const { data } = await client.get(`/news/category/${encodeURIComponent(sport)}`, { params: { limit } });
      return { items: normalizeList(data), source: 'api' };
    } catch {
      return { items: getNewsBySport(sport).slice(0, limit), source: 'mock' };
    }
  },

  async latest(limit = 10) {
    const result = await newsApi.list({ page: 1, page_size: limit });
    if (result.source === 'mock') {
      return { items: getLatestNews(limit), source: 'mock' };
    }
    return result;
  },
};

export default newsApi;
