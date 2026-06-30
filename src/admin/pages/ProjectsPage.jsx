import { useState } from 'react';
import { Link } from 'react-router-dom';
import { PlusIcon } from '../components/AdminIcons';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import { studioPath } from '../../config/ecosystem';
import { useProjects, useProjectMutations, useCalendarFeed } from '../features/projects/hooks/useProjects';
import ViewToggle from '../features/projects/components/ViewToggle';
import ProjectsKanban from '../features/projects/components/ProjectsKanban';
import ProjectsTable from '../features/projects/components/ProjectsTable';
import ProjectsCalendar from '../features/projects/components/ProjectsCalendar';
import ProjectFormModal from '../features/projects/components/ProjectFormModal';

export default function ProjectsPage() {
  const [view, setView] = useState('kanban');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [monthDate, setMonthDate] = useState(new Date());

  const { data, isLoading, isError, refetch } = useProjects({ limit: 100 });
  const projects = data?.items || [];

  const monthStart = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1).toISOString();
  const monthEnd = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0, 23, 59, 59).toISOString();
  const { data: calendarFeed } = useCalendarFeed(monthStart, monthEnd);

  const { create, update, remove } = useProjectMutations();

  const openCreate = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (p) => { setEditing(p); setModalOpen(true); };

  const handleSubmit = (formData) => {
    if (editing) {
      update.mutate({ id: editing.id, data: formData }, { onSuccess: () => setModalOpen(false) });
    } else {
      create.mutate(formData, { onSuccess: () => setModalOpen(false) });
    }
  };

  const handleStageChange = (id, stage) => {
    update.mutate({ id, data: { stage } });
  };

  const handleDelete = (p) => {
    if (window.confirm(`Delete "${p.title}"? This cannot be undone.`)) {
      remove.mutate(p.id);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <StudioPageHeader
        title="Project Management"
        description="Create, track, and publish documentaries across the production pipeline"
      >
        <div className="flex flex-wrap items-center gap-3">
          <ViewToggle view={view} onChange={setView} />
          <button
            type="button"
            onClick={openCreate}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-untold-gold text-black text-sm font-semibold"
          >
            <PlusIcon className="w-4 h-4" />
            New Project
          </button>
        </div>
      </StudioPageHeader>

      <PipelineBar activeStep="idea" />

      {isLoading && <div className="h-64 skeleton rounded-xl" />}
      {isError && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6 text-center">
          <p className="text-red-400">Failed to load projects</p>
          <button type="button" onClick={() => refetch()} className="mt-2 text-sm text-untold-gold">Retry</button>
        </div>
      )}

      {!isLoading && !isError && (
        <>
          {view === 'kanban' && (
            <ProjectsKanban projects={projects} onEdit={openEdit} onStageChange={handleStageChange} />
          )}
          {view === 'table' && (
            <ProjectsTable projects={projects} onEdit={openEdit} onDelete={handleDelete} />
          )}
          {view === 'calendar' && (
            <ProjectsCalendar feed={calendarFeed} monthDate={monthDate} onMonthChange={setMonthDate} />
          )}
        </>
      )}

      <ProjectFormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        initial={editing}
        loading={create.isPending || update.isPending}
      />
    </div>
  );
}
