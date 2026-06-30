import { Link } from 'react-router-dom';
import { studioPath } from '../../../../config/ecosystem';
import { STAGE_LABELS } from '../../projects/constants';

export default function ResearchProjectsPanel({ projects, activeProjectId, loading }) {
  if (loading) return <div className="h-40 skeleton rounded-lg" />;

  if (!projects?.length) {
    return (
      <div className="text-center py-12 space-y-2">
        <p className="text-sm dark:text-untold-muted">No projects yet.</p>
        <Link to={studioPath('projects')} className="text-sm text-untold-gold hover:underline">
          Create a project →
        </Link>
      </div>
    );
  }

  return (
    <ul className="space-y-2 max-h-[560px] overflow-y-auto">
      {projects.map((p) => (
        <li key={p.id}>
          <Link
            to={studioPath(`research/${p.id}`)}
            className={`block rounded-lg border px-4 py-3 transition-colors ${
              String(p.id) === String(activeProjectId)
                ? 'border-untold-gold/40 bg-untold-gold/10'
                : 'dark:border-white/10 hover:border-untold-gold/30'
            }`}
          >
            <p className="text-sm font-medium dark:text-white truncate">{p.title}</p>
            <p className="text-xs dark:text-untold-muted mt-0.5">
              {STAGE_LABELS[p.stage] || p.stage}
              {p.sources_count != null && ` · ${p.sources_count} sources`}
            </p>
          </Link>
        </li>
      ))}
      <li className="pt-2">
        <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">
          Manage all projects →
        </Link>
      </li>
    </ul>
  );
}
