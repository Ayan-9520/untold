import { useState } from 'react';
import { formatRelativeTime } from '../../dashboard/utils';

export default function ProjectComments({ comments, onAdd, onDelete, currentUserId }) {
  const [text, setText] = useState('');

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onAdd(text.trim());
    setText('');
  };

  return (
    <div className="space-y-4">
      <form onSubmit={submit} className="flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a comment…"
          className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        />
        <button type="submit" className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium">Post</button>
      </form>
      <ul className="space-y-3">
        {(comments || []).map((c) => (
          <li key={c.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
            <div className="flex justify-between gap-2">
              <p className="text-sm font-medium dark:text-white">{c.author_name}</p>
              <span className="text-[10px] dark:text-untold-muted">{formatRelativeTime(c.created_at)}</span>
            </div>
            <p className="text-sm dark:text-untold-muted mt-1">{c.content}</p>
            {(c.user_id === currentUserId) && (
              <button type="button" onClick={() => onDelete(c.id)} className="text-xs text-red-400 mt-1 hover:underline">
                Delete
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
