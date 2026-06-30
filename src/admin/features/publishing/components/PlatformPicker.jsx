import { PUBLISH_PLATFORMS } from '../constants';

export default function PlatformPicker({ selected, onChange, multi }) {
  if (multi) {
    return (
      <div className="flex flex-wrap gap-2">
        {PUBLISH_PLATFORMS.map((p) => {
          const active = selected?.includes(p.id);
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => {
                const next = active ? selected.filter((x) => x !== p.id) : [...(selected || []), p.id];
                onChange(next);
              }}
              className={`px-3 py-2 rounded-lg border text-xs transition-colors ${
                active ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
              }`}
            >
              {p.icon} {p.label}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
      {PUBLISH_PLATFORMS.map((p) => (
        <button
          key={p.id}
          type="button"
          onClick={() => onChange(p.id)}
          className={`px-3 py-2.5 rounded-lg border text-xs text-left transition-colors ${
            selected === p.id ? 'border-untold-gold bg-untold-gold/10 text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted hover:border-white/20'
          }`}
        >
          <span className="text-lg mr-1">{p.icon}</span> {p.label}
        </button>
      ))}
    </div>
  );
}
