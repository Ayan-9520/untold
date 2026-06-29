import { formatEventDate } from '../../data/eventsCatalog';

export default function LiveEventCard({ event }) {
  const latest = event.liveUpdates?.[0];

  return (
    <article
      className="shrink-0 w-[300px] sm:w-[340px] rounded-xl overflow-hidden
        dark:bg-untold-surface light:bg-white
        border dark:border-red-900/40 light:border-red-200 card-hover
        ring-1 ring-red-500/20"
    >
      <div className="relative aspect-video overflow-hidden">
        <img
          src={event.thumbnail}
          alt={event.eventName}
          loading="lazy"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
        <span className="absolute top-3 left-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-600 text-white text-[10px] font-bold uppercase">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
          Live
        </span>
        <span className="absolute top-3 right-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-black/60 text-white">
          {event.sport}
        </span>
      </div>

      <div className="p-4">
        <h3 className="font-display text-lg font-bold line-clamp-2 dark:text-untold-white light:text-black">
          {event.eventName}
        </h3>
        <p className="mt-1 text-xs dark:text-untold-muted light:text-gray-500">
          {formatEventDate(event.date, event.endDate)}
        </p>
        {event.teamsOrPlayers?.length > 0 && (
          <p className="mt-2 text-sm font-medium dark:text-untold-gold light:text-untold-gold-dark">
            {event.teamsOrPlayers.join(' · ')}
          </p>
        )}

        {latest && (
          <div className="mt-3 p-3 rounded-lg dark:bg-white/5 light:bg-gray-50 border dark:border-white/10 light:border-gray-100">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-red-500 mb-1">
              Latest · {latest.time}
            </p>
            <p className="text-sm dark:text-untold-white/90 light:text-gray-700 line-clamp-2">
              {latest.text}
            </p>
          </div>
        )}

        {event.liveUpdates?.length > 1 && (
          <ul className="mt-2 space-y-1">
            {event.liveUpdates.slice(1, 3).map((u, i) => (
              <li key={i} className="text-xs dark:text-untold-muted light:text-gray-500 line-clamp-1">
                <span className="font-medium">{u.time}</span> — {u.text}
              </li>
            ))}
          </ul>
        )}
      </div>
    </article>
  );
}
