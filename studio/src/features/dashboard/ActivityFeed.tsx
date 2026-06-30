import type { ActivityLog } from '@/types/studio';
import { formatRelativeTime, formatStage } from './utils';

interface ActivityFeedProps {
  items: ActivityLog[];
}

export default function ActivityFeed({ items }: ActivityFeedProps) {
  if (!items.length) {
    return <p className="text-sm text-studio-muted py-4 text-center">No recent activity</p>;
  }

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item.id} className="flex gap-3 text-sm">
          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-studio-gold shrink-0" />
          <div className="min-w-0 flex-1">
            <p className="text-white">
              {item.action.replace(/\./g, ' · ')}
              {item.entity_type && (
                <span className="text-studio-muted"> — {formatStage(item.entity_type)}</span>
              )}
            </p>
            <p className="text-[10px] text-studio-muted mt-0.5">{formatRelativeTime(item.created_at)}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
