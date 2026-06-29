import { Link } from 'react-router-dom';

export default function EventUpdateFeed({ updates = [], title = 'Live Updates', showMatchLink = true }) {
  if (updates.length === 0) return null;

  return (
    <div className="rounded-xl border dark:border-untold-border light:border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b dark:border-untold-border light:border-gray-200 dark:bg-untold-surface/50 light:bg-gray-50">
        <h2 className="font-semibold dark:text-untold-white light:text-black">{title}</h2>
      </div>
      <ul className="divide-y dark:divide-untold-border light:divide-gray-200">
        {updates.map((u) => (
          <li key={u.id} className="px-4 py-3">
            <div className="flex items-start gap-3">
              <span className="shrink-0 w-2 h-2 rounded-full bg-red-500 mt-1.5 animate-pulse" />
              <div className="min-w-0 flex-1">
                {showMatchLink && u.eventName && (
                  <Link to={`/live/${u.matchId}`} className="text-[10px] font-semibold uppercase text-untold-gold hover:underline">
                    {u.sport} · {u.eventName}
                  </Link>
                )}
                <p className="text-sm dark:text-untold-white light:text-gray-800 mt-0.5">
                  {u.aiText || u.text || u.raw}
                </p>
                <p className="text-[10px] dark:text-untold-muted light:text-gray-400 mt-1">{u.time}</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
