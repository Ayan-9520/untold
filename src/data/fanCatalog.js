/** Fan ecosystem — Fan DNA, Fan Wars, Prediction League, Debate Arena */

export const FAN_DNA_DEFAULT = {
  passionLevel: 95,
  debateIndex: 88,
  loyaltyScore: 92,
  badge: 'Elite Fan',
  personality: 'Dangerous Debater',
  sportsTwin: 'MS Dhoni',
  sportsTwinMatch: 94,
  traits: ['Clutch Thinker', 'Calm Under Pressure', 'Finisher Mentality'],
};

export const DEBATE_ARENAS = [
  {
    id: 'messi-ronaldo',
    title: 'Messi vs Ronaldo',
    sport: 'Football',
    optionA: { id: 'messi', label: 'Messi', votes: 12480 },
    optionB: { id: 'ronaldo', label: 'Ronaldo', votes: 11820 },
    image: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80',
  },
  {
    id: 'kohli-dhoni',
    title: 'Kohli vs Dhoni',
    sport: 'Cricket',
    optionA: { id: 'kohli', label: 'Kohli', votes: 8920 },
    optionB: { id: 'dhoni', label: 'Dhoni', votes: 10240 },
    image: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=800&q=80',
  },
];

export const FAN_WARS = [
  {
    id: 'ind-pak',
    title: 'India vs Pakistan',
    sport: 'Cricket',
    teamA: { id: 'india', name: 'India', votes: 45200, color: 'bg-blue-600' },
    teamB: { id: 'pakistan', name: 'Pakistan', votes: 41800, color: 'bg-green-600' },
    status: 'live',
  },
  {
    id: 'rcb-csk',
    title: 'RCB vs CSK',
    sport: 'IPL',
    teamA: { id: 'rcb', name: 'RCB', votes: 28400, color: 'bg-red-600' },
    teamB: { id: 'csk', name: 'CSK', votes: 31200, color: 'bg-yellow-500' },
    status: 'live',
  },
  {
    id: 'real-barca',
    title: 'Real Madrid vs Barcelona',
    sport: 'Football',
    teamA: { id: 'real', name: 'Real Madrid', votes: 22100, color: 'bg-white' },
    teamB: { id: 'barca', name: 'Barcelona', votes: 23500, color: 'bg-blue-700' },
    status: 'open',
  },
];

export const PREDICTION_EVENTS = [
  {
    id: 'pred-ipl-final',
    title: 'IPL 2026 Final',
    sport: 'Cricket',
    closesAt: '2026-05-28T18:30:00Z',
    pool: 125000,
    questions: [
      { id: 'winner', label: 'Match Winner', options: ['Team A', 'Team B'] },
      { id: 'top-scorer', label: 'Top Scorer', options: ['Kohli', 'Rohit', 'Other'] },
    ],
    rewards: { coins: 500, badge: 'Oracle', premiumUnlock: false },
  },
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
];

export const PREDICTION_LEADERBOARD = [
  { rank: 1, name: 'CricketKing_99', points: 4820, accuracy: 78 },
  { rank: 2, name: 'GoalMachine', points: 4610, accuracy: 76 },
  { rank: 3, name: 'DhoniFan_Mumbai', points: 4390, accuracy: 74 },
  { rank: 4, name: 'F1Oracle', points: 4105, accuracy: 71 },
  { rank: 5, name: 'You', points: 1240, accuracy: 62, isUser: true },
];
