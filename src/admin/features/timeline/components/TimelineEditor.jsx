import { useCallback, useEffect, useState } from 'react';
import { matchShortcut } from '../engine/shortcuts';
import TimelineToolbar from './TimelineToolbar';
import TimelineCanvas from './TimelineCanvas';
import PreviewPanel from './PreviewPanel';
import ExportQueuePanel from './ExportQueuePanel';
import ShortcutsModal from './ShortcutsModal';
import { TRACK_TYPES } from '../constants';
import { formatRelativeTime } from '../../dashboard/utils';

export default function TimelineEditor({
  engine,
  snapshot,
  saveNow,
  saving,
  lastSaved,
  exports,
  onExport,
  exporting,
}) {
  const [showShortcuts, setShowShortcuts] = useState(false);

  const handleAction = useCallback((action) => {
    if (!engine) return;
    switch (action) {
      case 'playPause': engine.togglePlay(); break;
      case 'pause': engine.pause(); break;
      case 'stepBack': engine.setPlayhead((snapshot?.playhead ?? 0) - 1); break;
      case 'stepForward': engine.setPlayhead((snapshot?.playhead ?? 0) + 1); break;
      case 'undo': engine.undo(); break;
      case 'redo': engine.redo(); break;
      case 'split': engine.splitSelected(); break;
      case 'trim': engine.trimSelectedToPlayhead(); break;
      case 'merge': engine.mergeSelectedWithNext(); break;
      case 'delete': engine.deleteSelected(); break;
      case 'zoomIn': engine.zoomBy(20); break;
      case 'zoomOut': engine.zoomBy(-20); break;
      case 'save': saveNow(); break;
      case 'help': setShowShortcuts(true); break;
      default: break;
    }
  }, [engine, saveNow, snapshot?.playhead]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
      const action = matchShortcut(e);
      if (!action) return;
      e.preventDefault();
      handleAction(action);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [handleAction]);

  const trackHeight = 56;
  const canvasHeight = Math.max(280, 28 + (snapshot?.document?.tracks?.length || 6) * trackHeight);

  return (
    <div className="space-y-4">
      <TimelineToolbar
        snapshot={snapshot}
        onPlay={() => engine.play()}
        onPause={() => engine.pause()}
        onUndo={() => engine.undo()}
        onRedo={() => engine.redo()}
        onSplit={() => engine.splitSelected()}
        onTrim={() => engine.trimSelectedToPlayhead()}
        onMerge={() => engine.mergeSelectedWithNext()}
        onDelete={() => engine.deleteSelected()}
        onZoomIn={() => engine.zoomBy(20)}
        onZoomOut={() => engine.zoomBy(-20)}
        onSave={saveNow}
        onExport={() => onExport({ format: 'mp4' })}
        onHelp={() => setShowShortcuts(true)}
        onAddTrack={(type) => engine.addTrack(type)}
        saving={saving}
      />

      {lastSaved && (
        <p className="text-[10px] dark:text-untold-muted">
          Autosaved {formatRelativeTime(lastSaved)}
        </p>
      )}

      <div className="grid lg:grid-cols-[1fr_240px] gap-4">
        <TimelineCanvas snapshot={snapshot} engine={engine} height={canvasHeight} />
        <div className="space-y-4">
          <PreviewPanel snapshot={snapshot} />
          <ExportQueuePanel exports={exports} onExport={onExport} exporting={exporting} />
          <div className="rounded-xl border dark:border-white/10 p-3">
            <p className="text-xs font-semibold dark:text-white mb-2">Tracks</p>
            <ul className="space-y-1">
              {TRACK_TYPES.map((t) => (
                <li key={t.id} className="text-[10px] dark:text-untold-muted flex items-center gap-2">
                  <span>{t.icon}</span> {t.label}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <ShortcutsModal open={showShortcuts} onClose={() => setShowShortcuts(false)} />
    </div>
  );
}
