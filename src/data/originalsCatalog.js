/** Sport-wise catalog — documentaries, biopics & feature films */
import { SPORT_IMAGES } from './sportsImages';

export const ORIGINAL_SPORTS_AVAILABLE = [
  'Cricket',
  'Football',
  'Boxing',
  'Tennis',
  'Swimming',
  'Baseball',
  'Basketball',
  'Formula 1',
  'Olympics',
  'Hockey',
  'Gymnastics',
];

export const ORIGINAL_SPORTS_COMING_SOON = ['Kabaddi', 'MMA'];

export const ORIGINAL_SPORTS = [
  'All',
  ...ORIGINAL_SPORTS_AVAILABLE,
  ...ORIGINAL_SPORTS_COMING_SOON,
];

export const ORIGINAL_FORMATS = ['All', 'Documentary', 'Biopic', 'Feature Film', 'Series'];

export const SPORT_CARD_THEMES = {
  Cricket: {
    image: SPORT_IMAGES.Cricket,
    accent: 'border-l-green-500',
    badge: 'bg-green-600/90',
    gradient: 'from-green-950/90 via-black/60 to-transparent',
  },
  Football: {
    image: SPORT_IMAGES.Football,
    accent: 'border-l-emerald-500',
    badge: 'bg-emerald-600/90',
    gradient: 'from-emerald-950/90 via-black/60 to-transparent',
  },
  Boxing: {
    image: SPORT_IMAGES.Boxing,
    accent: 'border-l-red-600',
    badge: 'bg-red-600/90',
    gradient: 'from-red-950/90 via-black/60 to-transparent',
  },
  Tennis: {
    image: SPORT_IMAGES.Tennis,
    accent: 'border-l-yellow-500',
    badge: 'bg-yellow-600/90',
    gradient: 'from-yellow-950/80 via-black/60 to-transparent',
  },
  Swimming: {
    image: SPORT_IMAGES.Swimming,
    accent: 'border-l-cyan-500',
    badge: 'bg-cyan-600/90',
    gradient: 'from-cyan-950/90 via-black/60 to-transparent',
  },
  Baseball: {
    image: SPORT_IMAGES.Baseball,
    accent: 'border-l-orange-500',
    badge: 'bg-orange-600/90',
    gradient: 'from-orange-950/90 via-black/60 to-transparent',
  },
  Basketball: {
    image: SPORT_IMAGES.Basketball,
    accent: 'border-l-orange-600',
    badge: 'bg-orange-700/90',
    gradient: 'from-orange-950/90 via-black/60 to-transparent',
  },
  'Formula 1': {
    image: SPORT_IMAGES['Formula 1'],
    accent: 'border-l-red-500',
    badge: 'bg-red-600/90',
    gradient: 'from-red-950/90 via-black/70 to-transparent',
  },
  Olympics: {
    image: SPORT_IMAGES.Olympics,
    accent: 'border-l-blue-500',
    badge: 'bg-blue-600/90',
    gradient: 'from-blue-950/90 via-black/70 to-transparent',
  },
  Hockey: {
    image: SPORT_IMAGES.Hockey,
    accent: 'border-l-sky-500',
    badge: 'bg-sky-600/90',
    gradient: 'from-sky-950/90 via-black/70 to-transparent',
  },
  Gymnastics: {
    image: SPORT_IMAGES.Gymnastics,
    accent: 'border-l-pink-500',
    badge: 'bg-pink-600/90',
    gradient: 'from-pink-950/90 via-black/70 to-transparent',
  },
  Kabaddi: {
    image: SPORT_IMAGES.Kabaddi,
    accent: 'border-l-amber-500',
    badge: 'bg-amber-600/90',
    gradient: 'from-amber-950/90 via-black/70 to-transparent',
  },
  MMA: {
    image: SPORT_IMAGES.MMA,
    accent: 'border-l-rose-600',
    badge: 'bg-rose-600/90',
    gradient: 'from-rose-950/90 via-black/70 to-transparent',
  },
};

export const COMING_SOON_PLACEHOLDERS = {
  Kabaddi: [
    { id: 'kab-soon-1', teaser: 'Raid masters & arena legends' },
    { id: 'kab-soon-2', teaser: 'Pro Kabaddi untold stories' },
    { id: 'kab-soon-3', teaser: 'Strength, strategy, and glory' },
  ],
  MMA: [
    { id: 'mma-soon-1', teaser: 'Octagon rivalries & comeback kings' },
    { id: 'mma-soon-2', teaser: 'Fight night documentaries' },
    { id: 'mma-soon-3', teaser: 'Behind the belt — UNTOLD originals' },
  ],
};

export function isComingSoonSport(sport) {
  return ORIGINAL_SPORTS_COMING_SOON.includes(sport);
}

export function filterOriginalsCatalog(items, sport = 'All', format = 'All') {
  const excluded = new Set(['film-83', 'film-escape', 'doc-hoop-dreams', 'doc-dhoni-untold']);
  const available = items.filter(
    (item) => ORIGINAL_SPORTS_AVAILABLE.includes(item.sport) && !excluded.has(item.id)
  );
  return available.filter((item) => {
    const sportMatch = sport === 'All' || item.sport === sport;
    const formatMatch = format === 'All' || item.format === format;
    return sportMatch && formatMatch;
  });
}

export function getOriginalsSportCounts(items = originalsCatalog) {
  const excluded = new Set(['film-83', 'film-escape', 'doc-hoop-dreams', 'doc-dhoni-untold']);
  const available = items.filter(
    (item) => ORIGINAL_SPORTS_AVAILABLE.includes(item.sport) && !excluded.has(item.id)
  );
  const counts = { All: available.length };
  available.forEach((item) => {
    counts[item.sport] = (counts[item.sport] || 0) + 1;
  });
  return counts;
}

export function getCardTitle(item) {
  return item.title;
}

export const originalsCatalog = [
  // Cricket
  {
    id: 'bio-dhoni',
    title: 'M.S. Dhoni: The Untold Story',
    description: 'From ticket collector to World Cup captain — the journey of Captain Cool.',
    sport: 'Cricket',
    format: 'Biopic',
    duration: '3h 4m',
    year: 2016,
    rating: 'U/A',
    image: 'https://images.unsplash.com/photo-1540747913346-19a32ad3b0f2?w=800&q=80&auto=format&fit=crop',
    featured: true,
    trending: true,
  },
  {
    id: 'bio-sachin',
    title: 'Sachin: A Billion Dreams',
    description: 'The God of Cricket — a billion prayers, one relentless dream.',
    sport: 'Cricket',
    format: 'Biopic',
    duration: '2h 20m',
    year: 2017,
    rating: 'U',
    image: 'https://images.unsplash.com/photo-1624526268812-aa279e45b2d7?w=800&q=80&auto=format&fit=crop',
    trending: true,
  },
  {
    id: 'doc-1983',
    title: "UNTOLD: India's 1983",
    description: 'The upset that made a billion believers.',
    sport: 'Cricket',
    format: 'Documentary',
    duration: '1h 28m',
    year: 2023,
    rating: 'TV-PG',
    image: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=800&q=80&auto=format&fit=crop',
  },

  // Football
  {
    id: 'doc-maradona',
    title: 'Diego Maradona',
    description: 'Asif Kapadia’s intimate portrait of genius, chaos, and immortality in Naples.',
    sport: 'Football',
    format: 'Documentary',
    duration: '2h 10m',
    year: 2019,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80&auto=format&fit=crop',
    featured: true,
    trending: true,
  },
  {
    id: 'doc-pele',
    title: 'Pelé',
    description: 'The king of football — from poverty to three World Cups.',
    sport: 'Football',
    format: 'Documentary',
    duration: '1h 48m',
    year: 2021,
    rating: 'TV-PG',
    image: 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=800&q=80&auto=format&fit=crop',
    trending: true,
  },
  {
    id: 'doc-escobars',
    title: 'The Two Escobars',
    description: '30 for 30 — how football and fate collided in Colombia.',
    sport: 'Football',
    format: 'Documentary',
    duration: '1h 44m',
    year: 2010,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=800&q=80&auto=format&fit=crop',
  },
  {
    id: 'doc-messi-ronaldo',
    title: 'UNTOLD: Messi vs Ronaldo',
    description: 'A decade-long rivalry that divided the football world.',
    sport: 'Football',
    format: 'Documentary',
    duration: '1h 35m',
    year: 2024,
    rating: 'TV-PG',
    image: 'https://images.unsplash.com/photo-1529900748604-07564a03e7a6?w=800&q=80&auto=format&fit=crop',
  },

  // Basketball
  {
    id: 'series-last-dance',
    title: 'The Last Dance',
    description: "ESPN's epic on Jordan, the Bulls, and the cost of greatness.",
    sport: 'Basketball',
    format: 'Series',
    duration: '10 episodes',
    year: 2020,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&q=80&auto=format&fit=crop',
    trending: true,
  },
  {
    id: 'doc-malice',
    title: 'UNTOLD: Malice at the Palace',
    description: 'The infamous 2004 NBA brawl that shocked America.',
    sport: 'Basketball',
    format: 'Documentary',
    duration: '1h 8m',
    year: 2021,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1519861537503-4c3a5f1b84c4?w=800&q=80&auto=format&fit=crop',
  },
  {
    id: 'film-air',
    title: 'Air',
    description: 'How Nike signed Michael Jordan and changed sports forever.',
    sport: 'Basketball',
    format: 'Feature Film',
    duration: '1h 51m',
    year: 2023,
    rating: 'R',
    image: 'https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?w=800&q=80&auto=format&fit=crop',
  },

  // Tennis
  {
    id: 'doc-borg-mcenroe',
    title: 'Borg vs McEnroe',
    description: 'Fire and ice — Wimbledon 1980 and a rivalry for the ages.',
    sport: 'Tennis',
    format: 'Feature Film',
    duration: '1h 40m',
    year: 2017,
    rating: 'R',
    image: 'https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=800&q=80&auto=format&fit=crop',
  },
  {
    id: 'doc-breaking-point',
    title: 'UNTOLD: Breaking Point',
    description: "Mardy Fish and the battle no one saw at the US Open.",
    sport: 'Tennis',
    format: 'Documentary',
    duration: '1h 9m',
    year: 2021,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1595435934249-2067dca82767?w=800&q=80&auto=format&fit=crop',
  },
  {
    id: 'doc-venus-serena',
    title: 'Venus and Serena',
    description: 'Sisters who changed tennis — and each other.',
    sport: 'Tennis',
    format: 'Documentary',
    duration: '1h 39m',
    year: 2012,
    rating: 'PG-13',
    image: 'https://images.unsplash.com/photo-1622163642999-6c563c436f62?w=800&q=80&auto=format&fit=crop',
  },

  // Boxing
  {
    id: 'doc-ali',
    title: 'When We Were Kings',
    description: 'Ali vs Foreman — the Rumble in the Jungle, Kinshasa 1974.',
    sport: 'Boxing',
    format: 'Documentary',
    duration: '1h 29m',
    year: 1996,
    rating: 'PG',
    image: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=800&q=80&auto=format&fit=crop',
    trending: true,
  },
  {
    id: 'film-creed',
    title: 'Creed',
    description: "Adonis Johnson steps out of Apollo's shadow — and into the ring.",
    sport: 'Boxing',
    format: 'Feature Film',
    duration: '2h 13m',
    year: 2015,
    rating: 'PG-13',
    image: 'https://images.unsplash.com/photo-1471189641895-2c585a68bc2c?w=800&q=80&auto=format&fit=crop',
  },
  {
    id: 'doc-untold-devil',
    title: 'UNTOLD: Deal with the Devil',
    description: 'Christy Martin — triumph and tragedy in the ring.',
    sport: 'Boxing',
    format: 'Documentary',
    duration: '1h 17m',
    year: 2021,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1599043513900-ed6fe01d3663?w=800&q=80&auto=format&fit=crop',
  },

  // Gymnastics
  {
    id: 'film-i-tonya',
    title: 'I, Tonya',
    description: 'Tonya Harding, Nancy Kerrigan, and the scandal that shook the Olympics.',
    sport: 'Gymnastics',
    format: 'Feature Film',
    duration: '2h',
    year: 2017,
    rating: 'R',
    image: 'https://images.unsplash.com/photo-1517649763962-0c62306601b7?w=800&q=80',
    trending: true,
  },
  {
    id: 'doc-athlete-a',
    title: 'Athlete A',
    description: 'The gymnasts who took down Larry Nassar and USA Gymnastics.',
    sport: 'Gymnastics',
    format: 'Documentary',
    duration: '1h 43m',
    year: 2020,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80',
  },
  {
    id: 'doc-simone',
    title: 'Simone Biles Rising',
    description: 'Pressure, perfection, and the GOAT who chose herself.',
    sport: 'Gymnastics',
    format: 'Documentary',
    duration: '1h 52m',
    year: 2024,
    rating: 'TV-PG',
    image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80',
  },

  // Baseball
  {
    id: 'film-moneyball',
    title: 'Moneyball',
    description: 'How the Oakland A\'s changed baseball with data and daring.',
    sport: 'Baseball',
    format: 'Feature Film',
    duration: '2h 13m',
    year: 2011,
    rating: 'PG-13',
    image: 'https://images.unsplash.com/photo-1566577739090-0d1bf7750eed?w=800&q=80&auto=format&fit=crop',
    trending: true,
  },
  {
    id: 'film-42',
    title: '42',
    description: 'Jackie Robinson breaks the color barrier in Major League Baseball.',
    sport: 'Baseball',
    format: 'Feature Film',
    duration: '2h 8m',
    year: 2013,
    rating: 'PG-13',
    image: 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&q=80&auto=format&fit=crop',
  },
  {
    id: 'doc-battered-bastards',
    title: 'The Battered Bastards of Baseball',
    description: 'An independent minor-league team that became a cult legend.',
    sport: 'Baseball',
    format: 'Documentary',
    duration: '1h 13m',
    year: 2014,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1518604666860-9ce0a3b76be0?w=800&q=80&auto=format&fit=crop',
  },

  // Hockey
  {
    id: 'doc-miracle',
    title: 'Miracle',
    description: 'USA vs USSR — the 1980 Olympic hockey upset that stunned the world.',
    sport: 'Hockey',
    format: 'Feature Film',
    duration: '2h 15m',
    year: 2004,
    rating: 'PG',
    image: 'https://images.unsplash.com/photo-1515703407324-5f753afd8be8?w=800&q=80',
  },
  {
    id: 'doc-crime-penalty',
    title: 'UNTOLD: Crime & Penalty',
    description: 'How a gambling ring nearly destroyed an NHL franchise.',
    sport: 'Hockey',
    format: 'Documentary',
    duration: '1h 15m',
    year: 2021,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1515703407324-5f753afd8be8?w=800&q=80',
  },

  // Swimming
  {
    id: 'doc-phelps',
    title: 'The Weight of Gold',
    description: 'Olympic athletes and the mental health crisis behind the medals.',
    sport: 'Swimming',
    format: 'Documentary',
    duration: '1h',
    year: 2020,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&q=80&auto=format&fit=crop',
  },

  // Formula 1
  {
    id: 'doc-senna',
    title: 'Senna',
    description: 'Ayrton Senna — speed, faith, and the deadliest rivalry in F1.',
    sport: 'Formula 1',
    format: 'Documentary',
    duration: '1h 46m',
    year: 2010,
    rating: 'PG-13',
    image: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80',
    trending: true,
  },
  {
    id: 'film-rush',
    title: 'Rush',
    description: 'Hunt vs Lauda — glory and horror at 200 mph.',
    sport: 'Formula 1',
    format: 'Feature Film',
    duration: '2h 3m',
    year: 2013,
    rating: 'R',
    image: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80',
  },
  {
    id: 'series-drive-survive',
    title: 'Formula 1: Drive to Survive',
    description: 'Behind the visor — teams, egos, and championship pressure.',
    sport: 'Formula 1',
    format: 'Series',
    duration: 'Multi-season',
    year: 2019,
    rating: 'TV-MA',
    image: 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80',
  },

  // Olympics
  {
    id: 'doc-olympic-dreams',
    title: 'Olympic Dreams',
    description: 'Three athletes, one village — the human side of the Games.',
    sport: 'Olympics',
    format: 'Documentary',
    duration: '1h 37m',
    year: 2019,
    rating: 'TV-PG',
    image: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=800&q=80',
  },
  {
    id: 'doc-munich',
    title: 'One Day in September',
    description: 'Munich 1972 — tragedy at the Olympic Games.',
    sport: 'Olympics',
    format: 'Documentary',
    duration: '1h 34m',
    year: 1999,
    rating: 'R',
    image: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=800&q=80',
  },
];
