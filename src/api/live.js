import client from './client';
import { getWsBase } from '../config/runtime';

const WS_BASE = getWsBase();

export function normalizeMatch(item) {
  if (!item) return null;
  const teams = item.teamsOrPlayers || item.teams_or_players || [];
  const score = item.score || {};
  return {
    id: item.id,
    dbId: item.db_id || item.dbId,
    eventName: item.eventName || item.event_name,
    sport: item.sport,
    teamsOrPlayers: teams,
    score: {
      home: score.home,
      away: score.away,
      display: score.display || `${score.home || 0} - ${score.away || 0}`,
    },
    status: item.status,
    timer: item.timer,
    thumbnail: item.thumbnail || item.thumbnail_url,
    location: item.location,
    league: item.league,
    featured: item.featured ?? false,
    commentary: item.commentary,
    eventUpdates: item.eventUpdates || item.event_updates,
  };
}

function normalizeList(items = []) {
  return items.map(normalizeMatch).filter(Boolean);
}

export const liveApi = {
  async getOverview() {
    const { data } = await client.get('/live');
    return {
      featured: normalizeMatch(data.featured),
      matches: normalizeList(data.matches),
      source: 'api',
    };
  },

  async getFeatured() {
    const { data } = await client.get('/live/featured');
    return { data: normalizeMatch(data), source: 'api' };
  },

  async getMatches(sport) {
    const { data } = await client.get('/live/matches', { params: { sport: sport === 'All' ? undefined : sport } });
    return { data: normalizeList(data.items), source: 'api' };
  },

  async getMatch(id) {
    const { data } = await client.get(`/live/matches/${id}`);
    return { data: normalizeMatch(data), source: 'api' };
  },

  async getEvents(matchId) {
    const { data } = await client.get(`/live/matches/${matchId}/events`);
    return { data: data.items || [], source: 'api' };
  },

  async getCommentary(matchId) {
    const { data } = await client.get(`/live/matches/${matchId}/commentary`);
    const items = (data.items || []).map((c, i) => ({
      id: c.id || `c-${i}`,
      text: c.text || c.ai_text,
      minute: c.minute || c.time,
      time: c.time || c.minute,
      type: c.type || 'commentary',
    }));
    return { data: items, source: 'api' };
  },

  async getHighlights(limit = 12) {
    const { data } = await client.get('/live/matches', { params: { limit } });
    const items = (data.items || []).slice(0, limit);
    return { data: normalizeList(items), source: 'api' };
  },

  async getUpdates(limit = 20) {
    const { data: matches } = await this.getMatches();
    const updates = [];
    for (const m of matches.slice(0, 5)) {
      const { data: events } = await this.getEvents(m.id);
      events.forEach((e, i) => {
        updates.push({
          ...e,
          id: `${m.id}-u${i}`,
          matchId: m.id,
          eventName: m.eventName,
          sport: m.sport,
          aiText: e.raw,
        });
      });
    }
    return { data: updates.slice(0, limit), source: 'api' };
  },

  connectLive(onMessage) {
    const ws = new WebSocket(`${WS_BASE}/ws/live`);
    ws.onopen = () => ws.send('ping');
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        onMessage?.(payload);
      } catch {
        /* ignore */
      }
    };
    return () => ws.close();
  },

  async generateCommentary(rawEvent) {
    const { data } = await client.post('/live/commentary/generate', { raw_event: rawEvent });
    return data;
  },
};

export default liveApi;
