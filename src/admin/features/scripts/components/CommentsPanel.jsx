import { useState } from 'react';
import { formatRelativeTime } from '../../dashboard/utils';

export default function CommentsPanel({ comments, onAdd, adding }) {
  const [text, setText] = useState('');

  return (
    <div className="space-y-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!text.trim()) return;
          onAdd(text.trim());
          setText('');
        }}
        className="flex gap-2"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a comment…"
          className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        />
        <button
          type="submit"
          disabled={adding || !text.trim()}
          className="px-3 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50"
        >
          Post
        </button>
      </form>
      <ul className="space-y-2">
        {comments.map((c) => (
          <li key={c.id} className="rounded-lg border dark:border-white/10 px-3 py-2">
            <p className="text-sm dark:text-white">{c.content}</p>
            <p className="text-[10px] dark:text-untold-muted mt-1">
              {c.author_name} · {formatRelativeTime(c.created_at)}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
