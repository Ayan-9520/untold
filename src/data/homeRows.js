/**
 * Netflix-style homepage rows — curated order for UNTOLD ORIGINALS
 */
export const HOME_FEATURED_ROWS = [
  // Core experience
  { type: 'trending', title: 'Trending Now', subtitle: 'What the world is watching right now', viewAll: '/originals' },
  { type: 'latest', title: 'Latest Releases', subtitle: 'Fresh documentaries & biopic series', viewAll: '/originals' },
  { type: 'continue', title: 'Continue Watching', subtitle: 'Pick up where you left off' },

  // Sports storytelling
  { type: 'vertical', vertical: 'sports', title: 'Sports Legends', viewAll: '/legends' },
  { type: 'category', category: 'rivalries', title: 'Greatest Rivalries', viewAll: '/rivalries' },
  { type: 'vertical', vertical: 'ufc', title: 'Combat & UFC', viewAll: '/explore?vertical=ufc' },

  // Business & culture
  { type: 'vertical', vertical: 'business', title: 'Business & Startups', viewAll: '/explore?vertical=business' },
  { type: 'vertical', vertical: 'influencers', title: 'Creators & Influencers', viewAll: '/explore?vertical=influencers' },

  // Entertainment
  { type: 'vertical', vertical: 'hollywood', title: 'Hollywood', viewAll: '/explore?vertical=hollywood' },
  { type: 'vertical', vertical: 'bollywood', title: 'Bollywood', viewAll: '/explore?vertical=bollywood' },

  // Knowledge & power
  { type: 'vertical', vertical: 'technology', title: 'Technology & AI', viewAll: '/explore?vertical=technology' },
  { type: 'vertical', vertical: 'science', title: 'Science & Space', viewAll: '/explore?vertical=science' },
  { type: 'vertical', vertical: 'history', title: 'History & Wars', viewAll: '/explore?vertical=history' },
  { type: 'vertical', vertical: 'politics', title: 'Politics & Leaders', viewAll: '/explore?vertical=politics' },

  // Premium picks
  { type: 'award', title: 'Award Winning', subtitle: 'Festival favourites & critic picks', viewAll: '/originals' },
  { type: 'editors', title: "Editor's Choice", subtitle: 'Curated by the UNTOLD editorial team', viewAll: '/originals' },

  // Deep dives & format
  { type: 'vertical', vertical: 'crime', title: 'Crime & Mystery', viewAll: '/explore?vertical=crime' },
  { type: 'category', category: 'secrets', title: 'Secrets & Investigations', viewAll: '/secrets' },
  { type: 'category', category: 'shorts', title: 'Shorts & Reels', viewAll: '/shorts', variant: 'short' },
  { type: 'category', category: 'originals', title: 'Full Documentary Collections', viewAll: '/originals' },
];
