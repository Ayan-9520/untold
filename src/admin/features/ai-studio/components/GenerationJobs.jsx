import JobStatusBadge from './JobStatusBadge';
import { formatRelativeTime } from '../../dashboard/utils';

function JobRow({ job, onRetry, onCancel, actions }) {
  return (
    <li className="rounded-lg border dark:border-white/10 px-3 py-2 space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium dark:text-white capitalize truncate">
            {job.module} · {job.provider}
          </p>
          <p className="text-xs dark:text-untold-muted truncate">{job.prompt}</p>
        </div>
        <JobStatusBadge status={job.status} />
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] dark:text-untold-muted">
        <span>#{job.id} · {formatRelativeTime(job.created_at)}{job.retry_count ? ` · retry ${job.retry_count}` : ''}</span>
        {actions && (
          <div className="flex gap-2">
            {job.status === 'failed' || job.status === 'cancelled' ? (
              <button type="button" onClick={() => onRetry(job.id)} className="text-untold-gold hover:underline">Retry</button>
            ) : null}
            {job.status === 'queued' || job.status === 'running' ? (
              <button type="button" onClick={() => onCancel(job.id)} className="text-red-400 hover:underline">Cancel</button>
            ) : null}
          </div>
        )}
      </div>
      {job.output_text && job.status === 'completed' && (
        <pre className="text-xs dark:text-untold-muted whitespace-pre-wrap max-h-24 overflow-y-auto font-mono bg-black/20 rounded p-2">
          {job.output_text.slice(0, 400)}{job.output_text.length > 400 ? '…' : ''}
        </pre>
      )}
      {job.error && job.status === 'failed' && (
        <p className="text-xs text-red-400">{job.error}</p>
      )}
    </li>
  );
}

export default function GenerationQueue({ queue, onRetry, onCancel }) {
  const all = [...(queue?.running || []), ...(queue?.queued || [])];
  if (!all.length) {
    return <p className="text-sm dark:text-untold-muted">Queue is empty.</p>;
  }
  return (
    <ul className="space-y-2">
      {all.map((job) => (
        <JobRow key={job.id} job={job} onRetry={onRetry} onCancel={onCancel} actions />
      ))}
    </ul>
  );
}

export function GenerationHistory({ history, onRetry, onCancel }) {
  if (!history?.items?.length) {
    return <p className="text-sm dark:text-untold-muted">No generations yet.</p>;
  }
  return (
    <ul className="space-y-2 max-h-[520px] overflow-y-auto">
      {history.items.map((job) => (
        <JobRow key={job.id} job={job} onRetry={onRetry} onCancel={onCancel} actions />
      ))}
    </ul>
  );
}
