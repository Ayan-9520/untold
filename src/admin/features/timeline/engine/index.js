import { DEFAULT_ZOOM, MAX_ZOOM, MIN_ZOOM, clamp } from '../constants';
import { cloneDocument, normalizeDocument } from './document';
import { HistoryStack } from './history';
import {
  addClip,
  addTrack,
  mergeClips,
  moveClip,
  removeClip,
  setTrackMuted,
  setZoom,
  splitClip,
  trimClip,
} from './operations';
import { PlaybackController } from './playback';

/**
 * TimelineEngine — core state machine.
 * Rendering and React UI subscribe to this; they never mutate document directly.
 */
export class TimelineEngine {
  constructor(initialDocument = null) {
    this.document = normalizeDocument(initialDocument || { duration: 120, fps: 30, tracks: [], settings: { zoom: DEFAULT_ZOOM } });
    this.playhead = 0;
    this.zoom = this.document.settings?.zoom ?? DEFAULT_ZOOM;
    this.selectedClipId = null;
    this.selectedTrackId = null;
    this.history = new HistoryStack();
    this.listeners = new Set();
    this.playback = new PlaybackController((t) => {
      this.playhead = t;
      this.emit();
    });
    this.playback.setDuration(this.document.duration);
  }

  subscribe(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  emit() {
    const snap = this.getSnapshot();
    for (const fn of this.listeners) fn(snap);
  }

  getSnapshot() {
    return {
      document: cloneDocument(this.document),
      playhead: this.playhead,
      zoom: this.zoom,
      selectedClipId: this.selectedClipId,
      selectedTrackId: this.selectedTrackId,
      playing: this.playback.playing,
      canUndo: this.history.canUndo(),
      canRedo: this.history.canRedo(),
      duration: this.document.duration,
    };
  }

  loadDocument(doc, { playhead, zoom, clearHistory = true } = {}) {
    this.document = normalizeDocument(doc);
    if (playhead != null) this.playhead = playhead;
    if (zoom != null) this.zoom = zoom;
    else this.zoom = this.document.settings?.zoom ?? DEFAULT_ZOOM;
    this.playback.setDuration(this.document.duration);
    if (clearHistory) this.history.clear();
    this.emit();
  }

  _commit(mutator) {
    this.history.push(this.document);
    this.document = mutator(this.document);
    this.document.settings = { ...this.document.settings, zoom: this.zoom };
    this.playback.setDuration(this.document.duration);
    this.emit();
  }

  setPlayhead(t) {
    this.playhead = clamp(t, 0, this.document.duration);
    this.playback.setPlayhead(this.playhead);
    this.emit();
  }

  setZoom(z) {
    this.zoom = clamp(z, MIN_ZOOM, MAX_ZOOM);
    this._commit((doc) => setZoom(doc, this.zoom));
  }

  zoomBy(delta) {
    this.setZoom(this.zoom + delta);
  }

  selectClip(clipId) {
    this.selectedClipId = clipId;
    const found = clipId && this.document.tracks.flatMap((t) => t.clips).find((c) => c.id === clipId);
    if (found) {
      const track = this.document.tracks.find((t) => t.clips.some((c) => c.id === clipId));
      this.selectedTrackId = track?.id ?? null;
    }
    this.emit();
  }

  selectTrack(trackId) {
    this.selectedTrackId = trackId;
    this.emit();
  }

  play() { this.playback.play(); }
  pause() { this.playback.pause(); }
  togglePlay() { this.playback.toggle(); }

  undo() {
    const prev = this.history.undo(this.document);
    if (!prev) return;
    this.document = normalizeDocument(prev);
    this.playback.setDuration(this.document.duration);
    this.emit();
  }

  redo() {
    const next = this.history.redo(this.document);
    if (!next) return;
    this.document = normalizeDocument(next);
    this.playback.setDuration(this.document.duration);
    this.emit();
  }

  trimSelected(trimIn, trimOut) {
    if (!this.selectedClipId) return;
    this._commit((doc) => trimClip(doc, this.selectedClipId, { trimIn, trimOut }));
  }

  trimSelectedToPlayhead() {
    if (!this.selectedClipId) return;
    const found = this.document.tracks.flatMap((t) => t.clips).find((c) => c.id === this.selectedClipId);
    if (!found) return;
    const local = this.playhead - found.start;
    if (local <= 0 || local >= found.duration) return;
    this._commit((doc) => trimClip(doc, this.selectedClipId, {
      trimIn: found.trimIn ?? 0,
      trimOut: (found.trimIn ?? 0) + local,
    }));
  }

  splitSelected() {
    if (!this.selectedClipId) return;
    this._commit((doc) => splitClip(doc, this.selectedClipId, this.playhead));
  }

  mergeSelectedWithNext() {
    if (!this.selectedClipId) return;
    const track = this.document.tracks.find((t) => t.clips.some((c) => c.id === this.selectedClipId));
    if (!track) return;
    const idx = track.clips.findIndex((c) => c.id === this.selectedClipId);
    const next = track.clips[idx + 1];
    if (!next) return;
    this._commit((doc) => mergeClips(doc, this.selectedClipId, next.id));
  }

  deleteSelected() {
    if (!this.selectedClipId) return;
    const id = this.selectedClipId;
    this.selectedClipId = null;
    this._commit((doc) => removeClip(doc, id));
  }

  moveSelected(trackId, newStart) {
    if (!this.selectedClipId) return;
    this._commit((doc) => moveClip(doc, this.selectedClipId, trackId, newStart));
  }

  addTrack(type, name) {
    this._commit((doc) => addTrack(doc, type, name));
  }

  addClip(trackId, clipData) {
    this._commit((doc) => addClip(doc, trackId, clipData));
  }

  toggleTrackMute(trackId) {
    const track = this.document.tracks.find((t) => t.id === trackId);
    if (!track) return;
    this._commit((doc) => setTrackMuted(doc, trackId, !track.muted));
  }

  destroy() {
    this.playback.destroy();
    this.listeners.clear();
  }
}

export { normalizeDocument, cloneDocument } from './document';
export * from './operations';
export { HistoryStack } from './history';
export { PlaybackController } from './playback';
export { SHORTCUTS, matchShortcut } from './shortcuts';
