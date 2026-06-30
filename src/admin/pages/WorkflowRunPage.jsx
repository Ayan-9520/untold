import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import WorkflowCanvas from '../components/workflow/WorkflowCanvas';
import StudioLiveBadge from '../components/StudioLiveBadge';
import { studioPlatform } from '../api/adminApi';
import { useWorkflowSocket } from '../hooks/useWorkflowSocket';
import { studioPath } from '../../config/ecosystem';

const runKey = (id) => ['workflow-run', id];

export default function WorkflowRunPage() {
  const { runId } = useParams();
  const id = Number(runId);
  const qc = useQueryClient();
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('untold-admin-token') : null;
  const [live, setLive] = useState(true);

  const { data: catalogData } = useQuery({
    queryKey: ['workflow-catalog'],
    queryFn: () => studioPlatform.getWorkflowNodeCatalog(),
  });

  const { data: run, refetch } = useQuery({
    queryKey: runKey(id),
    queryFn: () => studioPlatform.getProductionPipelineRun(id),
    enabled: !!id,
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      return ['queued', 'running', 'pending_approval', 'scheduled'].includes(status) ? 2500 : false;
    },
  });

  const { data: logsData } = useQuery({
    queryKey: [...runKey(id), 'logs'],
    queryFn: () => studioPlatform.getWorkflowLogs(id),
    enabled: !!id,
    refetchInterval: run?.status === 'running' ? 2500 : false,
  });

  useWorkflowSocket({
    token,
    runId: live ? id : null,
    onEvent: () => {
      refetch();
      qc.invalidateQueries({ queryKey: [...runKey(id), 'logs'] });
    },
  });

  const actionMutation = useMutation({
    mutationFn: ({ action, notes }) => {
      const map = {
        run: () => studioPlatform.runWorkflow(id),
        cancel: () => studioPlatform.cancelProductionPipelineRun(id),
        retry: () => studioPlatform.retryWorkflow(id),
        approve: () => studioPlatform.approveWorkflow(id, notes),
        reject: () => studioPlatform.rejectWorkflow(id, notes),
      };
      return map[action]();
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: runKey(id) });
    },
  });

  const graph = run?.graph_snapshot;
  const nodeExecutions = run?.node_executions;

  return (
    <div className="studio-page">
      <StudioPageHeader
        title={`Run #${id}`}
        description={run?.topic || 'Workflow execution'}
        actions={
          <div className="flex gap-2 flex-wrap items-center">
            <StudioLiveBadge active={live && ['running', 'queued'].includes(run?.status)} />
            <Link to={studioPath('workflows')} className="studio-btn studio-btn--ghost text-sm">
              ← Dashboard
            </Link>
            {run?.status === 'pending_approval' && (
              <>
                <button type="button" className="studio-btn studio-btn--primary text-sm" onClick={() => actionMutation.mutate({ action: 'approve' })}>
                  Approve
                </button>
                <button type="button" className="studio-btn studio-btn--ghost text-sm" onClick={() => actionMutation.mutate({ action: 'reject' })}>
                  Reject
                </button>
              </>
            )}
            {['failed', 'cancelled', 'completed'].includes(run?.status) && (
              <button type="button" className="studio-btn studio-btn--secondary text-sm" onClick={() => actionMutation.mutate({ action: 'retry' })}>
                Retry
              </button>
            )}
            {['queued', 'running'].includes(run?.status) && (
              <button type="button" className="studio-btn studio-btn--ghost text-sm" onClick={() => actionMutation.mutate({ action: 'cancel' })}>
                Cancel
              </button>
            )}
          </div>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
        <div className="studio-card p-3">
          <div className="text-[10px] uppercase dark:text-untold-muted">Status</div>
          <div className="text-sm font-medium mt-1">{run?.status}</div>
        </div>
        <div className="studio-card p-3">
          <div className="text-[10px] uppercase dark:text-untold-muted">Progress</div>
          <div className="text-sm font-medium mt-1">{run?.progress ?? 0}%</div>
        </div>
        <div className="studio-card p-3">
          <div className="text-[10px] uppercase dark:text-untold-muted">Trigger</div>
          <div className="text-sm font-medium mt-1">{run?.trigger_type || 'manual'}</div>
        </div>
        <div className="studio-card p-3">
          <div className="text-[10px] uppercase dark:text-untold-muted">Retries</div>
          <div className="text-sm font-medium mt-1">{run?.retry_count ?? 0}</div>
        </div>
      </div>

      {graph && (
        <div className="mt-4">
          <WorkflowCanvas
            initialGraph={graph}
            catalog={catalogData?.nodes || []}
            nodeExecutions={nodeExecutions}
            onGraphChange={undefined}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <section className="studio-card p-4 max-h-80 overflow-y-auto">
          <h2 className="text-sm font-semibold mb-2">Execution logs</h2>
          {(logsData?.logs || []).map((log, i) => (
            <div key={i} className="text-xs py-1 border-b dark:border-white/5 font-mono">
              <span className="dark:text-untold-muted">{log.ts?.slice(11, 19)}</span>{' '}
              <span className={log.level === 'error' ? 'text-red-400' : log.level === 'warn' ? 'text-amber-400' : ''}>
                {log.message}
              </span>
            </div>
          ))}
        </section>

        <section className="studio-card p-4 max-h-80 overflow-y-auto">
          <h2 className="text-sm font-semibold mb-2">Node states</h2>
          {nodeExecutions ? (
            Object.values(nodeExecutions).map((node) => (
              <div key={node.node_id} className="flex justify-between text-xs py-1 border-b dark:border-white/5">
                <span>{node.label || node.node_id}</span>
                <span className="uppercase dark:text-untold-muted">{node.status}</span>
              </div>
            ))
          ) : (
            <p className="text-xs dark:text-untold-muted">Linear pipeline — see stages in quick run view.</p>
          )}
        </section>
      </div>
    </div>
  );
}
