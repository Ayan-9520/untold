import { useEffect, useRef } from 'react';
import { TimelineRenderer } from '../renderer';

/** Mounts canvas renderer — UI shell only; drawing is in TimelineRenderer. */
export default function TimelineCanvas({ snapshot, engine, height = 360 }) {
  const canvasRef = useRef(null);
  const rendererRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !engine) return;
    rendererRef.current = new TimelineRenderer(canvasRef.current, {
      onClipClick: (clipId, trackId) => {
        engine.selectClip(clipId);
        engine.selectTrack(trackId);
      },
      onSeek: (t) => engine.setPlayhead(t),
    });
    rendererRef.current.resize();
    return () => rendererRef.current?.destroy();
  }, [engine]);

  useEffect(() => {
    rendererRef.current?.render(snapshot);
  }, [snapshot]);

  return (
    <div className="rounded-xl border dark:border-white/10 overflow-hidden bg-black/40" style={{ height }}>
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
}
