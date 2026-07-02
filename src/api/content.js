import { api } from './client';
import { heroContent as heroSlidesContent, heroSlides as fallbackSlides } from '../data/heroSlides';

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
    subtitleUrl: v.subtitle_url,
    introEndSeconds: v.intro_end_seconds,
    nextVideoId: v.next_video_id,
  };
}

function buildSlide(video) {
  const mapped = mapVideo(video);
  return {
    id: `hero-${mapped.id}`,
    featuredId: mapped.id,
    featuredTitle: mapped.title,
    featuredTagline: mapped.description?.slice(0, 140) || mapped.category,
    title: mapped.title,
    subtitle: mapped.description?.slice(0, 140) || mapped.category,
    sport: mapped.category,
    format: mapped.videoType === 'series' ? 'Series' : 'Documentary',
    heroImage: mapped.heroImage || mapped.image,
    cardImage: mapped.image,
    posterImage: mapped.image,
    fullImage: mapped.heroImage || mapped.image,
    cta: 'Watch Now',
    secondaryCta: 'Explore Originals',
    tagline: mapped.category || 'UNTOLD',
    rating: mapped.rating,
    duration: mapped.duration,
    year: mapped.year,
    eyebrow: 'UNTOLD ORIGINALS',
  };
}

export const contentApi = {
  async getHero() {
    const [featured, trending] = await Promise.all([
      api.videos.list({ featured: true, page_size: 5 }),
      api.videos.list({ trending: true, page_size: 5 }),
    ]);
    const seen = new Set();
    const videos = [];
    for (const v of [...featured.items, ...trending.items]) {
      if (!seen.has(v.id)) {
        seen.add(v.id);
        videos.push(v);
      }
    }
    const slides = videos.length ? videos.map(buildSlide) : fallbackSlides;
    return {
      data: {
        ...heroSlidesContent,
        slides,
      },
    };
  },

  async getFeatured() {
    const { items } = await api.videos.list({ featured: true, page_size: 1 });
    if (!items[0]) throw new Error('No featured video');
    return { data: mapVideo(items[0]) };
  },

  async getDocumentaries() {
    const { items } = await api.videos.list({ video_type: 'documentary', page_size: 50 });
    return { data: items.map(mapVideo) };
  },

  async getOriginals() {
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
    return { data: apiItems };
  },

  async getLegends() {
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

  async getRivalries() {
    const { items } = await api.videos.list({ category: 'rivalries', page_size: 20 });
    return {
      data: items.map((v) => {
        const m = mapVideo(v);
        return { id: m.id, title: m.title, description: m.description, image: m.image, category: m.category, episodes: 1 };
      }),
    };
  },

  async getStories() {
    const { items } = await api.videos.list({ category: 'stories', page_size: 50 });
    return { data: items.map(mapVideo) };
  },

  async getSecrets() {
    const { items } = await api.videos.list({ category: 'secrets', page_size: 50 });
    return { data: items.map(mapVideo) };
  },

  async getTrending() {
    const { items } = await api.videos.list({ trending: true, page_size: 10 });
    return { data: items.map(mapVideo) };
  },

  async getShorts() {
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

  async getDocumentaryById(id) {
    const v = await api.videos.get(id);
    return { data: mapVideo(v) };
  },

  async searchCatalog(q) {
    const { items } = await api.videos.search(q);
    return { data: items.map(mapVideo) };
  },

  async getCatalogByCategory(cat) {
    const { items } = await api.videos.list({ category: cat, page_size: 50 });
    return { data: items.map(mapVideo) };
  },

  async submitContact(formData) {
    const res = await api.contact.submit({
      name: formData.name,
      email: formData.email,
      subject: formData.subject,
      message: formData.message,
    });
    return { data: { success: true, message: res.message } };
  },
};

export default contentApi;
