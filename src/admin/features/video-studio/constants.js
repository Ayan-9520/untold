export const VIDEO_TYPES = [
  { id: 'b_roll', label: 'B-roll', icon: '🎞️' },
  { id: 'drone', label: 'Drone Style', icon: '🛸' },
  { id: 'animation', label: 'Animation', icon: '✨' },
  { id: 'sports_intro', label: 'Sports Intro', icon: '🏟️' },
  { id: 'cinematic', label: 'Cinematic Motion', icon: '🎬' },
  { id: 'motion_graphics', label: 'Motion Graphics', icon: '📊' },
  { id: 'slow_motion', label: 'Slow Motion', icon: '⏱️' },
];

export const ASPECT_RATIOS = ['16:9', '9:16', '1:1'];

export const DURATION_OPTIONS = [4, 6, 8, 10, 12, 15, 20, 30];

export const JOB_STATUS_STYLES = {
  queued: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  running: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  completed: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  failed: 'bg-red-500/15 text-red-400 border-red-500/30',
  cancelled: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
};
