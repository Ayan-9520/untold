import { RESEARCH_CONTEXT_SECTIONS } from '../constants';

export default function ResearchContextSidebar({ active, onSelect, counts = {} }) {
  return (
    <nav className="space-y-1">
      <p className="text-[10px] uppercase tracking-wider dark:text-untold-muted mb-2 px-2">Context</p>
      {RESEARCH_CONTEXT_SECTIONS.map((section) => {
        const count = counts[section.id];
        return (
          <button
            key={section.id}
            type="button"
            onClick={() => onSelect(section.id)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between gap-2 ${
              active === section.id
                ? 'bg-untold-gold/15 text-untold-gold'
                : 'dark:text-untold-muted hover:bg-white/5'
            }`}
          >
            <span>{section.label}</span>
            {count > 0 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/10">{count}</span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
