/**
 * Curated UNTOLD catalog — global sports storytelling (API-ready)
 */
import { originalsCatalog } from './originalsCatalog';
import { verticalCatalog } from './verticalCatalog';
import { getSampleVideoUrl } from './sampleVideos';
import { sportImage } from './sportsImages';

export const CATEGORIES = [
  { slug: 'originals', name: 'Originals', description: 'Premium flagship documentaries & sports films' },
  { slug: 'shorts', name: 'Shorts', description: 'Reels and bite-sized moments' },
  { slug: 'legends', name: 'Legends', description: 'Athlete legacy storytelling' },
  { slug: 'rivalries', name: 'Rivalries', description: 'Greatest feuds in sports history' },
  { slug: 'stories', name: 'Stories', description: 'Emotional & inspirational narratives' },
  { slug: 'secrets', name: 'Secrets', description: 'Behind-the-scenes untold truths' },
];

const IMG = {
  get Cricket() { return sportImage('Cricket'); },
  get Football() { return sportImage('Football'); },
  get Basketball() { return sportImage('Basketball'); },
  get Tennis() { return sportImage('Tennis'); },
  get Boxing() { return sportImage('Boxing'); },
  get MMA() { return sportImage('MMA'); },
  get 'Formula 1'() { return sportImage('Formula 1'); },
  get Olympics() { return sportImage('Olympics'); },
  get Kabaddi() { return sportImage('Kabaddi'); },
  get Wrestling() { return sportImage('Wrestling'); },
  get Hockey() { return sportImage('Hockey'); },
};

function entry(id, title, description, category, sport, duration, year, rating, opts = {}) {
  const cat = CATEGORIES.find((c) => c.slug === category);
  const streamUrl = opts.videoUrl ?? opts.trailerUrl ?? getSampleVideoUrl(id);
  return {
    id,
    slug: id,
    title,
    description,
    category,
    categoryName: cat?.name || category,
    sport,
    pillar: opts.pillar || cat?.name || category,
    format: opts.format || (category === 'shorts' ? 'Short' : 'Documentary'),
    duration,
    year,
    rating,
    thumbnail: IMG[sport] || IMG.Football,
    image: IMG[sport] || IMG.Football,
    featured: !!opts.featured,
    trending: !!opts.trending,
    videoType: category === 'shorts' ? 'short' : 'documentary',
    accessTier: opts.accessTier || 'free',
    trailerUrl: streamUrl,
    videoUrl: streamUrl,
  };
}

const CURATED = [
  entry('orig-revolution', 'UNTOLD: The Revolution', 'The movement that reshaped modern sport.', 'originals', 'Football', '1h 32m', 2024, 'TV-MA', { trending: true, format: 'Documentary', pillar: 'Stories' }),
  entry('orig-dhoni', 'UNTOLD: Rise of Dhoni', 'From Ranchi to World Cup glory.', 'originals', 'Cricket', '1h 28m', 2024, 'TV-PG', { format: 'Biopic', pillar: 'Legends' }),
  entry('orig-messi-ronaldo', 'UNTOLD: Messi vs Ronaldo', 'A rivalry that divided football.', 'originals', 'Football', '1h 35m', 2023, 'TV-PG', { featured: true, trending: true, format: 'Documentary', pillar: 'Rivalries' }),
  entry('orig-last-dance', 'UNTOLD: The Last Dance', 'Inside the Bulls dynasty.', 'originals', 'Basketball', '1h 45m', 2020, 'TV-MA'),
  entry('orig-1983', 'UNTOLD: 1983 World Cup', "India's impossible triumph.", 'originals', 'Cricket', '1h 30m', 2023, 'TV-PG'),
  entry('orig-senna', 'UNTOLD: Senna Legacy', 'Speed, faith, and immortality.', 'originals', 'Formula 1', '1h 46m', 2022, 'TV-MA'),
  entry('orig-locker', 'UNTOLD: Locker Room', 'When the cameras stop rolling.', 'originals', 'Football', '52m', 2024, 'TV-MA'),
  entry('orig-investigation', 'UNTOLD: The Investigation', 'Scandals exposed.', 'originals', 'Football', '1h 20m', 2023, 'TV-MA'),
  entry('short-goals', 'Greatest Goals', 'Strikes that shook stadiums.', 'shorts', 'Football', '0:58', 2024, 'TV-PG', { trending: true }),
  entry('short-knockouts', 'Best Knockouts', 'Combat\'s most brutal finishes.', 'shorts', 'Boxing', '0:47', 2024, 'TV-PG'),
  entry('short-finish', 'Fastest Finishes', 'Blink and you miss history.', 'shorts', 'MMA', '0:42', 2024, 'TV-PG'),
  entry('short-goat', 'GOAT Moments', 'Generational plays in 90 seconds.', 'shorts', 'Basketball', '1:30', 2024, 'TV-PG'),
  entry('short-emotional', 'Emotional Wins', 'Tears, triumph, and roar.', 'shorts', 'Cricket', '1:12', 2024, 'TV-PG'),
  entry('short-six', 'Six Heard Around the World', 'One shot united a billion.', 'shorts', 'Cricket', '0:55', 2024, 'TV-PG'),
  entry('short-f1', 'Overtake of the Century', 'Wheel-to-wheel at 300 km/h.', 'shorts', 'Formula 1', '0:38', 2024, 'TV-PG'),
  entry('short-olympics', 'Gold in the Final Stride', 'Olympic glory in the last metre.', 'shorts', 'Olympics', '1:05', 2024, 'TV-PG'),
  entry('short-kabaddi', 'Kabaddi Raid Masterclass', 'Strength and audacity.', 'shorts', 'Kabaddi', '0:52', 2024, 'TV-PG'),
  entry('short-wrestling', 'Pin in 12 Seconds', 'Explosive takedowns.', 'shorts', 'Wrestling', '0:48', 2024, 'TV-PG'),
  entry('leg-kapil', 'Kapil Dev', 'The Haryana Hurricane — 1983 and beyond.', 'legends', 'Cricket', '1h 15m', 2023, 'TV-PG'),
  entry('leg-sachin', 'Sachin Tendulkar', 'A billion dreams.', 'legends', 'Cricket', '2h 20m', 2017, 'U', { trending: true }),
  entry('leg-dhoni', 'MS Dhoni', 'Captain Cool.', 'legends', 'Cricket', '1h 32m', 2024, 'TV-PG', { trending: true }),
  entry('leg-kohli', 'Virat Kohli', 'Aggression and dominance.', 'legends', 'Cricket', '1h 10m', 2024, 'TV-PG'),
  entry('leg-lara', 'Brian Lara', '400 not out.', 'legends', 'Cricket', '1h 8m', 2022, 'TV-PG'),
  entry('leg-pele', 'Pelé', 'The king of football.', 'legends', 'Football', '1h 48m', 2021, 'TV-PG'),
  entry('leg-maradona', 'Diego Maradona', 'Genius and immortality.', 'legends', 'Football', '2h 10m', 2019, 'TV-MA', { trending: true }),
  entry('leg-messi', 'Lionel Messi', 'Records and redemption.', 'legends', 'Football', '1h 25m', 2023, 'TV-PG'),
  entry('leg-ronaldo', 'Cristiano Ronaldo', 'The machine that refused to stop.', 'legends', 'Football', '1h 22m', 2023, 'TV-PG'),
  entry('leg-cruyff', 'Johan Cruyff', 'Total Football.', 'legends', 'Football', '1h 18m', 2020, 'TV-PG'),
  entry('leg-federer', 'Roger Federer', 'Grace under pressure.', 'legends', 'Tennis', '1h 30m', 2023, 'TV-PG'),
  entry('leg-nadal', 'Rafael Nadal', 'King of Clay.', 'legends', 'Tennis', '1h 28m', 2023, 'TV-PG'),
  entry('leg-djokovic', 'Novak Djokovic', 'The mental fortress.', 'legends', 'Tennis', '1h 26m', 2024, 'TV-PG'),
  entry('leg-jordan', 'Michael Jordan', 'His Airness — six rings.', 'legends', 'Basketball', '1h 45m', 2020, 'TV-MA', { trending: true }),
  entry('leg-kobe', 'Kobe Bryant', 'Mamba Mentality.', 'legends', 'Basketball', '1h 20m', 2021, 'TV-MA'),
  entry('leg-lebron', 'LeBron James', 'Chasing the ghost of Chicago.', 'legends', 'Basketball', '1h 35m', 2023, 'TV-PG'),
  entry('leg-ali', 'Muhammad Ali', 'The greatest of all time.', 'legends', 'Boxing', '1h 29m', 1996, 'PG'),
  entry('leg-tyson', 'Mike Tyson', 'Iron Mike.', 'legends', 'Boxing', '1h 15m', 2022, 'TV-MA'),
  entry('leg-senna', 'Ayrton Senna', 'Beyond the limit.', 'legends', 'Formula 1', '1h 46m', 2010, 'PG-13'),
  entry('leg-schumi', 'Michael Schumacher', 'Seven titles in red.', 'legends', 'Formula 1', '1h 52m', 2021, 'TV-PG'),
  entry('leg-hamilton', 'Lewis Hamilton', 'Record breaker.', 'legends', 'Formula 1', '1h 40m', 2024, 'TV-PG'),
  entry('leg-bolt', 'Usain Bolt', 'The fastest man ever.', 'legends', 'Olympics', '58m', 2023, 'TV-PG'),
  entry('riv-ind-pak', 'India vs Pakistan', 'More than cricket.', 'rivalries', 'Cricket', '1h 30m', 2023, 'TV-PG', { trending: true }),
  entry('riv-sachin-warne', 'Sachin vs Warne', 'Master vs spin wizard.', 'rivalries', 'Cricket', '52m', 2022, 'TV-PG'),
  entry('riv-kohli-babar', 'Kohli vs Babar', 'Modern cricket\'s duel.', 'rivalries', 'Cricket', '48m', 2024, 'TV-PG'),
  entry('riv-messi-ronaldo', 'Messi vs Ronaldo', 'A divided planet.', 'rivalries', 'Football', '1h 35m', 2023, 'TV-PG', { trending: true }),
  entry('riv-el-clasico', 'Barcelona vs Real Madrid', 'El Clásico.', 'rivalries', 'Football', '1h 22m', 2022, 'TV-PG'),
  entry('riv-fed-nadal', 'Federer vs Nadal', 'Grass vs clay.', 'rivalries', 'Tennis', '1h 18m', 2023, 'TV-PG'),
  entry('riv-djoko-nadal', 'Djokovic vs Nadal', '53 meetings.', 'rivalries', 'Tennis', '1h 12m', 2024, 'TV-PG'),
  entry('riv-senna-prost', 'Senna vs Prost', 'Teammates turned enemies.', 'rivalries', 'Formula 1', '1h 40m', 2021, 'TV-MA'),
  entry('riv-ham-ver', 'Hamilton vs Verstappen', 'The 2021 title war.', 'rivalries', 'Formula 1', '1h 25m', 2022, 'TV-MA'),
  entry('story-comeback', 'The Greatest Comeback', 'Down and out — then glory.', 'stories', 'Football', '1h 5m', 2023, 'TV-PG', { trending: true }),
  entry('story-underdog', 'Underdog Champions', 'Nobody believed — except them.', 'stories', 'Cricket', '1h 12m', 2023, 'TV-PG'),
  entry('story-injury', 'Road to Recovery', 'Injury to trophy lift.', 'stories', 'Basketball', '58m', 2024, 'TV-PG'),
  entry('story-retire', 'The Final Whistle', 'Emotional retirements.', 'stories', 'Tennis', '52m', 2023, 'TV-PG'),
  entry('story-historic', 'Historic Wins', 'The impossible became real.', 'stories', 'Olympics', '1h 8m', 2022, 'TV-PG'),
  entry('story-1983', "India's 1983", 'A billion believers born.', 'stories', 'Cricket', '1h 28m', 2023, 'TV-PG'),
  entry('story-lebron', 'The Decision', 'South Beach.', 'stories', 'Basketball', '1h 15m', 2020, 'TV-PG'),
  entry('story-agassi', 'Open: Agassi Untold', 'Rebel to legend.', 'stories', 'Tennis', '1h 20m', 2021, 'TV-PG'),
  entry('sec-locker', 'Locker Room Secrets', 'What cameras never caught.', 'secrets', 'Football', '1h 10m', 2024, 'TV-MA', { trending: true }),
  entry('sec-dressing', 'Dressing Room Politics', 'Power behind closed doors.', 'secrets', 'Cricket', '58m', 2023, 'TV-MA'),
  entry('sec-transfer', 'Transfer Secrets', 'Midnight deals.', 'secrets', 'Football', '1h 5m', 2023, 'TV-MA'),
  entry('sec-scandal', 'Sports Scandals Exposed', 'When the game lost its soul.', 'secrets', 'Cricket', '1h 15m', 2022, 'TV-MA'),
  entry('sec-fixed', 'The Fixed Match', "Cricket's darkest hour.", 'secrets', 'Cricket', '1h 8m', 2023, 'TV-MA'),
  entry('sec-doping', 'The Doping Files', 'Stripped medals.', 'secrets', 'Olympics', '1h 12m', 2022, 'TV-MA'),
  entry('sec-boardroom', 'Boardroom Battles', 'Broken trust.', 'secrets', 'Football', '55m', 2024, 'TV-MA'),
  entry('sec-whistle', 'The Whistleblower', 'One voice vs an empire.', 'secrets', 'Hockey', '1h 2m', 2023, 'TV-MA'),
];

function mapOriginal(item) {
  return entry(item.id, item.title, item.description, 'originals', item.sport, item.duration, item.year, item.rating, {
    format: item.format,
    featured: item.featured,
    trending: item.trending,
  });
}

const fromOriginals = originalsCatalog.map(mapOriginal);
const seen = new Set();
const merged = [];

for (const v of [...CURATED, ...fromOriginals, ...verticalCatalog]) {
  if (!seen.has(v.id)) {
    seen.add(v.id);
    merged.push(v);
  }
}

export const videoCatalog = merged;

export function getVideoById(id) {
  return videoCatalog.find((v) => v.id === id || v.slug === id || String(v.id) === String(id));
}

export function searchVideos(query) {
  const q = query.trim().toLowerCase();
  if (!q) return videoCatalog;
  return videoCatalog.filter(
    (v) =>
      v.title.toLowerCase().includes(q) ||
      v.description?.toLowerCase().includes(q) ||
      v.sport?.toLowerCase().includes(q) ||
      v.vertical?.toLowerCase().includes(q) ||
      v.categoryName?.toLowerCase().includes(q) ||
      v.format?.toLowerCase().includes(q) ||
      (v.genres && v.genres.some((g) => g.toLowerCase().includes(q)))
  );
}

export function getByVertical(verticalId, limit = 12) {
  return videoCatalog.filter((v) => v.vertical === verticalId).slice(0, limit);
}

export function getByCategory(categorySlug) {
  if (!categorySlug || categorySlug === 'all') return videoCatalog;
  return videoCatalog.filter((v) => v.category === categorySlug);
}
