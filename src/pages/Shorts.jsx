import { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import VideoCard, { VideoCardSkeleton } from '../components/ui/VideoCard';
import ContentFilterBar from '../components/ui/ContentFilterBar';
import ReelsFeed from '../app/components/ReelsFeed';
import { contentApi } from '../api/content';
import { PlayIcon } from '../components/icons';
import { useLocalizedContent } from '../hooks/useLocalizedContent';
import {
  buildSportCounts,
  filterBySport,
  getSportsFromItems,
  toSportOptions,
} from '../utils/contentFilters';
import { SHORTS_GRID_CLASS } from '../constants/contentLayout';

export default function Shorts() {
  const { t } = useTranslation();
  const { localizeVideo, localizeSport, ui } = useLocalizedContent();
  const [shorts, setShorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reelsOpen, setReelsOpen] = useState(false);
  const [startIndex, setStartIndex] = useState(0);
  const [activeSport, setActiveSport] = useState('All');

  useEffect(() => {
    contentApi.getShorts().then(({ data }) => {
      setShorts(data);
      setLoading(false);
    });
  }, []);

  const localizedShorts = useMemo(() => shorts.map(localizeVideo), [shorts, localizeVideo]);

  const sports = useMemo(() => getSportsFromItems(localizedShorts, 'category'), [localizedShorts]);
  const sportCounts = useMemo(() => buildSportCounts(localizedShorts, 'category'), [localizedShorts]);
  const filtered = useMemo(
    () => filterBySport(localizedShorts, activeSport, 'category'),
    [localizedShorts, activeSport]
  );

  const sportOptions = useMemo(
    () => toSportOptions(sports, sportCounts).map((opt) => ({
      ...opt,
      label: opt.label === 'All' ? ui('all', t('content.ui.all', 'All')) : localizeSport(opt.label),
    })),
    [sports, sportCounts, localizeSport, ui, t]
  );

  const openReels = (index = 0) => {
    const list = activeSport === 'All' ? localizedShorts : filtered;
    const globalIndex = activeSport === 'All' ? index : localizedShorts.findIndex((s) => s.id === list[index]?.id);
    setStartIndex(globalIndex >= 0 ? globalIndex : 0);
    setReelsOpen(true);
    document.body.style.overflow = 'hidden';
  };

  const closeReels = () => {
    setReelsOpen(false);
    document.body.style.overflow = '';
  };

  if (reelsOpen) {
    const ordered = [...localizedShorts.slice(startIndex), ...localizedShorts.slice(0, startIndex)];
    return (
      <div className="fixed inset-0 z-[100] bg-black">
        <button
          onClick={closeReels}
          className="absolute top-4 right-4 z-50 p-2 rounded-full bg-black/50 text-white text-sm px-3"
        >
          ✕ {ui('close', t('common.cancel', 'Close'))}
        </button>
        <div className="mx-auto max-w-[430px] h-full">
          <ReelsFeed shorts={ordered} showHeader={false} withBottomNav={false} />
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={t('nav.shorts')}
        description={t('home.shortsSubtitle')}
        path="/shorts"
      />

      <section className="pt-28 pb-12 sm:pt-36 sm:pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-5">
            <div>
              <p className="dark:text-untold-gold light:text-untold-gold-dark text-xs font-semibold tracking-[0.3em] uppercase mb-2">
                {ui('reels', t('content.ui.reels', 'Reels'))}
              </p>
              <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
                {t('nav.shorts')}
              </h1>
              <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">
                {ui('swipeVertical', t('content.ui.swipeVertical', 'Swipe vertically — bite-sized sports moments.'))}
              </p>
            </div>
            <button
              onClick={() => openReels(0)}
              className="self-start sm:self-auto inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-untold-gold text-untold-dark text-sm font-semibold hover:bg-untold-gold-light transition-colors"
            >
              <PlayIcon className="w-4 h-4" />
              {ui('watchReels', t('content.ui.watchReels', 'Watch Reels'))}
            </button>
          </div>

          {!loading && localizedShorts.length > 0 && (
            <ContentFilterBar
              primary={{
                label: ui('sport', t('content.ui.sport', 'Sport')),
                options: sportOptions,
                active: activeSport,
                onChange: setActiveSport,
              }}
              resultCount={filtered.length}
              resultLabel={ui('shortsLabel', t('nav.shorts'))}
              onClear={() => setActiveSport('All')}
            />
          )}

          <div className={SHORTS_GRID_CLASS}>
            {loading
              ? [...Array(10)].map((_, i) => (
                  <VideoCardSkeleton key={i} variant="short" fluid />
                ))
              : filtered.map((short, i) => (
                  <div
                    key={short.id}
                    className="cursor-pointer w-full"
                    onClick={() => openReels(i)}
                  >
                    <VideoCard
                      title={short.title}
                      image={short.image}
                      duration={short.duration}
                      views={short.views}
                      variant="short"
                      fluid
                    />
                  </div>
                ))}
          </div>

          {!loading && filtered.length === 0 && (
            <p className="text-center py-12 text-sm dark:text-untold-muted light:text-gray-500">
              {ui('noShorts', t('content.ui.noShorts', 'No shorts for this sport yet.'))}
            </p>
          )}
        </div>
      </section>
    </>
  );
}
