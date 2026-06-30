import { useState } from 'react';
import { Link } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { studioPath, PRODUCTS } from '../../config/ecosystem';
import { useProjects } from '../features/projects/hooks/useProjects';
import {
  usePublishingOverview,
  usePublishingQueue,
  usePublishingMutations,
} from '../features/publishing/hooks/usePublishing';
import PublishingQueueTable from '../features/publishing/components/PublishingQueueTable';
import { PUBLISH_PLATFORMS, VISIBILITY_STATES } from '../features/publishing/constants';

const FEATURES = [
  { icon: '🎬', label: 'UNTOLD Originals' },
  { icon: '▶️', label: 'YouTube' },
  { icon: '📸', label: 'Instagram' },
  { icon: '👤', label: 'Facebook' },
  { icon: '𝕏', label: 'X' },
  { icon: '📅', label: 'Schedule' },
  { icon: '✅', label: 'Approval workflow' },
  { icon: '🔍', label: 'SEO metadata' },
  { icon: '🖼️', label: 'Thumbnail' },
  { icon: '📤', label: 'Publishing queue' },
  { icon: '↻', label: 'Retry failed' },
];

export default function ContentPage() {
  const [queueFilter, setQueueFilter] = useState('');
  const { data: overview, isError } = usePublishingOverview();
  const { data: queue, isLoading: queueLoading } = usePublishingQueue({
    status: queueFilter || undefined,
  });
  const { data: projectsData, isLoading: projectsLoading } = useProjects({ stage: 'publishing', limit: 50 });
  const mutations = usePublishingMutations(null);

  const projects = projectsData?.items || [];

  return (
    <div className="space-y-8 animate-fade-in">
      <StudioPageHeader
        section="Publish"
        title="Publishing CMS"
        description={`Schedule, approve, and publish to ${PRODUCTS.ORIGINALS.name}, YouTube, Instagram, Facebook & X.`}
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>
      <PipelineBar activeStep="publisher" />

      {overview && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {[
            { label: 'Queue', value: overview.total_jobs },
            { label: 'Pending approval', value: overview.pending_approval },
            { label: 'Scheduled', value: overview.scheduled },
            { label: 'Failed', value: overview.failed },
            { label: 'Published', value: overview.published },
          ].map((s) => (
            <div key={s.label} className="ai-stat-card text-center">
              <p className="text-xl font-bold text-untold-gold">{s.value}</p>
              <p className="text-xs dark:text-untold-muted mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {FEATURES.map((f) => (
          <div key={f.label} className="studio-module-card">
            <span className="text-2xl">{f.icon}</span>
            <p className="text-sm font-medium dark:text-white mt-2">{f.label}</p>
          </div>
        ))}
      </div>

      <section className="rounded-xl border dark:border-white/10 p-4 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-semibold dark:text-white">Publishing queue</h2>
          <div className="flex gap-2">
            {['', 'pending_approval', 'scheduled', 'failed', 'published'].map((f) => (
              <button
                key={f || 'all'}
                type="button"
                onClick={() => setQueueFilter(f)}
                className={`text-xs px-2 py-1 rounded-full border ${
                  queueFilter === f ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
                }`}
              >
                {f ? f.replace('_', ' ') : 'All'}
              </button>
            ))}
          </div>
        </div>
        {queueLoading ? (
          <div className="h-32 skeleton rounded-lg" />
        ) : (
          <PublishingQueueTable
            jobs={queue}
            onApprove={(id) => mutations.approveJob.mutate({ jobId: id })}
            onReject={(id) => mutations.rejectJob.mutate({ jobId: id })}
            onRetry={(id) => mutations.retryJob.mutate(id)}
          />
        )}
      </section>

      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold dark:text-white">Publishing workspaces</h2>
          <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">All projects →</Link>
        </div>
        {projectsLoading ? (
          <div className="h-32 skeleton rounded-xl" />
        ) : projects.length === 0 ? (
          <div className="rounded-xl border dark:border-white/10 p-8 text-center">
            <p className="text-sm dark:text-untold-muted">No projects in publishing stage.</p>
            <Link to={studioPath('projects')} className="text-sm text-untold-gold mt-2 inline-block">Move a project to publishing →</Link>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={studioPath(`content/${p.id}`)}
                className="studio-production-row hover:border-untold-gold/30 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium dark:text-white text-sm truncate">{p.title}</p>
                  <p className="text-xs dark:text-untold-muted mt-0.5 capitalize">
                    {p.publishing_status || 'draft'} · {p.assignee}
                  </p>
                </div>
                <span className="text-xs text-untold-gold shrink-0">Configure publish →</span>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="grid sm:grid-cols-2 gap-4">
        <div className="rounded-xl border dark:border-white/10 p-4">
          <p className="text-xs font-semibold dark:text-white mb-3">Platforms</p>
          <ul className="space-y-2">
            {PUBLISH_PLATFORMS.map((p) => (
              <li key={p.id} className="flex justify-between text-xs dark:text-untold-muted">
                <span>{p.icon} {p.label}</span>
                <span>{overview?.platform_counts?.[p.id] ?? 0} jobs</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border dark:border-white/10 p-4">
          <p className="text-xs font-semibold dark:text-white mb-3">Visibility</p>
          <ul className="space-y-2">
            {VISIBILITY_STATES.map((v) => (
              <li key={v.id} className="flex justify-between text-xs dark:text-untold-muted">
                <span>{v.label}</span>
                <span>{overview?.visibility_counts?.[v.id] ?? 0} projects</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
