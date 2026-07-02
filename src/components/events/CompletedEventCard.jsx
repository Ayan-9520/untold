import { formatEventDate } from '../../utils/eventDates';

export default function CompletedEventCard({ event }) {
  return (
    <article
      className="flex flex-col sm:flex-row gap-4 p-5 sm:p-6 rounded-xl
        dark:bg-untold-surface light:bg-gray-50
        border dark:border-untold-border light:border-gray-200 card-hover"
    >
      <div className="shrink-0 sm:w-40 aspect-video sm:aspect-[4/3] rounded-lg overflow-hidden">
        <img
          src={event.thumbnail}
          alt={event.eventName}
          loading="lazy"
          className="h-full w-full object-cover"
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider dark:text-untold-gold light:text-untold-gold-dark">
            {event.sport}
          </span>
          <span className="text-xs dark:text-untold-muted light:text-gray-400">
            {formatEventDate(event.date, event.endDate)}
          </span>
        </div>

        <h3 className="font-display text-xl font-bold dark:text-untold-white light:text-black">
          {event.eventName}
        </h3>

        {event.result && (
          <p className="mt-2 text-sm font-semibold dark:text-untold-white light:text-gray-800">
            Result: <span className="text-untold-gold">{event.result}</span>
          </p>
        )}

        {event.highlights?.length > 0 && (
          <ul className="mt-3 space-y-1">
            {event.highlights.slice(0, 3).map((h, i) => (
              <li key={i} className="text-sm dark:text-untold-white/75 light:text-gray-600 flex items-start gap-2">
                <span className="text-untold-gold shrink-0">▸</span>
                {h}
              </li>
            ))}
          </ul>
        )}

        {event.analysis && (
          <p className="mt-3 text-sm italic dark:text-untold-muted light:text-gray-500 line-clamp-2">
            {event.analysis}
          </p>
        )}
      </div>
    </article>
  );
}
