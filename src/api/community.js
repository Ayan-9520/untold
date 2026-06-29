import client from './client';
import {
  FAN_DNA_DEFAULT,
  DEBATE_ARENAS,
  FAN_WARS,
  PREDICTION_EVENTS,
  PREDICTION_LEADERBOARD,
} from '../data/fanCatalog';

export const communityApi = {
  async getFanDNA() {
    try {
      const { data } = await client.get('/community/fan-dna');
      return data;
    } catch {
      return FAN_DNA_DEFAULT;
    }
  },

  async getDebates() {
    try {
      const { data } = await client.get('/community/debates');
      return data.items || DEBATE_ARENAS;
    } catch {
      return DEBATE_ARENAS;
    }
  },

  async getFanWars() {
    try {
      const { data } = await client.get('/community/fan-wars');
      return data.items || FAN_WARS;
    } catch {
      return FAN_WARS;
    }
  },

  async voteFanWar(warId, side) {
    try {
      const { data } = await client.post('/community/fan-wars/vote', { war_id: warId, side });
      return data;
    } catch {
      return { ok: true, war_id: warId, side };
    }
  },

  async getPredictions() {
    try {
      const { data } = await client.get('/community/predictions');
      return data;
    } catch {
      return { events: PREDICTION_EVENTS, leaderboard: PREDICTION_LEADERBOARD };
    }
  },

  async submitPrediction(eventId, answers) {
    try {
      const { data } = await client.post('/community/predictions', { event_id: eventId, answers });
      return data;
    } catch {
      return { ok: true, event_id: eventId, points_earned: 50 };
    }
  },

  async getLeaderboard() {
    try {
      const { data } = await client.get('/community/leaderboard');
      return data.items || PREDICTION_LEADERBOARD;
    } catch {
      return PREDICTION_LEADERBOARD;
    }
  },
};
