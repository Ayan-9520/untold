export const IMAGE_TYPES = [
  { id: 'poster', label: 'Poster', icon: '🎬' },
  { id: 'thumbnail', label: 'Thumbnail', icon: '🎯' },
  { id: 'concept_art', label: 'Concept Art', icon: '🎨' },
  { id: 'environment', label: 'Environment', icon: '🏟️' },
  { id: 'illustration', label: 'Illustration', icon: '✏️' },
  { id: 'sports', label: 'Sports Artwork', icon: '🏆' },
  { id: 'background', label: 'Background', icon: '🖼️' },
];

export const ASPECT_RATIOS = ['16:9', '9:16', '1:1', '4:5'];

export const JOB_STATUS_STYLES = {
  queued: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  running: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  completed: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  failed: 'bg-red-500/15 text-red-400 border-red-500/30',
  cancelled: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
};
