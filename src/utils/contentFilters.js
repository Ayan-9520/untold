/** Helpers for sport/category filter bars */

export function buildSportCounts(items, sportKey = 'sport') {
  const counts = { All: items.length };
  items.forEach((item) => {
    const sport = item[sportKey];
    if (sport) counts[sport] = (counts[sport] || 0) + 1;
  });
  return counts;
}

export function getSportsFromItems(items, sportKey = 'sport') {
  return ['All', ...[...new Set(items.map((i) => i[sportKey]).filter(Boolean))].sort()];
}

export function toSportOptions(sports, counts = {}, extras = {}) {
  return sports.map((sport) => ({
    value: sport,
    label: sport,
    count: sport !== 'All' ? counts[sport] : undefined,
    ...extras[sport],
  }));
}

export function filterBySport(items, sport, sportKey = 'sport') {
  if (!sport || sport === 'All') return items;
  return items.filter((item) => item[sportKey] === sport);
}
