import { TRACK_TYPE_MAP } from '../constants';

export default function PreviewPanel({ snapshot }) {
  if (!snapshot) return <div className="h-40 skeleton rounded-xl" />;
  const { document, playhead, selectedClipId } = snapshot;
  const allClips = document.tracks.flatMap((t) => t.clips.map((c) => ({ ...c, trackType: t.type })));
  const active = allClips.find(
    (c) => c.id === selectedClipId || (playhead >= c.start && playhead < c.start + c.duration),
  );
  const meta = active ? TRACK_TYPE_MAP[active.trackType] : null;

  return (
    <div className="rounded-xl border dark:border-white/10 dark:bg-black/30 p-4 min-h-[140px]">
      <p className="text-xs font-semibold dark:text-white mb-2">Preview @ {playhead.toFixed(2)}s</p>
      {active ? (
        <div className="space-y-1">
          <p className="text-sm dark:text-white">{meta?.icon} {active.label}</p>
          <p className="text-xs dark:text-untold-muted capitalize">{active.trackType} · {active.duration.toFixed(1)}s</p>
          {active.caption && <p className="text-xs text-untold-gold mt-2">"{active.caption}"</p>}
          {active.assetUrl && (
            <img src={active.assetUrl} alt="" className="mt-2 max-h-24 rounded object-contain" />
          )}
        </div>
      ) : (
        <p className="text-xs dark:text-untold-muted">No clip at playhead</p>
      )}
    </div>
  );
}
