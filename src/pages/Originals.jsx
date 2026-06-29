import { useMemo, useState } from 'react';
import SEO from '../components/SEO';
import OriginalSportCard from '../components/originals/OriginalSportCard';
import ComingSoonCard from '../components/originals/ComingSoonCard';
import OriginalsFilterBar from '../components/originals/OriginalsFilterBar';
import {
  originalsCatalog,
  COMING_SOON_PLACEHOLDERS,
  isComingSoonSport,
  filterOriginalsCatalog,
  getOriginalsSportCounts,
} from '../data/originalsCatalog';
import { CONTENT_GRID_CLASS } from '../constants/contentLayout';

const SPORT_COUNTS = getOriginalsSportCounts();

export default function Originals() {
  const [activeSport, setActiveSport] = useState('All');
  const [activeFormat, setActiveFormat] = useState('All');

  const isComingSoon = isComingSoonSport(activeSport);
  const filtered = useMemo(
    () => filterOriginalsCatalog(originalsCatalog, activeSport, activeFormat),
    [activeSport, activeFormat]
  );
  const comingSoonCards = isComingSoon ? COMING_SOON_PLACEHOLDERS[activeSport] || [] : [];

  const handleSportChange = (sport) => {
    setActiveSport(sport);
    if (isComingSoonSport(sport)) setActiveFormat('All');
  };

  const clearFilters = () => {
    setActiveSport('All');
    setActiveFormat('All');
  };

  return (
    <>
      <SEO
        title="Originals"
        description="UNTOLD Originals — premium sport-wise documentaries, biopics, and feature films. Cricket, football, tennis, boxing, and more."
        path="/originals"
      />

      <section className="pt-28 pb-12 sm:pt-36 sm:pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6 max-w-2xl mx-auto">
            <p className="text-untold-gold text-xs font-semibold tracking-[0.3em] uppercase mb-2">
              UNTOLD Originals
            </p>
            <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black leading-tight">
              The Stories Behind The Glory
            </h1>
            <p className="mt-3 text-sm sm:text-base dark:text-untold-muted light:text-gray-600 leading-relaxed">
              Premium documentaries, biopics, and feature films — curated sport by sport.
            </p>
          </div>

          <OriginalsFilterBar
            activeSport={activeSport}
            activeFormat={activeFormat}
            onSportChange={handleSportChange}
            onFormatChange={setActiveFormat}
            resultCount={filtered.length}
            isComingSoon={isComingSoon}
            sportCounts={SPORT_COUNTS}
            onClear={clearFilters}
          />

          {isComingSoon ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 max-w-3xl mx-auto">
              {comingSoonCards.map((card) => (
                <ComingSoonCard key={card.id} sport={activeSport} teaser={card.teaser} />
              ))}
            </div>
          ) : (
            <div className={CONTENT_GRID_CLASS}>
              {filtered.map((item) => (
                <OriginalSportCard key={item.id} item={item} />
              ))}
            </div>
          )}

          {!isComingSoon && filtered.length === 0 && (
            <div className="text-center py-16">
              <p className="dark:text-untold-muted light:text-gray-500 mb-4">
                No titles match this sport and format yet.
              </p>
              <button
                type="button"
                onClick={clearFilters}
                className="text-untold-gold font-medium hover:underline"
              >
                Clear filters
              </button>
            </div>
          )}

          {isComingSoon && (
            <p className="text-center mt-10 text-sm dark:text-untold-muted light:text-gray-500">
              Browse available sports —{' '}
              <button type="button" onClick={() => handleSportChange('Football')} className="text-untold-gold hover:underline">
                Football
              </button>
              ,{' '}
              <button type="button" onClick={() => handleSportChange('Basketball')} className="text-untold-gold hover:underline">
                Basketball
              </button>
              ,{' '}
              <button type="button" onClick={() => handleSportChange('Formula 1')} className="text-untold-gold hover:underline">
                F1
              </button>
              ,{' '}
              <button type="button" onClick={() => handleSportChange('Cricket')} className="text-untold-gold hover:underline">
                Cricket
              </button>
              , and more.
            </p>
          )}
        </div>
      </section>
    </>
  );
}
