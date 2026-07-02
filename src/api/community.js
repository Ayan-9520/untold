import client from './client';

function normalizeFanWar(war) {
  return {
    id: war.id,
    title: war.title,
    sport: war.sport,
    status: war.status,
    teamA: war.teamA || war.team_a,
    teamB: war.teamB || war.team_b,
  };
}

function normalizeDebate(debate) {
  return {
    ...debate,
    optionA: debate.optionA || debate.option_a,
    optionB: debate.optionB || debate.option_b,
  };
}

export const communityApi = {
  async getFanDNA() {
    const { data } = await client.get('/community/fan-dna');
    return data;
  },

  async getDebates() {
    const { data } = await client.get('/community/debates');
    return (data.items || []).map(normalizeDebate);
  },

  async getFanWars() {
    const { data } = await client.get('/community/fan-wars');
    return (data.items || []).map(normalizeFanWar);
  },

  async voteFanWar(warId, side) {
    const { data } = await client.post('/community/fan-wars/vote', { war_id: warId, side });
    return data;
  },

  async getPredictions() {
    const { data } = await client.get('/community/predictions');
    return {
      events: data.events || [],
      leaderboard: data.leaderboard || [],
    };
  },

  async submitPrediction(eventId, answers) {
    const { data } = await client.post('/community/predictions', { event_id: eventId, answers });
    return data;
  },

  async getLeaderboard() {
    const { data } = await client.get('/community/leaderboard');
    return data.items || [];
  },
};
