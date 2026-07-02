import client from './client';

export async function fetchEventsOverview({ sport, search } = {}) {
  const params = {};
  if (sport && sport !== 'All') params.sport = sport;
  if (search?.trim()) params.search = search.trim();
  const { data } = await client.get('/events', { params });
  return data;
}

export default { fetchEventsOverview };
