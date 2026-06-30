import { useState } from 'react';
import { SOURCE_TYPES } from '../constants';

export default function SourceList({ sources, onAdd, onFilter }) {
  const [search, setSearch] = useState('');
  const [type, setType] = useState('');
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');

  const applyFilter = () => onFilter?.({ search: search || undefined, source_type: type || undefined });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search references…" className="flex-1 min-w-[120px] rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
        <select value={type} onChange={(e) => setType(e.target.value)} className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-2 py-2 text-xs dark:text-white">
          <option value="">All types</option>
          {SOURCE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <button type="button" onClick={applyFilter} className="text-xs px-3 py-2 rounded-lg border dark:border-white/10 text-untold-gold">Filter</button>
      </div>
      <form
        className="flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          onAdd({ title, url: url || null, source_type: type || 'article' });
          setTitle('');
          setUrl('');
        }}
      >
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Reference title" required className="flex-1 min-w-[140px] rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="URL" className="flex-1 min-w-[140px] rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
        <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Add</button>
      </form>
      <ul className="space-y-2">
        {sources.map((s) => (
          <li key={s.id} className="flex justify-between gap-3 rounded-lg border dark:border-white/10 px-3 py-2">
            <div>
              {s.url ? <a href={s.url} target="_blank" rel="noreferrer" className="text-sm text-untold-gold hover:underline">{s.title}</a> : <p className="text-sm dark:text-white">{s.title}</p>}
              <p className="text-xs dark:text-untold-muted capitalize">{s.source_type}{s.credibility_score != null ? ` · ${Math.round(s.credibility_score * 100)}% credible` : ''}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
