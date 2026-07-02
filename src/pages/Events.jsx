import { useEffect, useMemo, useState } from 'react';
import SEO from '../components/SEO';
import EventHeroBanner from '../components/events/EventHeroBanner';
import ContentFilterBar from '../components/ui/ContentFilterBar';
import EventCard from '../components/events/EventCard';
import LiveEventCard from '../components/events/LiveEventCard';
import CompletedEventCard from '../components/events/CompletedEventCard';
import SectionHeader from '../components/ui/SectionHeader';
import ContentRow from '../components/ui/ContentRow';
import ShortsCard from '../components/ui/ShortsCard';
import VideoCard from '../components/ui/VideoCard';
import Loader from '../components/ui/Loader';
import { fetchEventsOverview } from '../api/events';
import { toSportOptions, getSportsFromItems } from '../utils/contentFilters';

function sportKey(sport) {
  return sport === 'MMA' || sport === 'Boxing' ? 'Combat' : sport;
}

export default function Events() {
  const [sport, setSport] = useState('All');
  const [query, setQuery] = useState('');
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');
    fetchEventsOverview({ sport, search: query })
      .then((data) => {
        if (!cancelled) setOverview(data);
      })
      .catch(() => {
        if (!cancelled) setError('Unable to load events. Please try again.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [sport, query]);

  const items = overview?.items ?? [];
  const featured = overview?.featured ?? items[0] ?? null;

  const upcoming = useMemo(() => items.filter((e) => e.status === 'upcoming'), [items]);
  const live = useMemo(() => items.filter((e) => e.status === 'live'), [items]);
  const completed = useMemo(() => items.filter((e) => e.status === 'completed'), [items]);

  const sportCounts = useMemo(() => {
    const counts = { All: items.length };
    items.forEach((e) => {
      const key = sportKey(e.sport);
      counts[key] = (counts[key] || 0) + 1;
    });
    return counts;
  }, [items]);

  const sportOptions = useMemo(() => {
    const sports = getSportsFromItems(items.map((e) => ({ sport: sportKey(e.sport) })));
    return toSportOptions(sports, sportCounts);
  }, [items, sportCounts]);

  const shorts = (overview?.shorts ?? []).map((s) => ({
    ...s,
    thumbnail: s.thumbnail || s.image,
  }));

  const stories = (overview?.stories ?? []).map((s) => ({
    ...s,
    thumbnail: s.thumbnail || s.image,
    sport: s.sport || s.category || 'Sports',
    type: s.type || 'story',
    duration: s.duration || '',
  }));

  if (loading && !overview) {
    return <Loader fullScreen label="Loading events" />;
  }

  return (
    <>
      <SEO
        title="Events"
        description="Live sports coverage, upcoming tournaments, and event highlights on UNTOLD — cricket, football, tennis, F1, and more."
        path="/events"
      />

      {featured && <EventHeroBanner event={featured} />}

      <section className="py-6 sm:py-8 border-b dark:border-untold-border light:border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="relative max-w-xl mx-auto mb-4">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search events, teams, tournaments…"
              aria-label="Search events"
              className="w-full rounded-full px-5 py-2.5 pl-11 text-sm
                dark:bg-untold-surface light:bg-gray-50
                dark:border-untold-border light:border-gray-200 border
                dark:text-untold-white light:text-black
                focus:outline-none focus:ring-2 focus:ring-untold-gold"
            />
            <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 dark:text-untold-muted light:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <ContentFilterBar
            sticky={false}
            primary={{
              label: 'Sport',
              options: sportOptions,
              active: sport,
              onChange: setSport,
            }}
            resultCount={items.length}
            resultLabel="events"
            onClear={() => { setSport('All'); setQuery(''); }}
            showClear={sport !== 'All' || query.trim()}
          />
        </div>
      </section>

      {error && (
        <div className="py-8 text-center px-4">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {live.length > 0 && (
        <section className="py-12 sm:py-16" aria-labelledby="live-events">
          <SectionHeader title="Live Now" subtitle="Ongoing events with real-time updates" />
          <ContentRow>
            {live.map((event) => (
              <LiveEventCard key={event.id} event={event} />
            ))}
          </ContentRow>
        </section>
      )}

      {upcoming.length > 0 && (
        <section className="py-12 sm:py-16 dark:bg-untold-surface/30 light:bg-gray-50/50" aria-labelledby="upcoming-events">
          <SectionHeader title="Upcoming Events" subtitle="Tournaments and matches on the horizon" />
          <ContentRow>
            {upcoming.map((event) => (
              <EventCard key={event.id} event={event} variant="upcoming" />
            ))}
          </ContentRow>
        </section>
      )}

      {completed.length > 0 && (
        <section className="py-12 sm:py-16" aria-labelledby="completed-events">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <SectionHeader title="Recently Completed" subtitle="Results, highlights, and match summaries" />
            <div className="grid gap-4 sm:gap-6">
              {completed.map((event) => (
                <CompletedEventCard key={event.id} event={event} />
              ))}
            </div>
          </div>
        </section>
      )}

      {!loading && items.length === 0 && !error && (
        <div className="py-16 text-center px-4">
          <p className="text-lg dark:text-untold-muted light:text-gray-500">No events match your search.</p>
        </div>
      )}

      {shorts.length > 0 && (
        <section className="py-12 sm:py-16 dark:bg-untold-surface/30 light:bg-gray-50/50" aria-labelledby="event-shorts">
          <SectionHeader title="Event Shorts" subtitle="Top goals, wickets, knockouts, and fastest laps" viewAllLink="/shorts" />
          <ContentRow>
            {shorts.map((short) => (
              <ShortsCard
                key={short.id}
                title={short.title}
                image={short.thumbnail}
                duration={short.duration}
                views={short.views}
                to="/shorts"
              />
            ))}
          </ContentRow>
        </section>
      )}

      {stories.length > 0 && (
        <section className="py-12 sm:py-16 pb-20" aria-labelledby="event-stories">
          <SectionHeader title="Event Stories" subtitle="Pre-match previews and post-match storytelling" viewAllLink="/stories" />
          <ContentRow>
            {stories.map((story) => (
              <div key={story.id} className="shrink-0 w-[260px] sm:w-[280px]">
                <VideoCard
                  title={story.title}
                  image={story.thumbnail}
                  category={story.sport}
                  format={story.type}
                  duration={story.duration}
                  showDescription={false}
                />
              </div>
            ))}
          </ContentRow>
        </section>
      )}
    </>
  );
}
