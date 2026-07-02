import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import SectionHeader from '../components/ui/SectionHeader';
import ContentFilterBar from '../components/ui/ContentFilterBar';
import FeaturedLiveMatch from '../components/live/FeaturedLiveMatch';
import LiveScoreCard from '../components/live/LiveScoreCard';
import LiveHighlights from '../components/live/LiveHighlights';
import EventUpdateFeed from '../components/live/EventUpdateFeed';
import BreakingNewsTicker from '../components/engagement/BreakingNewsTicker';
import LiveSchedule from '../components/live/LiveSchedule';
import liveApi from '../api/live';
import { buildSportCounts, toSportOptions, getSportsFromItems } from '../utils/contentFilters';

export default function Live() {
  const { t } = useTranslation();
  const [sport, setSport] = useState('All');
  const [featured, setFeatured] = useState(null);
  const [matches, setMatches] = useState([]);
  const [highlights, setHighlights] = useState([]);
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [overview, hl, upd] = await Promise.all([
          liveApi.getOverview(),
          liveApi.getHighlights(10),
          liveApi.getUpdates(12),
        ]);
        setFeatured(overview.featured);
        setMatches((overview.matches || []).filter((m) => m.id !== overview.featured?.id));
        setHighlights(hl.data || []);
        setUpdates(upd.data || []);
      } catch (err) {
        setFeatured(null);
        setMatches([]);
        setHighlights([]);
        setUpdates([]);
        setError(err.message || 'Unable to load live data');
      } finally {
        setLoading(false);
      }
    }
    load();

    const disconnect = liveApi.connectLive(() => load());
    return disconnect;
  }, []);

  const filtered = sport === 'All' ? matches : matches.filter((m) => m.sport === sport);
  const sportCounts = buildSportCounts(matches);
  const sportOptions = toSportOptions(getSportsFromItems(matches), sportCounts);

  if (loading) return <Loader fullScreen label="Loading live scores" />;

  if (error) {
    return (
      <div className="pt-32 pb-20 text-center px-4">
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">{t('live.unavailable')}</h1>
        <p className="mt-2 text-sm dark:text-untold-muted light:text-gray-600">{error}</p>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={t('nav.live')}
        description={t('live.subtitle')}
        path="/live"
      />

      <div className="pt-20 sm:pt-24">
        <BreakingNewsTicker />
      </div>

      <section className="py-6 sm:py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mb-6 text-center sm:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-600/20 text-red-500 text-xs font-bold uppercase tracking-wider mb-3">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            Live Engine
          </div>
          <h1 className="font-display text-3xl sm:text-4xl font-bold dark:text-untold-white light:text-black">
            {t('live.title')}
          </h1>
          <p className="mt-2 text-sm sm:text-base dark:text-untold-muted light:text-gray-600 max-w-2xl">
            {t('live.subtitle')}
          </p>
        </div>

        <FeaturedLiveMatch match={featured} />
        <LiveSchedule matches={[featured, ...matches].filter(Boolean)} />
      </section>

      <section className="py-10 sm:py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionHeader title={t('live.matches')} subtitle={t('home.eventsSubtitle')} />
          <ContentFilterBar
            primary={{
              label: 'Sport',
              options: sportOptions,
              active: sport,
              onChange: setSport,
            }}
            resultCount={filtered.length}
            resultLabel="matches"
            onClear={() => setSport('All')}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((m) => (
              <LiveScoreCard key={m.id} match={m} compact />
            ))}
          </div>
        </div>
      </section>

      <LiveHighlights highlights={highlights} />

      <section className="py-10 sm:py-12 dark:bg-untold-surface/30 light:bg-gray-50/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <EventUpdateFeed updates={updates} title="Event Updates Feed" />
        </div>
      </section>
    </>
  );
}
