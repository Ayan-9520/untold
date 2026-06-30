import { Link } from 'react-router-dom';
import { formatStage } from '../utils';
import { studioPath } from '../../../../config/ecosystem';

export default function RecentProductionsList({ projects = [] }) {
  if (!projects.length) {
    return (
      <p className="text-sm dark:text-untold-muted light:text-gray-500 py-4 text-center">
        No active productions
      </p>
    );
  }

  return (
    <div className="divide-y dark:divide-white/10 light:divide-gray-200">
      {projects.map((p) => (
        <Link
          key={p.id}
          to={studioPath('research')}
          className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0 hover:dark:bg-white/[0.02] hover:light:bg-black/[0.02] -mx-2 px-2 rounded-lg transition-colors"
        >
          <div className="min-w-0">
            <p className="font-medium dark:text-white light:text-black text-sm truncate">{p.title}</p>
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">
              {formatStage(p.stage)} · {p.assignee}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {p.publishing_status === 'published' && (
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400">
                Live
              </span>
            )}
            <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-untold-gold/15 text-untold-gold capitalize">
              {p.status}
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}
