import { useEffect, useRef, useState } from 'react';
import streamingApi from '../../api/streaming';

export default function VideoPlayer({ videoId, fallbackUrl, poster, title, onProgress }) {
  const videoRef = useRef(null);
  const [streamUrl, setStreamUrl] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const lastSave = useRef(0);

  useEffect(() => {
    let active = true;

    const useFallback = () => {
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
      useFallback();
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
        useFallback();
      })
      .catch(() => {
        if (!active) return;
        useFallback();
      });

    return () => { active = false; };
  }, [videoId, fallbackUrl]);

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

    el.addEventListener('timeupdate', onTimeUpdate);
    return () => el.removeEventListener('timeupdate', onTimeUpdate);
  }, [videoId, streamUrl, onProgress]);

  if (loading) {
    return (
      <div className="aspect-video rounded-xl bg-black/80 flex items-center justify-center text-white/70 text-sm">
        Loading stream…
      </div>
    );
  }

  if (error) {
    return (
      <div className="aspect-video rounded-xl bg-black/80 flex flex-col items-center justify-center text-center p-6">
        <p className="text-white/80 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl overflow-hidden aspect-video w-full max-w-4xl dark:bg-black light:bg-black">
      <video
        ref={videoRef}
        src={streamUrl}
        controls
        autoPlay
        playsInline
        poster={poster}
        title={title}
        className="w-full h-full object-contain bg-black"
      />
    </div>
  );
}
