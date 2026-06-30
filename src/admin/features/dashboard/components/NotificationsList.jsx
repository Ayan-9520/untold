import { Link } from 'react-router-dom';
import { formatRelativeTime } from '../utils';
import { studioPath } from '../../../../config/ecosystem';

export default function NotificationsList({ items = [] }) {
  if (!items.length) {
    return (
      <p className="text-sm dark:text-untold-muted light:text-gray-500 py-4 text-center">
        No notifications
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {items.map((n) => (
        <li key={n.id}>
          <Link
            to={studioPath('notifications')}
            className={`block rounded-lg px-3 py-2.5 border transition-colors ${
              n.is_read
                ? 'dark:border-white/10 light:border-gray-200'
                : 'border-untold-gold/30 bg-untold-gold/5'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-medium dark:text-white light:text-black leading-snug">{n.title}</p>
              {!n.is_read && <span className="w-2 h-2 rounded-full bg-untold-gold shrink-0 mt-1" />}
            </div>
            {n.body && (
              <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-1 line-clamp-2">{n.body}</p>
            )}
            <p className="text-[10px] dark:text-untold-muted light:text-gray-500 mt-1.5">
              {formatRelativeTime(n.created_at)}
            </p>
          </Link>
        </li>
      ))}
    </ul>
  );
}
