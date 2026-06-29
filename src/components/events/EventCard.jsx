import EventCountdown from './EventCountdown';
import { formatEventDate } from '../../data/eventsCatalog';

export default function EventCard({ event, variant = 'upcoming' }) {
  return (
    <article
      className="shrink-0 w-[280px] sm:w-[320px] rounded-xl overflow-hidden
        dark:bg-untold-surface light:bg-white
        border dark:border-untold-border light:border-gray-200 card-hover"
    >
      <div className="relative aspect-video overflow-hidden">
        <img
          src={event.thumbnail}
          alt={event.eventName}
          loading="lazy"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
        <span className="absolute top-3 left-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-untold-gold text-untold-dark">
          {event.sport}
        </span>
        {variant === 'upcoming' && (
          <div className="absolute bottom-3 right-3">
            <EventCountdown targetDate={event.date} compact />
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="font-display text-lg font-bold line-clamp-2 dark:text-untold-white light:text-black">
          {event.eventName}
        </h3>
        <p className="mt-1 text-xs dark:text-untold-muted light:text-gray-500">
          {formatEventDate(event.date, event.endDate)}
          {event.location && ` · ${event.location}`}
        </p>
        {event.teamsOrPlayers?.length > 0 && (
          <p className="mt-2 text-sm font-medium dark:text-untold-gold light:text-untold-gold-dark line-clamp-1">
            {event.teamsOrPlayers.join(' vs ')}
          </p>
        )}
        <p className="mt-2 text-sm line-clamp-2 dark:text-untold-white/70 light:text-gray-600">
          {event.preview || event.description}
        </p>
      </div>
    </article>
  );
}
