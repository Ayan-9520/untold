import { useEffect, useState } from 'react';
import { AI_ACTIONS } from '../constants';

export default function ResearchAgentPanel({
  providers,
  onRun,
  running,
  summary,
  followUps,
  defaultProvider = '',
  defaultAction = 'full_research',
  initialPrompt = '',
}) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [action, setAction] = useState(defaultAction);
  const [provider, setProvider] = useState(defaultProvider);

  useEffect(() => {
    setAction(defaultAction);
  }, [defaultAction]);

  useEffect(() => {
    setProvider(defaultProvider);
  }, [defaultProvider]);

  useEffect(() => {
    if (initialPrompt) setPrompt(initialPrompt);
  }, [initialPrompt]);

  return (
    <div className="space-y-4 max-w-3xl">
      <p className="text-sm dark:text-untold-muted">
        AI Research Agent — provider-abstracted. Swap LLM or search backends without changing the app.
      </p>
      {providers?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {providers.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => setProvider(p.id)}
              className={`text-[10px] px-2 py-1 rounded-full border ${
                provider === p.id ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
              } ${!p.available ? 'opacity-40' : ''}`}
            >
              {p.label}{p.available ? '' : ' (off)'}
            </button>
          ))}
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        {AI_ACTIONS.map((a) => (
          <button
            key={a.id}
            type="button"
            onClick={() => setAction(a.id)}
            className={`text-xs px-2 py-1 rounded-lg border ${
              action === a.id ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
            }`}
          >
            {a.icon} {a.label}
          </button>
        ))}
      </div>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={4}
        placeholder="What should the agent research? e.g. Verify career timeline 2010–2020, find primary statistics…"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />
      <button
        type="button"
        disabled={!prompt.trim() || running}
        onClick={() => onRun({ prompt, action, provider: provider || undefined })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
      >
        {running ? 'Researching…' : 'Run AI Agent'}
      </button>
      {summary && (
        <div className="rounded-lg border dark:border-white/10 p-4">
          <p className="text-xs font-semibold text-untold-gold mb-2">Latest output</p>
          <p className="text-sm dark:text-untold-muted whitespace-pre-wrap">{summary}</p>
        </div>
      )}
      {followUps?.length > 0 && (
        <div>
          <p className="text-xs font-semibold dark:text-white mb-2">Follow-up questions</p>
          <ul className="text-sm dark:text-untold-muted space-y-1 list-disc list-inside">
            {followUps.map((q) => <li key={q}>{q}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
