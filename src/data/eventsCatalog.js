/**
 * UNTOLD Events catalog — major global sports events (API-ready)
 * Status: upcoming | live | completed
 */

const IMG = {
  Cricket: 'https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80',
  Football: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80',
  Tennis: 'https://images.unsplash.com/photo-1554068865-24cecd4e24b8?w=1200&q=80',
  'Formula 1': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1200&q=80',
  Boxing: 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=1200&q=80',
  MMA: 'https://images.unsplash.com/photo-1555597673-b21d5c48148c?w=1200&q=80',
  Olympics: 'https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=1200&q=80',
  Basketball: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&q=80',
};

export const EVENT_SPORTS = ['All', 'Cricket', 'Football', 'Tennis', 'Formula 1', 'Combat', 'Olympics'];

function evt(id, eventName, sport, startDate, endDate, status, teamsOrPlayers, description, opts = {}) {
  return {
    id,
    eventName,
    sport,
    date: startDate,
    endDate,
    status,
    teamsOrPlayers,
    thumbnail: opts.thumbnail || IMG[sport] || IMG.Football,
    description,
    location: opts.location || '',
    result: opts.result || null,
    highlights: opts.highlights || [],
    liveUpdates: opts.liveUpdates || [],
    featured: !!opts.featured,
    preview: opts.preview || null,
    analysis: opts.analysis || null,
  };
}

export const eventsCatalog = [
  // —— LIVE ——
  evt(
    'evt-ind-eng-test',
    'India vs England — 2nd Test',
    'Cricket',
    '2026-06-24',
    '2026-06-28',
    'live',
    ['India', 'England'],
    'Lord\'s Test — Kohli vs Anderson in a series decider. Live coverage, key battles, and dressing-room access.',
    {
      location: 'Lord\'s, London',
      liveUpdates: [
        { time: '14:32', text: 'Kohli reaches fifty off 78 balls — Lord\'s roars.' },
        { time: '13:15', text: 'Anderson strikes — Gill caught behind for 42.' },
        { time: '11:40', text: 'India win the toss and elect to bat first.' },
      ],
    }
  ),
  evt(
    'evt-pl-final-day',
    'Premier League — Final Matchday',
    'Football',
    '2026-06-25',
    '2026-06-25',
    'live',
    ['Arsenal', 'Manchester City', 'Liverpool'],
    'Title race goes to the wire. Tactical breakdowns, fan reactions, and live match moments.',
    {
      location: 'England',
      featured: true,
      liveUpdates: [
        { time: '16:05', text: 'GOAL — Arsenal take the lead at the Emirates.' },
        { time: '15:58', text: 'City level through Haaland — title pendulum swings.' },
        { time: '15:00', text: 'All ten games kick off simultaneously.' },
      ],
    }
  ),
  evt(
    'evt-ufc-305',
    'UFC 305 — Main Event',
    'MMA',
    '2026-06-25',
    '2026-06-25',
    'live',
    ['Champion', 'Challenger'],
    'Title fight night — pre-fight analysis, live updates, and knockout highlights as they happen.',
    {
      location: 'Las Vegas, USA',
      liveUpdates: [
        { time: '22:10', text: 'Main event walkouts underway.' },
        { time: '21:45', text: 'Co-main ends in unanimous decision.' },
      ],
    }
  ),

  // —— UPCOMING ——
  evt(
    'evt-wimbledon',
    'Wimbledon Championships',
    'Tennis',
    '2026-06-29',
    '2026-07-12',
    'upcoming',
    ['Alcaraz', 'Sinner', 'Djokovic', 'Swiatek'],
    'Grass-court glory — previews, legacy stories, and rivalry watch on Centre Court.',
    { location: 'London, UK', preview: 'Can anyone stop the new generation on grass?' }
  ),
  evt(
    'evt-f1-british',
    'British Grand Prix',
    'Formula 1',
    '2026-07-06',
    '2026-07-06',
    'upcoming',
    ['Hamilton', 'Verstappen', 'Norris'],
    'Silverstone weekend — home-hero stories, team strategy, and race-day coverage.',
    { location: 'Silverstone, UK', preview: 'Hamilton\'s home race under new colours.' }
  ),
  evt(
    'evt-ipl-2027',
    'IPL 2027 Auction Preview',
    'Cricket',
    '2026-07-15',
    '2026-07-15',
    'upcoming',
    ['Mumbai Indians', 'CSK', 'RCB', 'KKR'],
    'Mega auction build-up — transfer secrets, retention strategies, and franchise battles.',
    { location: 'Dubai, UAE', preview: 'Who will break the bank this year?' }
  ),
  evt(
    'evt-icc-cwc',
    'ICC Cricket World Cup 2026',
    'Cricket',
    '2026-10-15',
    '2026-11-15',
    'upcoming',
    ['India', 'Australia', 'England', 'Pakistan'],
    'The biggest cricket carnival — previews, predictions, and rivalry stories before the first ball.',
    { location: 'India', featured: true, preview: 'Ten teams. One trophy. A billion dreams.' }
  ),
  evt(
    'evt-ind-pak',
    'India vs Pakistan — Asia Cup',
    'Cricket',
    '2026-08-22',
    '2026-08-22',
    'upcoming',
    ['India', 'Pakistan'],
    'More than a match — political tension, fan frenzy, and decades of rivalry unpacked.',
    { location: 'Dubai, UAE', preview: 'The fixture the world stops for.' }
  ),
  evt(
    'evt-asia-cup',
    'Asia Cup 2026',
    'Cricket',
    '2026-08-18',
    '2026-09-05',
    'upcoming',
    ['India', 'Pakistan', 'Sri Lanka', 'Bangladesh'],
    'Subcontinental supremacy — key players, form guide, and historic moments.',
    { location: 'UAE' }
  ),
  evt(
    'evt-champions-trophy',
    'ICC Champions Trophy 2026',
    'Cricket',
    '2026-02-10',
    '2026-03-10',
    'upcoming',
    ['India', 'Australia', 'South Africa'],
    'Elite eight battle for the mini World Cup — tactical previews and legend spotlights.',
    { location: 'Pakistan' }
  ),
  evt(
    'evt-world-cup-2026',
    'World Cup 2026',
    'Football',
    '2026-11-11',
    '2026-12-19',
    'upcoming',
    ['Brazil', 'Argentina', 'France', 'England'],
    'USA, Mexico, Canada — the greatest show on earth. Road to the final starts here.',
    { location: 'North America', preview: '48 teams. Three hosts. One crown.' }
  ),
  evt(
    'evt-ucl-knockout',
    'UEFA Champions League — Group Stage',
    'Football',
    '2026-09-15',
    '2026-12-10',
    'upcoming',
    ['Real Madrid', 'Barcelona', 'Bayern', 'Man City'],
    'Europe\'s elite return — tactical analysis, rivalry stories, and matchday coverage.',
    { location: 'Europe' }
  ),
  evt(
    'evt-el-clasico',
    'El Clásico — La Liga',
    'Football',
    '2026-10-25',
    '2026-10-25',
    'upcoming',
    ['Barcelona', 'Real Madrid'],
    'The world\'s biggest club fixture — form, tactics, and untold dressing-room stories.',
    { location: 'Barcelona, Spain', preview: 'New era, same hatred.' }
  ),
  evt(
    'evt-us-open',
    'US Open',
    'Tennis',
    '2026-08-24',
    '2026-09-07',
    'upcoming',
    ['Federer legacy', 'Alcaraz', 'Gauff'],
    'Flushing Meadows — hard-court drama, athlete journeys, and championship moments.',
    { location: 'New York, USA' }
  ),
  evt(
    'evt-f1-monaco-next',
    'Monaco Grand Prix 2027',
    'Formula 1',
    '2027-05-24',
    '2027-05-24',
    'upcoming',
    ['Verstappen', 'Leclerc', 'Norris'],
    'The crown jewel of F1 — glamour, strategy, and qualifying drama on the streets.',
    { location: 'Monte Carlo' }
  ),
  evt(
    'evt-f1-abu-dhabi',
    'Abu Dhabi Grand Prix',
    'Formula 1',
    '2026-11-29',
    '2026-11-29',
    'upcoming',
    ['Verstappen', 'Hamilton', 'Norris'],
    'Season finale under the lights — championship permutations and paddock secrets.',
    { location: 'Yas Marina, UAE' }
  ),
  evt(
    'evt-f1-championship',
    'Formula 1 World Championship 2026',
    'Formula 1',
    '2026-03-15',
    '2026-11-29',
    'upcoming',
    ['Red Bull', 'McLaren', 'Ferrari', 'Mercedes'],
    'Full season coverage — driver rivalries, team strategy, and race-weekend stories.',
    { location: 'Global' }
  ),
  evt(
    'evt-boxing-title',
    'Undisputed Heavyweight Title Fight',
    'Boxing',
    '2026-09-12',
    '2026-09-12',
    'upcoming',
    ['Champion', 'Challenger'],
    'The fight to unify the division — predictions, training camp access, and knockout history.',
    { location: 'Riyadh, Saudi Arabia', preview: 'Two champions. Four belts. One king.' }
  ),
  evt(
    'evt-olympics-la',
    'Summer Olympics — Los Angeles 2028',
    'Olympics',
    '2028-07-14',
    '2028-08-01',
    'upcoming',
    ['USA', 'China', 'Great Britain', 'India'],
    'Road to LA — athlete profiles, qualification stories, and medal predictions.',
    { location: 'Los Angeles, USA', preview: 'The world\'s greatest athletes converge.' }
  ),
  evt(
    'evt-commonwealth',
    'Commonwealth Games 2026',
    'Olympics',
    '2026-07-28',
    '2026-08-08',
    'upcoming',
    ['Australia', 'England', 'India', 'Canada'],
    'Multi-sport spectacle — medal coverage, athlete highlights, and historic moments.',
    { location: 'Glasgow, Scotland' }
  ),

  // —— COMPLETED ——
  evt(
    'evt-ipl-2026',
    'IPL 2026 — Final',
    'Cricket',
    '2026-05-26',
    '2026-05-26',
    'completed',
    ['Kolkata Knight Riders', 'Sunrisers Hyderabad'],
    'A season of sixes, super overs, and blockbuster auctions — relive the final and the untold stories.',
    {
      location: 'Ahmedabad, India',
      result: 'KKR won by 8 wickets',
      highlights: ['Starc\'s opening spell', 'Iyer\'s captain\'s knock', 'Victory lap at Narendra Modi Stadium'],
      analysis: 'KKR\'s bowling depth proved decisive in the playoffs.',
    }
  ),
  evt(
    'evt-ucl-final',
    'UEFA Champions League Final 2026',
    'Football',
    '2026-05-31',
    '2026-05-31',
    'completed',
    ['Real Madrid', 'Manchester City'],
    'European football\'s grandest night — tactical analysis, fan reactions, and post-match stories.',
    {
      location: 'Munich, Germany',
      result: 'Real Madrid 2-1 Manchester City',
      highlights: ['Vinícius Jr. opener', 'Haaland equaliser', 'Bellingham winner in extra time'],
      analysis: 'Madrid\'s experience in knockout football prevailed again.',
    }
  ),
  evt(
    'evt-monaco-gp',
    'Monaco Grand Prix 2026',
    'Formula 1',
    '2026-05-25',
    '2026-05-25',
    'completed',
    ['Leclerc', 'Piastri', 'Norris'],
    'The most glamorous race on the calendar — strategy, drama, and street-circuit mastery.',
    {
      location: 'Monte Carlo',
      result: 'Leclerc 1st, Piastri 2nd, Norris 3rd',
      highlights: ['Leclerc\'s home win', 'Safety car shuffle', 'Final-lap overtake attempt'],
      analysis: 'Ferrari finally delivered at home for their Monegasque hero.',
    }
  ),
  evt(
    'evt-french-open',
    'French Open 2026',
    'Tennis',
    '2026-05-26',
    '2026-06-08',
    'completed',
    ['Alcaraz', 'Sinner', 'Swiatek'],
    'Clay-court marathon — five-set epics, legacy stories, and Roland Garros magic.',
    {
      location: 'Paris, France',
      result: 'Alcaraz def. Sinner 3-2 in the final',
      highlights: ['Five-set final', 'Swiatek third consecutive title', 'Longest rally: 42 shots'],
      analysis: 'The new guard officially owns clay.',
    }
  ),
  evt(
    'evt-ind-aus-series',
    'India vs Australia — ODI Series',
    'Cricket',
    '2026-01-10',
    '2026-01-20',
    'completed',
    ['India', 'Australia'],
    'Border-Gavaskar tension in white-ball format — series recap and player reactions.',
    {
      location: 'India',
      result: 'India won 3-2',
      highlights: ['Kohli century in decider', 'Starc five-wicket haul', 'Super Over thriller'],
    }
  ),
  evt(
    'evt-australian-open',
    'Australian Open 2026',
    'Tennis',
    '2026-01-13',
    '2026-01-26',
    'completed',
    ['Sinner', 'Sabalenka', 'Djokovic'],
    'First Grand Slam of the year — heat, upsets, and Melbourne Park memories.',
    {
      location: 'Melbourne, Australia',
      result: 'Sinner def. Medvedev in the final',
      highlights: ['Midnight marathon semi-final', 'Sabalenka three-peat bid', 'Crowd-favourite run'],
    }
  ),
];

export const eventShorts = [
  { id: 'es-1', eventId: 'evt-ipl-2026', title: 'Final Six — KKR Seal It', sport: 'Cricket', duration: '0:42', thumbnail: IMG.Cricket, views: '1.2M' },
  { id: 'es-2', eventId: 'evt-ucl-final', title: 'Bellingham Winner — UCL', sport: 'Football', duration: '0:55', thumbnail: IMG.Football, views: '2.8M' },
  { id: 'es-3', eventId: 'evt-monaco-gp', title: 'Leclerc Home Win Lap', sport: 'Formula 1', duration: '0:38', thumbnail: IMG['Formula 1'], views: '890K' },
  { id: 'es-4', eventId: 'evt-ind-eng-test', title: 'Kohli Cover Drive — Lord\'s', sport: 'Cricket', duration: '0:28', thumbnail: IMG.Cricket, views: '456K' },
  { id: 'es-5', eventId: 'evt-pl-final-day', title: 'Title-Deciding Goal', sport: 'Football', duration: '0:48', thumbnail: IMG.Football, views: '3.1M' },
  { id: 'es-6', eventId: 'evt-ufc-305', title: 'Round 1 Knockdown', sport: 'MMA', duration: '0:35', thumbnail: IMG.MMA, views: '1.5M' },
  { id: 'es-7', eventId: 'evt-french-open', title: '42-Shot Rally — Final', sport: 'Tennis', duration: '1:12', thumbnail: IMG.Tennis, views: '720K' },
  { id: 'es-8', eventId: 'evt-icc-cwc', title: 'WC Promo — Greatest Catches', sport: 'Cricket', duration: '0:58', thumbnail: IMG.Cricket, views: '210K' },
  { id: 'es-9', eventId: 'evt-world-cup-2026', title: 'Road to 2026 — Best Goals', sport: 'Football', duration: '1:05', thumbnail: IMG.Football, views: '540K' },
  { id: 'es-10', eventId: 'evt-olympics-la', title: 'Bolt\'s Legacy — 9.58', sport: 'Olympics', duration: '0:45', thumbnail: IMG.Olympics, views: '980K' },
];

export const eventStories = [
  { id: 'est-1', eventId: 'evt-icc-cwc', title: 'World Cup Preview: India\'s Quest', sport: 'Cricket', duration: '12 min', thumbnail: IMG.Cricket, type: 'preview' },
  { id: 'est-2', eventId: 'evt-ind-pak', title: 'India vs Pakistan: More Than Cricket', sport: 'Cricket', duration: '18 min', thumbnail: IMG.Cricket, type: 'rivalry' },
  { id: 'est-3', eventId: 'evt-world-cup-2026', title: 'World Cup 2026: North America United', sport: 'Football', duration: '15 min', thumbnail: IMG.Football, type: 'preview' },
  { id: 'est-4', eventId: 'evt-el-clasico', title: 'El Clásico Tactical Breakdown', sport: 'Football', duration: '10 min', thumbnail: IMG.Football, type: 'analysis' },
  { id: 'est-5', eventId: 'evt-wimbledon', title: 'Wimbledon: Grass Court Kings', sport: 'Tennis', duration: '14 min', thumbnail: IMG.Tennis, type: 'legacy' },
  { id: 'est-6', eventId: 'evt-f1-british', title: 'Silverstone: Hamilton\'s Homecoming', sport: 'Formula 1', duration: '11 min', thumbnail: IMG['Formula 1'], type: 'preview' },
  { id: 'est-7', eventId: 'evt-ipl-2026', title: 'IPL Final: KKR\'s Redemption', sport: 'Cricket', duration: '16 min', thumbnail: IMG.Cricket, type: 'reaction' },
  { id: 'est-8', eventId: 'evt-ucl-final', title: 'Madrid Magic: Another UCL Night', sport: 'Football', duration: '13 min', thumbnail: IMG.Football, type: 'reaction' },
  { id: 'est-9', eventId: 'evt-boxing-title', title: 'Undisputed: The Road to Riyadh', sport: 'Boxing', duration: '9 min', thumbnail: IMG.Boxing, type: 'preview' },
  { id: 'est-10', eventId: 'evt-commonwealth', title: 'Commonwealth Games: India\'s Medal Hunt', sport: 'Olympics', duration: '12 min', thumbnail: IMG.Olympics, type: 'preview' },
];

export function getFeaturedEvent() {
  return eventsCatalog.find((e) => e.featured && e.status === 'live')
    || eventsCatalog.find((e) => e.featured)
    || eventsCatalog[0];
}

export function getEventsByStatus(status) {
  return eventsCatalog.filter((e) => e.status === status);
}

export function getEventsBySport(sport) {
  if (!sport || sport === 'All') return eventsCatalog;
  if (sport === 'Combat') return eventsCatalog.filter((e) => e.sport === 'MMA' || e.sport === 'Boxing');
  return eventsCatalog.filter((e) => e.sport === sport);
}

export function getEventById(id) {
  return eventsCatalog.find((e) => e.id === id);
}

export function searchEvents(query) {
  const q = query.trim().toLowerCase();
  if (!q) return eventsCatalog;
  return eventsCatalog.filter(
    (e) =>
      e.eventName.toLowerCase().includes(q) ||
      e.sport.toLowerCase().includes(q) ||
      e.description?.toLowerCase().includes(q) ||
      e.teamsOrPlayers?.some((t) => t.toLowerCase().includes(q)) ||
      e.location?.toLowerCase().includes(q)
  );
}

export function formatEventDate(start, end) {
  const opts = { month: 'short', day: 'numeric', year: 'numeric' };
  const s = new Date(start);
  const e = end ? new Date(end) : null;
  if (!e || start === end) return s.toLocaleDateString('en-US', opts);
  if (s.getMonth() === e.getMonth() && s.getFullYear() === e.getFullYear()) {
    return `${s.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – ${e.getDate()}, ${e.getFullYear()}`;
  }
  return `${s.toLocaleDateString('en-US', opts)} – ${e.toLocaleDateString('en-US', opts)}`;
}
