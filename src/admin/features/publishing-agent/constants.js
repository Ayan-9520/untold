export const PUBLISH_PLATFORMS = [
  { id: 'originals', label: 'UNTOLD Originals', icon: '🎬', color: '#d4af37' },
  { id: 'youtube', label: 'YouTube', icon: '▶️', color: '#ff0000' },
  { id: 'instagram', label: 'Instagram', icon: '📸', color: '#e1306c' },
  { id: 'facebook', label: 'Facebook', icon: '👤', color: '#1877f2' },
  { id: 'x', label: 'X', icon: '𝕏', color: '#e7e9ea' },
  { id: 'threads', label: 'Threads', icon: '🧵', color: '#999999' },
];

export const WEBHOOK_EVENTS = [
  'publish.queued',
  'publish.scheduled',
  'publish.approved',
  'publish.rejected',
  'publish.success',
  'publish.failed',
  'publish.retry',
];

export const RUN_STATUS_STYLES = {
  queued: 'text-sky-400',
  running: 'text-blue-400',
  scheduled: 'text-indigo-400',
  pending_approval: 'text-amber-400',
  completed: 'text-emerald-400',
  partial: 'text-orange-400',
  failed: 'text-red-400',
  cancelled: 'text-gray-500',
};

export const JOB_STATUS_COLORS = {
  pending_approval: 'text-yellow-400',
  scheduled: 'text-blue-400',
  queued: 'text-sky-400',
  processing: 'text-purple-400',
  published: 'text-emerald-400',
  failed: 'text-red-400',
  cancelled: 'text-gray-500',
};

export const APPROVAL_STYLES = {
  none: 'text-gray-400',
  pending: 'text-amber-400',
  approved: 'text-emerald-400',
  rejected: 'text-red-400',
};

export function formatPlatform(id) {
  return PUBLISH_PLATFORMS.find((p) => p.id === id)?.label || id;
}
