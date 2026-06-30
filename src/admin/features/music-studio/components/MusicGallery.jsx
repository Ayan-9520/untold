import JobStatusBadge from '../../ai-studio/components/JobStatusBadge';
import { JOB_STATUS_STYLES, MUSIC_CATEGORIES } from '../constants';

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

function catLabel(id) {
  return MUSIC_CATEGORIES.find((c) => c.id === id)?.label || id;
}

function MusicCard({ job, onFavorite, onSave, onDownload, onRetry }) {
  const statusClass = JOB_STATUS_STYLES[job.status] || JOB_STATUS_STYLES.queued;

  return (
    <article className={`rounded-xl border p-3 space-y-3 ${statusClass.split(' ').slice(1).join(' ') || 'dark:border-white/10'}`}>
      {job.status === 'completed' && job.result_url ? (
        <audio controls src={job.result_url} loop={job.loop} className="w-full" />
      ) : (
        <div className="h-16 rounded-lg border dark:border-white/10 bg-black/30 flex items-center justify-center text-xs dark:text-untold-muted px-3 text-center">
          {job.status === 'failed' ? job.error?.slice(0, 120) : job.status}
        </div>
      )}
      {(job.status === 'queued' || job.status === 'running') && (
        <ProgressBar progress={job.progress ?? job.output_meta?.progress} stage={job.stage ?? job.output_meta?.stage} />
      )}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs font-medium dark:text-white">{catLabel(job.category)}</p>
          <p className="text-[10px] dark:text-untold-muted line-clamp-2 mt-0.5">{job.prompt}</p>
          <p className="text-[10px] dark:text-untold-muted mt-0.5">
            {job.duration_seconds}s
            {job.loop ? ' · loop' : ''}
            {job.bpm || job.output_meta?.bpm ? ` · ${job.bpm || job.output_meta?.bpm} BPM` : ''}
          </p>
        </div>
        <JobStatusBadge status={job.status} />
      </div>
      <div className="flex flex-wrap gap-2 text-[10px]">
        <button type="button" onClick={() => onFavorite(job.id)} className="text-untold-gold hover:underline">
          {job.is_favorite ? '★ Favorited' : '☆ Favorite'}
        </button>
        {job.status === 'completed' && (
          <>
            <button type="button" onClick={() => onSave(job.id)} className="text-untold-gold hover:underline">Save to assets</button>
            <a href={onDownload(job.id)} target="_blank" rel="noreferrer" className="text-untold-gold hover:underline">Download</a>
          </>
        )}
        {(job.status === 'failed' || job.status === 'cancelled') && (
          <button type="button" onClick={() => onRetry(job.id)} className="text-untold-gold hover:underline">Retry</button>
        )}
      </div>
    </article>
  );
}

export function MusicGallery({ jobs, mutations, getDownloadUrl }) {
  if (!jobs?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No tracks yet</p>;
  }
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {jobs.map((job) => (
        <MusicCard
          key={job.id}
          job={job}
          onFavorite={(id) => mutations.toggleFavorite.mutate(id)}
          onSave={(id) => mutations.saveToAsset.mutate(id)}
          onDownload={getDownloadUrl}
          onRetry={(id) => mutations.retryJob.mutate(id)}
        />
      ))}
    </div>
  );
}

export function MusicQueuePanel({ queue, mutations }) {
  const items = [...(queue?.queued || []), ...(queue?.running || [])];
  if (!items.length) return <p className="text-sm dark:text-untold-muted">Queue empty</p>;
  return (
    <ul className="space-y-3">
      {items.map((j) => (
        <li key={j.id} className="rounded-lg border dark:border-white/10 px-3 py-3 space-y-2">
          <div className="flex justify-between gap-2 text-xs">
            <span className="dark:text-untold-muted truncate flex-1">{j.prompt}</span>
            <JobStatusBadge status={j.status} />
            {(j.status === 'queued' || j.status === 'running') && (
              <button type="button" onClick={() => mutations.cancelJob.mutate(j.id)} className="text-red-400 shrink-0">Cancel</button>
            )}
          </div>
          <p className="text-[10px] dark:text-untold-muted">{catLabel(j.category)} · {j.duration_seconds}s</p>
          {j.status === 'running' && (
            <ProgressBar progress={j.progress ?? j.output_meta?.progress} stage={j.stage ?? j.output_meta?.stage} />
          )}
        </li>
      ))}
    </ul>
  );
}
