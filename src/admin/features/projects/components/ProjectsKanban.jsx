import { PROJECT_STAGES, STAGE_LABELS } from '../constants';
import ProjectKanbanCard from './ProjectKanbanCard';

export default function ProjectsKanban({ projects, onEdit, onStageChange }) {
  const byStage = PROJECT_STAGES.reduce((acc, stage) => {
    acc[stage] = projects.filter((p) => p.stage === stage);
    return acc;
  }, {});

  return (
    <div className="flex gap-4 overflow-x-auto pb-4 -mx-1 px-1">
      {PROJECT_STAGES.map((stage) => (
        <div key={stage} className="min-w-[260px] flex-1 flex flex-col max-w-xs">
          <div className="flex items-center justify-between mb-3 px-1">
            <h3 className="text-xs font-semibold uppercase tracking-wider dark:text-untold-muted light:text-gray-500">
              {STAGE_LABELS[stage]}
            </h3>
            <span className="text-xs text-untold-gold font-medium">{byStage[stage].length}</span>
          </div>
          <div className="space-y-2 flex-1 rounded-xl border dark:border-white/5 light:border-gray-200 p-2 min-h-[120px] dark:bg-black/20 light:bg-gray-50/50">
            {byStage[stage].length === 0 ? (
              <p className="text-xs text-center dark:text-untold-muted/60 py-6">No projects</p>
            ) : (
              byStage[stage].map((p) => (
                <ProjectKanbanCard
                  key={p.id}
                  project={p}
                  onEdit={onEdit}
                  onStageChange={onStageChange}
                />
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
