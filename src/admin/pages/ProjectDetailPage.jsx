import { useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPath } from '../../config/ecosystem';
import { useAdminAuth } from '../context/AdminAuthContext';
import StageBadge from '../features/projects/components/StageBadge';
import ProjectTeamPanel from '../features/projects/components/ProjectTeamPanel';
import ProjectComments from '../features/projects/components/ProjectComments';
import ProjectAttachments from '../features/projects/components/ProjectAttachments';
import ProjectTimeline from '../features/projects/components/ProjectTimeline';
import ProjectFormModal from '../features/projects/components/ProjectFormModal';
import {
  useProject,
  useProjectComments,
  useProjectAttachments,
  useProjectTimeline,
  useProjectMutations,
} from '../features/projects/hooks/useProjects';
import { formatDueDate } from '../features/dashboard/utils';

const TABS = ['overview', 'team', 'comments', 'attachments', 'timeline'];

export default function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAdminAuth();
  const [tab, setTab] = useState('overview');
  const [editOpen, setEditOpen] = useState(false);

  const { data: project, isLoading, isError } = useProject(id);
  const { data: comments } = useProjectComments(id);
  const { data: attachments } = useProjectAttachments(id);
  const { data: timeline } = useProjectTimeline(id);
  const { update, remove, assignMember, removeMember, addComment, addAttachment, deleteComment, deleteAttachment } = useProjectMutations();

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;
  if (isError || !project) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Project not found</p>
        <Link to={studioPath('projects')} className="text-sm text-untold-gold mt-2 inline-block">← Back to projects</Link>
      </div>
    );
  }

  const handleDelete = () => {
    if (window.confirm('Delete this project permanently?')) {
      remove.mutate(project.id, { onSuccess: () => navigate(studioPath('projects')) });
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to={studioPath('projects')} className="text-xs text-untold-gold hover:underline">← All projects</Link>

      <StudioPageHeader title={project.title} description={project.description || 'No description'}>
        <div className="flex gap-2">
          <button type="button" onClick={() => setEditOpen(true)} className="px-3 py-1.5 text-sm rounded-lg border dark:border-white/10 text-untold-gold">
            Edit
          </button>
          <button type="button" onClick={handleDelete} className="px-3 py-1.5 text-sm rounded-lg border border-red-500/30 text-red-400">
            Delete
          </button>
        </div>
      </StudioPageHeader>

      <div className="flex flex-wrap gap-3 items-center">
        <StageBadge stage={project.stage} />
        <span className="text-xs dark:text-untold-muted capitalize">Status: {project.status}</span>
        <span className="text-xs dark:text-untold-muted">Assignee: {project.assignee}</span>
        {project.due_date && <span className="text-xs text-untold-gold">Due: {formatDueDate(project.due_date)}</span>}
      </div>

      {(project.tags || []).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {project.tags.map((t) => (
            <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-untold-gold/10 text-untold-gold">#{t}</span>
          ))}
        </div>
      )}

      <div className="flex gap-1 border-b dark:border-white/10 overflow-x-auto">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm capitalize border-b-2 -mb-px transition-colors ${
              tab === t ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30">
        {tab === 'overview' && (
          <dl className="grid sm:grid-cols-2 gap-4 text-sm">
            <div><dt className="text-xs dark:text-untold-muted">Category</dt><dd className="dark:text-white mt-1">{project.category || '—'}</dd></div>
            <div><dt className="text-xs dark:text-untold-muted">Language</dt><dd className="dark:text-white mt-1">{project.language}</dd></div>
            <div><dt className="text-xs dark:text-untold-muted">Version</dt><dd className="dark:text-white mt-1">v{project.version}</dd></div>
            <div><dt className="text-xs dark:text-untold-muted">Sources</dt><dd className="dark:text-white mt-1">{project.sources_count}</dd></div>
            <div><dt className="text-xs dark:text-untold-muted">Comments</dt><dd className="dark:text-white mt-1">{project.comment_count}</dd></div>
            <div><dt className="text-xs dark:text-untold-muted">Attachments</dt><dd className="dark:text-white mt-1">{project.attachment_count}</dd></div>
          </dl>
        )}
        {tab === 'team' && (
          <ProjectTeamPanel
            project={project}
            onAssign={(data) => assignMember.mutate({ projectId: project.id, data })}
            onRemove={(userId) => removeMember.mutate({ projectId: project.id, userId })}
            loading={assignMember.isPending}
          />
        )}
        {tab === 'comments' && (
          <ProjectComments
            comments={comments}
            currentUserId={user?.id}
            onAdd={(content) => addComment.mutate({ projectId: project.id, content })}
            onDelete={(commentId) => deleteComment.mutate({ projectId: project.id, commentId })}
          />
        )}
        {tab === 'attachments' && (
          <ProjectAttachments
            attachments={attachments}
            onAdd={(data) => addAttachment.mutate({ projectId: project.id, data })}
            onDelete={(attachmentId) => deleteAttachment.mutate({ projectId: project.id, attachmentId })}
          />
        )}
        {tab === 'timeline' && <ProjectTimeline entries={timeline} />}
      </div>

      <ProjectFormModal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        initial={project}
        onSubmit={(data) => update.mutate({ id: project.id, data }, { onSuccess: () => setEditOpen(false) })}
        loading={update.isPending}
      />
    </div>
  );
}
