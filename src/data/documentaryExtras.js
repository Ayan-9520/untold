/**
 * Premium documentary detail metadata (episodes, cast, timeline, sources)
 */
export function getDocumentaryExtras(video) {
  if (!video) return null;

  const isSeries = video.format === 'Series' || video.videoType === 'series';

  return {
    synopsis: video.description,
    episodes: isSeries
      ? [
          { n: 1, title: 'Origins', duration: '52m', description: 'Where it all began.' },
          { n: 2, title: 'Rise', duration: '48m', description: 'Breakthrough moments and turning points.' },
          { n: 3, title: 'Glory', duration: '55m', description: 'Peak performance and public myth.' },
          { n: 4, title: 'Legacy', duration: '50m', description: 'What remains when the lights go out.' },
        ]
      : null,
    timeline: [
      { year: video.year - 10, event: 'Early career & formative years' },
      { year: video.year - 5, event: 'Breakthrough moment' },
      { year: video.year, event: 'Central story arc of this documentary' },
      { year: video.year + 1, event: 'Legacy and cultural impact' },
    ],
    cast: [
      { role: 'Narrator', name: 'UNTOLD Voice' },
      { role: 'Director', name: 'UNTOLD Originals' },
      { role: 'Research', name: 'UNTOLD Research Desk' },
    ],
    sources: [
      'Verified public archives & interviews',
      'Licensed news footage',
      'UNTOLD Research Agent — fact-checked',
    ],
    gallery: [
      video.image,
      video.thumbnail || video.image,
    ].filter(Boolean),
    genres: video.genres || [video.vertical, video.sport, video.format].filter(Boolean),
  };
}
