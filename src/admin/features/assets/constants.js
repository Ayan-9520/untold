export const ASSET_FOLDERS = [
  { id: 'all', label: 'All assets', icon: '📁' },
  { id: 'images', label: 'Images', icon: '📷' },
  { id: 'videos', label: 'Videos', icon: '🎬' },
  { id: 'audio', label: 'Audio', icon: '🎵' },
  { id: 'documents', label: 'Documents', icon: '📄' },
  { id: 'thumbnails', label: 'Thumbnails', icon: '🎯' },
  { id: 'posters', label: 'Posters', icon: '🖼️' },
];

export function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let n = bytes;
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024;
    i += 1;
  }
  return `${n.toFixed(i ? 1 : 0)} ${units[i]}`;
}
