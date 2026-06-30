import { clamp } from '../constants';
import { cloneDocument, createClip, createTrack, findClip, findTrack, normalizeDocument } from './document';

/** Pure timeline edit operations — no DOM, no React. */
export function trimClip(doc, clipId, { trimIn, trimOut }) {
  const next = cloneDocument(doc);
  const found = findClip(next, clipId);
  if (!found) return next;
  const { clip } = found;
  const inVal = trimIn ?? clip.trimIn ?? 0;
  const outVal = trimOut ?? clip.trimOut ?? clip.duration;
  const span = Math.max(0.1, outVal - inVal);
  clip.trimIn = inVal;
  clip.trimOut = outVal;
  clip.duration = span;
  return normalizeDocument(next);
}

export function splitClip(doc, clipId, splitAtGlobal) {
  const next = cloneDocument(doc);
  const found = findClip(next, clipId);
  if (!found) return next;
  const { track, clip } = found;
  const local = splitAtGlobal - clip.start;
  if (local <= 0.1 || local >= clip.duration - 0.1) return next;

  const leftDuration = local;
  const rightDuration = clip.duration - local;
  const leftTrimOut = (clip.trimIn ?? 0) + leftDuration;
  const rightTrimIn = leftTrimOut;

  const right = createClip(clip.type, {
    ...clip,
    id: undefined,
    start: clip.start + leftDuration,
    duration: rightDuration,
    trimIn: rightTrimIn,
    trimOut: clip.trimOut ?? clip.duration,
    label: `${clip.label} (2)`,
  });

  clip.duration = leftDuration;
  clip.trimOut = leftTrimOut;
  clip.label = `${clip.label} (1)`;

  const idx = track.clips.findIndex((c) => c.id === clipId);
  track.clips.splice(idx + 1, 0, right);
  return normalizeDocument(next);
}

export function mergeClips(doc, clipIdA, clipIdB) {
  const next = cloneDocument(doc);
  const a = findClip(next, clipIdA);
  const b = findClip(next, clipIdB);
  if (!a || !b || a.track.id !== b.track.id) return next;

  const [first, second] = a.clip.start <= b.clip.start ? [a, b] : [b, a];
  const gap = second.clip.start - (first.clip.start + first.clip.duration);
  if (gap > 0.5) return next;

  first.clip.duration = second.clip.start + second.clip.duration - first.clip.start;
  first.clip.trimOut = second.clip.trimOut ?? second.clip.duration;
  first.clip.label = `${first.clip.label} + ${second.clip.label}`;

  first.track.clips = first.track.clips.filter((c) => c.id !== second.clip.id);
  return normalizeDocument(next);
}

export function moveClip(doc, clipId, trackId, newStart) {
  const next = cloneDocument(doc);
  const found = findClip(next, clipId);
  const target = findTrack(next, trackId);
  if (!found || !target || target.locked) return next;

  found.track.clips = found.track.clips.filter((c) => c.id !== clipId);
  found.clip.start = clamp(newStart, 0, next.duration);
  target.clips.push(found.clip);
  target.clips.sort((a, b) => a.start - b.start);
  return normalizeDocument(next);
}

export function removeClip(doc, clipId) {
  const next = cloneDocument(doc);
  const found = findClip(next, clipId);
  if (!found) return next;
  found.track.clips = found.track.clips.filter((c) => c.id !== clipId);
  return normalizeDocument(next);
}

export function addClip(doc, trackId, clipData) {
  const next = cloneDocument(doc);
  const track = findTrack(next, trackId);
  if (!track) return next;
  const clip = createClip(clipData.type || track.type, clipData);
  track.clips.push(clip);
  track.clips.sort((a, b) => a.start - b.start);
  return normalizeDocument(next);
}

export function addTrack(doc, type, name) {
  const next = cloneDocument(doc);
  next.tracks.push(createTrack(type, name));
  return normalizeDocument(next);
}

export function setTrackMuted(doc, trackId, muted) {
  const next = cloneDocument(doc);
  const track = findTrack(next, trackId);
  if (track) track.muted = muted;
  return next;
}

export function setZoom(doc, zoom) {
  const next = cloneDocument(doc);
  next.settings = { ...next.settings, zoom };
  return next;
}
