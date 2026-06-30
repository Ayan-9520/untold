import { VISIBILITY_STATES } from '../constants';

export default function VisibilitySelect({ value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {VISIBILITY_STATES.map((v) => (
        <button
          key={v.id}
          type="button"
          onClick={() => onChange(v.id)}
          className={`px-3 py-1.5 rounded-full border text-xs font-medium transition-colors ${
            value === v.id ? v.color : 'dark:border-white/10 dark:text-untold-muted'
          }`}
        >
          {v.label}
        </button>
      ))}
    </div>
  );
}
