import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import EventCard from '../events/EventCard';
import LiveEventCard from '../events/LiveEventCard';
import { getEventsByStatus, getFeaturedEvent } from '../../data/eventsCatalog';

export default function EventsRow() {
  const live = getEventsByStatus('live').slice(0, 2);
  const upcoming = getEventsByStatus('upcoming').slice(0, 4);
  const featured = getFeaturedEvent();

  const items = [
    ...live.map((e) => ({ type: 'live', event: e })),
    ...upcoming.map((e) => ({ type: 'upcoming', event: e })),
  ].slice(0, 6);

  if (items.length === 0) return null;

  return (
    <section className="py-12 sm:py-16" aria-labelledby="home-events">
      <SectionHeader
        title="Events"
        subtitle={featured?.status === 'live' ? 'Live coverage happening now' : 'Upcoming tournaments & match coverage'}
        viewAllLink="/events"
      />
      <ContentRow>
        {items.map(({ type, event }) =>
          type === 'live' ? (
            <LiveEventCard key={event.id} event={event} />
          ) : (
            <Link key={event.id} to="/events" className="shrink-0">
              <EventCard event={event} variant="upcoming" />
            </Link>
          )
        )}
      </ContentRow>
    </section>
  );
}
