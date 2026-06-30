import { useState, useEffect, useCallback, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPath } from '../../config/ecosystem';
import {
  useScriptByProject,
  useScriptMutations,
  useDebouncedScriptAutosave,
} from '../features/scripts/hooks/useScripts';
import RichTextEditor from '../features/scripts/components/RichTextEditor';
import CollaboratorAvatars from '../features/scripts/components/CollaboratorAvatars';
import VersionHistoryPanel from '../features/scripts/components/VersionHistoryPanel';
import CommentsPanel from '../features/scripts/components/CommentsPanel';
import ApprovalPanel from '../features/scripts/components/ApprovalPanel';
import ScriptWriterPanel from '../features/scripts/components/ScriptWriterPanel';
import ScriptAIHistoryPanel from '../features/scripts/components/ScriptAIHistoryPanel';
import ExportMenu from '../features/scripts/components/ExportMenu';
import { studioPlatform } from '../api/adminApi';

const PANELS = ['editor', 'ai', 'history', 'versions', 'comments', 'approval'];
const PANEL_LABELS = {
  editor: 'Script',
  ai: 'AI Writer',
  history: 'AI History',
  versions: 'Versions',
  comments: 'Comments',
  approval: 'Approval',
};

const STYLES = [
  { value: 'documentary', label: 'Documentary' },
  { value: 'netflix', label: 'Netflix' },
  { value: 'bbc', label: 'BBC' },
  { value: 'espn', label: 'ESPN' },
];

export default function ScriptWorkspacePage() {
  const { projectId } = useParams();
  const { data, isLoading, isError, refetch } = useScriptByProject(projectId);
  const scriptId = data?.workspace?.id;
  const mutations = useScriptMutations(scriptId, projectId);

  const [panel, setPanel] = useState('editor');
  const [content, setContent] = useState('');
  const [style, setStyle] = useState('documentary');
  const [contentVersion, setContentVersion] = useState(1);
  const [saveStatus, setSaveStatus] = useState('saved');
  const [conflict, setConflict] = useState(false);
  const [aiResult, setAiResult] = useState('');
  const [suggestedStyle, setSuggestedStyle] = useState(null);
  const contentVersionRef = useRef(1);

  const getExpectedVersion = useCallback(() => contentVersionRef.current, []);
  const debouncedSave = useDebouncedScriptAutosave(mutations.autosave, getExpectedVersion);

  useEffect(() => {
    if (mutations.autosave.data?.content_version) {
      contentVersionRef.current = mutations.autosave.data.content_version;
      setContentVersion(mutations.autosave.data.content_version);
    }
  }, [mutations.autosave.data]);

  useEffect(() => {
    if (data?.workspace) {
      const w = data.workspace;
      if (w.content != null && w.content_version !== contentVersionRef.current && document.activeElement?.closest('.script-rich-editor') == null) {
        setContent(w.content);
      }
      setStyle(w.style || 'documentary');
      setContentVersion(w.content_version);
      contentVersionRef.current = w.content_version;
    }
  }, [data?.workspace?.id, data?.workspace?.content_version, data?.workspace?.content]);

  useEffect(() => {
    if (!scriptId) return undefined;
    const id = setInterval(() => mutations.heartbeat.mutate(), 12_000);
    mutations.heartbeat.mutate();
    return () => clearInterval(id);
  }, [scriptId]);

  useEffect(() => {
    if (mutations.autosave.isError) {
      setConflict(true);
      setSaveStatus('conflict');
    }
  }, [mutations.autosave.isError]);

  const onContentChange = (html) => {
    setContent(html);
    setSaveStatus('saving');
    setConflict(false);
    debouncedSave(html, style);
    setTimeout(() => setSaveStatus('saved'), 1600);
  };

  const onStyleChange = (newStyle) => {
    setStyle(newStyle);
    setSaveStatus('saving');
    debouncedSave(content, newStyle);
  };

  const captureSelection = useCallback(() => {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed) return '';
    return sel.toString();
  }, []);

  const handleExportPdf = async (id, safeName) => {
    const html = await studioPlatform.exportScriptMarkdown(id);
    const printWin = window.open('', '_blank');
    if (printWin) {
      printWin.document.write(
        `<html><head><title>${safeName}</title><style>body{font-family:Georgia,serif;padding:40px;line-height:1.6}pre{white-space:pre-wrap}</style></head><body><pre>${html.replace(/</g, '&lt;')}</pre></body></html>`,
      );
      printWin.document.close();
      printWin.print();
    }
  };

  const handleApplyAI = (html) => {
    const merged = `${content}${html}`;
    setContent(merged);
    debouncedSave(merged, style);
  };

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;
  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Script workspace unavailable</p>
        <button type="button" onClick={() => refetch()} className="text-sm text-untold-gold mt-2">Retry</button>
      </div>
    );
  }

  const { workspace, versions, comments, approval, ai_history, providers } = data;

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to={studioPath('scripts')} className="text-xs text-untold-gold hover:underline">← Script Studio</Link>

      <StudioPageHeader
        section="Script Studio"
        title={workspace.project_title || workspace.title}
        description="AI script writer · collaborative editing · approval · export"
      >
        <div className="flex flex-wrap gap-3 items-center">
          <CollaboratorAvatars collaborators={workspace.active_collaborators} />
          <span
            className={`text-[10px] uppercase tracking-wider ${
              saveStatus === 'saving' ? 'text-amber-400' : saveStatus === 'conflict' ? 'text-red-400' : 'text-emerald-400'
            }`}
          >
            {saveStatus === 'saving' ? 'Auto-saving…' : saveStatus === 'conflict' ? 'Conflict' : 'Saved'}
          </span>
          <ExportMenu
            scriptId={scriptId}
            title={workspace.title}
            onExportMarkdown={studioPlatform.exportScriptMarkdown}
            onExportPdf={handleExportPdf}
            onExportWord={studioPlatform.exportScriptWord}
          />
          <button
            type="button"
            onClick={() => mutations.saveVersion.mutate()}
            className="px-3 py-1.5 text-xs rounded-lg bg-untold-gold text-black font-medium"
          >
            Save version
          </button>
        </div>
      </StudioPageHeader>

      {conflict && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 flex items-center justify-between gap-3">
          <p className="text-sm text-red-300">Another editor saved changes. Refresh to load the latest version.</p>
          <button type="button" onClick={() => refetch()} className="text-xs text-untold-gold hover:underline shrink-0">
            Refresh
          </button>
        </div>
      )}

      <div className="flex gap-1 overflow-x-auto border-b dark:border-white/10 pb-px">
        {PANELS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPanel(p)}
            className={`px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 -mb-px transition-colors ${
              panel === p ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
            }`}
          >
            {PANEL_LABELS[p]}
          </button>
        ))}
      </div>

      <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 min-h-[400px]">
        {panel === 'editor' && (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-xs dark:text-untold-muted">
                v{workspace.current_version} · edit gen {contentVersion}
                {workspace.last_edited_by_name ? ` · last edit ${workspace.last_edited_by_name}` : ''}
              </p>
              <select
                value={style}
                onChange={(e) => onStyleChange(e.target.value)}
                className="text-xs rounded-lg border dark:border-white/10 dark:bg-black/30 px-2 py-1 dark:text-white"
              >
                {STYLES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label} style</option>
                ))}
              </select>
              <span className={`text-xs capitalize px-2 py-0.5 rounded-full ${
                workspace.status === 'approved' ? 'bg-emerald-500/15 text-emerald-400' :
                workspace.status === 'review' ? 'bg-amber-500/15 text-amber-400' :
                'bg-white/5 dark:text-untold-muted'
              }`}>
                {workspace.status}
              </span>
            </div>
            <RichTextEditor value={content} onChange={onContentChange} placeholder="Write your documentary script…" />
          </div>
        )}

        {panel === 'ai' && (
          <ScriptWriterPanel
            providers={providers}
            onRun={(payload) => {
              mutations.runAI.mutate(payload, {
                onSuccess: (res) => {
                  setAiResult(res.result);
                  setSuggestedStyle(res.suggested_style);
                  if (res.applied && res.result) {
                    refetch();
                  }
                },
              });
            }}
            running={mutations.runAI.isPending}
            lastResult={aiResult}
            suggestedStyle={suggestedStyle}
            onApply={handleApplyAI}
            onCaptureSelection={captureSelection}
          />
        )}

        {panel === 'history' && (
          <ScriptAIHistoryPanel history={ai_history} />
        )}

        {panel === 'versions' && (
          <VersionHistoryPanel
            versions={versions}
            onRestore={(id) => mutations.restoreVersion.mutate(id)}
            restoring={mutations.restoreVersion.isPending}
          />
        )}

        {panel === 'comments' && (
          <CommentsPanel
            comments={comments}
            onAdd={(text) => mutations.addComment.mutate(text)}
            adding={mutations.addComment.isPending}
          />
        )}

        {panel === 'approval' && (
          <ApprovalPanel
            workspace={workspace}
            approval={approval}
            onRequest={mutations.requestApproval.mutate}
            onApprove={mutations.approveScript.mutate}
            onReject={mutations.rejectScript.mutate}
            busy={
              mutations.requestApproval.isPending ||
              mutations.approveScript.isPending ||
              mutations.rejectScript.isPending
            }
          />
        )}
      </div>
    </div>
  );
}
