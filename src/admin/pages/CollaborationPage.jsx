import { useCallback, useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';
import { useProjects } from '../features/projects/hooks/useProjects';
import { useCollaborationSocket } from '../hooks/useCollaborationSocket';
import { studioPath } from '../../config/ecosystem';

const collabKey = (projectId) => ['collaboration', projectId];

const PANELS = ['editor', 'comments', 'tasks', 'approvals', 'files', 'activity'];
const PANEL_LABELS = {
  editor: 'Realtime Editor',
  comments: 'Comments',
  tasks: 'Tasks',
  approvals: 'Approvals',
  files: 'Files',
  activity: 'Activity',
};

function PresenceBar({ presence }) {
  if (!presence?.length) {
    return <p className="text-xs dark:text-untold-muted">No one else is here right now.</p>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {presence.map((p) => (
        <span
          key={p.user_id}
          className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] border dark:border-white/10"
          style={{ borderColor: `${p.color}55` }}
        >
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          {p.name}
          <span className="dark:text-untold-muted uppercase">{p.status}</span>
        </span>
      ))}
    </div>
  );
}

function ConflictModal({ conflict, onResolve, onClose }) {
  if (!conflict) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="studio-card p-6 max-w-lg w-full">
        <h3 className="text-lg font-semibold text-amber-400">Edit conflict</h3>
        <p className="text-sm dark:text-untold-muted mt-2">
          Someone else saved while you were editing. Server is v{conflict.server_version}.
        </p>
        <div className="flex gap-2 mt-4 flex-wrap">
          <button type="button" className="studio-btn studio-btn--primary text-xs" onClick={() => onResolve('accept_server')}>
            Use server version
          </button>
          <button type="button" className="studio-btn studio-btn--secondary text-xs" onClick={() => onResolve('accept_client')}>
            Keep my version
          </button>
          <button type="button" className="studio-btn studio-btn--ghost text-xs" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default function CollaborationPage() {
  const { projectId: paramId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const projectId = Number(paramId || searchParams.get('project') || 0);
  const [panel, setPanel] = useState('editor');
  const [editorText, setEditorText] = useState('');
  const [comment, setComment] = useState('');
  const [conflict, setConflict] = useState(null);
  const [livePatches, setLivePatches] = useState([]);
  const qc = useQueryClient();
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('untold-admin-token') : null;

  const { data: projectsData } = useProjects({ limit: 100 });
  const projects = projectsData?.items || [];

  const invalidate = useCallback(() => {
    if (projectId) qc.invalidateQueries({ queryKey: collabKey(projectId) });
  }, [qc, projectId]);

  const { data: overview } = useQuery({
    queryKey: collabKey(projectId),
    queryFn: () => studioPlatform.getCollaborationOverview(projectId),
    enabled: !!projectId,
    refetchInterval: 8000,
  });

  const { data: document, refetch: refetchDoc } = useQuery({
    queryKey: [...collabKey(projectId), 'document'],
    queryFn: () =>
      studioPlatform.getOrCreateCollabDocument(projectId, {
        resource_type: 'script',
        title: 'Production Script',
      }),
    enabled: !!projectId,
  });

  const { data: comments } = useQuery({
    queryKey: [...collabKey(projectId), 'comments'],
    queryFn: () => studioPlatform.listCollabComments(projectId),
    enabled: !!projectId && panel === 'comments',
  });

  const { data: tasks } = useQuery({
    queryKey: [...collabKey(projectId), 'tasks'],
    queryFn: () => studioPlatform.listCollabTasks(projectId),
    enabled: !!projectId && panel === 'tasks',
  });

  const { data: approvals } = useQuery({
    queryKey: [...collabKey(projectId), 'approvals'],
    queryFn: () => studioPlatform.listCollabApprovals(projectId),
    enabled: !!projectId && panel === 'approvals',
  });

  const { data: files } = useQuery({
    queryKey: [...collabKey(projectId), 'files'],
    queryFn: () => studioPlatform.listCollabFiles(projectId),
    enabled: !!projectId && panel === 'files',
  });

  const { data: activity } = useQuery({
    queryKey: [...collabKey(projectId), 'activity'],
    queryFn: () => studioPlatform.getCollabActivity(projectId),
    enabled: !!projectId && panel === 'activity',
  });

  useEffect(() => {
    if (document?.content?.text != null) setEditorText(document.content.text);
  }, [document?.id, document?.version]);

  const { sendPatch } = useCollaborationSocket({
    token,
    projectId,
    resourceType: 'document',
    resourceId: document?.id,
    onEvent: (ev) => {
      if (ev.event === 'live_patch' && ev.content_delta?.text) {
        setLivePatches((p) => [...p.slice(-5), `${ev.name}: editing…`]);
      }
      if (ev.event === 'document_saved' || ev.event === 'comment_added') invalidate();
    },
  });

  useEffect(() => {
    if (!projectId || !token) return undefined;
    const iv = setInterval(() => {
      studioPlatform.updateCollabPresence(projectId, {
        resource_type: 'document',
        resource_id: document?.id,
        status: panel === 'editor' ? 'editing' : 'viewing',
      });
    }, 15000);
    return () => clearInterval(iv);
  }, [projectId, token, document?.id, panel]);

  const saveMutation = useMutation({
    mutationFn: () =>
      studioPlatform.saveCollabDocument(document.id, {
        content: { text: editorText },
        expected_version: document.version,
        changelog: 'Manual save',
      }),
    onSuccess: (result) => {
      if (result.conflict) {
        setConflict(result);
        return;
      }
      setConflict(null);
      refetchDoc();
      invalidate();
    },
  });

  const resolveMutation = useMutation({
    mutationFn: (resolution) =>
      studioPlatform.resolveCollabConflict(conflict.conflict_id, { resolution }),
    onSuccess: () => {
      setConflict(null);
      refetchDoc();
    },
  });

  const commentMutation = useMutation({
    mutationFn: (content) => studioPlatform.addCollabComment(projectId, { content }),
    onSuccess: () => {
      setComment('');
      invalidate();
      qc.invalidateQueries({ queryKey: [...collabKey(projectId), 'comments'] });
    },
  });

  const handleEditorChange = (text) => {
    setEditorText(text);
    sendPatch({ content_delta: { text }, cursor: { line: 0 } });
  };

  if (!projectId) {
    return (
      <div className="studio-page">
        <StudioPageHeader title="Enterprise Collaboration" description="Select a project to collaborate in realtime" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-6">
          {projects.map((p) => (
            <Link key={p.id} to={studioPath(`collaboration/${p.id}`)} className="studio-card p-4 hover:border-untold-gold/40">
              <div className="font-medium">{p.title}</div>
              <div className="text-xs dark:text-untold-muted mt-1">{p.stage}</div>
            </Link>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="Enterprise Collaboration"
        description={overview ? `Project #${projectId} — ${overview.pending_tasks} tasks · ${overview.pending_approvals} approvals` : 'Loading…'}
        actions={
          <Link to={studioPath(`projects/${projectId}`)} className="studio-btn studio-btn--ghost text-sm">
            Open project →
          </Link>
        }
      />

      <div className="studio-card p-4 mt-4">
        <h3 className="text-[10px] uppercase tracking-wider dark:text-untold-muted mb-2">Team presence</h3>
        <PresenceBar presence={overview?.presence} />
      </div>

      <div className="flex gap-1 mt-4 flex-wrap">
        {PANELS.map((p) => (
          <button
            key={p}
            type="button"
            className={`px-3 py-1.5 rounded-full text-xs ${panel === p ? 'bg-untold-gold/20 text-untold-gold' : 'dark:text-untold-muted'}`}
            onClick={() => setPanel(p)}
          >
            {PANEL_LABELS[p]}
          </button>
        ))}
      </div>

      <div className="mt-4">
        {panel === 'editor' && document && (
          <div className="studio-card p-4">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm font-medium">{document.title} · v{document.version}</span>
              <button type="button" className="studio-btn studio-btn--primary text-xs" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
                Save
              </button>
            </div>
            {livePatches.length > 0 && (
              <p className="text-[10px] text-sky-400 mb-2">{livePatches[livePatches.length - 1]}</p>
            )}
            <textarea
              className="studio-input w-full min-h-[320px] font-mono text-sm"
              value={editorText}
              onChange={(e) => handleEditorChange(e.target.value)}
              placeholder="Collaborative script — changes broadcast in realtime. Use @[user_id] to mention teammates."
            />
          </div>
        )}

        {panel === 'comments' && (
          <div className="studio-card p-4 space-y-3">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                commentMutation.mutate(comment);
              }}
              className="flex gap-2"
            >
              <input className="studio-input flex-1" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Comment — use @[123] to mention" />
              <button type="submit" className="studio-btn studio-btn--primary text-xs">Post</button>
            </form>
            {(comments || []).map((c) => (
              <div key={c.id} className={`py-2 border-b dark:border-white/5 ${c.resolved ? 'opacity-50' : ''}`}>
                <div className="text-xs font-medium">{c.author_name}</div>
                <p className="text-sm mt-1">{c.content}</p>
                {c.mentions?.length > 0 && (
                  <p className="text-[10px] text-untold-gold mt-1">Mentioned: {c.mentions.join(', ')}</p>
                )}
              </div>
            ))}
          </div>
        )}

        {panel === 'tasks' && (
          <div className="studio-card p-4 space-y-2">
            {(tasks || []).map((t) => (
              <div key={t.id} className="flex justify-between py-2 border-b dark:border-white/5 text-sm">
                <span>{t.title}</span>
                <span className="text-[10px] uppercase dark:text-untold-muted">{t.status}</span>
              </div>
            ))}
          </div>
        )}

        {panel === 'approvals' && (
          <div className="studio-card p-4 space-y-2">
            {(approvals || []).map((a) => (
              <div key={a.id} className="py-2 border-b dark:border-white/5 text-sm">
                <div className="flex justify-between">
                  <span>{a.entity_type} #{a.entity_id}</span>
                  <span className="text-[10px] uppercase">{a.status}</span>
                </div>
                <p className="text-xs dark:text-untold-muted mt-1">by {a.requested_by_name}</p>
              </div>
            ))}
          </div>
        )}

        {panel === 'files' && (
          <div className="studio-card p-4 space-y-2">
            {(files || []).map((f) => (
              <div key={f.id} className="flex justify-between py-2 border-b dark:border-white/5 text-sm">
                <a href={f.url || '#'} className="text-untold-gold hover:underline" target="_blank" rel="noreferrer">{f.name}</a>
                <span className="text-[10px] dark:text-untold-muted">v{f.version}</span>
              </div>
            ))}
          </div>
        )}

        {panel === 'activity' && (
          <div className="studio-card p-4 space-y-1 max-h-96 overflow-y-auto">
            {(activity || overview?.recent_activity || []).map((a) => (
              <div key={a.id} className="text-xs py-1.5 border-b dark:border-white/5 font-mono">
                <span className="dark:text-untold-muted">{a.created_at?.slice(0, 16)}</span>{' '}
                <span className="text-untold-gold">{a.user_name}</span> {a.action}
              </div>
            ))}
          </div>
        )}
      </div>

      <ConflictModal conflict={conflict} onResolve={(r) => resolveMutation.mutate(r)} onClose={() => setConflict(null)} />
    </div>
  );
}
