import { Link } from 'react-router-dom';
import { studioPath } from '../../../../config/ecosystem';
import { PROJECT_STAGES, STAGE_LABELS } from '../constants';
import StageBadge from './StageBadge';
import { formatDueDate } from '../../dashboard/utils';

export default function ProjectKanbanCard({ project, onEdit, onStageChange }) {
  return (
    <div className="rounded-lg border dark:border-white/10 light:border-gray-200 dark:bg-untold-card/50 light:bg-gray-50 p-3 space-y-2 shadow-sm">
      <Link to={studioPath(`projects/${project.id}`)} className="block">
        <p className="text-sm font-medium dark:text-white light:text-black line-clamp-2 hover:text-untold-gold">
          {project.title}
        </p>
      </Link>
      <p className="text-xs dark:text-untold-muted light:text-gray-500">{project.assignee}</p>
      {project.due_date && (
        <p className="text-[10px] text-untold-gold">{formatDueDate(project.due_date)}</p>
      )}
      {(project.tags || []).length > 0 && (
        <div className="flex flex-wrap gap-1">
          {project.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-untold-muted">#{tag}</span>
          ))}
        </div>
      )}
      <div className="flex items-center justify-between gap-2 pt-1 flex-wrap">
        <StageBadge stage={project.stage} />
        <select
          value={project.stage}
          onChange={(e) => onStageChange(project.id, e.target.value)}
          className="text-[10px] rounded border dark:border-white/10 light:border-gray-300 dark:bg-black/30 px-1 py-0.5 dark:text-untold-muted max-w-[90px]"
          aria-label="Change stage"
        >
          {PROJECT_STAGES.map((s) => (
            <option key={s} value={s}>{STAGE_LABELS[s]}</option>
          ))}
        </select>
        <button type="button" onClick={() => onEdit(project)} className="text-[10px] text-untold-gold hover:underline">
          Edit
        </button>
      </div>
    </div>
  );
}
