/**
 * UNTOLD engagement data — debates, polls, signature series (API-ready)
 */

export const debates = [
  {
    id: 'debate-goat-football',
    question: 'Who changed football forever?',
    subtitle: 'GOAT Debate',
    sport: 'Football',
    featured: true,
    options: [
      { id: 'messi', label: 'Lionel Messi', votes: 48200 },
      { id: 'ronaldo', label: 'Cristiano Ronaldo', votes: 45100 },
    ],
  },
  {
    id: 'debate-captain-cricket',
    question: 'Best Indian captain?',
    subtitle: 'Captaincy',
    sport: 'Cricket',
    options: [
      { id: 'dhoni', label: 'MS Dhoni', votes: 62400 },
      { id: 'kohli', label: 'Virat Kohli', votes: 38900 },
    ],
  },
  {
    id: 'debate-rivalry-tennis',
    question: 'Greatest rivalry in tennis?',
    subtitle: 'Rivalries',
    sport: 'Tennis',
    options: [
      { id: 'fed-nadal', label: 'Federer vs Nadal', votes: 31200 },
      { id: 'djoko-nadal', label: 'Djokovic vs Nadal', votes: 24800 },
    ],
  },
  {
    id: 'debate-f1-legends',
    question: 'Who defined Formula 1?',
    subtitle: 'Motorsport',
    sport: 'Formula 1',
    options: [
      { id: 'senna', label: 'Ayrton Senna', votes: 28500 },
      { id: 'schumi', label: 'Michael Schumacher', votes: 26100 },
    ],
  },
];

export const polls = [
  {
    id: 'poll-ipl-winner',
    question: 'IPL 2027 favourites?',
    options: [
      { id: 'csk', label: 'CSK', votes: 8900 },
      { id: 'mi', label: 'Mumbai Indians', votes: 7200 },
      { id: 'rcb', label: 'RCB', votes: 12400 },
      { id: 'kkr', label: 'KKR', votes: 6100 },
    ],
  },
  {
    id: 'poll-wc-winner',
    question: 'ICC World Cup 2026 winner?',
    options: [
      { id: 'india', label: 'India', votes: 45200 },
      { id: 'aus', label: 'Australia', votes: 18900 },
      { id: 'eng', label: 'England', votes: 11200 },
    ],
  },
  {
    id: 'poll-el-clasico',
    question: 'Next El Clásico winner?',
    options: [
      { id: 'barca', label: 'Barcelona', votes: 15600 },
      { id: 'madrid', label: 'Real Madrid', votes: 17800 },
    ],
  },
];

export const signatureSeries = [
  {
    id: 'series-monday-rivalry',
    title: 'Monday Rivalry',
    schedule: 'Every Monday',
    description: 'The feuds that defined eras — new rivalry deep-dives weekly.',
    slug: 'rivalries',
    path: '/rivalries',
    accent: 'Rivalries',
  },
  {
    id: 'series-wednesday-secrets',
    title: 'Wednesday Secrets',
    schedule: 'Every Wednesday',
    description: 'Locker room truths, scandals, and stories they tried to bury.',
    slug: 'secrets',
    path: '/secrets',
    accent: 'Secrets',
  },
  {
    id: 'series-friday-legends',
    title: 'Friday Legends',
    schedule: 'Every Friday',
    description: 'Icons who changed their sport — legacy storytelling.',
    slug: 'legends',
    path: '/legends',
    accent: 'Legends',
  },
  {
    id: 'series-goat-debates',
    title: 'UNTOLD GOAT Debates',
    schedule: 'Signature Series',
    description: 'Messi vs Ronaldo, Sachin vs Lara — the debates that never end.',
    slug: 'originals',
    path: '/originals',
    accent: 'Originals',
  },
  {
    id: 'series-dark-side',
    title: 'Dark Side of Sports',
    schedule: 'Signature Series',
    description: 'Scandals, controversies, and the price of glory.',
    slug: 'secrets',
    path: '/secrets',
    accent: 'Investigations',
  },
];

export function getFeaturedDebate() {
  return debates.find((d) => d.featured) || debates[0];
}

export function getDebateById(id) {
  return debates.find((d) => d.id === id);
}

export function getPollById(id) {
  return polls.find((p) => p.id === id);
}
