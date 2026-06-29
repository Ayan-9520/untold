import { useState } from 'react';
import Badge from '../ui/Badge';

export default function FlipbookViewer({ issue, sections = [] }) {
  const pages = sections.length > 0 ? sections : [{ id: 'cover', title: issue.title, excerpt: issue.theme }];
  const [page, setPage] = useState(0);
  const current = pages[page];

  return (
    <div className="rounded-xl border dark:border-untold-border light:border-gray-200 overflow-hidden dark:bg-untold-surface light:bg-white">
      <div className="flex items-center justify-between px-4 py-3 border-b dark:border-untold-border light:border-gray-200">
        <span className="text-sm font-medium dark:text-untold-white light:text-black">
          Flipbook · Page {page + 1} / {pages.length}
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={page === 0}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1 rounded text-sm dark:bg-white/10 light:bg-gray-100 disabled:opacity-40"
          >
            ← Prev
          </button>
          <button
            type="button"
            disabled={page >= pages.length - 1}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1 rounded text-sm bg-untold-gold text-untold-dark disabled:opacity-40"
          >
            Next →
          </button>
        </div>
      </div>

      <div className="relative aspect-[4/5] sm:aspect-[3/4] max-h-[70vh] bg-black">
        {current.image && (
          <img src={current.image} alt="" className="absolute inset-0 w-full h-full object-cover opacity-40" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/70 to-black/40 p-6 sm:p-10 flex flex-col justify-end">
          <Badge variant="gold" size="sm" className="w-fit mb-3">
            {current.id?.replace('-', ' ') || 'Section'}
          </Badge>
          <h2 className="font-display text-2xl sm:text-3xl font-bold text-white">{current.title}</h2>
          <p className="mt-3 text-sm sm:text-base text-white/80 max-w-xl leading-relaxed">
            {current.excerpt || current.body}
          </p>
          {current.stats && (
            <div className="mt-4 flex gap-4">
              {current.stats.map((s) => (
                <div key={s.label}>
                  <p className="text-2xl font-bold text-untold-gold">{s.value}</p>
                  <p className="text-xs text-white/60">{s.label}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
