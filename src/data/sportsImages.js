/**
 * Shared sports imagery — documentaries, hero, cards, events (not game-specific)
 */
export const SPORT_IMAGES = {
  Cricket: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=85&auto=format&fit=crop',
  Football: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=85&auto=format&fit=crop',
  Basketball: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&q=85&auto=format&fit=crop',
  Tennis: 'https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=1200&q=85&auto=format&fit=crop',
  Boxing: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=1200&q=85&auto=format&fit=crop',
  MMA: 'https://images.unsplash.com/photo-1555597673-b21d5c48148c?w=1200&q=85&auto=format&fit=crop',
  'Formula 1': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=85&auto=format&fit=crop',
  Olympics: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=1200&q=85&auto=format&fit=crop',
  Hockey: 'https://images.unsplash.com/photo-1515703407324-5f753afd8be8?w=1200&q=85&auto=format&fit=crop',
  Swimming: 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=1200&q=85&auto=format&fit=crop',
  Baseball: 'https://images.unsplash.com/photo-1566577739090-0d1bf7750eed?w=1200&q=85&auto=format&fit=crop',
  Kabaddi: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=1200&q=85&auto=format&fit=crop',
  Wrestling: 'https://images.unsplash.com/photo-1555597673-b21d5c48148c?w=1200&q=85&auto=format&fit=crop',
  Gymnastics: 'https://images.unsplash.com/photo-1517649763962-0c62306601b7?w=1200&q=85&auto=format&fit=crop',
};

export const HERO_POSTER_IMAGES = {
  rivalryFootball: 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=900&q=85&auto=format&fit=crop',
  biopicBasketball: 'https://images.unsplash.com/photo-1519861531473-9200292dcfe3?w=900&q=85&auto=format&fit=crop',
  documentaryF1: 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=900&q=85&auto=format&fit=crop',
  legendBoxing: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=900&q=85&auto=format&fit=crop',
  rivalryTennis: 'https://images.unsplash.com/photo-1622279457126-caf9917aa3c3?w=900&q=85&auto=format&fit=crop',
  storyOlympics: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=900&q=85&auto=format&fit=crop',
};

export function sportImage(sport) {
  return SPORT_IMAGES[sport] || SPORT_IMAGES.Football;
}
