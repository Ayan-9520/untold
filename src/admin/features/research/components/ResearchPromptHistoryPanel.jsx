import { formatRelativeTime } from '../../dashboard/utils';

export default function ResearchPromptHistoryPanel({ history, onReuse }) {
  if (!history?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-12">No prompts sent to the research agent yet.</p>;
  }

  return (
    <ul className="space-y-3 max-h-[560px] overflow-y-auto">
      {history.map((item) => (
        <li key={item.id} className="rounded-lg border dark:border-white/10 px-4 py-3">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <span className="text-xs font-medium text-untold-gold capitalize">{item.action.replace(/_/g, ' ')}</span>
            <span className="text-[10px] dark:text-untold-muted">
              {item.provider} · {formatRelativeTime(item.created_at)}
            </span>
          </div>
          <p className="text-sm dark:text-white whitespace-pre-wrap font-mono text-xs leading-relaxed">{item.prompt}</p>
          {onReuse && (
            <button
              type="button"
              onClick={() => onReuse(item)}
              className="text-xs text-untold-gold mt-2 hover:underline"
            >
              Use in conversation →
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
