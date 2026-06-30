import { useState } from 'react';
import { SCRIPT_AI_GROUPS, SCRIPT_LANGUAGES, SCRIPT_TONES, ALL_SCRIPT_ACTIONS } from '../constants';
import { sanitizeHtml } from '../../../../utils/sanitizeHtml';

export default function ScriptWriterPanel({
  providers,
  onRun,
  running,
  lastResult,
  onApply,
  onCaptureSelection,
  suggestedStyle,
}) {
  const [action, setAction] = useState('generate');
  const [prompt, setPrompt] = useState('');
  const [selection, setSelection] = useState('');
  const [lang, setLang] = useState('es');
  const [tone, setTone] = useState('authoritative');
  const [provider, setProvider] = useState('');

  const current = ALL_SCRIPT_ACTIONS.find((a) => a.id === action);
  const showTone = action === 'tone';
  const showLang = action === 'translate';

  const handleRun = (apply = false) => {
    onRun({
      action,
      prompt: prompt || null,
      selection: selection || null,
      target_language: lang,
      tone: showTone ? tone : null,
      provider: provider || undefined,
      apply,
    });
  };

  return (
    <div className="space-y-5 max-w-3xl">
      <p className="text-sm dark:text-untold-muted">
        AI Script Writer — provider-abstracted. Every generation is stored in history.
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

      {SCRIPT_AI_GROUPS.map((group) => (
        <div key={group.id}>
          <p className="text-[10px] uppercase tracking-wider dark:text-untold-muted mb-2">{group.label}</p>
          <div className="flex flex-wrap gap-2">
            {group.actions.map((a) => (
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
        </div>
      ))}

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={3}
        placeholder={
          action === 'generate' ? 'Describe the scene, beat, or section to generate…'
            : action === 'chapter' ? 'Chapter title or act name…'
              : action === 'scene' ? 'Scene description or interview prompt…'
                : action === 'hook' ? 'Optional hook angle…'
                  : action === 'cta' ? 'Call-to-action message…'
                    : 'Optional instructions…'
        }
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />

      <div className="space-y-2">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                const captured = onCaptureSelection?.();
                if (captured) setSelection(captured);
              }}
              className="text-xs px-3 py-1.5 rounded-lg border dark:border-white/10 text-untold-gold"
            >
              Capture editor selection
            </button>
          </div>
          <textarea
            value={selection}
            onChange={(e) => setSelection(e.target.value)}
            rows={4}
            placeholder="Text to transform (leave empty to use full script)"
            className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white font-mono text-xs"
          />
        </div>

      {showTone && (
        <select
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        >
          {SCRIPT_TONES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      )}

      {showLang && (
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        >
          {SCRIPT_LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
      )}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={running}
          onClick={() => handleRun(false)}
          className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50"
        >
          {running ? 'Writing…' : `Run ${current?.label || 'AI'}`}
        </button>
        <button
          type="button"
          disabled={running || !lastResult}
          onClick={() => handleRun(true)}
          className="px-4 py-2 text-sm rounded-lg border dark:border-white/10 text-untold-gold disabled:opacity-50"
        >
          Run & apply to script
        </button>
      </div>

      {lastResult && (
        <div className="rounded-lg border border-untold-gold/20 bg-untold-gold/5 p-4 space-y-3">
          <p className="text-xs font-semibold text-untold-gold">AI output</p>
          {suggestedStyle && (
            <p className="text-[10px] text-untold-gold">Suggested style: {suggestedStyle}</p>
          )}
          <div
            className="text-sm dark:text-untold-muted prose-invert max-h-56 overflow-y-auto"
            dangerouslySetInnerHTML={{ __html: sanitizeHtml(lastResult) }}
          />
          {onApply && (
            <button type="button" onClick={() => onApply(lastResult)} className="text-xs text-untold-gold hover:underline">
              Insert at end of script
            </button>
          )}
        </div>
      )}
    </div>
  );
}
