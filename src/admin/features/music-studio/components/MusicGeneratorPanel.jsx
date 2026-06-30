import { useState } from 'react';
import { MUSIC_CATEGORIES, DURATION_OPTIONS } from '../constants';

export default function MusicGeneratorPanel({
  providers,
  category,
  onCategoryChange,
  onGenerate,
  generating,
  previewing,
  onPreview,
  initialPrompt = '',
}) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [duration, setDuration] = useState(60);
  const [loop, setLoop] = useState(true);
  const [fadeIn, setFadeIn] = useState(2);
  const [fadeOut, setFadeOut] = useState(3);
  const [provider, setProvider] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const current = MUSIC_CATEGORIES.find((c) => c.id === category) || MUSIC_CATEGORIES[0];

  const payload = () => ({
    prompt: prompt.trim(),
    category,
    duration_seconds: duration,
    loop,
    fade_in_seconds: fadeIn,
    fade_out_seconds: fadeOut,
    provider: provider || undefined,
  });

  const handlePreview = async () => {
    if (!prompt.trim()) return;
    const result = await onPreview({
      ...payload(),
      duration_seconds: Math.min(12, duration),
    });
    if (result?.audio_url) setPreviewUrl(result.audio_url);
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Generate original background music with category mood, duration, seamless loop, and fade controls.
      </p>

      <div className="flex flex-wrap gap-2">
        {MUSIC_CATEGORIES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => onCategoryChange(c.id)}
            className={`text-xs px-2 py-1 rounded-lg border ${
              category === c.id ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
            }`}
          >
            {c.icon} {c.label}
          </button>
        ))}
      </div>

      {providers?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {providers.map((p) => (
            <button
              key={p.id}
              type="button"
              disabled={!p.available}
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
        rows={4}
        placeholder={`Describe the ${current.label.toLowerCase()} score mood, energy, and instrumentation…`}
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />

      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Duration
          <select
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          >
            {DURATION_OPTIONS.map((d) => <option key={d} value={d}>{d}s</option>)}
          </select>
        </label>
        <label className="text-xs dark:text-untold-muted flex items-center gap-2 pt-5">
          <input type="checkbox" checked={loop} onChange={(e) => setLoop(e.target.checked)} />
          Seamless loop
        </label>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Fade in — {fadeIn.toFixed(1)}s
          <input type="range" min="0" max="10" step="0.5" value={fadeIn} onChange={(e) => setFadeIn(Number(e.target.value))} className="w-full" />
        </label>
        <label className="text-xs dark:text-untold-muted space-y-1 block">
          Fade out — {fadeOut.toFixed(1)}s
          <input type="range" min="0" max="15" step="0.5" value={fadeOut} onChange={(e) => setFadeOut(Number(e.target.value))} className="w-full" />
        </label>
      </div>

      {previewUrl && <audio controls src={previewUrl} loop={loop} className="w-full" />}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={!prompt.trim() || previewing}
          onClick={handlePreview}
          className="px-3 py-2 text-sm rounded-lg border dark:border-white/10 dark:text-white disabled:opacity-50"
        >
          {previewing ? 'Previewing…' : 'Preview'}
        </button>
        <button
          type="button"
          disabled={!prompt.trim() || generating}
          onClick={() => onGenerate(payload())}
          className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
        >
          {generating ? 'Queuing…' : `Generate ${current.label} score`}
        </button>
      </div>
    </div>
  );
}
