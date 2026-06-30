import { formatRelativeTime } from '../../dashboard/utils';

export default function RevisionHistoryPanel({ revisions, onRestore, restoring }) {
  if (!revisions?.length) {
    return <p className="text-sm dark:text-untold-muted">Revisions are created on import, reorder, and manual save.</p>;
  }
  return (
    <ul className="space-y-2 max-h-[480px] overflow-y-auto">
      {revisions.map((r) => (
        <li key={r.id} className="flex items-start justify-between gap-3 rounded-lg border dark:border-white/10 px-3 py-2">
          <div className="min-w-0">
            <p className="text-sm font-medium dark:text-white">
              v{r.version}
              {r.label ? <span className="text-untold-muted font-normal"> — {r.label}</span> : null}
            </p>
            <p className="text-[10px] dark:text-untold-muted mt-0.5">
              {r.scene_count} scenes · {r.author_name} · {formatRelativeTime(r.created_at)}
            </p>
          </div>
          <button
            type="button"
            disabled={restoring}
            onClick={() => onRestore(r.id)}
            className="text-xs text-untold-gold hover:underline shrink-0 disabled:opacity-50"
          >
            Restore
          </button>
        </li>
      ))}
    </ul>
  );
}
