import { useState } from 'react';
import SeoMetadataForm from './SeoMetadataForm';
import ThumbnailPicker from './ThumbnailPicker';
import VisibilitySelect from './VisibilitySelect';
import SchedulePublishForm from './SchedulePublishForm';
import PublishingQueueTable from './PublishingQueueTable';
import { usePublishingMutations } from '../hooks/usePublishing';

const TABS = ['package', 'schedule', 'jobs'];

export default function PublishingWorkspace({ workspace }) {
  const [tab, setTab] = useState('package');
  const [pkg, setPkg] = useState({
    seo_title: workspace.seo_title || '',
    seo_description: workspace.seo_description || '',
    seo_keywords: workspace.seo_keywords || [],
    thumbnail_url: workspace.thumbnail_url || '',
    visibility: workspace.visibility || 'draft',
  });

  const mutations = usePublishingMutations(workspace.project_id);

  const savePackage = () => mutations.updatePackage.mutate(pkg);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2 items-center justify-between">
        <VisibilitySelect
          value={pkg.visibility}
          onChange={(v) => {
            setPkg({ ...pkg, visibility: v });
            mutations.updatePackage.mutate({ visibility: v });
          }}
        />
        <button
          type="button"
          onClick={savePackage}
          disabled={mutations.updatePackage.isPending}
          className="text-xs px-3 py-1.5 rounded-lg border dark:border-white/10 text-untold-gold"
        >
          Save metadata
        </button>
      </div>

      <div className="flex gap-1 border-b dark:border-white/10">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-3 py-2 text-xs capitalize border-b-2 -mb-px ${
              tab === t ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
            }`}
          >
            {t === 'jobs' ? `Jobs (${workspace.jobs?.length || 0})` : t}
          </button>
        ))}
      </div>

      {tab === 'package' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <ThumbnailPicker url={pkg.thumbnail_url} onChange={(url) => setPkg({ ...pkg, thumbnail_url: url })} />
          <SeoMetadataForm values={pkg} onChange={setPkg} />
        </div>
      )}

      {tab === 'schedule' && (
        <SchedulePublishForm
          workspace={workspace}
          scheduling={mutations.schedule.isPending}
          onSchedule={(data) => mutations.schedule.mutate(data, { onSuccess: () => setTab('jobs') })}
        />
      )}

      {tab === 'jobs' && (
        <PublishingQueueTable
          jobs={workspace.jobs}
          onApprove={(id) => mutations.approveJob.mutate({ jobId: id })}
          onReject={(id) => mutations.rejectJob.mutate({ jobId: id })}
          onRetry={(id) => mutations.retryJob.mutate(id)}
        />
      )}

      {workspace.pending_approvals > 0 && (
        <p className="text-xs text-yellow-400">
          {workspace.pending_approvals} job(s) awaiting approval
        </p>
      )}
    </div>
  );
}
