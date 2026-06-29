import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BackIcon,
  PlayIcon,
  VolumeIcon,
  VolumeOffIcon,
  MaximizeIcon,
  BookmarkIcon,
  ShareIcon,
} from '../../components/icons';
import { useWatchlist } from '../context/WatchlistContext';

export default function StreamPlayer({ content }) {
  const navigate = useNavigate();
  const { isInWatchlist, toggleWatchlist } = useWatchlist();
  const [playing, setPlaying] = useState(true);
  const [muted, setMuted] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [progress, setProgress] = useState(0);
  const hideTimer = useRef(null);

  const inList = isInWatchlist(content?.id);

  useEffect(() => {
    if (!playing) return;
    const interval = setInterval(() => {
      setProgress((p) => (p >= 100 ? 0 : p + 0.15));
    }, 200);
    return () => clearInterval(interval);
  }, [playing]);

  const resetHideTimer = () => {
    setShowControls(true);
    clearTimeout(hideTimer.current);
    hideTimer.current = setTimeout(() => setShowControls(false), 4000);
  };

  useEffect(() => {
    resetHideTimer();
    return () => clearTimeout(hideTimer.current);
  }, []);

  if (!content) return null;

  const formatTime = (pct) => {
    const totalSec = 68 * 60;
    const current = Math.floor((pct / 100) * totalSec);
    const m = Math.floor(current / 60);
    const s = current % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black mx-auto max-w-[430px]"
      onClick={resetHideTimer}
    >
      <div className="relative w-full h-dvh">
        <img
          src={content.heroImage || content.image}
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/30" />

        {/* Controls overlay */}
        <div
          className={`absolute inset-0 flex flex-col justify-between transition-opacity duration-300
            ${showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        >
          {/* Top bar */}
          <div className="flex items-center justify-between px-4 pt-[env(safe-area-inset-top)] pb-3 bg-gradient-to-b from-black/70 to-transparent">
            <button
              onClick={() => navigate(-1)}
              className="p-2 -ml-2 rounded-full active:bg-white/10"
              aria-label="Go back"
            >
              <BackIcon className="w-5 h-5 text-white" />
            </button>
            <h1 className="text-sm font-medium text-white truncate flex-1 text-center px-4">
              {content.title}
            </h1>
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleWatchlist(content);
              }}
              className="p-2 -mr-2 rounded-full active:bg-white/10"
            >
              <BookmarkIcon
                className={`w-5 h-5 ${inList ? 'text-untold-gold' : 'text-white'}`}
                filled={inList}
              />
            </button>
          </div>

          {/* Center play/pause */}
          <div className="flex items-center justify-center">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setPlaying(!playing);
              }}
              className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center
                active:scale-95 transition-transform"
            >
              {playing ? (
                <div className="flex gap-1">
                  <div className="w-1.5 h-6 bg-white rounded-full" />
                  <div className="w-1.5 h-6 bg-white rounded-full" />
                </div>
              ) : (
                <PlayIcon className="w-7 h-7 text-white ml-1" />
              )}
            </button>
          </div>

          {/* Bottom controls */}
          <div className="px-4 pb-[env(safe-area-inset-bottom)] pt-8 bg-gradient-to-t from-black/80 to-transparent">
            <div className="mb-3">
              <div className="relative h-1 bg-white/20 rounded-full overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 bg-untold-gold rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="flex justify-between mt-1.5">
                <span className="text-[10px] text-white/60">{formatTime(progress)}</span>
                <span className="text-[10px] text-white/60">{content.duration}</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setMuted(!muted);
                  }}
                  className="p-1 active:scale-90 transition-transform"
                >
                  {muted ? (
                    <VolumeOffIcon className="w-5 h-5 text-white" />
                  ) : (
                    <VolumeIcon className="w-5 h-5 text-white" />
                  )}
                </button>
                <button className="p-1 active:scale-90 transition-transform">
                  <ShareIcon className="w-5 h-5 text-white" />
                </button>
              </div>
              <button className="p-1 active:scale-90 transition-transform">
                <MaximizeIcon className="w-5 h-5 text-white" />
              </button>
            </div>

            <p className="text-xs text-white/50 mt-3 line-clamp-1">{content.description}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
