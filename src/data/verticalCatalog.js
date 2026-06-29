/**
 * UNTOLD ORIGINALS — vertical taxonomy & premium documentary catalog
 */
import { getSampleVideoUrl } from './sampleVideos';
import { sportImage } from './sportsImages';

export const VERTICALS = [
  { id: 'sports', label: 'Sports Legends', explore: '?vertical=sports' },
  { id: 'football', label: 'Football', explore: '?sport=Football' },
  { id: 'cricket', label: 'Cricket', explore: '?sport=Cricket' },
  { id: 'formula-1', label: 'Formula 1', explore: '?sport=Formula%201' },
  { id: 'olympics', label: 'Olympics', explore: '?sport=Olympics' },
  { id: 'ufc', label: 'UFC & Combat', explore: '?vertical=ufc' },
  { id: 'basketball', label: 'Basketball', explore: '?sport=Basketball' },
  { id: 'business', label: 'Business & Startups', explore: '?vertical=business' },
  { id: 'hollywood', label: 'Hollywood', explore: '?vertical=hollywood' },
  { id: 'bollywood', label: 'Bollywood', explore: '?vertical=bollywood' },
  { id: 'music', label: 'Music Legends', explore: '?vertical=music' },
  { id: 'influencers', label: 'Influencers & Creators', explore: '?vertical=influencers' },
  { id: 'science', label: 'Science & Space', explore: '?vertical=science' },
  { id: 'technology', label: 'Technology & AI', explore: '?vertical=technology' },
  { id: 'politics', label: 'Politics & Leaders', explore: '?vertical=politics' },
  { id: 'history', label: 'History & Wars', explore: '?vertical=history' },
  { id: 'crime', label: 'Crime & Mystery', explore: '?vertical=crime' },
  { id: 'luxury', label: 'Luxury & Brands', explore: '?vertical=luxury' },
];

const IMG = {
  business: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=85',
  hollywood: 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&q=85',
  bollywood: 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800&q=85',
  music: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=85',
  influencers: 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800&q=85',
  science: 'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=85',
  technology: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=85',
  politics: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=85',
  history: 'https://images.unsplash.com/photo-1461360370896-922624d12a74?w=800&q=85',
  crime: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=85',
  luxury: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=85',
  ufc: sportImage('MMA'),
};

function doc(id, title, description, vertical, opts = {}) {
  const streamUrl = getSampleVideoUrl(id);
  return {
    id,
    slug: id,
    title,
    description,
    category: opts.category || 'originals',
    categoryName: 'Originals',
    vertical,
    sport: opts.sport || vertical,
    format: opts.format || 'Documentary',
    pillar: opts.pillar || 'Stories',
    duration: opts.duration || '1h 12m',
    year: opts.year || 2025,
    rating: opts.rating || 'TV-14',
    language: opts.language || 'English',
    quality: opts.quality || '4K',
    genres: opts.genres || [vertical],
    thumbnail: opts.image || IMG[vertical] || sportImage('Football'),
    image: opts.image || IMG[vertical] || sportImage('Football'),
    featured: !!opts.featured,
    trending: !!opts.trending,
    awardWinning: !!opts.awardWinning,
    editorsChoice: !!opts.editorsChoice,
    upcoming: !!opts.upcoming,
    videoType: opts.videoType || 'documentary',
    accessTier: opts.accessTier || 'premium',
    trailerUrl: streamUrl,
    videoUrl: streamUrl,
  };
}

export const verticalCatalog = [
  // Business & entrepreneurs
  doc('vo-tesla', 'UNTOLD: Elon Musk — Mars or Bust', 'From PayPal to SpaceX — the relentless architect of the future.', 'business', { format: 'Biopic', featured: true, trending: true, genres: ['Entrepreneurs', 'Technology', 'Space'] }),
  doc('vo-jobs', 'UNTOLD: Steve Jobs — Think Different', 'The visionary who rewrote computing, music, and culture.', 'business', { format: 'Biopic', awardWinning: true }),
  doc('vo-amazon', 'UNTOLD: The Everything Store', 'How Jeff Bezos built the empire that changed retail forever.', 'business', { format: 'Documentary', genres: ['Companies', 'Startups'] }),
  doc('vo-zerotoone', 'UNTOLD: Startup Nation', 'Founders, failures, and billion-dollar pivots in Silicon Valley.', 'business', { format: 'Series', genres: ['Startups', 'Case Studies'] }),

  // Hollywood & Bollywood
  doc('vo-nolan', 'UNTOLD: Christopher Nolan — Time & Obsession', 'Inside the mind of cinema\'s most ambitious storyteller.', 'hollywood', { format: 'Biopic', trending: true, editorsChoice: true }),
  doc('vo-streep', 'UNTOLD: Meryl Streep — The Standard', 'Eight decades of excellence on screen.', 'hollywood', { format: 'Documentary' }),
  doc('vo-khan', 'UNTOLD: Shah Rukh Khan — King of Bollywood', 'From Delhi stages to global icon.', 'bollywood', { format: 'Biopic', featured: true, trending: true }),
  doc('vo-amitabh', 'UNTOLD: Amitabh Bachchan — The Angry Young Man', 'The voice of a generation and the face of Indian cinema.', 'bollywood', { format: 'Biopic' }),

  // Music & creators
  doc('vo-taylor', 'UNTOLD: Taylor Swift — The Eras', 'Songwriter, strategist, and cultural phenomenon.', 'music', { format: 'Biopic', trending: true }),
  doc('vo-beatles', 'UNTOLD: The Beatles — Four Lads Who Shook the World', 'Liverpool to legend — the untold studio years.', 'music', { format: 'Documentary', awardWinning: true }),
  doc('vo-mrbeast', 'UNTOLD: MrBeast — Billion Dollar Clicks', 'YouTube\'s biggest creator and the business behind the stunts.', 'influencers', { format: 'Documentary', genres: ['YouTubers', 'Entrepreneurs'] }),
  doc('vo-creator', 'UNTOLD: The Creator Economy', 'How influencers built media empires without studios.', 'influencers', { format: 'Series' }),

  // Science, tech, AI, space
  doc('vo-hawking', 'UNTOLD: Stephen Hawking — A Brief History of Courage', 'Mind over matter — cosmology\'s greatest voice.', 'science', { format: 'Biopic', editorsChoice: true }),
  doc('vo-apollo', 'UNTOLD: Apollo — Race to the Moon', 'Engineers, astronauts, and the cost of glory.', 'science', { format: 'Documentary', genres: ['Space', 'History'], quality: '4K' }),
  doc('vo-ai-rise', 'UNTOLD: The AI Revolution', 'From labs to everyday life — who controls the future?', 'technology', { format: 'Documentary', trending: true, genres: ['AI', 'Technology'] }),
  doc('vo-openai', 'UNTOLD: OpenAI — The Partnership That Changed Everything', 'Sam Altman, breakthroughs, and the race for AGI.', 'technology', { format: 'Documentary', genres: ['AI', 'Companies'] }),

  // Politics, history, wars
  doc('vo-mandela', 'UNTOLD: Mandela — Long Walk to Freedom', 'Prison, president, and the power of reconciliation.', 'politics', { format: 'Biopic', awardWinning: true }),
  doc('vo-churchill', 'UNTOLD: Churchill — Darkest Hour', 'Wartime leadership when the world stood on the edge.', 'history', { format: 'Documentary', genres: ['Wars', 'Leaders'] }),
  doc('vo-dday', 'UNTOLD: D-Day — The Untold Hours', 'Soldiers, strategists, and sacrifice on June 6.', 'history', { format: 'Documentary', genres: ['Military', 'Wars'] }),

  // Crime & mystery
  doc('vo-theranos', 'UNTOLD: Theranos — Bad Blood', 'Silicon Valley\'s most infamous fraud.', 'crime', { format: 'Documentary', trending: true, genres: ['Business', 'Mystery'] }),
  doc('vo-zodiac', 'UNTOLD: Unsolved — The Zodiac Files', 'Investigative deep-dive into America\'s coldest case.', 'crime', { format: 'Series', genres: ['Mystery', 'Crime'] }),

  // Luxury & brands
  doc('vo-lvmh', 'UNTOLD: LVMH — Empire of Desire', 'Bernard Arnault and the architecture of luxury.', 'luxury', { format: 'Documentary', genres: ['Luxury Brands', 'Billionaires'] }),
  doc('vo-ferrari', 'UNTOLD: Ferrari — Red Machine', 'Enzo\'s dream, racing glory, and the ultimate brand.', 'luxury', { format: 'Biopic', sport: 'Formula 1' }),

  // UFC (combat vertical)
  doc('vo-mcgregor', 'UNTOLD: McGregor — Notorious', 'Dublin pubs to global pay-per-view king.', 'ufc', { format: 'Biopic', sport: 'MMA', trending: true }),
  doc('vo-khabib', 'UNTOLD: Khabib — Eagle\'s Flight', 'Undefeated — family, faith, and the octagon.', 'ufc', { format: 'Documentary', sport: 'MMA' }),
];

export function getByVertical(verticalId, limit = 12) {
  if (verticalId === 'sports') {
    return verticalCatalog.filter((v) =>
      ['football', 'cricket', 'formula-1', 'olympics', 'basketball', 'ufc'].includes(v.vertical)
        || v.sport
    ).slice(0, limit);
  }
  return verticalCatalog.filter((v) => v.vertical === verticalId).slice(0, limit);
}

export function getAwardWinning(limit = 8) {
  return verticalCatalog.filter((v) => v.awardWinning).slice(0, limit);
}

export function getEditorsChoice(limit = 8) {
  return verticalCatalog.filter((v) => v.editorsChoice).slice(0, limit);
}

export function getLatestReleases(limit = 10) {
  return [...verticalCatalog].sort((a, b) => b.year - a.year).slice(0, limit);
}

export function getUpcoming(limit = 6) {
  return verticalCatalog.filter((v) => v.upcoming).slice(0, limit);
}

export function getVerticalById(id) {
  return VERTICALS.find((v) => v.id === id);
}
