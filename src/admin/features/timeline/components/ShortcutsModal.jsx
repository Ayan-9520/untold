import { SHORTCUTS } from '../engine/shortcuts';

export default function ShortcutsModal({ open, onClose }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={onClose}>
      <div
        className="w-full max-w-md rounded-xl border dark:border-white/10 dark:bg-untold-card p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-semibold dark:text-white">Keyboard shortcuts</h3>
          <button type="button" onClick={onClose} className="text-untold-muted">✕</button>
        </div>
        <ul className="space-y-2">
          {SHORTCUTS.map((s) => (
            <li key={s.action} className="flex justify-between text-xs">
              <span className="dark:text-untold-muted">{s.label}</span>
              <kbd className="px-2 py-0.5 rounded bg-white/5 font-mono dark:text-white">{s.keys}</kbd>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
