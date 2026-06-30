import { formatRelativeTime } from '../../dashboard/utils';

const STATUS_COLORS = {
  queued: 'text-yellow-400',
  processing: 'text-blue-400',
  completed: 'text-emerald-400',
  failed: 'text-red-400',
};

export default function ExportQueuePanel({ exports, onExport, exporting }) {
  return (
    <div className="rounded-xl border dark:border-white/10 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold dark:text-white">Export queue</p>
        <button
          type="button"
          disabled={exporting}
          onClick={() => onExport({ format: 'mp4', resolution: '1080p' })}
          className="text-xs text-untold-gold hover:underline disabled:opacity-40"
        >
          + Queue MP4
        </button>
      </div>
      {!exports?.length ? (
        <p className="text-xs dark:text-untold-muted">No exports yet</p>
      ) : (
        <ul className="space-y-2 max-h-40 overflow-y-auto">
          {exports.map((job) => (
            <li key={job.id} className="flex items-center justify-between text-xs dark:text-untold-muted">
              <span>
                <span className={STATUS_COLORS[job.status] || ''}>{job.status}</span>
                {' · '}{job.format.toUpperCase()} · {job.progress}%
              </span>
              <span className="flex items-center gap-2">
                {job.output_url && job.status === 'completed' && (
                  <a href={job.output_url} className="text-untold-gold hover:underline" download>Download</a>
                )}
                <span>{formatRelativeTime(job.created_at)}</span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
