import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import StudioSectionLoader from '../components/StudioSectionLoader';
import { useStudioAssets } from '../hooks/useStudioData';

const FALLBACK_CATEGORIES = [
  { icon: '📷', label: 'Photos', count: 0 },
  { icon: '🎬', label: 'Videos', count: 0 },
  { icon: '🎵', label: 'Music', count: 0 },
  { icon: '🏷️', label: 'Logos', count: 48 },
  { icon: '🔊', label: 'Sound effects', count: 0 },
  { icon: '🚁', label: 'Drone footage', count: 0 },
  { icon: '📼', label: 'Archive', count: 0 },
];

export default function AssetsPage() {
  const { data, loading, live } = useStudioAssets();
  const categories = data?.categories || FALLBACK_CATEGORIES;

  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Produce"
        title="Asset Library"
        description="Central store for photos, footage, music, logos, and archive media used across productions."
      >
        <StudioLiveBadge live={live} />
      </StudioPageHeader>
      <PipelineBar activeStep="video" />

      {data && (
        <p className="text-xs dark:text-untold-muted light:text-gray-500">
          {data.total_items.toLocaleString()} items · {data.video_count} linked to OTT catalog
        </p>
      )}

      {loading ? (
        <StudioSectionLoader rows={3} />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {categories.map((cat) => (
            <article key={cat.label} className="studio-module-card">
              <span className="text-2xl">{cat.icon}</span>
              <p className="text-sm font-semibold dark:text-white light:text-black mt-3">{cat.label}</p>
              <p className="text-xs text-untold-gold mt-1">{cat.count.toLocaleString()} items</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
