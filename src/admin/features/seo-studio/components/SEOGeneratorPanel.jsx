import { useState } from 'react';
import { CONTENT_TYPES } from '../constants';

export default function SEOGeneratorPanel({ overview, onGenerate, generating, projectId }) {
  const [topic, setTopic] = useState('');
  const [contentType, setContentType] = useState('video');
  const [keyword, setKeyword] = useState('');
  const [variants, setVariants] = useState(3);
  const [provider, setProvider] = useState('');

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Generate YouTube titles, meta tags, OpenGraph, Twitter cards, Schema.org, and scored variants.
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
      <textarea value={topic} onChange={(e) => setTopic(e.target.value)} rows={3} placeholder="Topic / video title / article subject"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted block">
          Content type
          <select value={contentType} onChange={(e) => setContentType(e.target.value)} className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white">
            {CONTENT_TYPES.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
          </select>
        </label>
        <label className="text-xs dark:text-untold-muted block">
          Target keyword
          <input value={keyword} onChange={(e) => setKeyword(e.target.value)} className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white" />
        </label>
      </div>
      <label className="text-xs dark:text-untold-muted block">
        Variants — {variants}
        <input type="range" min="1" max="5" value={variants} onChange={(e) => setVariants(Number(e.target.value))} className="w-full" />
      </label>
      <button type="button" disabled={!topic.trim() || generating}
        onClick={() => onGenerate({
          topic: topic.trim(), content_type: contentType, target_keyword: keyword.trim(),
          variant_count: variants, project_id: projectId || undefined, provider: provider || undefined,
        })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50">
        {generating ? 'Queuing…' : 'Generate SEO pack'}
      </button>
    </div>
  );
}
