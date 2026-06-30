/** Playback clock — independent of React render cycle. */
export class PlaybackController {
  constructor(onTick) {
    this.onTick = onTick;
    this.playing = false;
    this.playhead = 0;
    this.duration = 120;
    this._raf = null;
    this._last = 0;
  }

  setDuration(d) {
    this.duration = d;
    if (this.playhead > d) this.playhead = 0;
  }

  setPlayhead(t) {
    this.playhead = Math.max(0, Math.min(t, this.duration));
    this.onTick?.(this.playhead, this.playing);
  }

  play() {
    if (this.playing) return;
    this.playing = true;
    this._last = performance.now();
    this._loop();
    this.onTick?.(this.playhead, true);
  }

  pause() {
    this.playing = false;
    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = null;
    this.onTick?.(this.playhead, false);
  }

  toggle() {
    if (this.playing) this.pause();
    else this.play();
  }

  _loop = () => {
    const now = performance.now();
    const dt = (now - this._last) / 1000;
    this._last = now;
    this.playhead += dt;
    if (this.playhead >= this.duration) {
      this.playhead = 0;
      this.pause();
      return;
    }
    this.onTick?.(this.playhead, true);
    this._raf = requestAnimationFrame(this._loop);
  };

  destroy() {
    this.pause();
  }
}
