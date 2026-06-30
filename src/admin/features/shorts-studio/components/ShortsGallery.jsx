import JobStatusBadge from '../../ai-studio/components/JobStatusBadge';
import { JOB_STATUS_STYLES } from '../constants';

function ClipPreview({ clip }) {
  if (!clip?.url) return null;
  return (
    <iframe title={clip.platform_label} src={clip.url} className="w-full h-40 rounded-lg border dark:border-white/10 bg-black/40" sandbox="allow-scripts" />
  );
}

export function ShortsGallery({ jobs, mutations, getDownloadUrl }) {
  if (!jobs?.length) return <p className="text-sm dark:text-untold-muted text-center py-8">No shorts yet</p>;
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {jobs.map((job) => {
        const statusClass = JOB_STATUS_STYLES[job.status] || JOB_STATUS_STYLES.queued;
        return (
          <article key={job.id} className={`rounded-xl border p-3 space-y-3 ${statusClass.split(' ').slice(1).join(' ') || 'dark:border-white/10'}`}>
            {job.thumbnail_url && <img src={job.thumbnail_url} alt="" className="w-24 rounded border dark:border-white/10" />}
            {job.clips?.[0] && <ClipPreview clip={job.clips[0]} />}
            <div className="flex justify-between gap-2">
              <p className="text-xs dark:text-white line-clamp-2">{job.topic || job.prompt}</p>
              <JobStatusBadge status={job.status} />
            </div>
            {job.highlights?.length > 0 && (
              <ul className="text-[10px] dark:text-untold-muted space-y-1">
                {job.highlights.slice(0, 3).map((h) => (
                  <li key={h.id}>{h.label} · {h.start_seconds}s ({Math.round(h.score * 100)}%)</li>
                ))}
              </ul>
            )}
            {job.hook && <p className="text-[10px] text-untold-gold/90">Hook: {job.hook}</p>}
            {job.hashtags?.length > 0 && <p className="text-[10px] dark:text-untold-muted">{job.hashtags.join(' ')}</p>}
            <div className="flex flex-wrap gap-2 text-[10px]">
              {job.status === 'completed' && (
                <>
                  <button type="button" onClick={() => mutations.saveToAsset.mutate(job.id)} className="text-untold-gold hover:underline">Save</button>
                  <a href={getDownloadUrl(job.id)} target="_blank" rel="noreferrer" className="text-untold-gold hover:underline">Download</a>
                  {job.project_id && (
                    <button type="button" onClick={() => mutations.queuePublish.mutate({ id: job.id, data: {} })} className="text-untold-gold hover:underline">
                      Queue publish
                    </button>
                  )}
                </>
              )}
              {(job.status === 'failed' || job.status === 'cancelled') && (
                <button type="button" onClick={() => mutations.retryJob.mutate(job.id)} className="text-untold-gold hover:underline">Retry</button>
              )}
            </div>
            {job.publish_queue?.length > 0 && (
              <p className="text-[10px] text-emerald-400">{job.publish_queue.length} publish job(s) queued</p>
            )}
          </article>
        );
      })}
    </div>
  );
}

export function ShortsQueuePanel({ queue, mutations }) {
  const items = [...(queue?.queued || []), ...(queue?.running || [])];
  if (!items.length) return <p className="text-sm dark:text-untold-muted">Queue empty</p>;
  return (
    <ul className="space-y-2">
      {items.map((j) => (
        <li key={j.id} className="flex justify-between gap-2 text-xs rounded-lg border dark:border-white/10 px-3 py-2">
          <span className="dark:text-untold-muted truncate">{j.topic || j.prompt}</span>
          <JobStatusBadge status={j.status} />
          {(j.status === 'queued' || j.status === 'running') && (
            <button type="button" onClick={() => mutations.cancelJob.mutate(j.id)} className="text-red-400">Cancel</button>
          )}
        </li>
      ))}
    </ul>
  );
}
