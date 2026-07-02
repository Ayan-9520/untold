import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SectionHeader from '../ui/SectionHeader';
import ContentRow from '../ui/ContentRow';
import EventCard from '../events/EventCard';
import LiveEventCard from '../events/LiveEventCard';
import { fetchEventsOverview } from '../../api/events';

export default function EventsRow() {
  const [items, setItems] = useState([]);
  const [featured, setFeatured] = useState(null);

  useEffect(() => {
    fetchEventsOverview()
      .then((data) => {
        const live = data.items.filter((e) => e.status === 'live').slice(0, 2);
        const upcoming = data.items.filter((e) => e.status === 'upcoming').slice(0, 4);
        setFeatured(data.featured);
        setItems([
          ...live.map((e) => ({ type: 'live', event: e })),
          ...upcoming.map((e) => ({ type: 'upcoming', event: e })),
        ].slice(0, 6));
      })
      .catch(() => setItems([]));
  }, []);

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
