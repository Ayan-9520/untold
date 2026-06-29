import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const FAN_DESKTOP = {
  [-2]: { rotate: -20, x: -96, y: 20, scale: 0.74, z: 1 },
  [-1]: { rotate: -10, x: -48, y: 10, scale: 0.88, z: 2 },
  0: { rotate: -2, x: 0, y: 0, scale: 1, z: 5 },
  1: { rotate: 10, x: 48, y: 10, scale: 0.88, z: 3 },
  2: { rotate: 20, x: 96, y: 20, scale: 0.74, z: 2 },
};

const FAN_MOBILE = {
  [-1]: { rotate: -14, x: -42, y: 10, scale: 0.86, z: 2 },
  0: { rotate: 0, x: 0, y: 0, scale: 1, z: 5 },
  1: { rotate: 14, x: 42, y: 10, scale: 0.86, z: 3 },
};

function relativeOffset(slideIndex, activeIndex, total) {
  let d = slideIndex - activeIndex;
  const half = total / 2;
  while (d > half) d -= total;
  while (d < -half) d += total;
  return d;
}

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 767px)');
    const update = () => setIsMobile(mq.matches);
    update();
    mq.addEventListener('change', update);
    return () => mq.removeEventListener('change', update);
  }, []);
  return isMobile;
}

export default function HeroFanCards({ slides, index, onSelect, onEnlarge }) {
  const len = slides.length;
  const isMobile = useIsMobile();

  return (
    <div className="hero-fan-stack" role="group" aria-label="Featured originals">
      {slides.map((slide, i) => {
        const offset = relativeOffset(i, index, len);
        if (isMobile && Math.abs(offset) > 1) return null;

        const layoutMap = isMobile ? FAN_MOBILE : FAN_DESKTOP;
        const layout = layoutMap[offset] ?? layoutMap[0];
        const isActive = i === index;
        const src =
          slide.cardImage || slide.fullImage || slide.posterImage || slide.heroImage;

        return (
          <motion.button
            key={slide.id}
            type="button"
            onClick={() => (isActive ? onEnlarge() : onSelect(i))}
            className={`hero-fan-card ${isActive ? 'hero-fan-card--active' : ''}`}
            style={{ zIndex: layout.z }}
            initial={false}
            animate={{
              rotate: layout.rotate,
              x: layout.x,
              y: layout.y,
              scale: layout.scale,
              opacity: isActive ? 1 : 0.8,
            }}
            transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
            aria-label={isActive ? `View ${slide.featuredTitle}` : `Show ${slide.featuredTitle}`}
            aria-current={isActive ? 'true' : undefined}
          >
            <div className="hero-fan-card-inner">
              <img
                src={src}
                alt={slide.featuredTitle || ''}
                className="hero-fan-card-img"
                style={{ objectPosition: slide.cardPosition || slide.posterPosition || 'center top' }}
              />
              {isActive && <div className="hero-fan-card-shine" aria-hidden="true" />}
            </div>
          </motion.button>
        );
      })}
    </div>
  );
}
