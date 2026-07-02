import { useState, useEffect } from 'react';
import { api } from '../../api/client';

const FALLBACK_CATEGORIES = [
  { slug: 'legends', name: 'Legends' },
  { slug: 'rivalries', name: 'Rivalries' },
  { slug: 'stories', name: 'Stories' },
  { slug: 'secrets', name: 'Secrets' },
];

export default function CategorySlider({ active, onChange, includeAll = true }) {
  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);

  useEffect(() => {
    api.categories.list()
      .then((items) => {
        if (items?.length) {
          setCategories(items.map((c) => ({ slug: c.slug, name: c.name })));
        }
      })
      .catch(() => setCategories(FALLBACK_CATEGORIES));
  }, []);

  const items = includeAll ? [{ slug: 'all', name: 'All' }, ...categories] : categories;

  return (
    <div className="flex gap-2 overflow-x-auto scrollbar-hide px-4 sm:px-6 lg:px-8 pb-1 snap-x snap-mandatory">
      {items.map((cat) => {
        const key = cat.slug;
        const isActive = active === key;
        return (
          <button
            key={key}
            type="button"
            onClick={() => onChange(key)}
            className={`snap-start shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300
              ${isActive
                ? 'bg-untold-gold text-untold-dark shadow-sm'
                : 'dark:bg-white/5 light:bg-black/5 dark:text-untold-muted light:text-gray-600 hover:text-untold-gold'
              }`}
          >
            {cat.name}
          </button>
        );
      })}
    </div>
  );
}
