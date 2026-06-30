import { Link } from 'react-router-dom';
import { studioPath } from '../../../../config/ecosystem';
import StageBadge from './StageBadge';
import { formatDueDate } from '../../dashboard/utils';

export default function ProjectsTable({ projects, onEdit, onDelete }) {
  if (!projects.length) {
    return <p className="text-sm text-center dark:text-untold-muted py-12">No projects yet</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border dark:border-white/10 light:border-gray-200">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b dark:border-white/10 light:border-gray-200 dark:bg-untold-card/50">
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider dark:text-untold-muted">Title</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider dark:text-untold-muted">Stage</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider dark:text-untold-muted hidden md:table-cell">Assignee</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider dark:text-untold-muted hidden lg:table-cell">Due</th>
            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider dark:text-untold-muted hidden lg:table-cell">Tags</th>
            <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wider dark:text-untold-muted">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y dark:divide-white/5 light:divide-gray-100">
          {projects.map((p) => (
            <tr key={p.id} className="hover:dark:bg-white/[0.02] hover:light:bg-gray-50">
              <td className="px-4 py-3">
                <Link to={studioPath(`projects/${p.id}`)} className="font-medium dark:text-white light:text-black hover:text-untold-gold">
                  {p.title}
                </Link>
              </td>
              <td className="px-4 py-3"><StageBadge stage={p.stage} /></td>
              <td className="px-4 py-3 dark:text-untold-muted light:text-gray-600 hidden md:table-cell">{p.assignee}</td>
              <td className="px-4 py-3 text-xs dark:text-untold-muted hidden lg:table-cell">
                {p.due_date ? formatDueDate(p.due_date) : '—'}
              </td>
              <td className="px-4 py-3 hidden lg:table-cell">
                <div className="flex flex-wrap gap-1">
                  {(p.tags || []).slice(0, 3).map((t) => (
                    <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-untold-muted">#{t}</span>
                  ))}
                </div>
              </td>
              <td className="px-4 py-3 text-right space-x-2">
                <button type="button" onClick={() => onEdit(p)} className="text-xs text-untold-gold hover:underline">Edit</button>
                <button type="button" onClick={() => onDelete(p)} className="text-xs text-red-400 hover:underline">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
