import {
  LABEL_WIDTH,
  RULER_HEIGHT,
  TRACK_HEIGHT,
  TRACK_TYPE_MAP,
  formatTimecode,
} from '../constants';
import { WaveformRenderer } from './WaveformRenderer';

/**
 * TimelineRenderer — canvas drawing engine.
 * Reads snapshot from TimelineEngine; never owns state.
 */
export class TimelineRenderer {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.options = options;
    this.snapshot = null;
    this.scrollLeft = 0;
    this._onClipClick = options.onClipClick || (() => {});
    this._onSeek = options.onSeek || (() => {});
    this._dpr = window.devicePixelRatio || 1;
    this._boundResize = () => this.resize();
    window.addEventListener('resize', this._boundResize);
    this._boundClick = (e) => this._handleClick(e);
    canvas.addEventListener('click', this._boundClick);
  }

  destroy() {
    window.removeEventListener('resize', this._boundResize);
    this.canvas.removeEventListener('click', this._boundClick);
  }

  resize() {
    const parent = this.canvas.parentElement;
    if (!parent) return;
    const w = parent.clientWidth;
    const h = parent.clientHeight;
    this._dpr = window.devicePixelRatio || 1;
    this.canvas.width = w * this._dpr;
    this.canvas.height = h * this._dpr;
    this.canvas.style.width = `${w}px`;
    this.canvas.style.height = `${h}px`;
    this.ctx.setTransform(this._dpr, 0, 0, this._dpr, 0, 0);
    this.render(this.snapshot);
  }

  render(snapshot) {
    if (!snapshot) return;
    this.snapshot = snapshot;
    const { document, playhead, zoom, selectedClipId } = snapshot;
    const ctx = this.ctx;
    const w = this.canvas.width / this._dpr;
    const h = this.canvas.height / this._dpr;
    const tracks = document.tracks || [];
    const contentH = RULER_HEIGHT + tracks.length * TRACK_HEIGHT;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, w, h);

    this._drawRuler(ctx, w, document.duration, zoom, playhead);
    let y = RULER_HEIGHT;
    for (const track of tracks) {
      this._drawTrack(ctx, track, y, w, zoom, selectedClipId);
      y += TRACK_HEIGHT;
    }

    // Playhead line
    const px = LABEL_WIDTH + playhead * zoom - this.scrollLeft;
    ctx.strokeStyle = '#d4af37';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(px, 0);
    ctx.lineTo(px, Math.max(h, contentH));
    ctx.stroke();

    // Scroll hint
    const totalW = document.duration * zoom + LABEL_WIDTH;
    if (totalW > w) {
      ctx.fillStyle = '#ffffff22';
      ctx.fillRect(w - 4, 0, 4, h);
    }
  }

  _drawRuler(ctx, w, duration, zoom, playhead) {
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, w, RULER_HEIGHT);
    ctx.fillStyle = '#888';
    ctx.font = '10px system-ui';
    const step = zoom >= 120 ? 1 : zoom >= 60 ? 5 : 10;
    for (let t = 0; t <= duration; t += step) {
      const x = LABEL_WIDTH + t * zoom - this.scrollLeft;
      if (x < LABEL_WIDTH || x > w) continue;
      ctx.fillRect(x, RULER_HEIGHT - 6, 1, 6);
      ctx.fillText(formatTimecode(t), x + 2, 12);
    }
    ctx.fillStyle = '#d4af37';
    ctx.fillText(formatTimecode(playhead), 4, 12);
  }

  _drawTrack(ctx, track, y, w, zoom, selectedClipId) {
    const meta = TRACK_TYPE_MAP[track.type] || TRACK_TYPE_MAP.video;
    ctx.fillStyle = y % (TRACK_HEIGHT * 2) === RULER_HEIGHT ? '#121212' : '#0e0e0e';
    ctx.fillRect(0, y, w, TRACK_HEIGHT);

    // Label column
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, y, LABEL_WIDTH, TRACK_HEIGHT);
    ctx.strokeStyle = '#333';
    ctx.strokeRect(0, y, LABEL_WIDTH, TRACK_HEIGHT);
    ctx.fillStyle = track.muted ? '#666' : '#ccc';
    ctx.font = '11px system-ui';
    ctx.fillText(`${meta.icon} ${track.name}`.slice(0, 18), 8, y + TRACK_HEIGHT / 2 + 4);

    // Track lane
    ctx.fillStyle = '#0d0d0d';
    ctx.fillRect(LABEL_WIDTH, y, w - LABEL_WIDTH, TRACK_HEIGHT);
    ctx.strokeStyle = '#222';
    ctx.strokeRect(LABEL_WIDTH, y, w - LABEL_WIDTH, TRACK_HEIGHT);

    for (const clip of track.clips) {
      this._drawClip(ctx, clip, track, y, zoom, selectedClipId);
    }
  }

  _drawClip(ctx, clip, track, trackY, zoom, selectedClipId) {
    const x = LABEL_WIDTH + clip.start * zoom - this.scrollLeft;
    const width = Math.max(4, clip.duration * zoom);
    const y = trackY + 6;
    const height = TRACK_HEIGHT - 12;
    const selected = clip.id === selectedClipId;
    const color = clip.color || '#3b82f6';

    ctx.fillStyle = selected ? color : `${color}cc`;
    ctx.strokeStyle = selected ? '#fff' : color;
    ctx.lineWidth = selected ? 2 : 1;
    ctx.beginPath();
    ctx.roundRect(x, y, width, height, 4);
    ctx.fill();
    ctx.stroke();

    if (track.type === 'audio' || clip.type === 'audio') {
      const peaks = clip.waveformPeaks || WaveformRenderer.demoPeaks();
      WaveformRenderer.draw(ctx, x + 2, y + 2, width - 4, height - 4, peaks, color);
    }

    if (width > 40) {
      ctx.fillStyle = '#fff';
      ctx.font = '10px system-ui';
      ctx.fillText(clip.label?.slice(0, Math.floor(width / 7)) || '', x + 4, y + 14);
    }

    // Transition markers
    if (clip.transitionIn) {
      ctx.fillStyle = '#ec4899';
      ctx.fillRect(x, y, 4, height);
    }
    if (clip.transitionOut) {
      ctx.fillStyle = '#ec4899';
      ctx.fillRect(x + width - 4, y, 4, height);
    }
  }

  _handleClick(e) {
    if (!this.snapshot) return;
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Ruler seek
    if (y < RULER_HEIGHT && x > LABEL_WIDTH) {
      const t = (x - LABEL_WIDTH + this.scrollLeft) / this.snapshot.zoom;
      this._onSeek(Math.max(0, t));
      return;
    }

    const trackIdx = Math.floor((y - RULER_HEIGHT) / TRACK_HEIGHT);
    const tracks = this.snapshot.document.tracks || [];
    if (trackIdx < 0 || trackIdx >= tracks.length) return;
    const track = tracks[trackIdx];
    const localX = x - LABEL_WIDTH + this.scrollLeft;
    for (const clip of track.clips) {
      const cx = clip.start * this.snapshot.zoom;
      const cw = clip.duration * this.snapshot.zoom;
      if (localX >= cx && localX <= cx + cw) {
        this._onClipClick(clip.id, track.id);
        return;
      }
    }
  }

  setScrollLeft(px) {
    this.scrollLeft = px;
    this.render(this.snapshot);
  }
}

export { WaveformRenderer };
