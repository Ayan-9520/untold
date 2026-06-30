import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { studioPlatform } from '../api/adminApi';
import StudioProductionFlow from '../components/StudioProductionFlow';
import { WORKFLOW_AGENTS } from '../../config/ecosystem';

const workflowKey = ['workflow-engine'];

const TRANSLATION_LANGUAGES = [
  { code: '', label: 'None' },
  { code: 'es', label: 'Spanish' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ar', label: 'Arabic' },
  { code: 'fr', label: 'French' },
  { code: 'ja', label: 'Japanese' },
  { code: 'de', label: 'German' },
  { code: 'pt', label: 'Portuguese' },
];

function StageRow({ stage, index }) {
  const statusClass =
    stage.status === 'completed'
      ? 'text-emerald-400'
      : stage.status === 'running'
        ? 'text-untold-gold'
        : stage.status === 'failed'
          ? 'text-red-400'
          : 'dark:text-untold-muted';

  return (
    <div className="flex items-start gap-3 py-3 border-b dark:border-white/5 last:border-0">
      <span className="text-xs font-mono dark:text-untold-muted w-5">{index + 1}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium">{stage.label}</span>
          <span className={`text-[10px] uppercase tracking-wide ${statusClass}`}>{stage.status}</span>
        </div>
        {stage.output_preview && (
          <p className="text-xs dark:text-untold-muted mt-1 line-clamp-2">{stage.output_preview}</p>
        )}
        {stage.result_url && (
          <a href={stage.result_url} target="_blank" rel="noreferrer" className="text-[10px] text-untold-gold mt-1 inline-block">
            View output →
          </a>
        )}
        {stage.error && <p className="text-xs text-red-400 mt-1">{stage.error}</p>}
      </div>
    </div>
  );
}

export default function ProductionPipelinePage() {
  const qc = useQueryClient();
  const [topic, setTopic] = useState('');
  const [requiresApproval, setRequiresApproval] = useState(false);
  const [translationLanguage, setTranslationLanguage] = useState('');
  const [promptOverrides, setPromptOverrides] = useState({});
  const [showPrompts, setShowPrompts] = useState(false);
  const [activeRunId, setActiveRunId] = useState(null);

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: workflowKey });
    if (activeRunId) qc.invalidateQueries({ queryKey: [...workflowKey, 'run', activeRunId] });
    if (activeRunId) qc.invalidateQueries({ queryKey: [...workflowKey, 'logs', activeRunId] });
  };

  const { data: overview, isError } = useQuery({
    queryKey: workflowKey,
    queryFn: () => studioPlatform.getProductionPipelineOverview(),
  });

  const defaultPrompts = overview?.prompts || [];

  useEffect(() => {
    if (!defaultPrompts.length) return;
    setPromptOverrides((prev) => {
      if (Object.keys(prev).length) return prev;
      return Object.fromEntries(defaultPrompts.map((p) => [p.key, p.template]));
    });
  }, [defaultPrompts]);

  const updatePrompt = (key, value) => {
    setPromptOverrides((prev) => ({ ...prev, [key]: value }));
  };

  const startMutation = useMutation({
    mutationFn: (payload) => studioPlatform.startProductionPipeline(payload),
    onSuccess: (run) => {
      setActiveRunId(run.id);
      invalidate();
    },
  });

  const actionMutation = useMutation({
    mutationFn: ({ action, id, notes }) => {
      const map = {
        run: () => studioPlatform.runWorkflow(id),
        cancel: () => studioPlatform.cancelProductionPipelineRun(id),
        retry: () => studioPlatform.retryWorkflow(id),
        approve: () => studioPlatform.approveWorkflow(id, notes),
        reject: () => studioPlatform.rejectWorkflow(id, notes),
      };
      return map[action]();
    },
    onSuccess: invalidate,
  });

  const { data: activeRun } = useQuery({
    queryKey: [...workflowKey, 'run', activeRunId],
    queryFn: () => studioPlatform.getProductionPipelineRun(activeRunId),
    enabled: !!activeRunId,
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      return ['queued', 'running', 'pending_approval'].includes(status) ? 2000 : false;
    },
  });

  const { data: logsData } = useQuery({
    queryKey: [...workflowKey, 'logs', activeRunId],
    queryFn: () => studioPlatform.getWorkflowLogs(activeRunId),
    enabled: !!activeRunId,
    refetchInterval: activeRun?.status === 'running' ? 3000 : false,
  });

  const run = activeRun || overview?.recent_runs?.[0];
  const isRunning = run?.status === 'queued' || run?.status === 'running';
  const pendingApproval = run?.status === 'pending_approval';

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="Workflow Engine"
        title="Idea → Analytics"
        description="Full production chain — research through publishing and analytics."
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      <PipelineBar />

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30 space-y-4">
          <h3 className="text-sm font-semibold">Start workflow</h3>
          <p className="text-xs dark:text-untold-muted">
            Enter a documentary topic. The engine runs all {WORKFLOW_AGENTS.length} production stages automatically.
          </p>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            rows={3}
            placeholder="e.g. The untold story of women's boxing pioneer Christy Martin"
            className="w-full rounded-lg border dark:border-white/10 bg-transparent px-3 py-2 text-sm"
          />
          <label className="flex items-center gap-2 text-xs dark:text-untold-muted">
            <input
              type="checkbox"
              checked={requiresApproval}
              onChange={(e) => setRequiresApproval(e.target.checked)}
            />
            Require approval before run
          </label>
          <div>
            <label className="text-xs dark:text-untold-muted block mb-1">Translation language (optional)</label>
            <select
              value={translationLanguage}
              onChange={(e) => setTranslationLanguage(e.target.value)}
              className="w-full rounded-lg border dark:border-white/10 bg-transparent px-3 py-2 text-sm"
            >
              {TRANSLATION_LANGUAGES.map((lang) => (
                <option key={lang.code || 'none'} value={lang.code}>{lang.label}</option>
              ))}
            </select>
          </div>
          <button
            type="button"
            onClick={() => setShowPrompts((v) => !v)}
            className="text-xs text-untold-gold hover:underline"
          >
            {showPrompts ? 'Hide agent prompts' : 'Edit agent prompts'}
          </button>
          {showPrompts && defaultPrompts.length > 0 && (
            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {defaultPrompts.map((p) => (
                <div key={p.key}>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <label className="text-xs font-medium">{p.label}</label>
                    <span className="text-[10px] dark:text-untold-muted font-mono">{p.placeholders?.join(' ')}</span>
                  </div>
                  <textarea
                    value={promptOverrides[p.key] ?? p.template}
                    onChange={(e) => updatePrompt(p.key, e.target.value)}
                    rows={3}
                    className="w-full rounded-lg border dark:border-white/10 bg-transparent px-3 py-2 text-xs font-mono"
                  />
                </div>
              ))}
            </div>
          )}
          <button
            type="button"
            disabled={topic.trim().length < 3 || startMutation.isPending || isRunning}
            onClick={() => {
              const prompts = Object.fromEntries(
                defaultPrompts.map((p) => [p.key, promptOverrides[p.key] ?? p.template]),
              );
              startMutation.mutate({
                topic: topic.trim(),
                requires_approval: requiresApproval,
                translation_language: translationLanguage || null,
                prompts,
              });
            }}
            className="px-4 py-2 rounded-lg bg-untold-gold text-black text-sm font-medium disabled:opacity-40"
          >
            {startMutation.isPending ? 'Creating…' : requiresApproval ? 'Create workflow' : 'Run workflow'}
          </button>
        </div>

        <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30">
          <h3 className="text-sm font-semibold mb-4">Production flow</h3>
          <StudioProductionFlow compact />
        </div>
      </div>

      {run && (
        <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
            <div>
              <h3 className="text-sm font-semibold">{run.topic}</h3>
              <p className="text-xs dark:text-untold-muted mt-0.5">
                {run.current_stage ? `Agent: ${run.current_stage}` : 'Workflow Engine'}
                {' · '}
                <span className="text-untold-gold">{run.status}</span>
                {run.progress > 0 && ` · ${run.progress}%`}
              </p>
            </div>
            {run.progress > 0 && (
              <div className="w-40 h-1.5 rounded-full bg-white/10 overflow-hidden">
                <div className="h-full bg-untold-gold transition-all" style={{ width: `${run.progress}%` }} />
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2 mb-4">
            {pendingApproval && (
              <>
                <button type="button" onClick={() => actionMutation.mutate({ action: 'approve', id: run.id })} className="text-xs px-3 py-1.5 rounded-lg border border-emerald-500/40 text-emerald-400">Approve</button>
                <button type="button" onClick={() => actionMutation.mutate({ action: 'reject', id: run.id })} className="text-xs px-3 py-1.5 rounded-lg border border-red-500/40 text-red-400">Reject</button>
              </>
            )}
            {!isRunning && !pendingApproval && run.status !== 'completed' && (
              <button type="button" onClick={() => actionMutation.mutate({ action: 'run', id: run.id })} className="text-xs px-3 py-1.5 rounded-lg border dark:border-white/10">Run</button>
            )}
            {isRunning && (
              <button type="button" onClick={() => actionMutation.mutate({ action: 'cancel', id: run.id })} className="text-xs px-3 py-1.5 rounded-lg border border-red-500/40 text-red-400">Cancel</button>
            )}
            {['failed', 'cancelled', 'completed'].includes(run.status) && (
              <button type="button" onClick={() => actionMutation.mutate({ action: 'retry', id: run.id })} className="text-xs px-3 py-1.5 rounded-lg border dark:border-white/10">Retry</button>
            )}
          </div>
          {(run.stages || []).map((stage, i) => (
            <StageRow key={stage.id} stage={stage} index={i} />
          ))}
          {run.error_message && <p className="text-sm text-red-400 mt-3">{run.error_message}</p>}

          {logsData?.logs?.length > 0 && (
            <div className="mt-4 pt-4 border-t dark:border-white/10">
              <h4 className="text-xs font-semibold mb-2 dark:text-untold-muted">Logs</h4>
              <ul className="space-y-1 max-h-48 overflow-y-auto font-mono text-[10px]">
                {logsData.logs.map((entry, i) => (
                  <li key={i} className={entry.level === 'error' ? 'text-red-400' : entry.level === 'warn' ? 'text-amber-400' : 'dark:text-untold-muted'}>
                    <span className="opacity-60">{entry.ts?.slice(11, 19)}</span>
                    {entry.stage && <span className="text-untold-gold ml-1">[{entry.stage}]</span>}
                    {' '}{entry.message}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {overview?.recent_runs?.length > 1 && (
        <div className="rounded-xl border dark:border-white/10 p-5 dark:bg-untold-card/30">
          <h3 className="text-sm font-semibold mb-3">Recent workflows</h3>
          <ul className="space-y-2">
            {overview.recent_runs.slice(0, 5).map((r) => (
              <li key={r.id}>
                <button
                  type="button"
                  onClick={() => setActiveRunId(r.id)}
                  className="text-left text-xs w-full py-2 border-b dark:border-white/5 hover:text-untold-gold"
                >
                  <span className="font-medium">{r.topic}</span>
                  <span className="dark:text-untold-muted ml-2">{r.status}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
