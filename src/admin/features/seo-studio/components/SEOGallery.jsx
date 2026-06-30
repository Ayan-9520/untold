import { useState } from 'react';
import JobStatusBadge from '../../ai-studio/components/JobStatusBadge';
import { JOB_STATUS_STYLES, APPROVAL_STYLES } from '../constants';
import SEOVariantDetail from './SEOVariantDetail';

function ProgressBar({ progress, stage }) {
  const pct = Math.min(100, Math.max(0, progress || 0));
  return (
    <div className="space-y-1">
      <div className="h-1.5 rounded-full bg-black/40 overflow-hidden">
        <div className="h-full bg-untold-gold transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      {stage && <p className="text-[10px] dark:text-untold-muted capitalize">{stage.replace(/_/g, ' ')} · {pct}%</p>}
    </div>
  );
}

function VariantCard({ variant, selected, onSelect, expanded, onToggleExpand }) {
  return (
    <div className={`rounded-lg border p-3 space-y-2 text-xs ${selected ? 'border-untold-gold' : 'dark:border-white/10'}`}>
      <div className="flex justify-between items-center">
        <span className="font-medium dark:text-white">{variant.label}</span>
        <span className="text-untold-gold font-bold">{variant.seo_score}/100</span>
      </div>
      <p className="dark:text-white font-medium line-clamp-2">{variant.youtube_title}</p>
      <p className="dark:text-untold-muted line-clamp-2">{variant.description}</p>
      {variant.suggestions?.length > 0 && (
        <ul className="text-[10px] text-amber-400/90 list-disc pl-4">
          {variant.suggestions.slice(0, 2).map((s, i) => <li key={i}>{s}</li>)}
        </ul>
      )}
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={onSelect} className="text-untold-gold hover:underline">
          {selected ? '✓ Selected' : 'Select variant'}
        </button>
        <button type="button" onClick={onToggleExpand} className="dark:text-untold-muted hover:underline">
          {expanded ? 'Hide details' : 'View all fields'}
        </button>
      </div>
      <SEOVariantDetail variant={variant} expanded={expanded} />
    </div>
  );
}

export function SEOGallery({ jobs, mutations }) {
  const [expandedId, setExpandedId] = useState(null);

  if (!jobs?.length) return <p className="text-sm dark:text-untold-muted text-center py-8">No SEO packs yet</p>;

  const handleExport = async (jobId, variantId) => {
    const data = await mutations.exportPack(jobId, variantId);
    const blob = new Blob([JSON.stringify(data.pack, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `seo-pack-${jobId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {jobs.map((job) => {
        const statusClass = JOB_STATUS_STYLES[job.status] || JOB_STATUS_STYLES.queued;
        const approvalClass = APPROVAL_STYLES[job.approval_status] || APPROVAL_STYLES.none;
        const selectedId = job.selected_variant_id;

        return (
          <article key={job.id} className={`rounded-xl border p-4 space-y-3 ${statusClass.split(' ').slice(1).join(' ') || 'dark:border-white/10'}`}>
            <div className="flex justify-between gap-2">
              <div>
                <p className="text-sm font-medium dark:text-white">{job.topic || job.prompt}</p>
                <p className="text-[10px] dark:text-untold-muted capitalize">
                  {job.content_type} · Best score {job.seo_score ?? '—'}/100
                  {job.target_keyword ? ` · "${job.target_keyword}"` : ''}
                </p>
              </div>
              <div className="text-right space-y-1">
                <JobStatusBadge status={job.status} />
                <p className={`text-[10px] capitalize ${approvalClass}`}>Approval: {job.approval_status}</p>
              </div>
            </div>
            {job.variants?.length > 0 && (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {job.variants.map((v) => (
                  <VariantCard
                    key={v.id}
                    variant={v}
                    selected={v.id === selectedId || v.is_selected}
                    expanded={expandedId === v.id}
                    onToggleExpand={() => setExpandedId(expandedId === v.id ? null : v.id)}
                    onSelect={() => mutations.selectVariant.mutate({ id: job.id, variantId: v.id })}
                  />
                ))}
              </div>
            )}
            {job.status === 'completed' && (
              <div className="flex flex-wrap gap-2 text-[10px]">
                <button type="button" onClick={() => handleExport(job.id, selectedId)} className="text-untold-gold hover:underline">Export JSON</button>
                {job.project_id && (
                  <button type="button" onClick={() => mutations.applyToProject.mutate({ id: job.id, projectId: job.project_id, variantId: selectedId })} className="text-untold-gold hover:underline">
                    Apply to project
                  </button>
                )}
                <button type="button" onClick={() => mutations.requestApproval.mutate({ id: job.id, data: { project_id: job.project_id } })} className="text-untold-gold hover:underline">Request approval</button>
                <button type="button" onClick={() => mutations.approve.mutate({ id: job.id, data: {} })} className="text-emerald-400 hover:underline">Approve</button>
                <button type="button" onClick={() => mutations.reject.mutate({ id: job.id, data: {} })} className="text-red-400 hover:underline">Reject</button>
              </div>
            )}
            {(job.status === 'failed' || job.status === 'cancelled') && (
              <button type="button" onClick={() => mutations.retryJob.mutate(job.id)} className="text-[10px] text-untold-gold hover:underline">Retry</button>
            )}
          </article>
        );
      })}
    </div>
  );
}

export function SEOQueuePanel({ queue, mutations }) {
  const items = [...(queue?.queued || []), ...(queue?.running || [])];
  if (!items.length) return <p className="text-sm dark:text-untold-muted">Queue empty</p>;
  return (
    <ul className="space-y-3">
      {items.map((j) => (
        <li key={j.id} className="rounded-lg border dark:border-white/10 px-3 py-3 space-y-2">
          <div className="flex justify-between gap-2 text-xs">
            <span className="dark:text-untold-muted truncate">{j.topic || j.prompt}</span>
            <JobStatusBadge status={j.status} />
            {(j.status === 'queued' || j.status === 'running') && (
              <button type="button" onClick={() => mutations.cancelJob.mutate(j.id)} className="text-red-400">Cancel</button>
            )}
          </div>
          {j.status === 'running' && (
            <ProgressBar progress={j.progress ?? j.output_meta?.progress} stage={j.stage ?? j.output_meta?.stage} />
          )}
        </li>
      ))}
    </ul>
  );
}
