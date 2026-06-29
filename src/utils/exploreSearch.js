import { searchVideos, videoCatalog } from '../data/videoCatalog';
import { searchEvents } from '../data/eventsCatalog';
import { searchNews } from '../data/newsCatalog';

/**
 * Unified platform search — videos, events, news, athletes
 */
export function exploreSearch(query) {
  const q = query.trim().toLowerCase();
  if (!q) return { videos: [], events: [], news: [], athletes: [] };

  const videos = searchVideos(q);
  const events = searchEvents(q);
  const news = searchNews(q);

  const athletes = videoCatalog
    .filter((v) => v.category === 'legends' && (
      v.title.toLowerCase().includes(q) ||
      v.sport?.toLowerCase().includes(q)
    ))
    .map((v) => ({ id: v.id, name: v.title, sport: v.sport, image: v.image }));

  return { videos, events, news, athletes };
}

export function filterVideosBySport(videos, sport) {
  if (!sport || sport === 'All') return videos;
  if (sport === 'MMA' || sport === 'Boxing') {
    return videos.filter((v) => v.sport === sport);
  }
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
