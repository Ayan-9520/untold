import type { StudioTask } from '@/types/studio';
import { formatDueDate } from './utils';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface DeadlinesListProps {
  items: StudioTask[];
}

const priorityVariant = (p: string) => {
  if (p === 'urgent' || p === 'high') return 'gold' as const;
  return 'default' as const;
};

export default function DeadlinesList({ items }: DeadlinesListProps) {
  if (!items.length) {
    return <p className="text-sm text-studio-muted py-4 text-center">No upcoming deadlines</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((task) => {
        const overdue = task.due_date && formatDueDate(task.due_date).includes('overdue');
        return (
          <li
            key={task.id}
            className={cn(
              'flex items-center justify-between gap-3 rounded-lg border border-studio-border/60 px-3 py-2.5',
              overdue && 'border-red-500/30 bg-red-500/5'
            )}
          >
            <div className="min-w-0">
              <p className="text-sm text-white truncate">{task.title}</p>
              <p className={cn('text-xs mt-0.5', overdue ? 'text-red-400' : 'text-studio-muted')}>
                {formatDueDate(task.due_date)}
              </p>
            </div>
            <Badge variant={priorityVariant(task.priority)} className="capitalize shrink-0">
              {task.priority}
            </Badge>
          </li>
        );
      })}
    </ul>
  );
}
