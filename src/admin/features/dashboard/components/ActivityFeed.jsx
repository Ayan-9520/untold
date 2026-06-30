import { formatRelativeTime, formatStage } from '../utils';

export default function ActivityFeed({ items = [] }) {
  if (!items.length) {
    return (
      <p className="text-sm dark:text-untold-muted light:text-gray-500 py-4 text-center">
        No recent activity
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item.id} className="flex gap-3 text-sm">
          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-untold-gold shrink-0" />
          <div className="min-w-0 flex-1">
            <p className="dark:text-white light:text-black">
              {item.action.replace(/\./g, ' · ')}
              {item.entity_type && (
                <span className="dark:text-untold-muted light:text-gray-500">
                  {' '}
                  — {formatStage(item.entity_type)}
                </span>
              )}
            </p>
            <p className="text-[10px] dark:text-untold-muted light:text-gray-500 mt-0.5">
              {formatRelativeTime(item.created_at)}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}
