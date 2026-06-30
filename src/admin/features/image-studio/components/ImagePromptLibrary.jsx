import { useState } from 'react';

export default function ImagePromptLibrary({ prompts, imageType, onUse }) {
  const filtered = prompts?.filter((p) => {
    if (!imageType) return true;
    const t = p.parameters?.image_type;
    return !t || t === imageType;
  }) || [];

  if (!filtered.length) {
    return <p className="text-sm dark:text-untold-muted">No prompts for this type yet.</p>;
  }

  return (
    <ul className="space-y-2 max-h-96 overflow-y-auto">
      {filtered.map((p) => (
        <li key={p.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
          <p className="text-sm font-medium dark:text-white">{p.title}</p>
          {p.description && <p className="text-[10px] dark:text-untold-muted mt-0.5">{p.description}</p>}
          <button type="button" onClick={() => onUse(p)} className="text-xs text-untold-gold mt-2 hover:underline">
            Use prompt →
          </button>
        </li>
      ))}
    </ul>
  );
}

export function CollectionsPanel({ collections, onCreate, creating }) {
  const [name, setName] = useState('');

  return (
    <div className="space-y-4">
      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          onCreate({ name });
          setName('');
        }}
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New collection name"
          required
          className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        />
        <button type="submit" disabled={creating} className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50">
          Create
        </button>
      </form>
      <ul className="space-y-2">
        {collections?.map((c) => (
          <li key={c.id} className="rounded-lg border dark:border-white/10 px-3 py-2 flex justify-between text-sm">
            <span className="dark:text-white">{c.name}</span>
            <span className="text-xs dark:text-untold-muted">{c.item_count} images</span>
          </li>
        ))}
        {!collections?.length && <p className="text-xs dark:text-untold-muted">No collections yet</p>}
      </ul>
    </div>
  );
}
