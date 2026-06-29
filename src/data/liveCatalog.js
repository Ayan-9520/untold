/**
 * UNTOLD Live — Phase 1 mock catalog
 * Sports API → Backend → AI Engine → UI (API-ready structure)
 * No live video streaming — scores, commentary, updates, highlights only
 */

const IMG = {
  Cricket: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80',
  Football: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80',
  Tennis: 'https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=1200&q=80',
  'Formula 1': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=80',
  Boxing: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=1200&q=80',
  MMA: 'https://images.unsplash.com/photo-1555597673-b21d5c48148c?w=1200&q=80',
};

export const LIVE_SPORTS = ['All', 'Cricket', 'Football', 'Tennis', 'Formula 1', 'Boxing', 'MMA'];

/** Transform raw API event into AI commentary line */
export function generateAICommentary(update) {
  const templates = {
    goal: (t) => `GOAL! ${t} — the stadium erupts!`,
    wicket: (t) => `WICKET! ${t} — a huge moment in this contest.`,
    knockout: (t) => `KNOCKOUT! ${t} — it's over!`,
    point: (t) => `MATCH POINT! ${t}`,
    lap: (t) => `FASTEST LAP! ${t}`,
    incident: (t) => `INCIDENT: ${t}`,
    default: (t) => t,
  };
  const fn = templates[update.type] || templates.default;
  return fn(update.raw || update.text);
}

function match(
  id,
  eventName,
  sport,
  teams,
  score,
  status,
  timer,
  opts = {}
) {
  const eventUpdates = opts.eventUpdates || [];
  const commentary = eventUpdates.map((u, i) => ({
    id: `${id}-c${i}`,
    time: u.time,
    minute: u.minute || u.time,
    text: u.aiText || generateAICommentary(u),
    type: u.type || 'update',
  }));

  return {
    id,
    eventName,
    sport,
    teamsOrPlayers: teams,
    score,
    status,
    timer,
    thumbnail: opts.thumbnail || IMG[sport] || IMG.Football,
    location: opts.location || '',
    featured: !!opts.featured,
    league: opts.league || '',
    eventUpdates,
    commentary,
    highlights: opts.highlights || [],
    timeline: opts.timeline || [],
    predictions: opts.predictions || null,
  };
}

export const liveCatalog = [
  match('live-ind-aus', 'India vs Australia — 3rd ODI', 'Cricket', ['India', 'Australia'],
    { home: '287/4', away: '245', display: '287/4 vs 245' }, 'live', '42.3 overs',
    {
      featured: true, location: 'Wankhede, Mumbai', league: 'India Tour of Australia',
      eventUpdates: [
        { time: '18:42', minute: '42.3', type: 'wicket', raw: 'Kohli departs for 89 — caught at long-on' },
        { time: '18:15', minute: '38.1', type: 'default', raw: 'Kohli and Hardik rebuild after early scare' },
        { time: '17:30', minute: '32.0', type: 'wicket', raw: 'Rohit falls for 45 — Australia strike back' },
      ],
      highlights: [
        { id: 'h1', title: 'Kohli cover drive for six', type: 'boundary', minute: '36.2', thumbnail: IMG.Cricket },
        { id: 'h2', title: 'Starc yorker removes Rohit', type: 'wicket', minute: '32.0', thumbnail: IMG.Cricket },
      ],
      timeline: [
        { id: 't1', minute: '32.0', type: 'wicket', label: 'Wicket', detail: 'Rohit c Maxwell b Starc 45' },
        { id: 't2', minute: '36.2', type: 'six', label: 'Six', detail: 'Kohli — 89m six over long-off' },
        { id: 't3', minute: '42.3', type: 'wicket', label: 'Wicket', detail: 'Kohli c Head b Zampa 89' },
      ],
      predictions: { question: 'Who wins?', options: [{ id: 'ind', label: 'India', votes: 62 }, { id: 'aus', label: 'Australia', votes: 38 }] },
    }
  ),
  match('live-el-clasico', 'Real Madrid vs Barcelona', 'Football', ['Real Madrid', 'Barcelona'],
    { home: 2, away: 1, display: '2 - 1' }, 'live', "78'",
    {
      location: 'Santiago Bernabéu', league: 'La Liga',
      eventUpdates: [
        { time: '20:58', minute: "78'", type: 'goal', raw: 'Bellingham scores in the 78th minute — Madrid lead!' },
        { time: '20:12', minute: "52'", type: 'goal', raw: 'Lewandowski equalizes from the penalty spot' },
        { time: '19:45', minute: "23'", type: 'goal', raw: 'Vinícius Jr opens the scoring with a curling finish' },
      ],
      highlights: [
        { id: 'h1', title: 'Vinícius Jr opener', type: 'goal', minute: "23'", thumbnail: IMG.Football },
        { id: 'h2', title: 'Bellingham header', type: 'goal', minute: "78'", thumbnail: IMG.Football },
      ],
      timeline: [
        { id: 't1', minute: "23'", type: 'goal', label: 'Goal', detail: 'Vinícius Jr — Real Madrid 1-0' },
        { id: 't2', minute: "52'", type: 'goal', label: 'Goal', detail: 'Lewandowski (pen) — 1-1' },
        { id: 't3', minute: "78'", type: 'goal', label: 'Goal', detail: 'Bellingham — Real Madrid 2-1' },
      ],
    }
  ),
  match('live-wimbledon-final', 'Wimbledon Gentlemen\'s Final', 'Tennis', ['Alcaraz', 'Sinner'],
    { home: '2', away: '1', display: '2-1 sets' }, 'live', 'Set 4 · 4-3',
    {
      location: 'Centre Court, London', league: 'Grand Slam',
      eventUpdates: [
        { time: '16:20', minute: 'Set 4', type: 'point', raw: 'Alcaraz breaks Sinner — leads 4-3 in the fourth' },
        { time: '15:45', minute: 'Set 3', type: 'default', raw: 'Sinner takes the third set 7-5 — we go to four' },
        { time: '14:30', minute: 'Set 2', type: 'default', raw: 'Alcaraz levels at one set apiece' },
      ],
      highlights: [
        { id: 'h1', title: 'Alcaraz passing shot winner', type: 'point', minute: 'Set 4', thumbnail: IMG.Tennis },
      ],
    }
  ),
  match('live-monaco-gp', 'Monaco Grand Prix', 'Formula 1', ['Verstappen', 'Norris', 'Leclerc'],
    { home: 'P1', away: 'P2', display: 'VER P1 · NOR P2' }, 'live', 'Lap 52/78',
    {
      location: 'Monte Carlo', league: 'Formula 1',
      eventUpdates: [
        { time: '15:52', minute: 'Lap 52', type: 'lap', raw: 'Norris sets fastest lap — closing on Verstappen' },
        { time: '15:30', minute: 'Lap 48', type: 'incident', raw: 'Safety car deployed — debris at Tabac' },
        { time: '15:00', minute: 'Lap 42', type: 'default', raw: 'Verstappen extends lead to 4.2 seconds' },
      ],
      highlights: [
        { id: 'h1', title: 'Norris fastest lap', type: 'lap', minute: 'Lap 52', thumbnail: IMG['Formula 1'] },
      ],
    }
  ),
  match('live-ind-eng-test', 'India vs England — 2nd Test', 'Cricket', ['India', 'England'],
    { home: '312/6', away: '287', display: '312/6 vs 287' }, 'live', 'Day 3 · 67 overs',
    {
      location: 'Lord\'s, London', league: 'Test Series',
      eventUpdates: [
        { time: '14:32', minute: '67.0', type: 'default', raw: 'Kohli reaches fifty off 78 balls — Lord\'s roars' },
        { time: '13:15', minute: '58.2', type: 'wicket', raw: 'Anderson strikes — Gill caught behind for 42' },
      ],
    }
  ),
  match('live-pl-title', 'Arsenal vs Manchester City', 'Football', ['Arsenal', 'Man City'],
    { home: 1, away: 1, display: '1 - 1' }, 'live', "67'",
    {
      location: 'Emirates Stadium', league: 'Premier League',
      eventUpdates: [
        { time: '16:05', minute: "34'", type: 'goal', raw: 'Saka puts Arsenal ahead — title race alive!' },
        { time: '15:58', minute: "28'", type: 'goal', raw: 'Haaland levels — City respond immediately' },
      ],
    }
  ),
  match('live-liverpool', 'Liverpool vs Chelsea', 'Football', ['Liverpool', 'Chelsea'],
    { home: 2, away: 0, display: '2 - 0' }, 'live', "55'",
    { location: 'Anfield', league: 'Premier League',
      eventUpdates: [{ time: '16:20', minute: "55'", type: 'goal', raw: 'Salah doubles Liverpool\'s lead' }] },
  ),
  match('live-ucl-semi', 'Bayern Munich vs Real Madrid', 'Football', ['Bayern', 'Real Madrid'],
    { home: 1, away: 2, display: '1 - 2' }, 'live', "HT",
    { location: 'Allianz Arena', league: 'Champions League',
      eventUpdates: [{ time: '21:00', minute: 'HT', type: 'default', raw: 'Halftime — Madrid lead on aggregate' }] },
  ),
  match('live-ipl-final', 'IPL 2026 Final', 'Cricket', ['Mumbai Indians', 'Chennai Super Kings'],
    { home: '189/3', away: '142', display: '189/3 vs 142' }, 'live', '16.2 overs',
    { location: 'Narendra Modi Stadium', league: 'IPL',
      eventUpdates: [{ time: '22:10', minute: '16.2', type: 'six', raw: 'Hardik launches into the night sky — MI cruising' }] },
  ),
  match('live-asia-cup', 'India vs Pakistan', 'Cricket', ['India', 'Pakistan'],
    { home: '156/2', away: '', display: '156/2' }, 'live', '18.4 overs',
    { location: 'Dubai', league: 'Asia Cup',
      eventUpdates: [{ time: '19:45', minute: '18.4', type: 'wicket', raw: 'Babar departs — Pakistan need 45 from 30 balls' }] },
  ),
  match('live-ufc-305', 'UFC 305 — Main Event', 'MMA', ['Pereira', 'Adesanya'],
    { home: 'R3', away: '', display: 'Round 3 of 5' }, 'live', '2:34 R3',
    { location: 'Las Vegas', league: 'UFC',
      eventUpdates: [{ time: '22:10', minute: 'R3', type: 'default', raw: 'Pereira lands heavy leg kick — Adesanya hurt' }] },
  ),
  match('live-boxing-title', 'Heavyweight Title Fight', 'Boxing', ['Usyk', 'Fury'],
    { home: 'R8', away: '', display: 'Round 8 of 12' }, 'live', 'R8 · 1:12',
    { location: 'Riyadh', league: 'WBC',
      eventUpdates: [{ time: '23:05', minute: 'R8', type: 'default', raw: 'Fury rocks Usyk with a right hand — crowd on its feet' }] },
  ),
  match('live-f1-british', 'British Grand Prix', 'Formula 1', ['Hamilton', 'Russell', 'Verstappen'],
    { home: 'P3', away: 'P1', display: 'VER P1 · HAM P3' }, 'live', 'Lap 38/52',
    { location: 'Silverstone', league: 'Formula 1',
      eventUpdates: [{ time: '14:20', minute: 'Lap 38', type: 'incident', raw: 'Hamilton overtakes Russell at Copse — home hero roars' }] },
  ),
  match('live-us-open', 'US Open — Women\'s SF', 'Tennis', ['Swiatek', 'Gauff'],
    { home: '1', away: '0', display: '1-0 sets' }, 'live', 'Set 2 · 3-2',
    { location: 'Flushing Meadows', league: 'Grand Slam',
      eventUpdates: [{ time: '18:30', minute: 'Set 2', type: 'point', raw: 'Swiatek breaks — leads 3-2 in the second' }] },
  ),
  match('live-serie-a', 'Inter Milan vs AC Milan', 'Football', ['Inter', 'AC Milan'],
    { home: 0, away: 0, display: '0 - 0' }, 'live', "32'",
    { location: 'San Siro', league: 'Serie A',
      eventUpdates: [{ time: '20:32', minute: "32'", type: 'default', raw: 'Derby della Madonnina — tense and tactical so far' }] },
  ),
  match('live-ligue1', 'PSG vs Marseille', 'Football', ['PSG', 'Marseille'],
    { home: 3, away: 1, display: '3 - 1' }, 'live', "82'",
    { location: 'Parc des Princes', league: 'Ligue 1',
      eventUpdates: [{ time: '21:42', minute: "82'", type: 'goal', raw: 'Mbappé completes his hat-trick — Le Classique sealed' }] },
  ),
  match('live-bbl', 'Big Bash League — Final', 'Cricket', ['Perth Scorchers', 'Sydney Sixers'],
    { home: '178/5', away: '165', display: '178/5 vs 165' }, 'live', '19.1 overs',
    { location: 'Perth', league: 'BBL',
      eventUpdates: [{ time: '11:20', minute: '19.1', type: 'wicket', raw: 'Sixers lose their captain — Scorchers favourites' }] },
  ),
  match('live-mma-bellator', 'Bellator 300 — Co-Main', 'MMA', ['Pitbull', 'Stots'],
    { home: 'R2', away: '', display: 'Round 2' }, 'live', 'R2 · 3:45',
    { location: 'San Diego', league: 'Bellator',
      eventUpdates: [{ time: '21:30', minute: 'R2', type: 'knockout', raw: 'Pitbull drops Stots — title defence continues' }] },
  ),
  match('live-f1-monza', 'Italian Grand Prix', 'Formula 1', ['Leclerc', 'Sainz', 'Piastri'],
    { home: 'P1', away: 'P2', display: 'LEC P1 · SAI P2' }, 'live', 'Lap 45/53',
    { location: 'Monza', league: 'Formula 1',
      eventUpdates: [{ time: '15:10', minute: 'Lap 45', type: 'default', raw: 'Ferrari 1-2 at home — Tifosi in dreamland' }] },
  ),
  match('live-wtc-final', 'World Test Championship Final', 'Cricket', ['India', 'Australia'],
    { home: '245', away: '198/4', display: '245 vs 198/4' }, 'live', 'Day 2 · Stumps soon',
    { location: 'The Oval', league: 'WTC',
      eventUpdates: [{ time: '18:00', minute: 'Day 2', type: 'wicket', raw: 'Smith falls — Australia trail by 47 with 6 wickets left' }] },
  ),
  match('live-copa', 'Copa América — Semi Final', 'Football', ['Argentina', 'Colombia'],
    { home: 1, away: 1, display: '1 - 1' }, 'live', "ET 105'",
    { location: 'Miami', league: 'Copa América',
      eventUpdates: [{ time: '22:45', minute: "105'", type: 'goal', raw: 'Messi scores in extra time — Argentina lead!' }],
      predictions: { question: 'GOAT debate — who is greater?', options: [{ id: 'messi', label: 'Messi', votes: 71 }, { id: 'ronaldo', label: 'Ronaldo', votes: 29 }] },
    }
  ),
  match('live-atp-500', 'ATP 500 — Dubai Final', 'Tennis', ['Medvedev', 'Rublev'],
    { home: '1', away: '1', display: '1-1 sets' }, 'live', 'Set 3 · 2-2',
    { location: 'Dubai', league: 'ATP',
      eventUpdates: [{ time: '17:15', minute: 'Set 3', type: 'default', raw: 'Deciding set — both players holding serve' }] },
  ),
];

export function getFeaturedLiveMatch() {
  return liveCatalog.find((m) => m.featured) || liveCatalog[0];
}

export function getLiveMatches(sport = 'All') {
  if (sport === 'All') return liveCatalog;
  return liveCatalog.filter((m) => m.sport === sport);
}

export function getLiveMatchById(id) {
  return liveCatalog.find((m) => m.id === id) || null;
}

export function getAllHighlights(limit = 12) {
  return liveCatalog
    .flatMap((m) => (m.highlights || []).map((h) => ({ ...h, matchId: m.id, eventName: m.eventName, sport: m.sport })))
    .slice(0, limit);
}

export function getAllEventUpdates(limit = 20) {
  return liveCatalog
    .flatMap((m) =>
      (m.eventUpdates || []).map((u, i) => ({
        ...u,
        id: `${m.id}-u${i}`,
        matchId: m.id,
        eventName: m.eventName,
        sport: m.sport,
        aiText: u.aiText || generateAICommentary(u),
      }))
    )
    .sort((a, b) => (b.time > a.time ? 1 : -1))
    .slice(0, limit);
}

export function searchLiveMatches(query) {
  const q = query.toLowerCase().trim();
  if (!q) return liveCatalog;
  return liveCatalog.filter(
    (m) =>
      m.eventName.toLowerCase().includes(q) ||
      m.sport.toLowerCase().includes(q) ||
      m.teamsOrPlayers.some((t) => t.toLowerCase().includes(q))
  );
}
