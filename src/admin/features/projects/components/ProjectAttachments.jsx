import { useState } from 'react';
import { formatBytes } from '../../dashboard/utils';

export default function ProjectAttachments({ attachments, onAdd, onDelete }) {
  const [filename, setFilename] = useState('');
  const [url, setUrl] = useState('');

  const submit = (e) => {
    e.preventDefault();
    if (!filename.trim()) return;
    onAdd({ filename: filename.trim(), url: url.trim() || null, asset_type: 'document' });
    setFilename('');
    setUrl('');
  };

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <input
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          placeholder="Filename"
          className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        />
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="URL (optional)"
          className="rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        />
        <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Add</button>
      </form>
      <ul className="space-y-2">
        {(attachments || []).map((a) => (
          <li key={a.id} className="flex items-center justify-between gap-3 rounded-lg border dark:border-white/10 px-3 py-2">
            <div className="min-w-0">
              {a.url ? (
                <a href={a.url} target="_blank" rel="noreferrer" className="text-sm text-untold-gold hover:underline truncate block">
                  {a.filename}
                </a>
              ) : (
                <p className="text-sm dark:text-white truncate">{a.filename}</p>
              )}
              <p className="text-[10px] dark:text-untold-muted">{formatBytes(a.size_bytes)} · {a.asset_type}</p>
            </div>
            <button type="button" onClick={() => onDelete(a.id)} className="text-xs text-red-400 shrink-0 hover:underline">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
