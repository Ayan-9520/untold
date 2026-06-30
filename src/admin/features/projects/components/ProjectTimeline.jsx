import { formatRelativeTime } from '../../dashboard/utils';

export default function ProjectTimeline({ entries }) {
  if (!entries?.length) {
    return <p className="text-sm dark:text-untold-muted py-4 text-center">No activity yet</p>;
  }

  return (
    <ol className="relative border-l dark:border-untold-gold/30 ml-3 space-y-4">
      {entries.map((e) => (
        <li key={e.id} className="ml-4">
          <span className="absolute -left-1.5 w-3 h-3 rounded-full bg-untold-gold border-2 border-untold-dark" />
          <p className="text-sm dark:text-white">{e.action.replace(/\./g, ' · ')}</p>
          <p className="text-xs dark:text-untold-muted mt-0.5">
            {e.user_name} · {formatRelativeTime(e.created_at)}
          </p>
        </li>
      ))}
    </ol>
  );
}
