/** Publishing CMS constants */

export const PUBLISH_PLATFORMS = [
  { id: 'originals', label: 'UNTOLD Originals', icon: '🎬', color: '#d4af37' },
  { id: 'youtube', label: 'YouTube', icon: '▶️', color: '#ff0000' },
  { id: 'instagram', label: 'Instagram', icon: '📸', color: '#e1306c' },
  { id: 'facebook', label: 'Facebook', icon: '👤', color: '#1877f2' },
  { id: 'x', label: 'X', icon: '𝕏', color: '#e7e9ea' },
  { id: 'threads', label: 'Threads', icon: '🧵', color: '#999999' },
];

export const PLATFORM_MAP = Object.fromEntries(PUBLISH_PLATFORMS.map((p) => [p.id, p]));

export const VISIBILITY_STATES = [
  { id: 'draft', label: 'Draft', color: 'text-gray-400 border-gray-500/30' },
  { id: 'published', label: 'Published', color: 'text-emerald-400 border-emerald-500/30' },
  { id: 'archived', label: 'Archived', color: 'text-amber-400 border-amber-500/30' },
];

export const JOB_STATUS_COLORS = {
  pending_approval: 'text-yellow-400',
  scheduled: 'text-blue-400',
  queued: 'text-sky-400',
  processing: 'text-purple-400',
  published: 'text-emerald-400',
  failed: 'text-red-400',
  cancelled: 'text-gray-500',
  pending: 'text-yellow-400',
};

export function formatPlatform(id) {
  return PLATFORM_MAP[id]?.label || id;
}
