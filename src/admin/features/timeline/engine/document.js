import { DEFAULT_ZOOM, TRACK_TYPE_MAP, uid } from '../constants';

const CLIP_COLORS = Object.fromEntries(
  Object.entries(TRACK_TYPE_MAP).map(([k, v]) => [k, v.color]),
);

/** Create an empty timeline document. */
export function createEmptyDocument(duration = 120) {
  return {
    duration,
    fps: 30,
    tracks: [],
    settings: { zoom: DEFAULT_ZOOM, snapEnabled: true },
  };
}

export function createTrack(type, name) {
  const meta = TRACK_TYPE_MAP[type] || TRACK_TYPE_MAP.video;
  return {
    id: uid(),
    type,
    name: name || meta.label,
    muted: false,
    locked: false,
    clips: [],
  };
}

export function createClip(type, overrides = {}) {
  const meta = TRACK_TYPE_MAP[type] || TRACK_TYPE_MAP.video;
  const duration = overrides.duration ?? 5;
  return {
    id: uid(),
    type,
    start: overrides.start ?? 0,
    duration,
    trimIn: overrides.trimIn ?? 0,
    trimOut: overrides.trimOut ?? duration,
    label: overrides.label ?? meta.label,
    assetUrl: overrides.assetUrl ?? null,
    color: overrides.color ?? meta.color,
    transitionIn: overrides.transitionIn ?? null,
    transitionOut: overrides.transitionOut ?? null,
    caption: overrides.caption ?? null,
    waveformPeaks: overrides.waveformPeaks ?? null,
  };
}

/** Deep-clone document for immutable history. */
export function cloneDocument(doc) {
  return JSON.parse(JSON.stringify(doc));
}

export function findClip(doc, clipId) {
  for (const track of doc.tracks) {
    const clip = track.clips.find((c) => c.id === clipId);
    if (clip) return { track, clip };
  }
  return null;
}

export function findTrack(doc, trackId) {
  return doc.tracks.find((t) => t.id === trackId) ?? null;
}

export function computeDuration(doc) {
  let max = doc.duration || 0;
  for (const track of doc.tracks) {
    for (const clip of track.clips) {
      max = Math.max(max, clip.start + clip.duration);
    }
  }
  return max;
}

export function normalizeDocument(doc) {
  const next = cloneDocument(doc);
  next.duration = computeDuration(next);
  if (!next.settings) next.settings = { zoom: DEFAULT_ZOOM, snapEnabled: true };
  for (const track of next.tracks) {
    for (const clip of track.clips) {
      if (!clip.color) clip.color = CLIP_COLORS[clip.type] || CLIP_COLORS.video;
      if (clip.trimOut == null) clip.trimOut = clip.duration;
    }
  }
  return next;
}
