import { searchVideos, videoCatalog } from '../data/videoCatalog';
import { searchEvents } from '../data/eventsCatalog';
import { searchNews } from '../data/newsCatalog';
import { VERTICALS } from '../data/verticalCatalog';

/**
 * Unified platform search — videos, events, news, people, verticals, topics
 */
export function exploreSearch(query) {
  const q = query.trim().toLowerCase();
  if (!q) return { videos: [], events: [], news: [], athletes: [], verticals: [], topics: [], companies: [] };

  const videos = searchVideos(q);
  const events = searchEvents(q);
  const news = searchNews(q);

  const athletes = videoCatalog
    .filter((v) =>
      v.category === 'legends' &&
      (v.title.toLowerCase().includes(q) || v.sport?.toLowerCase().includes(q))
    )
    .slice(0, 6)
    .map((v) => ({ id: v.id, name: v.title, sport: v.sport, image: v.image, type: 'person' }));

  const verticals = VERTICALS.filter(
    (v) => v.label.toLowerCase().includes(q) || v.id.includes(q)
  ).map((v) => ({ id: v.id, name: v.label, explore: v.explore, type: 'vertical' }));

  const topics = [...new Set(
    videoCatalog.flatMap((v) => v.genres || []).filter((g) => g.toLowerCase().includes(q))
  )].slice(0, 6).map((name) => ({ id: name, name, type: 'topic' }));

  const companies = videoCatalog
    .filter((v) =>
      v.vertical === 'business' ||
      v.title.toLowerCase().includes('amazon') ||
      v.title.toLowerCase().includes('tesla') ||
      v.title.toLowerCase().includes('openai') ||
      v.title.toLowerCase().includes('lvmh')
    )
    .filter((v) => v.title.toLowerCase().includes(q) || v.description?.toLowerCase().includes(q))
    .slice(0, 5)
    .map((v) => ({ id: v.id, name: v.title.replace(/^UNTOLD:\s*/i, ''), image: v.image, type: 'company' }));

  return { videos, events, news, athletes, verticals, topics, companies };
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
        const score = (v) => (v.trending ? 2 : 0) + (v.featured ? 1 : 0);
        return score(b) - score(a) || (b.year || 0) - (a.year || 0);
      });
  }
}

export function getRecommendedVideos(limit = 8) {
  const trending = videoCatalog.filter((v) => v.trending);
  const pool = trending.length >= limit ? trending : videoCatalog;
  return pool.slice(0, limit);
}

export function getTrendingVideos(limit = 8) {
  return videoCatalog.filter((v) => v.trending || v.featured).slice(0, limit);
}

export function globalSearch(query, limits = {}) {
  const { videos = 6, events = 3, news = 3, people = 4, verticals = 4, topics = 4, companies = 3 } = limits;
  const all = exploreSearch(query);
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
