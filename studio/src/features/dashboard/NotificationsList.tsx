import { Link } from 'react-router-dom';
import type { Notification } from '@/types/studio';
import { formatRelativeTime } from './utils';
import { cn } from '@/lib/utils';

interface NotificationsListProps {
  items: Notification[];
}

export default function NotificationsList({ items }: NotificationsListProps) {
  if (!items.length) {
    return <p className="text-sm text-studio-muted py-4 text-center">No notifications</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((n) => (
        <li key={n.id}>
          <Link
            to="/notifications"
            className={cn(
              'block rounded-lg px-3 py-2.5 border transition-colors',
              n.is_read
                ? 'border-studio-border/40 bg-transparent'
                : 'border-studio-gold/25 bg-studio-gold/5'
            )}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm font-medium text-white leading-snug">{n.title}</p>
              {!n.is_read && <span className="w-2 h-2 rounded-full bg-studio-gold shrink-0 mt-1" />}
            </div>
            {n.body && <p className="text-xs text-studio-muted mt-1 line-clamp-2">{n.body}</p>}
            <p className="text-[10px] text-studio-muted mt-1.5">{formatRelativeTime(n.created_at)}</p>
          </Link>
        </li>
      ))}
    </ul>
  );
}
