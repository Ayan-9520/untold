export const CONTENT_TYPES = [
  { id: 'video', label: 'Video' },
  { id: 'documentary', label: 'Documentary' },
  { id: 'shorts', label: 'Shorts' },
  { id: 'article', label: 'Article' },
  { id: 'podcast', label: 'Podcast' },
];

export const JOB_STATUS_STYLES = {
  queued: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  running: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  completed: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  failed: 'bg-red-500/15 text-red-400 border-red-500/30',
  cancelled: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
};

export const APPROVAL_STYLES = {
  none: 'text-gray-400',
  pending: 'text-amber-400',
  approved: 'text-emerald-400',
  rejected: 'text-red-400',
};
