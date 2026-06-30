import { useState } from 'react';
import { sanitizeHtml } from '../../../../utils/sanitizeHtml';

const AI_ACTIONS = [
  { id: 'generate', label: 'Generate', desc: 'Draft new script sections' },
  { id: 'rewrite', label: 'Rewrite', desc: 'Improve tone and clarity' },
  { id: 'summarize', label: 'Summarize', desc: 'Condense selection or script' },
  { id: 'translate', label: 'Translate', desc: 'Translate to another language' },
  { id: 'grammar', label: 'Grammar', desc: 'Fix grammar and punctuation' },
];

const LANGUAGES = [
  { code: 'es', label: 'Spanish' },
  { code: 'fr', label: 'French' },
  { code: 'de', label: 'German' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ar', label: 'Arabic' },
];

export default function AIToolsPanel({ onRun, running, lastResult, onApply }) {
  const [action, setAction] = useState('generate');
  const [prompt, setPrompt] = useState('');
  const [selection, setSelection] = useState('');
  const [lang, setLang] = useState('es');

  const handleRun = () => {
    onRun({
      action,
      prompt: prompt || null,
      selection: selection || null,
      target_language: lang,
    });
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {AI_ACTIONS.map((a) => (
          <button
            key={a.id}
            type="button"
            onClick={() => setAction(a.id)}
            className={`text-left rounded-lg border px-3 py-2 transition-colors ${
              action === a.id
                ? 'border-untold-gold/50 bg-untold-gold/10'
                : 'dark:border-white/10 hover:border-untold-gold/30'
            }`}
          >
            <p className="text-sm font-medium dark:text-white">{a.label}</p>
            <p className="text-[10px] dark:text-untold-muted mt-0.5">{a.desc}</p>
          </button>
        ))}
      </div>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={3}
        placeholder={action === 'generate' ? 'Describe the scene, tone, or beat to generate…' : 'Optional instructions…'}
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />

      {action !== 'generate' && (
        <textarea
          value={selection}
          onChange={(e) => setSelection(e.target.value)}
          rows={4}
          placeholder="Paste text to transform (leave empty to use full script)"
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white font-mono text-xs"
        />
      )}

      {action === 'translate' && (
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        >
          {LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
      )}

      <button
        type="button"
        disabled={running}
        onClick={handleRun}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50"
      >
        {running ? 'Running…' : `Run ${AI_ACTIONS.find((a) => a.id === action)?.label}`}
      </button>

      {lastResult && (
        <div className="rounded-lg border border-untold-gold/20 bg-untold-gold/5 p-4 space-y-3">
          <p className="text-xs font-semibold text-untold-gold">AI Result</p>
          <div
            className="text-sm dark:text-untold-muted prose-invert max-h-48 overflow-y-auto"
            dangerouslySetInnerHTML={{ __html: sanitizeHtml(lastResult) }}
          />
          {action !== 'generate' && onApply && (
            <button
              type="button"
              onClick={() => onApply(lastResult)}
              className="text-xs text-untold-gold hover:underline"
            >
              Insert at end of script
            </button>
          )}
        </div>
      )}
    </div>
  );
}
