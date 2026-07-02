import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import Button from '../ui/Button';
import { PlayIcon, InfoIcon, ChevronLeftIcon, ChevronRightIcon, BookmarkIcon } from '../icons';
import { heroSlides as defaultSlides } from '../../data/heroSlides';
import { useWatchlist } from '../../context/WatchlistContext';
import HeroTitle from './HeroTitle';
import HeroPosterLightbox from './HeroPosterLightbox';
import HeroFanCards from './HeroFanCards';
import HeroSportsGrid from './HeroSportsGrid';
import { useLocalizedContent } from '../../hooks/useLocalizedContent';

const AUTO_MS = 6000;

export default function HeroBanner({ content }) {
  const { t } = useTranslation();
  const slides = content?.slides?.length ? content.slides : defaultSlides;
  const [index, setIndex] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [paused, setPaused] = useState(false);

  const slide = slides[index];
  const featuredId = slide.featuredId;
  const { isInWatchlist, toggleWatchlist } = useWatchlist();
  const { localizeTitle, localizeCategory, localizeFormat } = useLocalizedContent();
  const inList = featuredId ? isInWatchlist(featuredId) : false;
  const slideTitle = localizeTitle(slide.featuredTitle || slide.title, slide.slug);
  const slideSport = slide.sport ? localizeCategory(slide.sport) : null;
  const slideFormat = slide.format ? localizeFormat(slide.format) : null;
  const fullSrc =
    slide.fullImage || slide.cardImage || slide.posterImage || slide.heroImage;
  const watchLink = slide.featuredId ? `/video/${slide.featuredId}` : '/originals';

  const go = useCallback(
    (dir) => setIndex((i) => (i + dir + slides.length) % slides.length),
    [slides.length]
  );

  useEffect(() => {
    if (slides.length < 2 || paused) return undefined;
    const timer = setInterval(() => go(1), AUTO_MS);
    return () => clearInterval(timer);
  }, [go, slides.length, paused, index]);

  useEffect(() => {
    setLightboxOpen(false);
  }, [index]);

  return (
    <section
      className="relative w-full overflow-x-hidden
        min-h-[calc(100dvh-var(--nav-height-mobile))] md:min-h-[calc(100vh-var(--nav-height))] lg:min-h-[680px] lg:max-h-[980px] lg:h-screen"
      aria-label="Featured documentaries"
      aria-roledescription="carousel"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <HeroSportsGrid />
      <div className="hero-top-scrim" aria-hidden="true" />

      <div className="relative z-10 flex flex-col justify-start lg:justify-center pt-4 md:pt-6 lg:pt-8 pb-10 md:pb-14">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 md:gap-8 lg:gap-10">
            {/* Cards first on mobile */}
            <div className="order-1 lg:order-2 w-full lg:w-auto flex flex-col items-center lg:items-end overflow-visible">
              <HeroFanCards
                slides={slides}
                index={index}
                onSelect={setIndex}
                onEnlarge={() => setLightboxOpen(true)}
              />
              {slides.length > 1 && (
                <div className="hero-fan-controls">
                  <button
                    type="button"
                    onClick={() => go(-1)}
                    aria-label="Previous slide"
                    className="hero-fan-nav-btn"
                  >
                    <ChevronLeftIcon className="w-4 h-4" />
                  </button>
                  <div className="hero-popup-dots" role="tablist" aria-label="Hero slides">
                    {slides.map((s, i) => (
                      <button
                        key={s.id}
                        type="button"
                        role="tab"
                        aria-label={`Slide ${i + 1}`}
                        aria-selected={i === index}
                        onClick={() => setIndex(i)}
                        className={`h-1 rounded-full transition-all duration-300
                          ${i === index ? 'w-6 bg-untold-gold' : 'w-3 bg-white/25 hover:bg-white/45'}`}
                      />
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={() => go(1)}
                    aria-label="Next slide"
                    className="hero-fan-nav-btn"
                  >
                    <ChevronRightIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Copy */}
            <AnimatePresence mode="wait">
              <motion.div
                key={slide.id}
                className="hero-copy-zone order-2 lg:order-1 flex-1 lg:max-w-[500px] text-center lg:text-left"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              >
                <p className="hero-eyebrow mb-2 sm:mb-3">
                  {slide.eyebrow || 'UNTOLD ORIGINALS'}
                </p>
                {(slide.sport || slide.pillar || slide.format) && (
                  <div className="hero-meta-tags mb-3 sm:mb-4">
                    {slideSport && <span className="hero-meta-tag">{slideSport}</span>}
                    {slide.pillar && <span className="hero-meta-tag hero-meta-tag--gold">{slide.pillar}</span>}
                    {slideFormat && <span className="hero-meta-tag">{slideFormat}</span>}
                  </div>
                )}
                <HeroTitle featuredTitle={slideTitle} />
                <p className="hero-tagline mt-3 sm:mt-4 mx-auto lg:mx-0">{slide.featuredTagline || slide.subtitle}</p>

                <div className="hero-ott-meta mt-4 flex flex-wrap gap-2 justify-center lg:justify-start text-xs text-white/75">
                  {slide.duration && <span className="hero-ott-badge">{slide.duration}</span>}
                  {slide.year && <span className="hero-ott-badge">{slide.year}</span>}
                  <span className="hero-ott-badge hero-ott-badge--gold">4K</span>
                  {slide.rating && <span className="hero-ott-badge">{slide.rating}</span>}
                  <span className="hero-ott-badge">{slide.language || 'English'}</span>
                </div>

                <div className="mt-5 sm:mt-7 flex flex-wrap gap-3 justify-center lg:justify-start">
                  <Link to={watchLink}>
                    <Button
                      size="lg"
                      icon={<PlayIcon className="w-5 h-5" />}
                      className="gold-glow-sm min-w-[140px] font-bold"
                    >
                      {slide.cta || t('hero.watchNow')}
                    </Button>
                  </Link>
                  <Link to={`${watchLink}?trailer=1`}>
                    <Button
                      variant="secondary"
                      size="lg"
                      className="bg-white/12 text-white hover:bg-white/20 border border-white/20 backdrop-blur-sm font-semibold min-w-[130px]"
                    >
                      {t('hero.watchTrailer')}
                    </Button>
                  </Link>
                  {featuredId && (
                    <Button
                      variant="secondary"
                      size="lg"
                      icon={<BookmarkIcon className="w-5 h-5" filled={inList} />}
                      onClick={() => toggleWatchlist({ id: featuredId, title: slide.featuredTitle || slide.title, image: slide.cardImage })}
                      className="bg-white/8 text-white hover:bg-white/15 border border-white/15"
                    >
                      {inList ? t('hero.inList') : t('hero.myList')}
                    </Button>
                  )}
                  <Link to="/originals">
                    <Button
                      variant="secondary"
                      size="lg"
                      icon={<InfoIcon className="w-5 h-5" />}
                      className="bg-white/8 text-white hover:bg-white/15 border border-white/15 font-semibold"
                    >
                      {slide.secondaryCta || t('hero.explore')}
                    </Button>
                  </Link>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      <HeroPosterLightbox
        image={fullSrc}
        title={slideTitle}
        open={lightboxOpen}
        onClose={() => setLightboxOpen(false)}
      />
    </section>
  );
}
