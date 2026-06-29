import { useState, useEffect, useMemo } from 'react';
import SEO from '../components/SEO';
import VideoCard, { VideoCardSkeleton } from '../components/ui/VideoCard';
import ContentFilterBar from '../components/ui/ContentFilterBar';
import ReelsFeed from '../app/components/ReelsFeed';
import { contentApi } from '../api/content';
import { PlayIcon } from '../components/icons';
import {
  buildSportCounts,
  filterBySport,
  getSportsFromItems,
  toSportOptions,
} from '../utils/contentFilters';
import { SHORTS_GRID_CLASS } from '../constants/contentLayout';

export default function Shorts() {
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

  const sports = useMemo(() => getSportsFromItems(shorts, 'category'), [shorts]);
  const sportCounts = useMemo(() => buildSportCounts(shorts, 'category'), [shorts]);
  const filtered = useMemo(
    () => filterBySport(shorts, activeSport, 'category'),
    [shorts, activeSport]
  );

  const openReels = (index = 0) => {
    const list = activeSport === 'All' ? shorts : filtered;
    const globalIndex = activeSport === 'All' ? index : shorts.findIndex((s) => s.id === list[index]?.id);
    setStartIndex(globalIndex >= 0 ? globalIndex : 0);
    setReelsOpen(true);
    document.body.style.overflow = 'hidden';
  };

  const closeReels = () => {
    setReelsOpen(false);
    document.body.style.overflow = '';
  };

  if (reelsOpen) {
    const ordered = [...shorts.slice(startIndex), ...shorts.slice(0, startIndex)];
    return (
      <div className="fixed inset-0 z-[100] bg-black">
        <button
          onClick={closeReels}
          className="absolute top-4 right-4 z-50 p-2 rounded-full bg-black/50 text-white text-sm px-3"
        >
          ✕ Close
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
        title="Shorts"
        description="Watch UNTOLD Reels — bite-sized sports moments like Instagram."
        path="/shorts"
      />

      <section className="pt-28 pb-12 sm:pt-36 sm:pb-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-5">
            <div>
              <p className="dark:text-untold-gold light:text-untold-gold-dark text-xs font-semibold tracking-[0.3em] uppercase mb-2">
                Reels
              </p>
              <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
                UNTOLD Shorts
              </h1>
              <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">
                Swipe vertically — bite-sized sports moments.
              </p>
            </div>
            <button
              onClick={() => openReels(0)}
              className="self-start sm:self-auto inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-untold-gold text-untold-dark text-sm font-semibold hover:bg-untold-gold-light transition-colors"
            >
              <PlayIcon className="w-4 h-4" />
              Watch Reels
            </button>
          </div>

          {!loading && shorts.length > 0 && (
            <ContentFilterBar
              primary={{
                label: 'Sport',
                options: toSportOptions(sports, sportCounts),
                active: activeSport,
                onChange: setActiveSport,
              }}
              resultCount={filtered.length}
              resultLabel="shorts"
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
              No shorts for this sport yet.
            </p>
          )}
        </div>
      </section>
    </>
  );
}
