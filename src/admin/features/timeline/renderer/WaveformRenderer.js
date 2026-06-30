import { LABEL_WIDTH, RULER_HEIGHT, TRACK_HEIGHT, TRACK_TYPE_MAP, formatTimecode } from '../constants';

/**
 * Canvas waveform drawer — used inside clip blocks for audio tracks.
 */
export class WaveformRenderer {
  static draw(ctx, x, y, width, height, peaks, color = '#22c55e') {
    if (!peaks?.length || width < 2) return;
    ctx.save();
    ctx.fillStyle = `${color}33`;
    ctx.fillRect(x, y, width, height);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    const mid = y + height / 2;
    const step = width / peaks.length;
    ctx.beginPath();
    for (let i = 0; i < peaks.length; i += 1) {
      const amp = peaks[i] * (height / 2 - 2);
      const px = x + i * step;
      ctx.moveTo(px, mid - amp);
      ctx.lineTo(px, mid + amp);
    }
    ctx.stroke();
    ctx.restore();
  }

  /** Generate demo peaks when none stored. */
  static demoPeaks(len = 48) {
    return Array.from({ length: len }, (_, i) => 0.2 + Math.abs(Math.sin(i * 0.4)) * 0.5);
  }
}
