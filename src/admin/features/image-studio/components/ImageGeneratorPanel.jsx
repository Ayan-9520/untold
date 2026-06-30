import { useState } from 'react';
import { IMAGE_TYPES, ASPECT_RATIOS } from '../constants';

export default function ImageGeneratorPanel({ providers, imageType, onTypeChange, onGenerate, generating, initialPrompt = '' }) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [aspect, setAspect] = useState('16:9');
  const [provider, setProvider] = useState('');
  const current = IMAGE_TYPES.find((t) => t.id === imageType) || IMAGE_TYPES[0];

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Original artwork only — prompts referencing copyrighted movie frames or protected characters are blocked.
      </p>
      <div className="flex flex-wrap gap-2">
        {IMAGE_TYPES.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => onTypeChange(t.id)}
            className={`text-xs px-2 py-1 rounded-lg border ${
              imageType === t.id ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
            }`}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>
      {providers?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {providers.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => setProvider(p.id)}
              className={`text-[10px] px-2 py-1 rounded-full border ${
                provider === p.id ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
              }`}
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
        placeholder={`Describe your original ${current.label.toLowerCase()}…`}
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />
      <div className="flex flex-wrap gap-3 items-center">
        <label className="text-xs dark:text-untold-muted flex items-center gap-2">
          Aspect
          <select value={aspect} onChange={(e) => setAspect(e.target.value)} className="rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-sm dark:text-white">
            {ASPECT_RATIOS.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </label>
      </div>
      <button
        type="button"
        disabled={!prompt.trim() || generating}
        onClick={() => onGenerate({
          prompt: prompt.trim(),
          image_type: imageType,
          aspect_ratio: aspect,
          provider: provider || undefined,
        })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
      >
        {generating ? 'Queuing…' : `Generate ${current.label}`}
      </button>
    </div>
  );
}
