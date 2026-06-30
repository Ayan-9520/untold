import { useState } from 'react';

export default function StoryboardGeneratorPanel({ providers, hasScript, onGenerate, running, lastResult }) {
  const [prompt, setPrompt] = useState('');
  const [replace, setReplace] = useState(false);
  const [duration, setDuration] = useState(15);
  const [provider, setProvider] = useState('');

  return (
    <div className="space-y-4 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        AI Storyboard Generator — converts your script into fully structured scenes with camera, lighting, mood, and transitions.
      </p>
      {!hasScript && (
        <p className="text-xs text-amber-400 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2">
          No script found for this project. Add a script in Script Studio first, or scenes will use a default opening.
        </p>
      )}
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
              {p.label}
            </button>
          ))}
        </div>
      )}
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={3}
        placeholder="Optional focus: e.g. Emphasize interview beats, 8–12 scenes, golden-hour exteriors…"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />
      <div className="flex flex-wrap items-center gap-4">
        <label className="flex items-center gap-2 text-xs dark:text-untold-muted">
          <input type="checkbox" checked={replace} onChange={(e) => setReplace(e.target.checked)} />
          Replace existing scenes
        </label>
        <label className="flex items-center gap-2 text-xs dark:text-untold-muted">
          Default duration
          <input
            type="number"
            min={5}
            max={120}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-16 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-sm dark:text-white"
          />
          s
        </label>
      </div>
      <button
        type="button"
        disabled={running}
        onClick={() => onGenerate({
          prompt: prompt || null,
          replace_existing: replace,
          default_duration_seconds: duration,
          provider: provider || undefined,
        })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
      >
        {running ? 'Generating…' : 'AI Generate from Script'}
      </button>
      {lastResult && (
        <div className="rounded-lg border border-untold-gold/20 bg-untold-gold/5 p-4 text-sm dark:text-untold-muted whitespace-pre-wrap">
          <p className="text-xs font-semibold text-untold-gold mb-2">
            {lastResult.scenes_created} scenes created · {lastResult.provider}
          </p>
          {lastResult.summary}
        </div>
      )}
    </div>
  );
}
