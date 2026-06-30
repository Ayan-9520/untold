import { useState } from 'react';
import PlatformPicker from './PlatformPicker';
import SeoMetadataForm from './SeoMetadataForm';
import ThumbnailPicker from './ThumbnailPicker';

export default function SchedulePublishForm({ workspace, onSchedule, scheduling }) {
  const [platform, setPlatform] = useState('originals');
  const [scheduledAt, setScheduledAt] = useState('');
  const [requiresApproval, setRequiresApproval] = useState(true);
  const [seo, setSeo] = useState({
    seo_title: workspace?.seo_title || '',
    seo_description: workspace?.seo_description || '',
    seo_keywords: workspace?.seo_keywords || [],
  });
  const [thumbnail, setThumbnail] = useState(workspace?.thumbnail_url || '');

  const submit = () => {
    onSchedule({
      platform,
      scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : null,
      requires_approval: requiresApproval,
      ...seo,
      thumbnail_url: thumbnail || null,
    });
  };

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs font-semibold dark:text-white mb-2">Publish to</p>
        <PlatformPicker selected={platform} onChange={setPlatform} />
      </div>

      <ThumbnailPicker url={thumbnail} onChange={setThumbnail} />
      <SeoMetadataForm values={seo} onChange={setSeo} />

      <div className="grid sm:grid-cols-2 gap-3">
        <div>
          <label className="text-xs dark:text-untold-muted block mb-1">Schedule (optional)</label>
          <input
            type="datetime-local"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
            className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
          />
        </div>
        <label className="flex items-center gap-2 text-xs dark:text-untold-muted pt-6 cursor-pointer">
          <input
            type="checkbox"
            checked={requiresApproval}
            onChange={(e) => setRequiresApproval(e.target.checked)}
            className="rounded"
          />
          Require approval before publish
        </label>
      </div>

      <button
        type="button"
        disabled={scheduling}
        onClick={submit}
        className="w-full py-2.5 rounded-lg bg-untold-gold text-black text-sm font-semibold disabled:opacity-50"
      >
        {scheduling ? 'Scheduling…' : scheduledAt ? 'Schedule publish' : 'Queue publish'}
      </button>
    </div>
  );
}
