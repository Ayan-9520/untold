import { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReelItem from './ReelItem';
import Logo from '../../components/brand/Logo';
import { BackIcon } from '../../components/icons';

export default function ReelsFeed({ shorts, showHeader = true, initialIndex = 0, withBottomNav = true }) {
  const [activeIndex, setActiveIndex] = useState(initialIndex);
  const scrollRef = useRef(null);
  const navigate = useNavigate();
  const reelHeight = withBottomNav
    ? 'calc(100dvh - 3.5rem - env(safe-area-inset-bottom))'
    : '100dvh';

  const handleInView = useCallback((index, active) => {
    if (active) setActiveIndex(index);
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el || initialIndex <= 0) return;
    const child = el.children[initialIndex];
    if (child) child.scrollIntoView({ behavior: 'instant' });
    setActiveIndex(initialIndex);
  }, [initialIndex, shorts?.length]);

  if (!shorts?.length) {
    return (
      <div className="h-dvh flex items-center justify-center bg-black text-white/60 text-sm">
        No reels available
      </div>
    );
  }

  return (
    <div
      className="relative w-full bg-black overflow-hidden"
      style={{ height: reelHeight }}
    >
      {/* Header overlay */}
      {showHeader && (
        <div className="absolute top-0 left-0 right-0 z-40 flex items-center justify-between px-4 pt-[max(env(safe-area-inset-top),12px)] pb-2 bg-gradient-to-b from-black/70 to-transparent pointer-events-none">
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2 rounded-full pointer-events-auto active:bg-white/10"
            aria-label="Back"
          >
            <BackIcon className="w-5 h-5 text-white" />
          </button>
          <div className="flex items-center gap-2 pointer-events-auto">
            <Logo variant="compact" />
            <span className="text-sm font-bold text-white tracking-wide">Reels</span>
          </div>
          <div className="w-9" />
        </div>
      )}

      {/* Vertical scroll feed */}
      <div
        ref={scrollRef}
        className="h-full w-full overflow-y-scroll snap-y snap-mandatory scrollbar-hide overscroll-y-contain touch-pan-y"
        style={{ WebkitOverflowScrolling: 'touch' }}
      >
        {shorts.map((short, i) => (
          <ReelItem
            key={short.id || i}
            short={short}
            index={i}
            isActive={activeIndex === i}
            onInView={handleInView}
            height={reelHeight}
          />
        ))}
      </div>

      {/* Side progress dots */}
      <div className="absolute right-1.5 top-1/2 -translate-y-1/2 z-30 flex flex-col gap-1 pointer-events-none">
        {shorts.map((_, j) => (
          <div
            key={j}
            className={`w-0.5 rounded-full transition-all duration-300 ${
              j === activeIndex ? 'h-5 bg-untold-gold' : 'h-1 bg-white/25'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
