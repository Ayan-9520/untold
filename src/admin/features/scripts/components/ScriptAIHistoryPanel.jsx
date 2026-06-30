import { formatRelativeTime } from '../../dashboard/utils';
import { ALL_SCRIPT_ACTIONS } from '../constants';
import { sanitizeHtml } from '../../../../utils/sanitizeHtml';

export default function ScriptAIHistoryPanel({ history }) {
  if (!history?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No AI generations yet</p>;
  }

  return (
    <ul className="space-y-2 max-h-[28rem] overflow-y-auto">
      {history.map((h) => {
        const label = ALL_SCRIPT_ACTIONS.find((a) => a.id === h.action)?.label || h.action;
        return (
          <li key={h.id} className="rounded-lg border dark:border-white/10 px-3 py-2 text-xs">
            <div className="flex justify-between gap-2">
              <span className="text-untold-gold">{label}</span>
              <span className="dark:text-untold-muted shrink-0">
                {h.provider}
                {h.generation_id ? ` · #${h.generation_id}` : ''}
                {' · '}
                {formatRelativeTime(h.created_at)}
              </span>
            </div>
            {h.prompt && <p className="dark:text-untold-muted mt-1 truncate">{h.prompt}</p>}
            {h.result_preview && (
              <p className="dark:text-untold-muted/80 mt-1 line-clamp-2" dangerouslySetInnerHTML={{ __html: sanitizeHtml(h.result_preview) }} />
            )}
          </li>
        );
      })}
    </ul>
  );
}
