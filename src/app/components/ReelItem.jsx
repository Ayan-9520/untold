import { useRef, useEffect, useState, useCallback } from 'react';
import { BookmarkIcon, ShareIcon, PlayIcon, VolumeIcon, VolumeOffIcon } from '../../components/icons';
import Logo from '../../components/brand/Logo';

function HeartIcon({ className, filled }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill={filled ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
  );
}

function CommentIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

const SAMPLE_VIDEOS = [
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerSwifties.mp4',
];

export function getReelVideoUrl(short, index) {
  return short.videoUrl || short.video_url || SAMPLE_VIDEOS[index % SAMPLE_VIDEOS.length];
}

export default function ReelItem({ short, index, isActive, onInView, height = '100dvh' }) {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(true);
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showHeart, setShowHeart] = useState(false);
  const lastTap = useRef(0);

  const videoUrl = getReelVideoUrl(short, index);

  // Intersection observer — play when reel is in view (Instagram-style)
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const active = entry.isIntersecting && entry.intersectionRatio >= 0.6;
        onInView?.(index, active);
        if (active) {
          videoRef.current?.play().catch(() => {});
          setPlaying(true);
        } else {
          videoRef.current?.pause();
          setPlaying(false);
          setProgress(0);
        }
      },
      { threshold: [0.6] }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [index, onInView]);

  useEffect(() => {
    if (isActive) {
      videoRef.current?.play().catch(() => {});
      setPlaying(true);
    } else {
      videoRef.current?.pause();
      setPlaying(false);
    }
  }, [isActive]);

  const handleTap = useCallback(() => {
    const now = Date.now();
    if (now - lastTap.current < 300) {
      setLiked(true);
      setShowHeart(true);
      setTimeout(() => setShowHeart(false), 800);
      lastTap.current = 0;
      return;
    }
    lastTap.current = now;

    setTimeout(() => {
      if (Date.now() - lastTap.current >= 280) {
        const v = videoRef.current;
        if (!v) return;
        if (v.paused) {
          v.play();
          setPlaying(true);
        } else {
          v.pause();
          setPlaying(false);
        }
      }
    }, 300);
  }, []);

  const onTimeUpdate = () => {
    const v = videoRef.current;
    if (v?.duration) setProgress((v.currentTime / v.duration) * 100);
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full snap-start snap-always shrink-0 bg-black"
      style={{ height }}
      onClick={handleTap}
    >
      {/* Progress bar */}
      <div className="absolute top-0 left-0 right-0 z-30 h-0.5 bg-white/20">
        <div
          className="h-full bg-untold-gold transition-[width] duration-100 ease-linear"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Video */}
      <video
        ref={videoRef}
        src={videoUrl}
        poster={short.image}
        className="absolute inset-0 h-full w-full object-cover"
        loop
        muted={muted}
        playsInline
        preload={index <= 1 ? 'auto' : 'metadata'}
        onTimeUpdate={onTimeUpdate}
      />

      {/* Poster fallback while loading */}
      <img
        src={short.image}
        alt=""
        className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-300 ${playing ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}
      />

      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/70 pointer-events-none" />

      {/* Double-tap heart */}
      {showHeart && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-20 animate-scale-in">
          <HeartIcon className="w-24 h-24 text-red-500 drop-shadow-2xl" filled />
        </div>
      )}

      {/* Pause indicator */}
      {!playing && isActive && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="w-16 h-16 rounded-full bg-black/40 backdrop-blur-sm flex items-center justify-center">
            <PlayIcon className="w-8 h-8 text-white ml-1" />
          </div>
        </div>
      )}

      {/* Right actions — Instagram style */}
      <div
        className="absolute right-3 bottom-28 z-20 flex flex-col items-center gap-5"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={() => setLiked(!liked)}
          className="flex flex-col items-center gap-1 active:scale-90 transition-transform"
        >
          <HeartIcon className={`w-7 h-7 ${liked ? 'text-red-500' : 'text-white'}`} filled={liked} />
          <span className="text-[10px] text-white font-medium">{liked ? '1.1K' : '1K'}</span>
        </button>
        <button className="flex flex-col items-center gap-1 active:scale-90 transition-transform">
          <CommentIcon className="w-7 h-7 text-white" />
          <span className="text-[10px] text-white font-medium">48</span>
        </button>
        <button
          onClick={() => setSaved(!saved)}
          className="active:scale-90 transition-transform"
        >
          <BookmarkIcon className={`w-7 h-7 ${saved ? 'text-untold-gold' : 'text-white'}`} filled={saved} />
        </button>
        <button className="active:scale-90 transition-transform">
          <ShareIcon className="w-7 h-7 text-white" />
        </button>
        <button
          onClick={() => setMuted(!muted)}
          className="mt-2 p-2 rounded-full bg-black/30 active:scale-90 transition-transform"
        >
          {muted ? <VolumeOffIcon className="w-5 h-5 text-white" /> : <VolumeIcon className="w-5 h-5 text-white" />}
        </button>
      </div>

      {/* Bottom caption */}
      <div className="absolute bottom-6 left-0 right-16 px-4 z-20 pointer-events-none">
        <div className="flex items-center gap-2 mb-2">
          <Logo variant="compact" />
          <span className="text-sm font-bold text-white">UNTOLD</span>
          <button className="text-[10px] font-semibold text-white border border-white/40 px-2 py-0.5 rounded pointer-events-auto">
            Follow
          </button>
        </div>
        <h3 className="text-sm font-semibold text-white leading-snug line-clamp-2">{short.title}</h3>
        <p className="text-xs text-white/60 mt-1">{short.views} views · {short.duration}</p>
      </div>
    </div>
  );
}
