/** Shows whether Studio data is live from API or offline fallback. */
export default function StudioLiveBadge({ live, className = '' }) {
  return (
    <span
      className={`studio-live-badge ${live ? 'studio-live-badge--live' : 'studio-live-badge--offline'} ${className}`}
      title={live ? 'Connected to UNTOLD API' : 'Offline — showing cached demo data'}
    >
      {live ? '● Live' : '○ Offline'}
    </span>
  );
}
