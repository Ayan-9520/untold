import { getHeroBackdropTiles } from '../../data/heroBackdrop';

const tiles = getHeroBackdropTiles(42);

export default function HeroSportsGrid() {
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
