import client from './client';

export const streamingApi = {
  async getStreamUrl(videoId) {
    const { data } = await client.get(`/stream/${videoId}`);
    return data;
  },

  async saveProgress(videoId, positionSeconds, durationSeconds) {
    const { data } = await client.post('/watch-progress', {
      video_id: videoId,
      position_seconds: Math.floor(positionSeconds),
      duration_seconds: durationSeconds ? Math.floor(durationSeconds) : undefined,
    });
    return data;
  },

  async getContinueWatching(limit = 12) {
    try {
      const { data } = await client.get('/continue-watching', { params: { limit } });
      return data;
    } catch {
      return [];
    }
  },
};

export async function downloadMagazine(issueId) {
  const { data } = await client.post(`/magazine/issues/${issueId}/download`);
  return data;
}

export default streamingApi;
