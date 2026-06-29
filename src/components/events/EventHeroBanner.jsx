import { Link } from 'react-router-dom';
import Button from '../ui/Button';
import { PlayIcon, InfoIcon } from '../icons';
import { formatEventDate } from '../../data/eventsCatalog';

const statusLabel = {
  live: 'Live Now',
  upcoming: 'Featured Event',
  completed: 'Event Highlights',
};

export default function EventHeroBanner({ event }) {
  if (!event) return null;

  return (
    <section className="relative h-[70vh] min-h-[480px] max-h-[720px] w-full overflow-hidden">
      <div className="absolute inset-0">
        <img src={event.thumbnail} alt="" className="h-full w-full object-cover" />
        <div className="absolute inset-0 dark:bg-black/55 light:bg-black/45" />
        <div className="absolute inset-0 hero-gradient" />
      </div>

      <div className="relative z-10 flex h-full items-end">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 pb-14 sm:pb-20">
          <div className="max-w-2xl animate-fade-in">
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {event.status === 'live' && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-600 text-white text-xs font-bold uppercase tracking-wider">
                  <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
                  Live
                </span>
              )}
              <span className="text-untold-gold-light text-sm font-semibold tracking-[0.25em] uppercase">
                {statusLabel[event.status] || 'Event'}
              </span>
              <span className="text-white/70 text-sm">{event.sport}</span>
            </div>

            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
              {event.eventName}
            </h1>

            <p className="mt-3 text-sm text-white/75">
              {formatEventDate(event.date, event.endDate)}
              {event.location && ` · ${event.location}`}
            </p>

            {event.teamsOrPlayers?.length > 0 && (
              <p className="mt-2 text-sm font-medium text-untold-gold-light">
                {event.teamsOrPlayers.join(' · ')}
              </p>
            )}

            <p className="mt-4 text-base sm:text-lg text-white/90 max-w-xl leading-relaxed">
              {event.description}
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" icon={<PlayIcon className="w-5 h-5" />}>
                {event.status === 'live' ? 'Watch Live' : event.status === 'completed' ? 'Watch Highlights' : 'Get Preview'}
              </Button>
              <Link to="/explore?category=shorts">
                <Button
                  variant="secondary"
                  size="lg"
                  icon={<InfoIcon className="w-5 h-5" />}
                  className="dark:bg-white/10 dark:text-white light:bg-white/15 light:text-white light:hover:bg-white/25 light:border light:border-white/25"
                >
                  Event Shorts
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-untold-gold/50 to-transparent" />
    </section>
  );
}
