import { useEffect, useRef, useState, useCallback } from 'react';
import streamingApi from '../../api/streaming';

const SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];

export default function VideoPlayer({ videoId, fallbackUrl, poster, title, onProgress }) {
  const containerRef = useRef(null);
  const videoRef = useRef(null);
  const [streamUrl, setStreamUrl] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [speed, setSpeed] = useState(1);
  const [subtitles, setSubtitles] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const lastSave = useRef(0);

  useEffect(() => {
    let active = true;

    const applyFallback = () => {
      if (!active) return;
      if (fallbackUrl) {
        setStreamUrl(fallbackUrl);
        setError(null);
        setLoading(false);
        return;
      }
      setError('Stream unavailable offline.');
      setLoading(false);
    };

    setLoading(true);
    setError(null);
    setStreamUrl(null);

    if (!videoId) {
      applyFallback();
      return () => { active = false; };
    }

    streamingApi
      .getStreamUrl(videoId)
      .then((data) => {
        if (!active) return;
        const url = data?.stream_url;
        if (url && (data.format !== 'token' || url.startsWith('http'))) {
          setStreamUrl(url);
          setLoading(false);
          return;
        }
        applyFallback();
      })
      .catch(() => {
        if (!active) return;
        applyFallback();
      });

    return () => { active = false; };
  }, [videoId, fallbackUrl]);

  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;
    el.playbackRate = speed;
  }, [speed, streamUrl]);

  useEffect(() => {
    const el = videoRef.current;
    if (!el || !streamUrl) return undefined;

    const onTimeUpdate = () => {
      const now = Date.now();
      if (now - lastSave.current < 15000) return;
      lastSave.current = now;
      if (videoId) {
        streamingApi.saveProgress(videoId, el.currentTime, el.duration).catch(() => {});
      }
      onProgress?.(el.currentTime, el.duration);
    };

    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);

    el.addEventListener('timeupdate', onTimeUpdate);
    el.addEventListener('play', onPlay);
    el.addEventListener('pause', onPause);
    return () => {
      el.removeEventListener('timeupdate', onTimeUpdate);
      el.removeEventListener('play', onPlay);
      el.removeEventListener('pause', onPause);
    };
  }, [videoId, streamUrl, onProgress]);

  const togglePlay = () => {
    const el = videoRef.current;
    if (!el) return;
    if (el.paused) el.play();
    else el.pause();
  };

  const toggleFullscreen = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    if (document.fullscreenElement) document.exitFullscreen();
    else el.requestFullscreen?.();
  }, []);

  const togglePiP = useCallback(async () => {
    const el = videoRef.current;
    if (!el) return;
    try {
      if (document.pictureInPictureElement) await document.exitPictureInPicture();
      else await el.requestPictureInPicture();
    } catch {
      /* unsupported */
    }
  }, []);

  if (loading) {
    return (
      <div className="ott-player ott-player--loading">
        <div className="ott-player-shimmer" />
        <p className="text-white/60 text-sm">Loading stream…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ott-player ott-player--error">
        <p className="text-white/80 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="ott-player">
      <video
        ref={videoRef}
        src={streamUrl}
        autoPlay
        playsInline
        poster={poster}
        title={title}
        className="ott-player-video"
        onClick={togglePlay}
      >
        {subtitles && (
          <track kind="subtitles" label="English" srcLang="en" default />
        )}
      </video>

      <div className="ott-player-bar">
        <button type="button" className="ott-player-btn" onClick={togglePlay} aria-label={isPlaying ? 'Pause' : 'Play'}>
          {isPlaying ? '⏸' : '▶'}
        </button>

        <label className="ott-player-speed">
          <span className="sr-only">Playback speed</span>
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="ott-player-speed-select"
            aria-label="Playback speed"
          >
            {SPEEDS.map((s) => (
              <option key={s} value={s}>{s === 1 ? '1×' : `${s}×`}</option>
            ))}
          </select>
        </label>

        <button
          type="button"
          className={`ott-player-btn ${subtitles ? 'ott-player-btn--active' : ''}`}
          onClick={() => setSubtitles((s) => !s)}
          aria-pressed={subtitles}
        >
          CC
        </button>

        <button type="button" className="ott-player-btn" onClick={togglePiP} aria-label="Picture in picture">
          PiP
        </button>

        <button type="button" className="ott-player-btn" onClick={toggleFullscreen} aria-label="Fullscreen">
          ⛶
        </button>
      </div>
    </div>
  );
}
