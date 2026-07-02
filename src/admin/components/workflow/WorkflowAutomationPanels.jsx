import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { studioPlatform } from '../../api/adminApi';

export function WorkflowTriggersPanel({ definitionId }) {
  const qc = useQueryClient();
  const key = ['workflow-triggers', definitionId];

  const { data: triggers, isLoading } = useQuery({
    queryKey: key,
    queryFn: () => studioPlatform.listWorkflowTriggers(definitionId),
    enabled: Boolean(definitionId),
  });

  const create = useMutation({
    mutationFn: (data) => studioPlatform.createWorkflowTrigger(definitionId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: key }),
  });

  const toggle = useMutation({
    mutationFn: ({ id, enabled }) => studioPlatform.updateWorkflowTrigger(definitionId, id, { enabled }),
    onSuccess: () => qc.invalidateQueries({ queryKey: key }),
  });

  const remove = useMutation({
    mutationFn: (id) => studioPlatform.deleteWorkflowTrigger(definitionId, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: key }),
  });

  const addTrigger = (type) => {
    const names = {
      webhook: 'Webhook trigger',
      api: 'API trigger',
      cron: 'Scheduled cron',
      email: 'Email trigger',
      event: 'Event trigger',
      manual: 'Manual trigger',
    };
    const config = type === 'event' ? { event_name: 'project.created' } : {};
    const cron_expression = type === 'cron' ? '0 9 * * 1' : undefined;
    create.mutate({ trigger_type: type, name: names[type] || type, config, cron_expression });
  };

  if (isLoading) return <p className="text-xs dark:text-untold-muted">Loading triggers…</p>;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1">
        {['webhook', 'api', 'cron', 'email', 'event'].map((t) => (
          <button key={t} type="button" className="studio-btn studio-btn--ghost text-[10px] capitalize" onClick={() => addTrigger(t)}>
            + {t}
          </button>
        ))}
      </div>
      {!triggers?.length ? (
        <p className="text-xs dark:text-untold-muted">No triggers configured.</p>
      ) : (
        triggers.map((tr) => (
          <div key={tr.id} className="border dark:border-white/10 rounded-lg p-2 text-xs space-y-1">
            <div className="flex justify-between gap-2">
              <span className="font-medium">{tr.name}</span>
              <span className="uppercase text-[10px] dark:text-untold-muted">{tr.trigger_type}</span>
            </div>
            {tr.webhook_url && <code className="block text-[9px] break-all opacity-80">{tr.webhook_url}</code>}
            {tr.api_key && <code className="block text-[9px] break-all text-untold-gold">{tr.api_key}</code>}
            {tr.email_url && <code className="block text-[9px] break-all opacity-80">{tr.email_url}</code>}
            {tr.cron_expression && <span className="text-[10px]">Cron: {tr.cron_expression}</span>}
            {tr.config?.event_name && <span className="text-[10px]">Event: {tr.config.event_name}</span>}
            <div className="flex gap-2 pt-1">
              <button type="button" className="studio-btn studio-btn--ghost text-[10px]" onClick={() => toggle.mutate({ id: tr.id, enabled: !tr.enabled })}>
                {tr.enabled ? 'Disable' : 'Enable'}
              </button>
              <button type="button" className="studio-btn studio-btn--ghost text-[10px] text-red-400" onClick={() => remove.mutate(tr.id)}>
                Delete
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export function WorkflowVersionHistory({ definitionId, onRestore }) {
  const { data: versions } = useQuery({
    queryKey: ['workflow-versions', definitionId],
    queryFn: () => studioPlatform.listWorkflowVersions(definitionId),
    enabled: Boolean(definitionId),
  });

  const restore = useMutation({
    mutationFn: (versionId) => studioPlatform.restoreWorkflowVersion(definitionId, versionId),
    onSuccess: onRestore,
  });

  if (!versions?.length) return <p className="text-xs dark:text-untold-muted">No versions yet.</p>;

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {versions.map((v) => (
        <div key={v.id} className="flex justify-between items-start gap-2 py-2 border-b dark:border-white/5 text-xs">
          <div>
            <div className="font-medium">v{v.version}</div>
            <div className="text-[10px] dark:text-untold-muted">{v.changelog || '—'}</div>
            <div className="text-[10px] dark:text-untold-muted">{v.created_at?.slice(0, 10)}</div>
          </div>
          <button type="button" className="studio-btn studio-btn--ghost text-[10px] shrink-0" onClick={() => restore.mutate(v.id)}>
            Restore
          </button>
        </div>
      ))}
    </div>
  );
}
