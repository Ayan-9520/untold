/** Derive documentary detail metadata from API video — no fabricated episodes. */

export function getDocumentaryExtras(video) {
  if (!video) return null;

  const timeline = video.year
    ? [{ year: video.year, event: `Release — ${video.title}` }]
    : [];

  return {
    synopsis: video.description || '',
    episodes: null,
    timeline,
    cast: [{ role: 'Production', name: 'UNTOLD Originals' }],
    sources: ['UNTOLD Research Desk — fact-checked editorial'],
    gallery: [video.image, video.thumbnail].filter(Boolean),
    genres: [video.category, video.sport, video.format, video.videoType].filter(Boolean),
  };
}
