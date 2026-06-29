/** Fan ecosystem — debates, fan wars, predictions across global sports */

export const FAN_DNA_DEFAULT = {
  passionLevel: 92,
  debateIndex: 86,
  loyaltyScore: 90,
  badge: 'Elite Fan',
  personality: 'Global Storyteller',
  sportsTwin: 'Roger Federer',
  sportsTwinMatch: 91,
  traits: ['Multi-Sport Mind', 'Debate Ready', 'Clutch Analyst'],
};

export const DEBATE_ARENAS = [
  {
    id: 'messi-ronaldo',
    title: 'Messi vs Ronaldo',
    sport: 'Football',
    optionA: { id: 'messi', label: 'Messi', votes: 12480 },
    optionB: { id: 'ronaldo', label: 'Ronaldo', votes: 11820 },
    image: 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=800&q=80',
  },
  {
    id: 'jordan-lebron',
    title: 'Jordan vs LeBron',
    sport: 'Basketball',
    optionA: { id: 'jordan', label: 'Jordan', votes: 14200 },
    optionB: { id: 'lebron', label: 'LeBron', votes: 13850 },
    image: 'https://images.unsplash.com/photo-1519861531473-9200292dcfe3?w=800&q=80',
  },
  {
    id: 'federer-nadal',
    title: 'Federer vs Nadal',
    sport: 'Tennis',
    optionA: { id: 'federer', label: 'Federer', votes: 9840 },
    optionB: { id: 'nadal', label: 'Nadal', votes: 10120 },
    image: 'https://images.unsplash.com/photo-1622279457126-caf9917aa3c3?w=800&q=80',
  },
  {
    id: 'ali-tyson',
    title: 'Ali vs Tyson',
    sport: 'Boxing',
    optionA: { id: 'ali', label: 'Ali', votes: 11200 },
    optionB: { id: 'tyson', label: 'Tyson', votes: 8900 },
    image: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=800&q=80',
  },
];

export const FAN_WARS = [
  {
    id: 'real-barca',
    title: 'Real Madrid vs Barcelona',
    sport: 'Football',
    teamA: { id: 'real', name: 'Real Madrid', votes: 22100, color: 'bg-white' },
    teamB: { id: 'barca', name: 'Barcelona', votes: 23500, color: 'bg-blue-700' },
    status: 'live',
  },
  {
    id: 'lakers-celtics',
    title: 'Lakers vs Celtics',
    sport: 'Basketball',
    teamA: { id: 'lakers', name: 'Lakers', votes: 19800, color: 'bg-yellow-500' },
    teamB: { id: 'celtics', name: 'Celtics', votes: 20400, color: 'bg-green-700' },
    status: 'live',
  },
  {
    id: 'ind-pak',
    title: 'India vs Pakistan',
    sport: 'Cricket',
    teamA: { id: 'india', name: 'India', votes: 45200, color: 'bg-blue-600' },
    teamB: { id: 'pakistan', name: 'Pakistan', votes: 41800, color: 'bg-green-600' },
    status: 'open',
  },
  {
    id: 'ham-ver',
    title: 'Hamilton vs Verstappen',
    sport: 'Formula 1',
    teamA: { id: 'hamilton', name: 'Hamilton', votes: 16400, color: 'bg-cyan-600' },
    teamB: { id: 'verstappen', name: 'Verstappen', votes: 17200, color: 'bg-orange-600' },
    status: 'open',
  },
];

export const PREDICTION_EVENTS = [
  {
    id: 'pred-cl-final',
    title: 'Champions League Final',
    sport: 'Football',
    closesAt: '2026-06-01T20:00:00Z',
    pool: 98000,
    questions: [
      { id: 'winner', label: 'Winner', options: ['Home', 'Away', 'Draw ET'] },
      { id: 'goals', label: 'Total Goals', options: ['Under 2.5', 'Over 2.5'] },
    ],
    rewards: { coins: 350, badge: 'Tactician', premiumUnlock: true },
  },
  {
    id: 'pred-wimbledon',
    title: 'Wimbledon Final',
    sport: 'Tennis',
    closesAt: '2026-07-12T14:00:00Z',
    pool: 72000,
    questions: [
      { id: 'winner', label: 'Champion', options: ['Player A', 'Player B'] },
      { id: 'sets', label: 'Total Sets', options: ['3', '4', '5'] },
    ],
    rewards: { coins: 280, badge: 'Court Oracle', premiumUnlock: false },
  },
  {
    id: 'pred-ufc-title',
    title: 'UFC Title Fight',
    sport: 'MMA',
    closesAt: '2026-06-25T22:00:00Z',
    pool: 64000,
    questions: [
      { id: 'winner', label: 'Winner', options: ['Champion', 'Challenger'] },
      { id: 'method', label: 'Finish', options: ['KO/TKO', 'Decision', 'Submission'] },
    ],
    rewards: { coins: 400, badge: 'Fight Analyst', premiumUnlock: true },
  },
];

export const PREDICTION_LEADERBOARD = [
  { rank: 1, name: 'GlobalSportsFan', points: 4820, accuracy: 78 },
  { rank: 2, name: 'GoalMachine', points: 4610, accuracy: 76 },
  { rank: 3, name: 'CourtVision', points: 4390, accuracy: 74 },
  { rank: 4, name: 'F1Oracle', points: 4105, accuracy: 71 },
  { rank: 5, name: 'You', points: 1240, accuracy: 62, isUser: true },
];
