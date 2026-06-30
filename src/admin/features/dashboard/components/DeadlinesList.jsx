import { formatDueDate } from '../utils';

const priorityClass = (priority) => {
  if (priority === 'urgent' || priority === 'high') return 'bg-untold-gold/15 text-untold-gold';
  return 'dark:bg-white/10 light:bg-gray-100 dark:text-untold-muted light:text-gray-600';
};

export default function DeadlinesList({ items = [] }) {
  if (!items.length) {
    return (
      <p className="text-sm dark:text-untold-muted light:text-gray-500 py-4 text-center">
        No upcoming deadlines
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {items.map((task) => {
        const overdue = task.due_date && formatDueDate(task.due_date).includes('overdue');
        return (
          <li
            key={task.id}
            className={`flex items-center justify-between gap-3 rounded-lg border px-3 py-2.5 ${
              overdue
                ? 'border-red-500/30 bg-red-500/5'
                : 'dark:border-white/10 light:border-gray-200'
            }`}
          >
            <div className="min-w-0">
              <p className="text-sm dark:text-white light:text-black truncate">{task.title}</p>
              <p className={`text-xs mt-0.5 ${overdue ? 'text-red-400' : 'dark:text-untold-muted light:text-gray-500'}`}>
                {formatDueDate(task.due_date)}
              </p>
            </div>
            <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full capitalize shrink-0 ${priorityClass(task.priority)}`}>
              {task.priority}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
