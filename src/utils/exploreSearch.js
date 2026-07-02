import { api } from '../api/client';
import newsApi, { normalizeArticle } from '../api/news';
import { fetchEventsOverview } from '../api/events';
import { VERTICALS } from '../data/verticalCatalog';

function mapApiVideo(v) {
  return {
    id: v.id,
    slug: v.slug,
    title: v.title,
    description: v.description,
    sport: v.category?.name || v.sport,
    category: v.category?.slug || v.category,
    categoryName: v.category?.name,
    vertical: v.vertical,
    format: v.video_type,
    duration: v.duration,
    year: v.year,
    rating: v.rating,
    image: v.image_url,
    thumbnail: v.image_url,
    trailerUrl: v.video_url,
    featured: v.is_featured,
    trending: v.is_trending,
    views: v.views_count,
    genres: v.genres || [],
  };
}

export async function fetchVideoCatalog(params = {}) {
  const { items } = await api.videos.list({ page_size: 100, ...params });
  return items.map(mapApiVideo);
}

export async function exploreSearchAsync(query) {
  const q = query.trim();
  if (!q) {
    return { videos: [], events: [], news: [], athletes: [], verticals: [], topics: [], companies: [] };
  }

  const [videoRes, newsRes, eventsRes] = await Promise.all([
    api.videos.search(q).catch(() => ({ items: [] })),
    newsApi.list({ search: q, page_size: 10 }).catch(() => ({ items: [] })),
    fetchEventsOverview({ search: q }).catch(() => ({ items: [] })),
  ]);

  const videos = (videoRes.items || []).map(mapApiVideo);
  const news = (newsRes.items || []).map(normalizeArticle);
  const events = (eventsRes.items || []).map((e) => ({
    id: e.id,
    title: e.title,
    sport: e.sport,
    status: e.status,
    type: 'event',
  }));

  const verticals = VERTICALS.filter(
    (v) => v.label.toLowerCase().includes(q.toLowerCase()) || v.id.includes(q.toLowerCase())
  ).map((v) => ({ id: v.id, name: v.label, explore: v.explore, type: 'vertical' }));

  const topics = [...new Set(
    videos.flatMap((v) => v.genres || []).filter((g) => g.toLowerCase().includes(q.toLowerCase()))
  )].slice(0, 6).map((name) => ({ id: name, name, type: 'topic' }));

  const athletes = videos
    .filter((v) => v.category === 'legends')
    .slice(0, 6)
    .map((v) => ({ id: v.id, name: v.title, sport: v.sport, image: v.image, type: 'person' }));

  return { videos, events, news, athletes, verticals, topics, companies: [] };
}

export function filterVideosBySport(videos, sport) {
  if (!sport || sport === 'All') return videos;
  return videos.filter((v) => v.sport === sport);
}

export function sortVideos(videos, sortBy) {
  const list = [...videos];
  switch (sortBy) {
    case 'latest':
      return list.sort((a, b) => (b.year || 0) - (a.year || 0));
    case 'title':
      return list.sort((a, b) => a.title.localeCompare(b.title));
    case 'popular':
    default:
      return list.sort((a, b) => {
        const score = (v) => (v.trending ? 2 : 0) + (v.featured ? 1 : 0) + (v.views || 0) / 10000;
        return score(b) - score(a) || (b.year || 0) - (a.year || 0);
      });
  }
}

export function getRecommendedVideos(catalog, limit = 8) {
  const trending = catalog.filter((v) => v.trending);
  const pool = trending.length >= limit ? trending : catalog;
  return pool.slice(0, limit);
}

export function getTrendingVideos(catalog, limit = 8) {
  return catalog.filter((v) => v.trending || v.featured).slice(0, limit);
}

export async function globalSearch(query, limits = {}) {
  const { videos = 6, events = 3, news = 3, people = 4, verticals = 4, topics = 4, companies = 3 } = limits;
  const all = await exploreSearchAsync(query);
  return {
    videos: all.videos.slice(0, videos),
    events: all.events.slice(0, events),
    news: all.news.slice(0, news),
    people: all.athletes.slice(0, people),
    verticals: all.verticals.slice(0, verticals),
    topics: all.topics.slice(0, topics),
    companies: all.companies.slice(0, companies),
  };
}
