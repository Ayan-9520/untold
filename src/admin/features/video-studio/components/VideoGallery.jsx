import JobStatusBadge from '../../ai-studio/components/JobStatusBadge';
import { JOB_STATUS_STYLES } from '../constants';

function ProgressBar({ progress, stage }) {
  const pct = Math.min(100, Math.max(0, progress || 0));
  return (
    <div className="space-y-1">
      <div className="h-1.5 rounded-full bg-black/40 overflow-hidden">
        <div className="h-full bg-untold-gold transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      {stage && <p className="text-[10px] dark:text-untold-muted capitalize">{stage} · {pct}%</p>}
    </div>
  );
}

export function VideoPreview({ job }) {
  const mime = job.mime_type || job.output_meta?.mime_type;
  const url = job.result_url;
  const poster = job.preview_url || job.output_meta?.poster_url;

  if (job.status === 'completed' && url) {
    if (mime?.startsWith('video/')) {
      return (
        <video src={url} poster={poster} controls className="w-full rounded-lg border dark:border-white/10 max-h-48 bg-black/40" />
      );
    }
    if (mime === 'text/html' || job.output_meta?.format === 'html_motion') {
      return (
        <iframe
          title={job.prompt}
          src={url}
          className="w-full h-48 rounded-lg border dark:border-white/10 bg-black/40"
          sandbox="allow-scripts"
        />
      );
    }
    if (poster) {
      return <img src={poster} alt={job.prompt} className="w-full rounded-lg border dark:border-white/10 max-h-48 object-contain bg-black/40" />;
    }
    return <img src={url} alt={job.prompt} className="w-full rounded-lg border dark:border-white/10 max-h-48 object-contain bg-black/40" />;
  }

  if (poster && job.status === 'running') {
    return (
      <div className="relative">
        <img src={poster} alt="" className="w-full rounded-lg border dark:border-white/10 max-h-48 object-contain bg-black/40 opacity-60" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs text-white bg-black/60 px-2 py-1 rounded">Rendering…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-32 rounded-lg border dark:border-white/10 bg-black/30 flex items-center justify-center text-xs dark:text-untold-muted px-3 text-center">
      {job.status === 'failed' ? job.error?.slice(0, 120) : job.status}
    </div>
  );
}

function VideoCard({ job, onSave, onDownload, onRetry }) {
  const statusClass = JOB_STATUS_STYLES[job.status] || JOB_STATUS_STYLES.queued;
  const isActive = job.status === 'queued' || job.status === 'running';

  return (
    <article className={`rounded-xl border p-3 space-y-3 ${statusClass.split(' ').slice(1).join(' ') || 'dark:border-white/10'}`}>
      <VideoPreview job={job} />
      {isActive && <ProgressBar progress={job.progress ?? job.output_meta?.progress} stage={job.stage ?? job.output_meta?.stage} />}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs font-medium dark:text-white capitalize">{job.video_type?.replace(/_/g, ' ')}</p>
          <p className="text-[10px] dark:text-untold-muted line-clamp-2 mt-0.5">{job.prompt}</p>
          {job.duration_seconds && (
            <p className="text-[10px] dark:text-untold-muted mt-0.5">{job.duration_seconds}s · {job.aspect_ratio}</p>
          )}
        </div>
        <JobStatusBadge status={job.status} />
      </div>
      <div className="flex flex-wrap gap-2 text-[10px]">
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

export function VideoGallery({ jobs, mutations, getDownloadUrl }) {
  if (!jobs?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No videos yet</p>;
  }
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {jobs.map((job) => (
        <VideoCard
          key={job.id}
          job={job}
          onSave={(id) => mutations.saveToAsset.mutate(id)}
          onDownload={getDownloadUrl}
          onRetry={(id) => mutations.retryJob.mutate(id)}
        />
      ))}
    </div>
  );
}

export function VideoQueuePanel({ queue, mutations }) {
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
          <p className="text-[10px] dark:text-untold-muted capitalize">{j.video_type?.replace(/_/g, ' ')}</p>
          {j.status === 'running' && (
            <ProgressBar progress={j.progress ?? j.output_meta?.progress} stage={j.stage ?? j.output_meta?.stage} />
          )}
        </li>
      ))}
    </ul>
  );
}
