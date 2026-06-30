import { formatRelativeTime } from '../../dashboard/utils';

export default function ResearchHistoryPanel({ history }) {
  if (!history?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No AI interactions yet</p>;
  }
  return (
    <ul className="space-y-2 max-h-96 overflow-y-auto">
      {history.map((h) => (
        <li key={h.id} className="rounded-lg border dark:border-white/10 px-3 py-2 text-xs">
          <div className="flex justify-between gap-2">
            <span className="text-untold-gold capitalize">{h.action.replace('_', ' ')}</span>
            <span className="dark:text-untold-muted">{h.provider} · {formatRelativeTime(h.created_at)}</span>
          </div>
          <p className="dark:text-untold-muted mt-1 truncate">{h.prompt}</p>
        </li>
      ))}
    </ul>
  );
}
