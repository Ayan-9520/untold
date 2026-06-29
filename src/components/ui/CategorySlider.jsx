import { CATEGORIES } from '../../data/videoCatalog';

export default function CategorySlider({ active, onChange, includeAll = true }) {
  const items = includeAll ? [{ slug: 'all', name: 'All' }, ...CATEGORIES] : CATEGORIES;

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
