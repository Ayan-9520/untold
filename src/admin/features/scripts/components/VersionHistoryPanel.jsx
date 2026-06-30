import { formatRelativeTime } from '../../dashboard/utils';

export default function VersionHistoryPanel({ versions, onRestore, restoring }) {
  if (!versions?.length) {
    return <p className="text-sm dark:text-untold-muted">No saved versions yet.</p>;
  }
  return (
    <ul className="space-y-2">
      {versions.map((v) => (
        <li key={v.id} className="flex items-start justify-between gap-3 rounded-lg border dark:border-white/10 px-3 py-2">
          <div className="min-w-0">
            <p className="text-sm font-medium dark:text-white">
              v{v.version}
              {v.snapshot_label ? <span className="text-untold-muted font-normal"> — {v.snapshot_label}</span> : null}
            </p>
            <p className="text-[10px] dark:text-untold-muted mt-0.5">
              {v.author_name} · {formatRelativeTime(v.created_at)}
            </p>
          </div>
          <button
            type="button"
            disabled={restoring}
            onClick={() => onRestore(v.id)}
            className="text-xs text-untold-gold hover:underline shrink-0 disabled:opacity-50"
          >
            Restore
          </button>
        </li>
      ))}
    </ul>
  );
}
