/** Timeline track & clip type constants — shared by engine and UI. */

export const TRACK_TYPES = [
  { id: 'video', label: 'Video', icon: '🎬', color: '#3b82f6' },
  { id: 'audio', label: 'Audio', icon: '🎵', color: '#22c55e' },
  { id: 'image', label: 'Images', icon: '🖼️', color: '#a855f7' },
  { id: 'text', label: 'Text', icon: '✏️', color: '#f59e0b' },
  { id: 'transition', label: 'Transitions', icon: '✨', color: '#ec4899' },
  { id: 'caption', label: 'Captions', icon: '💬', color: '#06b6d4' },
];

export const TRACK_TYPE_MAP = Object.fromEntries(TRACK_TYPES.map((t) => [t.id, t]));

export const DEFAULT_ZOOM = 80;
export const MIN_ZOOM = 20;
export const MAX_ZOOM = 400;
export const TRACK_HEIGHT = 56;
export const RULER_HEIGHT = 28;
export const LABEL_WIDTH = 140;

export function uid() {
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
}

export function formatTimecode(seconds) {
  const s = Math.max(0, seconds);
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  const frames = Math.floor((s % 1) * 30);
  return `${m}:${sec.toString().padStart(2, '0')}:${frames.toString().padStart(2, '0')}`;
}

export function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n));
}
