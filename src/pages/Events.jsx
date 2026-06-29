import { useMemo, useState } from 'react';
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
import {
  getFeaturedEvent,
  getEventsBySport,
  searchEvents,
  eventShorts,
  eventStories,
  eventsCatalog,
  EVENT_SPORTS,
} from '../data/eventsCatalog';
import { toSportOptions } from '../utils/contentFilters';

export default function Events() {
  const [sport, setSport] = useState('All');
  const [query, setQuery] = useState('');

  const featured = getFeaturedEvent();

  const filtered = useMemo(() => {
    let list = getEventsBySport(sport);
    if (query.trim()) list = searchEvents(query).filter((e) => sport === 'All' || getEventsBySport(sport).some((x) => x.id === e.id));
    return list;
  }, [sport, query]);

  const upcoming = useMemo(() => filtered.filter((e) => e.status === 'upcoming'), [filtered]);
  const live = useMemo(() => filtered.filter((e) => e.status === 'live'), [filtered]);
  const completed = useMemo(() => filtered.filter((e) => e.status === 'completed'), [filtered]);

  const sportCounts = useMemo(() => {
    const counts = { All: eventsCatalog.length };
    eventsCatalog.forEach((e) => {
      const key = e.sport === 'MMA' || e.sport === 'Boxing' ? 'Combat' : e.sport;
      counts[key] = (counts[key] || 0) + 1;
    });
    return counts;
  }, []);

  const filteredShorts = useMemo(() => {
    if (sport === 'All' && !query) return eventShorts;
    const eventIds = new Set(filtered.map((e) => e.id));
    let shorts = eventShorts.filter((s) => eventIds.has(s.eventId));
    if (query.trim()) {
      const q = query.toLowerCase();
      shorts = eventShorts.filter((s) => s.title.toLowerCase().includes(q) || s.sport.toLowerCase().includes(q));
    }
    return shorts;
  }, [sport, query, filtered]);

  const filteredStories = useMemo(() => {
    if (sport === 'All' && !query) return eventStories;
    const eventIds = new Set(filtered.map((e) => e.id));
    let stories = eventStories.filter((s) => eventIds.has(s.eventId));
    if (query.trim()) {
      const q = query.toLowerCase();
      stories = eventStories.filter((s) => s.title.toLowerCase().includes(q) || s.sport.toLowerCase().includes(q));
    }
    return stories;
  }, [sport, query, filtered]);

  return (
    <>
      <SEO
        title="Events"
        description="Live sports coverage, upcoming tournaments, and event highlights on UNTOLD — cricket, football, tennis, F1, and more."
        path="/events"
      />

      <EventHeroBanner event={featured} />

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
              options: toSportOptions(EVENT_SPORTS, sportCounts),
              active: sport,
              onChange: setSport,
            }}
            resultCount={filtered.length}
            resultLabel="events"
            onClear={() => { setSport('All'); setQuery(''); }}
            showClear={sport !== 'All' || query.trim()}
          />
        </div>
      </section>

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

      {filtered.length === 0 && (
        <div className="py-16 text-center px-4">
          <p className="text-lg dark:text-untold-muted light:text-gray-500">No events match your search.</p>
        </div>
      )}

      {filteredShorts.length > 0 && (
        <section className="py-12 sm:py-16 dark:bg-untold-surface/30 light:bg-gray-50/50" aria-labelledby="event-shorts">
          <SectionHeader title="Event Shorts" subtitle="Top goals, wickets, knockouts, and fastest laps" viewAllLink="/shorts" />
          <ContentRow>
            {filteredShorts.map((short) => (
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

      {filteredStories.length > 0 && (
        <section className="py-12 sm:py-16 pb-20" aria-labelledby="event-stories">
          <SectionHeader title="Event Stories" subtitle="Pre-match previews and post-match storytelling" viewAllLink="/stories" />
          <ContentRow>
            {filteredStories.map((story) => (
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
