import { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { getHeroBackdropTiles } from '../../data/heroBackdrop';

const FALLBACK_TILES = getHeroBackdropTiles(42);

export default function HeroSportsGrid() {
  const [tiles, setTiles] = useState(FALLBACK_TILES);

  useEffect(() => {
    api.videos.list({ trending: true, page_size: 42 })
      .then(({ items }) => {
        const images = items.map((v) => v.hero_image_url || v.image_url).filter(Boolean);
        if (images.length >= 12) {
          setTiles(Array.from({ length: 42 }, (_, i) => images[i % images.length]));
        }
      })
      .catch(() => setTiles(FALLBACK_TILES));
  }, []);

  return (
    <div className="hero-cinema-stage" aria-hidden="true">
      <div className="hero-cinema-grid-wrap">
        <div className="hero-cinema-grid">
          {tiles.map((src, i) => (
            <div key={i} className="hero-cinema-tile-wrap">
              <img src={src} alt="" loading="lazy" className="hero-cinema-tile" />
            </div>
          ))}
        </div>
      </div>
      <div className="hero-cinema-overlay" />
      <div className="hero-cinema-arc" />
    </div>
  );
}
