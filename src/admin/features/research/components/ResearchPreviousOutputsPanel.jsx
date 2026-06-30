import { formatRelativeTime } from '../../dashboard/utils';

function formatOutput(response) {
  if (!response) return 'No output recorded';
  const parts = [];
  if (response.summary) parts.push(response.summary);
  if (response.statistics?.length) {
    parts.push(`Statistics: ${response.statistics.map((s) => s.label || s.value || JSON.stringify(s)).join('; ')}`);
  }
  if (response.public_facts?.length) parts.push(`Facts: ${response.public_facts.join('; ')}`);
  if (response.follow_up_questions?.length) {
    parts.push(`Follow-ups:\n${response.follow_up_questions.map((q) => `• ${q}`).join('\n')}`);
  }
  if (!parts.length && response.suggestions?.length) parts.push(response.suggestions.join('\n'));
  return parts.join('\n\n') || JSON.stringify(response, null, 2);
}

export default function ResearchPreviousOutputsPanel({ history, versions }) {
  const aiOutputs = history || [];
  const savedVersions = versions || [];

  if (!aiOutputs.length && !savedVersions.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-12">No AI outputs or saved versions yet.</p>;
  }

  return (
    <div className="space-y-6 max-h-[560px] overflow-y-auto">
      {aiOutputs.length > 0 && (
        <section>
          <h4 className="text-xs font-semibold dark:text-untold-muted uppercase tracking-wider mb-3">AI outputs</h4>
          <ul className="space-y-3">
            {aiOutputs.map((item) => (
              <li key={item.id} className="rounded-lg border dark:border-white/10 px-4 py-3">
                <div className="flex flex-wrap justify-between gap-2 mb-2">
                  <span className="text-xs font-medium dark:text-white capitalize">{item.action.replace(/_/g, ' ')}</span>
                  <span className="text-[10px] dark:text-untold-muted">{formatRelativeTime(item.created_at)}</span>
                </div>
                <p className="text-sm dark:text-untold-muted whitespace-pre-wrap line-clamp-6">{formatOutput(item.response)}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {savedVersions.length > 0 && (
        <section>
          <h4 className="text-xs font-semibold dark:text-untold-muted uppercase tracking-wider mb-3">Saved versions</h4>
          <ul className="space-y-2">
            {savedVersions.map((v) => (
              <li key={v.id} className="rounded-lg border dark:border-white/10 px-4 py-3">
                <div className="flex justify-between gap-2 mb-1">
                  <span className="text-sm font-medium dark:text-white">Version {v.version}</span>
                  <span className="text-[10px] dark:text-untold-muted">{v.author_name} · {formatRelativeTime(v.created_at)}</span>
                </div>
                <p className="text-xs dark:text-untold-muted font-mono line-clamp-4 whitespace-pre-wrap">
                  {(v.workspace_content || '').slice(0, 400)}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
