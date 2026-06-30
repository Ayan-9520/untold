/** Keyboard shortcut definitions — consumed by UI layer. */
export const SHORTCUTS = [
  { keys: 'Space', action: 'playPause', label: 'Play / Pause' },
  { keys: 'J', action: 'stepBack', label: 'Step back 1s' },
  { keys: 'K', action: 'pause', label: 'Pause' },
  { keys: 'L', action: 'stepForward', label: 'Step forward 1s' },
  { keys: 'S', action: 'split', label: 'Split clip at playhead' },
  { keys: 'T', action: 'trim', label: 'Trim selected to playhead' },
  { keys: 'M', action: 'merge', label: 'Merge adjacent clips' },
  { keys: 'Delete', action: 'delete', label: 'Delete selected clip' },
  { keys: 'Ctrl+Z', action: 'undo', label: 'Undo' },
  { keys: 'Ctrl+Shift+Z', action: 'redo', label: 'Redo' },
  { keys: 'Ctrl+S', action: 'save', label: 'Save now' },
  { keys: '+', action: 'zoomIn', label: 'Zoom in' },
  { keys: '-', action: 'zoomOut', label: 'Zoom out' },
  { keys: '?', action: 'help', label: 'Keyboard shortcuts' },
];

export function matchShortcut(event) {
  const key = event.key;
  const ctrl = event.ctrlKey || event.metaKey;
  if (ctrl && event.shiftKey && key.toLowerCase() === 'z') return 'redo';
  if (ctrl && key.toLowerCase() === 'z') return 'undo';
  if (ctrl && key.toLowerCase() === 's') return 'save';
  if (key === ' ') return 'playPause';
  if (key === 'j' || key === 'J') return 'stepBack';
  if (key === 'k' || key === 'K') return 'pause';
  if (key === 'l' || key === 'L') return 'stepForward';
  if (key === 's' || key === 'S') return 'split';
  if (key === 't' || key === 'T') return 'trim';
  if (key === 'm' || key === 'M') return 'merge';
  if (key === 'Delete' || key === 'Backspace') return 'delete';
  if (key === '+' || key === '=') return 'zoomIn';
  if (key === '-') return 'zoomOut';
  if (key === '?') return 'help';
  return null;
}
