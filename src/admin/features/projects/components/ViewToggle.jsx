import { PROJECT_VIEWS } from '../constants';

const LABELS = { kanban: 'Kanban', table: 'Table', calendar: 'Calendar' };

export default function ViewToggle({ view, onChange }) {
  return (
    <div className="inline-flex rounded-lg border dark:border-white/10 light:border-gray-200 p-0.5">
      {PROJECT_VIEWS.map((v) => (
        <button
          key={v}
          type="button"
          onClick={() => onChange(v)}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            view === v
              ? 'bg-untold-gold text-black'
              : 'dark:text-untold-muted light:text-gray-500 hover:dark:text-white hover:light:text-black'
          }`}
        >
          {LABELS[v]}
        </button>
      ))}
    </div>
  );
}
