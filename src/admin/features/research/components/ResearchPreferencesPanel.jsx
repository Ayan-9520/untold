import { AI_ACTIONS, DEFAULT_RESEARCH_PREFERENCES } from '../constants';

export default function ResearchPreferencesPanel({ prefs, providers, onChange, onReset }) {
  return (
    <div className="max-w-lg space-y-5">
      <p className="text-sm dark:text-untold-muted">
        Preferences are saved locally in your browser and applied to new research sessions on this device.
      </p>

      <label className="block space-y-1">
        <span className="text-xs font-medium dark:text-white">Default AI action</span>
        <select
          value={prefs.defaultAction}
          onChange={(e) => onChange('defaultAction', e.target.value)}
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        >
          {AI_ACTIONS.map((a) => (
            <option key={a.id} value={a.id}>{a.label}</option>
          ))}
        </select>
      </label>

      <label className="block space-y-1">
        <span className="text-xs font-medium dark:text-white">Default provider</span>
        <select
          value={prefs.defaultProvider}
          onChange={(e) => onChange('defaultProvider', e.target.value)}
          className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
        >
          <option value="">Auto (registry default)</option>
          {(providers || []).map((p) => (
            <option key={p.id} value={p.id} disabled={!p.available}>{p.label}</option>
          ))}
        </select>
      </label>

      <label className="flex items-center gap-2 text-sm dark:text-untold-muted">
        <input
          type="checkbox"
          checked={prefs.showFollowUps}
          onChange={(e) => onChange('showFollowUps', e.target.checked)}
        />
        Show follow-up questions after agent runs
      </label>

      <label className="flex items-center gap-2 text-sm dark:text-untold-muted">
        <input
          type="checkbox"
          checked={prefs.autoExpandConversation}
          onChange={(e) => onChange('autoExpandConversation', e.target.checked)}
        />
        Open conversation after sending a prompt
      </label>

      <button
        type="button"
        onClick={onReset}
        className="text-xs px-3 py-1.5 rounded-lg border dark:border-white/10 dark:text-untold-muted hover:text-untold-gold"
      >
        Reset to defaults
      </button>

      <pre className="text-[10px] dark:text-untold-muted font-mono p-3 rounded-lg border dark:border-white/10 overflow-x-auto">
        {JSON.stringify(DEFAULT_RESEARCH_PREFERENCES, null, 2)}
      </pre>
    </div>
  );
}
