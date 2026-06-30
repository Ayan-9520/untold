import { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPath } from '../../config/ecosystem';
import { useStoryboard, useStoryboardMutations } from '../features/storyboard/hooks/useStoryboard';
import SceneList from '../features/storyboard/components/SceneList';
import RevisionHistoryPanel from '../features/storyboard/components/RevisionHistoryPanel';
import StoryboardStats from '../features/storyboard/components/StoryboardStats';
import StoryboardGeneratorPanel from '../features/storyboard/components/StoryboardGeneratorPanel';
import StoryboardAIHistoryPanel from '../features/storyboard/components/StoryboardAIHistoryPanel';
import StoryboardApprovalPanel from '../features/storyboard/components/StoryboardApprovalPanel';

const PANELS = ['scenes', 'ai', 'history', 'revisions', 'approval'];
const PANEL_LABELS = {
  scenes: 'Scenes',
  ai: 'AI Generator',
  history: 'AI History',
  revisions: 'Revisions',
  approval: 'Approval',
};

export default function StoryboardWorkspacePage() {
  const { projectId } = useParams();
  const { data, isLoading, isError, refetch } = useStoryboard(projectId);
  const mutations = useStoryboardMutations(projectId);
  const [panel, setPanel] = useState('scenes');
  const [aiResult, setAiResult] = useState(null);
  const updateTimers = useRef({});

  const debouncedUpdate = useCallback(
    (sceneId, patch) => {
      if (updateTimers.current[sceneId]) clearTimeout(updateTimers.current[sceneId]);
      updateTimers.current[sceneId] = setTimeout(() => {
        mutations.updateScene.mutate({ sceneId, data: patch });
      }, 600);
    },
    [mutations.updateScene],
  );

  useEffect(() => () => {
    Object.values(updateTimers.current).forEach(clearTimeout);
  }, []);

  const approvalBusy = mutations.requestApproval.isPending
    || mutations.approveStoryboard.isPending
    || mutations.rejectStoryboard.isPending;

  if (isLoading) return <div className="h-96 skeleton rounded-xl" />;
  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Storyboard workspace unavailable</p>
        <button type="button" onClick={() => refetch()} className="text-sm text-untold-gold mt-2">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <Link to={studioPath('storyboard')} className="text-xs text-untold-gold hover:underline">← Storyboard Studio</Link>

      <StudioPageHeader
        section="Storyboard Studio"
        title={data.project_title}
        description="AI script → scenes · drag reorder · revision history · approval"
      >
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => { setPanel('ai'); }}
            className="px-3 py-1.5 text-xs rounded-lg bg-untold-gold text-black font-medium"
          >
            AI Generate
          </button>
          <button
            type="button"
            disabled={mutations.importFromScript.isPending}
            onClick={() => mutations.importFromScript.mutate({ replace_existing: false })}
            className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold disabled:opacity-50"
          >
            Quick import
          </button>
          <button
            type="button"
            onClick={() => mutations.createScene.mutate({ duration_seconds: 15, status: 'draft' })}
            className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold"
          >
            + Add scene
          </button>
          <button
            type="button"
            onClick={() => mutations.saveRevision.mutate('Manual snapshot')}
            className="px-3 py-1.5 text-xs rounded-lg border dark:border-white/10 text-untold-gold"
          >
            Save revision
          </button>
        </div>
      </StudioPageHeader>

      <StoryboardStats sceneCount={data.scene_count} totalDuration={data.total_duration_seconds} />

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
            {p === 'revisions' ? ` (${data.revisions.length})` : ''}
          </button>
        ))}
      </div>

      <div className="min-h-[400px]">
        {panel === 'scenes' && (
          <SceneList
            scenes={data.scenes}
            onUpdate={debouncedUpdate}
            onDelete={(id) => mutations.deleteScene.mutate(id)}
            onReorder={(ids) => mutations.reorderScenes.mutate(ids)}
          />
        )}
        {panel === 'ai' && (
          <StoryboardGeneratorPanel
            providers={data.providers}
            hasScript={data.has_script}
            running={mutations.generateAI.isPending}
            lastResult={aiResult}
            onGenerate={(payload) => {
              mutations.generateAI.mutate(payload, {
                onSuccess: (res) => setAiResult(res),
              });
            }}
          />
        )}
        {panel === 'history' && (
          <StoryboardAIHistoryPanel history={data.ai_history} />
        )}
        {panel === 'revisions' && (
          <RevisionHistoryPanel
            revisions={data.revisions}
            onRestore={(id) => mutations.restoreRevision.mutate(id)}
            restoring={mutations.restoreRevision.isPending}
          />
        )}
        {panel === 'approval' && (
          <StoryboardApprovalPanel
            approvalStatus={data.approval_status}
            approval={data.approval}
            onRequest={mutations.requestApproval.mutate}
            onApprove={mutations.approveStoryboard.mutate}
            onReject={mutations.rejectStoryboard.mutate}
            busy={approvalBusy}
          />
        )}
      </div>
    </div>
  );
}
