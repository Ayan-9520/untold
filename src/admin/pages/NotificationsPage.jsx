import { useState, useEffect } from 'react';
import SearchFilter from '../components/SearchFilter';
import AdminErrorBanner from '../components/AdminErrorBanner';
import { notifications } from '../api/adminApi';
import { BellIcon } from '../components/AdminIcons';

const eventLabels = {
  view: { label: 'View', color: 'bg-blue-500/15 text-blue-400' },
  play: { label: 'Play', color: 'bg-emerald-500/15 text-emerald-400' },
  search: { label: 'Search', color: 'bg-purple-500/15 text-purple-400' },
  watchlist_add: { label: 'Watchlist', color: 'bg-untold-gold/15 text-untold-gold' },
  watchlist_remove: { label: 'Removed', color: 'bg-red-500/15 text-red-400' },
  login: { label: 'Login', color: 'bg-gray-500/15 text-gray-400' },
  register: { label: 'Register', color: 'bg-emerald-500/15 text-emerald-400' },
};

export default function NotificationsPage() {
  const [events, setEvents] = useState([]);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = () => {
    setLoading(true);
    setError(null);
    notifications.listEvents(100)
      .then(setEvents)
      .catch((err) => setError(err.message || 'Failed to load events'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const filtered = events.filter((e) => {
    const matchSearch = !search || e.event_type.includes(search.toLowerCase());
    const matchType = !typeFilter || e.event_type === typeFilter;
    return matchSearch && matchType;
  });

  const formatTime = (date) => {
    const d = new Date(date);
    const now = new Date();
    const diff = Math.floor((now - d) / 1000);
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return d.toLocaleDateString();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold dark:text-untold-white light:text-black">Notifications</h1>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-1">
          Platform activity feed and event log
        </p>
      </div>

      {error && <AdminErrorBanner message={error} onRetry={load} />}

      <SearchFilter
        value={search}
        onChange={setSearch}
        placeholder="Filter events..."
        filters={
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2.5 rounded-lg text-sm dark:bg-untold-surface light:bg-white border dark:border-white/10 light:border-gray-200"
          >
            <option value="">All Events</option>
            {Object.keys(eventLabels).map((t) => (
              <option key={t} value={t}>{eventLabels[t].label}</option>
            ))}
          </select>
        }
      />

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => <div key={i} className="h-16 rounded-xl skeleton" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-xl p-12 text-center dark:bg-untold-surface light:bg-white border dark:border-white/5">
          <BellIcon className="w-10 h-10 mx-auto dark:text-untold-muted light:text-gray-300" />
          <p className="mt-3 text-sm dark:text-untold-muted light:text-gray-500">No notifications found</p>
        </div>
      ) : (
        <div className="rounded-xl dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200 divide-y dark:divide-white/5 light:divide-gray-50">
          {filtered.map((event) => {
            const meta = eventLabels[event.event_type] || { label: event.event_type, color: 'bg-gray-500/15 text-gray-400' };
            return (
              <div key={event.id} className="flex items-start gap-4 px-5 py-4 hover:dark:bg-white/[0.02] transition-colors">
                <div className={`mt-0.5 p-2 rounded-lg ${meta.color}`}>
                  <BellIcon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${meta.color}`}>
                      {meta.label}
                    </span>
                    <span className="text-[10px] dark:text-untold-muted light:text-gray-400">
                      {formatTime(event.created_at)}
                    </span>
                  </div>
                  <p className="text-sm dark:text-untold-white light:text-black mt-1">
                    {event.event_type === 'login' && `User #${event.user_id} signed in`}
                    {event.event_type === 'register' && `New user #${event.user_id} registered`}
                    {event.event_type === 'watchlist_add' && `Video #${event.video_id} added to watchlist`}
                    {event.event_type === 'watchlist_remove' && `Video #${event.video_id} removed from watchlist`}
                    {event.event_type === 'view' && `Video #${event.video_id} viewed`}
                    {event.event_type === 'play' && `Video #${event.video_id} played`}
                    {!['login', 'register', 'watchlist_add', 'watchlist_remove', 'view', 'play'].includes(event.event_type) &&
                      `Event: ${event.event_type}`}
                  </p>
                  {event.metadata_json && (
                    <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5 truncate">
                      {event.metadata_json}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
