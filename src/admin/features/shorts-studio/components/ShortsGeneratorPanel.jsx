import { useState } from 'react';
import { SHORTS_PLATFORMS } from '../constants';

export default function ShortsGeneratorPanel({ overview, onGenerate, generating, projectId }) {
  const [sourceUrl, setSourceUrl] = useState('');
  const [topic, setTopic] = useState('');
  const [platforms, setPlatforms] = useState(SHORTS_PLATFORMS.map((p) => p.id));
  const [autoHighlights, setAutoHighlights] = useState(true);
  const [captions, setCaptions] = useState(true);
  const [autoZoom, setAutoZoom] = useState(true);
  const [hookOpt, setHookOpt] = useState(true);
  const [duration, setDuration] = useState(30);
  const [provider, setProvider] = useState('');

  const togglePlatform = (id) => {
    setPlatforms((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Paste a long-form video URL. AI detects highlights and exports vertical 9:16 clips per platform.
      </p>
      {overview?.providers?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {overview.providers.map((p) => (
            <button key={p.id} type="button" disabled={!p.available} onClick={() => setProvider(p.id)}
              className={`text-[10px] px-2 py-1 rounded-full border ${provider === p.id ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'}`}>
              {p.label}
            </button>
          ))}
        </div>
      )}
      <input value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="Long video URL (source)"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
      <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic / episode title (optional)"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
      <div className="flex flex-wrap gap-2">
        {SHORTS_PLATFORMS.map((p) => (
          <button key={p.id} type="button" onClick={() => togglePlatform(p.id)}
            className={`text-xs px-2 py-1 rounded-lg border ${platforms.includes(p.id) ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'}`}>
            {p.icon} {p.label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-4 text-xs dark:text-untold-muted">
        <label className="flex items-center gap-2"><input type="checkbox" checked={autoHighlights} onChange={(e) => setAutoHighlights(e.target.checked)} /> Auto highlights</label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={captions} onChange={(e) => setCaptions(e.target.checked)} /> Captions</label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={autoZoom} onChange={(e) => setAutoZoom(e.target.checked)} /> Auto zoom</label>
        <label className="flex items-center gap-2"><input type="checkbox" checked={hookOpt} onChange={(e) => setHookOpt(e.target.checked)} /> Hook optimization</label>
      </div>
      <label className="text-xs dark:text-untold-muted flex items-center gap-2">
        Clip duration
        <select value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-sm dark:text-white">
          {[15, 30, 45, 60].map((d) => <option key={d} value={d}>{d}s</option>)}
        </select>
      </label>
      <button type="button" disabled={!sourceUrl.trim() || !platforms.length || generating}
        onClick={() => onGenerate({
          source_video_url: sourceUrl.trim(), topic: topic.trim(), platforms,
          auto_highlights: autoHighlights, captions, auto_zoom: autoZoom,
          hook_optimization: hookOpt, clip_duration_seconds: duration,
          project_id: projectId || undefined, provider: provider || undefined,
        })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50">
        {generating ? 'Queuing…' : 'Generate shorts pack'}
      </button>
    </div>
  );
}
