import { formatRelativeTime } from '../../dashboard/utils';
import ResearchAgentPanel from './ResearchAgentPanel';

function outputPreview(response) {
  if (!response) return '';
  if (response.summary) return response.summary;
  if (response.suggestions?.length) return response.suggestions.join('\n');
  return JSON.stringify(response, null, 2).slice(0, 1200);
}

export default function ResearchConversationPanel({
  history,
  providers,
  running,
  summary,
  followUps,
  preferences,
  onRun,
  onReusePrompt,
  initialPrompt = '',
}) {
  const thread = [...(history || [])].reverse();

  return (
    <div className="grid lg:grid-cols-[1fr_340px] gap-6">
      <div className="space-y-4 max-h-[560px] overflow-y-auto pr-1">
        {thread.length === 0 && (
          <p className="text-sm dark:text-untold-muted text-center py-12">
            Start a conversation with the research agent — prompts and responses appear here.
          </p>
        )}
        {thread.map((item) => (
          <div key={item.id} className="space-y-2">
            <div className="rounded-lg border dark:border-white/10 bg-white/5 px-3 py-2 ml-8">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-[10px] uppercase tracking-wide text-untold-gold">You</span>
                <span className="text-[10px] dark:text-untold-muted">{formatRelativeTime(item.created_at)}</span>
              </div>
              <p className="text-sm dark:text-white whitespace-pre-wrap">{item.prompt}</p>
              <button
                type="button"
                onClick={() => onReusePrompt?.(item)}
                className="text-[10px] text-untold-gold mt-2 hover:underline"
              >
                Reuse prompt
              </button>
            </div>
            <div className="rounded-lg border border-untold-gold/20 bg-untold-gold/5 px-3 py-2 mr-8">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-[10px] uppercase tracking-wide text-untold-gold">
                  Agent · {item.action.replace(/_/g, ' ')}
                </span>
                <span className="text-[10px] dark:text-untold-muted">{item.provider}</span>
              </div>
              <p className="text-sm dark:text-untold-muted whitespace-pre-wrap">{outputPreview(item.response)}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border dark:border-white/10 p-4 dark:bg-black/20 lg:sticky lg:top-4 h-fit">
        <ResearchAgentPanel
          key={initialPrompt}
          providers={providers}
          running={running}
          summary={summary}
          followUps={preferences?.showFollowUps ? followUps : []}
          defaultProvider={preferences?.defaultProvider}
          defaultAction={preferences?.defaultAction}
          initialPrompt={initialPrompt}
          onRun={onRun}
        />
      </div>
    </div>
  );
}
