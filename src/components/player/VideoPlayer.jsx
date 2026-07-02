import { useEffect, useRef, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Hls from 'hls.js';
import streamingApi from '../../api/streaming';

const SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];
const QUALITIES = [
  { id: 'auto', label: 'Auto' },
  { id: -1, label: '1080p' },
  { id: -2, label: '720p' },
  { id: -3, label: '480p' },
];

function isHlsUrl(url) {
  return url && (url.includes('.m3u8') || url.includes('application/vnd.apple.mpegurl'));
}

export default function VideoPlayer({
  videoId,
  fallbackUrl,
  poster,
  title,
  onProgress,
  subtitleUrl: subtitleUrlProp,
  introEndSeconds,
  nextVideoId,
  nextVideoTitle,
  autoplayNext = true,
}) {
  const containerRef = useRef(null);
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [streamUrl, setStreamUrl] = useState(null);
  const [streamFormat, setStreamFormat] = useState('mp4');
  const [subtitleUrl, setSubtitleUrl] = useState(subtitleUrlProp);
  const [introEnd, setIntroEnd] = useState(introEndSeconds);
  const [nextId, setNextId] = useState(nextVideoId);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [speed, setSpeed] = useState(1);
  const [quality, setQuality] = useState('auto');
  const [subtitles, setSubtitles] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSkipIntro, setShowSkipIntro] = useState(false);
  const [showUpNext, setShowUpNext] = useState(false);
  const [upNextCountdown, setUpNextCountdown] = useState(10);
  const lastSave = useRef(0);

  useEffect(() => {
    let active = true;

    const applyFallback = () => {
      if (!active) return;
      if (fallbackUrl) {
        setStreamUrl(fallbackUrl);
        setStreamFormat(isHlsUrl(fallbackUrl) ? 'hls' : 'mp4');
        setError(null);
        setLoading(false);
        return;
      }
      setError('Stream unavailable.');
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
          setStreamFormat(data.format === 'hls' || isHlsUrl(url) ? 'hls' : 'mp4');
          if (data.subtitle_url) setSubtitleUrl(data.subtitle_url);
          if (data.intro_end_seconds) setIntroEnd(data.intro_end_seconds);
          if (data.next_video_id) setNextId(data.next_video_id);
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
    const video = videoRef.current;
    if (!video || !streamUrl) return undefined;

    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }

    const useHls = streamFormat === 'hls' || isHlsUrl(streamUrl);

    if (useHls && Hls.isSupported()) {
      const hls = new Hls({ enableWorker: true, lowLatencyMode: false });
      hlsRef.current = hls;
      hls.loadSource(streamUrl);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(() => {});
      });
      hls.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) {
          if (fallbackUrl && fallbackUrl !== streamUrl) {
            video.src = fallbackUrl;
          } else {
            setError('Playback error. Try again.');
          }
        }
      });
    } else if (useHls && video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = streamUrl;
    } else {
      video.src = streamUrl;
    }

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [streamUrl, streamFormat, fallbackUrl]);

  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;
    el.playbackRate = speed;
  }, [speed, streamUrl]);

  useEffect(() => {
    const hls = hlsRef.current;
    if (!hls) return;
    if (quality === 'auto') {
      hls.currentLevel = -1;
      return;
    }
    const level = Number(quality);
    if (!Number.isNaN(level)) hls.currentLevel = level;
  }, [quality, streamUrl]);

  useEffect(() => {
    const el = videoRef.current;
    if (!el || !streamUrl) return undefined;

    const onTimeUpdate = () => {
      const t = el.currentTime;
      const dur = el.duration || 0;

      if (introEnd && t < introEnd && t > 3) setShowSkipIntro(true);
      else setShowSkipIntro(false);

      if (nextId && dur > 0 && dur - t < 15) {
        setShowUpNext(true);
        setUpNextCountdown(Math.max(1, Math.ceil(dur - t)));
      } else {
        setShowUpNext(false);
      }

      const now = Date.now();
      if (now - lastSave.current < 15000) return;
      lastSave.current = now;
      if (videoId) {
        streamingApi.saveProgress(videoId, t, dur).catch(() => {});
      }
      onProgress?.(t, dur);
    };

    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    const onEnded = () => {
      if (autoplayNext && nextId) {
        window.location.href = `/video/${nextId}`;
      }
    };

    el.addEventListener('timeupdate', onTimeUpdate);
    el.addEventListener('play', onPlay);
    el.addEventListener('pause', onPause);
    el.addEventListener('ended', onEnded);
    return () => {
      el.removeEventListener('timeupdate', onTimeUpdate);
      el.removeEventListener('play', onPlay);
      el.removeEventListener('pause', onPause);
      el.removeEventListener('ended', onEnded);
    };
  }, [videoId, streamUrl, onProgress, introEnd, nextId, autoplayNext]);

  const togglePlay = () => {
    const el = videoRef.current;
    if (!el) return;
    if (el.paused) el.play();
    else el.pause();
  };

  const skipIntro = () => {
    const el = videoRef.current;
    if (el && introEnd) {
      el.currentTime = introEnd;
      setShowSkipIntro(false);
    }
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
    } catch { /* unsupported */ }
  }, []);

  const castVideo = useCallback(() => {
    const el = videoRef.current;
    if (!el) return;
    if (el.webkitShowPlaybackTargetPicker) {
      el.webkitShowPlaybackTargetPicker();
      return;
    }
    if (window.chrome?.cast?.isAvailable) {
      alert('Chromecast: open from Chrome browser menu → Cast');
    } else {
      alert('Casting requires Chrome with Cast extension or AirPlay on Safari.');
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
        playsInline
        poster={poster}
        title={title}
        className="ott-player-video"
        onClick={togglePlay}
      >
        {subtitles && subtitleUrl && (
          <track kind="subtitles" label="English" srcLang="en" src={subtitleUrl} default />
        )}
      </video>

      {showSkipIntro && (
        <button type="button" className="ott-skip-intro" onClick={skipIntro}>
          Skip Intro
        </button>
      )}

      {showUpNext && nextId && (
        <div className="ott-up-next">
          <p className="text-xs text-untold-muted uppercase tracking-wider">Up Next in {upNextCountdown}s</p>
          <p className="text-sm font-semibold text-white">{nextVideoTitle || 'Next episode'}</p>
          <Link to={`/video/${nextId}`} className="ott-up-next-play">Play now</Link>
        </div>
      )}

      <div className="ott-player-bar">
        <button type="button" className="ott-player-btn" onClick={togglePlay} aria-label={isPlaying ? 'Pause' : 'Play'}>
          {isPlaying ? '⏸' : '▶'}
        </button>

        <label className="ott-player-speed">
          <span className="sr-only">Quality</span>
          <select value={quality} onChange={(e) => setQuality(e.target.value)} className="ott-player-speed-select" aria-label="Quality">
            <option value="auto">Auto</option>
            {QUALITIES.filter((q) => q.id !== 'auto').map((q) => (
              <option key={q.id} value={q.id}>{q.label}</option>
            ))}
          </select>
        </label>

        <label className="ott-player-speed">
          <span className="sr-only">Speed</span>
          <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))} className="ott-player-speed-select" aria-label="Speed">
            {SPEEDS.map((s) => (
              <option key={s} value={s}>{s === 1 ? '1×' : `${s}×`}</option>
            ))}
          </select>
        </label>

        <button type="button" className={`ott-player-btn ${subtitles ? 'ott-player-btn--active' : ''}`} onClick={() => setSubtitles((s) => !s)} aria-pressed={subtitles}>
          CC
        </button>

        <button type="button" className="ott-player-btn" onClick={castVideo} aria-label="Cast">Cast</button>
        <button type="button" className="ott-player-btn" onClick={togglePiP} aria-label="PiP">PiP</button>
        <button type="button" className="ott-player-btn" onClick={toggleFullscreen} aria-label="Fullscreen">⛶</button>
      </div>
    </div>
  );
}
