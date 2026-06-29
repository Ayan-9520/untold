import { api } from './client';
import * as mock from '../data/mockContent';
import { heroContent as heroSlidesContent, heroSlides } from '../data/heroSlides';
import { originalsCatalog } from '../data/originalsCatalog';
import { videoCatalog, getVideoById, getByCategory, searchVideos } from '../data/videoCatalog';
import {
  eventsCatalog,
  getFeaturedEvent,
  getEventsByStatus,
  getEventsBySport,
  searchEvents,
  eventShorts,
  eventStories,
} from '../data/eventsCatalog';

function mapCatalogItem(v) {
  return {
    id: v.id,
    slug: v.slug,
    title: v.title,
    description: v.description,
    category: v.sport || v.categoryName || v.category,
    categorySlug: v.category,
    sport: v.sport,
    format: v.format,
    duration: v.duration,
    year: v.year,
    rating: v.rating,
    image: v.image || v.thumbnail,
    heroImage: v.image || v.thumbnail,
    thumbnail: v.thumbnail || v.image,
    videoUrl: v.trailerUrl,
    trailerUrl: v.trailerUrl,
    featured: v.featured,
    trending: v.trending,
    views: v.views_count,
    videoType: v.videoType,
  };
}

export function mapVideo(v) {
  return {
    id: v.id,
    slug: v.slug,
    title: v.title,
    description: v.description,
    category: v.category?.name || v.category || '',
    categorySlug: v.category?.slug || '',
    duration: v.duration,
    year: v.year,
    rating: v.rating,
    image: v.image_url,
    heroImage: v.hero_image_url || v.image_url,
    videoUrl: v.video_url,
    featured: v.is_featured,
    trending: v.is_trending,
    views: v.views_count,
    videoType: v.video_type,
  };
}

async function withFallback(fn, fallback) {
  try {
    return await fn();
  } catch (err) {
    console.warn('[UNTOLD API] fallback to mock:', err.message);
    return fallback();
  }
}

export const contentApi = {
  getHero: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ featured: true, page_size: 1 });
        const featured = items[0] ? mapVideo(items[0]) : null;
        return {
          data: {
            ...heroSlidesContent,
            slides: heroSlides,
          },
        };
      },
      () => ({ data: heroSlidesContent })
    ),

  getFeatured: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ featured: true, page_size: 1 });
        return { data: items[0] ? mapVideo(items[0]) : mapCatalogItem(videoCatalog.find((v) => v.featured) || videoCatalog[0]) };
      },
      () => ({
        data: mapCatalogItem(videoCatalog.find((v) => v.featured) || videoCatalog[0]) || mock.featuredDocumentary,
      })
    ),

  getDocumentaries: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ video_type: 'documentary', page_size: 50 });
        return { data: items.map(mapVideo) };
      },
      () => ({ data: mock.documentaries })
    ),

  getOriginals: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ page_size: 50 });
        const apiItems = items.map((v) => {
          const m = mapVideo(v);
          return {
            ...m,
            sport: m.category || 'Stories',
            format: m.videoType === 'series' ? 'Series' : 'Documentary',
            image: m.image,
          };
        });
        const slugs = new Set(apiItems.map((i) => i.slug));
        const merged = [
          ...apiItems,
          ...originalsCatalog.filter((c) => !slugs.has(c.id)),
        ];
        return { data: merged };
      },
      () => ({ data: getByCategory('originals').map(mapCatalogItem) })
    ),

  getLegends: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ category: 'legends', page_size: 20 });
        return {
          data: items.map((v) => {
            const m = mapVideo(v);
            return {
              id: m.id,
              title: m.title.split(':').pop()?.trim() || m.title,
              subtitle: m.title,
              description: m.description,
              image: m.image,
              category: m.category,
            };
          }),
        };
      },
      () => ({ data: getByCategory('legends').map((v) => ({
        id: v.id,
        title: v.sport,
        subtitle: v.title,
        description: v.description,
        image: v.image,
        category: v.sport,
      })) })
    ),

  getRivalries: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ category: 'rivalries', page_size: 20 });
        return {
          data: items.map((v) => {
            const m = mapVideo(v);
            return { id: m.id, title: m.title, description: m.description, image: m.image, category: m.category, episodes: 1 };
          }),
        };
      },
      () => ({ data: getByCategory('rivalries').map((v) => ({
        id: v.id,
        title: v.title,
        description: v.description,
        image: v.image,
        category: v.sport,
        episodes: 1,
      })) })
    ),

  getStories: () => ({ data: getByCategory('stories').map(mapCatalogItem) }),

  getSecrets: () => ({ data: getByCategory('secrets').map(mapCatalogItem) }),

  getTrending: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ trending: true, page_size: 10 });
        return { data: items.map(mapVideo) };
      },
      () => ({ data: videoCatalog.filter((v) => v.trending).map(mapCatalogItem) })
    ),

  getShorts: () =>
    withFallback(
      async () => {
        const { items } = await api.videos.list({ video_type: 'short', page_size: 20 });
        return {
          data: items.map((v) => ({
            id: v.id,
            title: v.title,
            duration: v.duration,
            views: `${Math.round((v.views_count || 0) / 1000)}K`,
            image: v.image_url,
            videoUrl: v.video_url,
          })),
        };
      },
      () => ({ data: getByCategory('shorts').map((v) => ({
        id: v.id,
        title: v.title,
        duration: v.duration,
        views: `${Math.round(50 + Math.random() * 200)}K`,
        image: v.image,
        videoUrl: v.trailerUrl,
      })) })
    ),

  getDocumentaryById: (id) =>
    withFallback(
      async () => {
        const v = await api.videos.get(id);
        return { data: mapVideo(v) };
      },
      async () => {
        const doc = getVideoById(id) || mock.documentaries.find((d) => d.id === id || String(d.id) === String(id));
        if (!doc) throw new Error('Not found');
        return { data: doc.slug ? mapCatalogItem(doc) : doc };
      }
    ),

  getCatalog: () => ({ data: videoCatalog.map(mapCatalogItem) }),

  searchCatalog: (q) => ({ data: searchVideos(q).map(mapCatalogItem) }),

  getCatalogByCategory: (cat) => ({ data: getByCategory(cat).map(mapCatalogItem) }),

  getEvents: () => ({ data: eventsCatalog }),

  getFeaturedEvent: () => ({ data: getFeaturedEvent() }),

  getEventsByStatus: (status) => ({ data: getEventsByStatus(status) }),

  getEventsBySport: (sport) => ({ data: getEventsBySport(sport) }),

  searchEvents: (q) => ({ data: searchEvents(q) }),

  getEventShorts: () => ({ data: eventShorts }),

  getEventStories: () => ({ data: eventStories }),

  submitContact: (formData) =>
    withFallback(
      async () => ({ data: { success: true, message: "Thank you for reaching out. We'll be in touch soon." } }),
      async () => ({ data: { success: true, message: "Thank you for reaching out. We'll be in touch soon." } })
    ),
};

export default contentApi;
