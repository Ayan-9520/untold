/**
 * UNTOLD sports news — mock articles (API-ready)
 */

const IMG = {
  Cricket: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=800&q=80',
  Football: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80',
  Tennis: 'https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=800&q=80',
  'Formula 1': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80',
  Olympics: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=800&q=80',
  MMA: 'https://images.unsplash.com/photo-1555597673-b21d5c48148c?w=800&q=80',
};

function article(id, title, excerpt, sport, publishedAt, opts = {}) {
  return {
    id,
    title,
    excerpt,
    sport,
    publishedAt,
    thumbnail: opts.thumbnail || IMG[sport] || IMG.Cricket,
    author: opts.author || 'UNTOLD Editorial',
    trending: !!opts.trending,
    category: opts.category || 'news',
  };
}

export const newsCatalog = [
  article('news-1', 'Kohli Fifty Steadies India at Lord\'s', 'Captain reaches milestone as second Test hangs in balance on day two.', 'Cricket', '2026-06-25T14:30:00Z', { trending: true }),
  article('news-2', 'Premier League Title Race: Final Day Drama', 'Three teams still in contention as simultaneous kick-offs decide the crown.', 'Football', '2026-06-25T12:00:00Z', { trending: true }),
  article('news-3', 'UFC 305: Main Event Walkouts Underway', 'Las Vegas card delivers as challengers look to dethrone the champion.', 'MMA', '2026-06-25T22:00:00Z', { trending: true }),
  article('news-4', 'Wimbledon Draw: Alcaraz Faces Tough Path', 'Defending champion lands in same half as rising stars.', 'Tennis', '2026-06-24T09:00:00Z'),
  article('news-5', 'ICC World Cup 2026: Host Cities Announced', 'Ten venues across India confirmed for cricket\'s biggest carnival.', 'Cricket', '2026-06-23T11:00:00Z', { trending: true }),
  article('news-6', 'Hamilton Targets Home Glory at Silverstone', 'Seven-time champion eyes first British GP win with new team.', 'Formula 1', '2026-06-22T16:00:00Z'),
  article('news-7', 'FIFA 2026: Group Stage Format Explained', '48 teams, new structure — everything fans need to know.', 'Football', '2026-06-21T10:00:00Z'),
  article('news-8', 'IPL 2027 Auction Date Confirmed', 'Franchises prepare retention lists ahead of mega auction in Dubai.', 'Cricket', '2026-06-20T08:00:00Z'),
  article('news-9', 'Olympics LA 2028: India\'s Medal Prospects', 'Shooting, wrestling, and hockey lead medal hopes for the contingent.', 'Olympics', '2026-06-19T14:00:00Z'),
  article('news-10', 'El Clásico Preview: New Era, Same Rivalry', 'Barcelona and Real Madrid clash with title implications on the line.', 'Football', '2026-06-18T12:00:00Z'),
  article('news-11', 'Sinner Withdraws from Halle Open', 'World No.1 cites fatigue ahead of Wimbledon preparations.', 'Tennis', '2026-06-17T09:30:00Z'),
  article('news-12', 'Verstappen Extends Lead in Constructors\' Standings', 'Red Bull capitalises on McLaren slip-up in Austria.', 'Formula 1', '2026-06-16T18:00:00Z'),
];

export function getTrendingNews(limit = 6) {
  return newsCatalog.filter((n) => n.trending).slice(0, limit);
}

export function getLatestNews(limit = 10) {
  return [...newsCatalog].sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt)).slice(0, limit);
}

export function searchNews(query) {
  const q = query.trim().toLowerCase();
  if (!q) return newsCatalog;
  return newsCatalog.filter(
    (n) =>
      n.title.toLowerCase().includes(q) ||
      n.excerpt.toLowerCase().includes(q) ||
      n.sport.toLowerCase().includes(q)
  );
}

export function getNewsBySport(sport) {
  if (!sport || sport === 'All') return newsCatalog;
  return newsCatalog.filter((n) => n.sport === sport);
}
