import { TRACK_TYPES } from '../constants';

export default function TimelineToolbar({
  snapshot,
  onPlay,
  onPause,
  onUndo,
  onRedo,
  onSplit,
  onTrim,
  onMerge,
  onDelete,
  onZoomIn,
  onZoomOut,
  onSave,
  onExport,
  onHelp,
  onAddTrack,
  saving,
}) {
  if (!snapshot) return null;
  const { playing, canUndo, canRedo, playhead, duration, zoom } = snapshot;

  return (
    <div className="flex flex-wrap items-center gap-2 p-2 rounded-xl border dark:border-white/10 dark:bg-untold-card/40">
      <button type="button" onClick={playing ? onPause : onPlay} className="px-3 py-1.5 text-xs rounded-lg bg-untold-gold text-black font-medium">
        {playing ? '⏸ Pause' : '▶ Play'}
      </button>
      <span className="text-xs dark:text-untold-muted font-mono px-2">
        {playhead.toFixed(1)}s / {duration.toFixed(0)}s
      </span>

      <div className="w-px h-6 bg-white/10" />

      <button type="button" disabled={!canUndo} onClick={onUndo} className="px-2 py-1 text-xs rounded border dark:border-white/10 disabled:opacity-30">↶ Undo</button>
      <button type="button" disabled={!canRedo} onClick={onRedo} className="px-2 py-1 text-xs rounded border dark:border-white/10 disabled:opacity-30">↷ Redo</button>

      <div className="w-px h-6 bg-white/10" />

      <button type="button" onClick={onSplit} className="px-2 py-1 text-xs rounded border dark:border-white/10 text-untold-gold">✂ Split</button>
      <button type="button" onClick={onTrim} className="px-2 py-1 text-xs rounded border dark:border-white/10">Trim</button>
      <button type="button" onClick={onMerge} className="px-2 py-1 text-xs rounded border dark:border-white/10">Merge</button>
      <button type="button" onClick={onDelete} className="px-2 py-1 text-xs rounded border dark:border-white/10 text-red-400">Delete</button>

      <div className="w-px h-6 bg-white/10" />

      <button type="button" onClick={onZoomOut} className="px-2 py-1 text-xs rounded border dark:border-white/10">−</button>
      <span className="text-[10px] dark:text-untold-muted w-12 text-center">{Math.round(zoom)}px/s</span>
      <button type="button" onClick={onZoomIn} className="px-2 py-1 text-xs rounded border dark:border-white/10">+</button>

      <div className="flex-1" />

      <select
        className="text-xs rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 dark:text-white"
        defaultValue=""
        onChange={(e) => {
          if (e.target.value) onAddTrack(e.target.value);
          e.target.value = '';
        }}
      >
        <option value="">+ Track</option>
        {TRACK_TYPES.map((t) => (
          <option key={t.id} value={t.id}>{t.icon} {t.label}</option>
        ))}
      </select>

      <button type="button" onClick={onSave} disabled={saving} className="px-2 py-1 text-xs rounded border dark:border-white/10">
        {saving ? 'Saving…' : '💾 Save'}
      </button>
      <button type="button" onClick={onExport} className="px-2 py-1 text-xs rounded-lg bg-untold-gold/20 text-untold-gold border border-untold-gold/30">
        Export
      </button>
      <button type="button" onClick={onHelp} className="px-2 py-1 text-xs rounded border dark:border-white/10" title="Shortcuts">?</button>
    </div>
  );
}
