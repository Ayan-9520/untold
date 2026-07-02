import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { studioPlatform } from '../api/adminApi';

const platformKey = ['agent-platform'];

function StatCard({ label, value, accent }) {
  return (
    <div className="studio-card p-4">
      <div className="text-[10px] uppercase dark:text-untold-muted">{label}</div>
      <div className={`text-2xl font-semibold ${accent || ''}`}>{value}</div>
    </div>
  );
}

export function AgentMonitoringPanel() {
  const { data, isLoading } = useQuery({
    queryKey: [...platformKey, 'monitoring'],
    queryFn: () => studioPlatform.getAgentMonitoring(),
    refetchInterval: 60_000,
  });

  if (isLoading) return <p className="text-sm dark:text-untold-muted mt-4">Loading monitoring…</p>;
  if (!data) return null;

  return (
    <div className="mt-6 space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard label="Installed" value={data.installed_count ?? 0} />
        <StatCard label="Enabled" value={data.enabled_count ?? 0} accent="text-emerald-400" />
        <StatCard label="Runs today" value={data.runs_today ?? 0} accent="text-untold-gold" />
        <StatCard label="Failed today" value={data.failed_today ?? 0} accent="text-red-400" />
        <StatCard label="Cost today" value={`$${(data.cost_today_usd ?? 0).toFixed(4)}`} />
        <StatCard label="Pending msgs" value={data.pending_messages ?? 0} accent="text-sky-400" />
      </div>

      {data.by_agent?.length > 0 && (
        <div className="studio-card p-4">
          <h3 className="text-sm font-semibold mb-3">Runs by agent (today)</h3>
          <div className="space-y-2">
            {data.by_agent.map((row) => (
              <div key={row.slug} className="flex justify-between text-xs">
                <code className="text-untold-gold">{row.slug}</code>
                <span className="dark:text-untold-muted">
                  {row.runs} runs · ${row.cost_usd.toFixed(4)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.recent_logs?.length > 0 && (
        <div className="studio-card p-4">
          <h3 className="text-sm font-semibold mb-3">Recent execution logs</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {data.recent_logs.map((log) => (
              <div key={log.id} className="text-xs py-2 border-b dark:border-white/5 flex justify-between gap-2">
                <div>
                  <code className="text-untold-gold">{log.agent_slug}</code>
                  <span className={`ml-2 ${log.status === 'failed' ? 'text-red-400' : 'text-emerald-400'}`}>
                    {log.status}
                  </span>
                  {log.message && <p className="dark:text-untold-muted mt-0.5 truncate max-w-md">{log.message}</p>}
                </div>
                <span className="dark:text-untold-muted shrink-0">{log.created_at?.slice(0, 16)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function AgentMemoryPanel({ installationId }) {
  const qc = useQueryClient();
  const [key, setKey] = useState('');
  const [content, setContent] = useState('');

  const { data: entries = [], isLoading } = useQuery({
    queryKey: [...platformKey, 'memory', installationId],
    queryFn: () => studioPlatform.listAgentMemory(installationId),
    enabled: !!installationId,
  });

  const save = useMutation({
    mutationFn: () => studioPlatform.upsertAgentMemory(installationId, { memory_key: key, content }),
    onSuccess: () => {
      setKey('');
      setContent('');
      qc.invalidateQueries({ queryKey: [...platformKey, 'memory', installationId] });
    },
  });

  const remove = useMutation({
    mutationFn: (memoryId) => studioPlatform.deleteAgentMemory(installationId, memoryId),
    onSuccess: () => qc.invalidateQueries({ queryKey: [...platformKey, 'memory', installationId] }),
  });

  if (isLoading) return <p className="text-xs dark:text-untold-muted">Loading memory…</p>;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <input className="studio-input w-full text-xs" placeholder="memory_key" value={key} onChange={(e) => setKey(e.target.value)} />
        <textarea className="studio-input w-full text-xs min-h-[80px]" placeholder="content" value={content} onChange={(e) => setContent(e.target.value)} />
        <button type="button" className="studio-btn studio-btn--primary text-xs w-full" disabled={!key || !content} onClick={() => save.mutate()}>
          Save memory
        </button>
      </div>
      <div className="space-y-2">
        {entries.map((e) => (
          <div key={e.id} className="text-xs py-2 border-b dark:border-white/5">
            <div className="flex justify-between gap-2">
              <code className="text-untold-gold">{e.memory_key}</code>
              <button type="button" className="text-red-400 text-[10px]" onClick={() => remove.mutate(e.id)}>Delete</button>
            </div>
            <p className="dark:text-untold-muted mt-1 line-clamp-3">{e.content}</p>
          </div>
        ))}
        {entries.length === 0 && <p className="text-xs dark:text-untold-muted">No memory entries yet.</p>}
      </div>
    </div>
  );
}

export function AgentSchedulesPanel({ installationId }) {
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [cron, setCron] = useState('0 9 * * *');

  const { data: schedules = [], isLoading } = useQuery({
    queryKey: [...platformKey, 'schedules', installationId],
    queryFn: () => studioPlatform.listAgentSchedules(installationId),
    enabled: !!installationId,
  });

  const create = useMutation({
    mutationFn: () => studioPlatform.createAgentSchedule(installationId, { name, cron_expression: cron, payload: {} }),
    onSuccess: () => {
      setName('');
      qc.invalidateQueries({ queryKey: [...platformKey, 'schedules', installationId] });
    },
  });

  const remove = useMutation({
    mutationFn: (id) => studioPlatform.deleteAgentSchedule(installationId, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [...platformKey, 'schedules', installationId] }),
  });

  if (isLoading) return <p className="text-xs dark:text-untold-muted">Loading schedules…</p>;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <input className="studio-input w-full text-xs" placeholder="Schedule name" value={name} onChange={(e) => setName(e.target.value)} />
        <input className="studio-input w-full text-xs font-mono" placeholder="Cron (0 9 * * *)" value={cron} onChange={(e) => setCron(e.target.value)} />
        <button type="button" className="studio-btn studio-btn--primary text-xs w-full" disabled={!name} onClick={() => create.mutate()}>
          Add schedule
        </button>
      </div>
      <div className="space-y-2">
        {schedules.map((s) => (
          <div key={s.id} className="text-xs py-2 border-b dark:border-white/5 flex justify-between gap-2">
            <div>
              <span className="font-medium">{s.name}</span>
              <p className="font-mono dark:text-untold-muted mt-0.5">{s.cron_expression}</p>
              {s.next_run_at && <p className="dark:text-untold-muted">Next: {s.next_run_at.slice(0, 16)}</p>}
            </div>
            <button type="button" className="text-red-400 shrink-0" onClick={() => remove.mutate(s.id)}>Delete</button>
          </div>
        ))}
        {schedules.length === 0 && <p className="text-xs dark:text-untold-muted">No schedules configured.</p>}
      </div>
    </div>
  );
}

export function AgentLogsPanel({ installationId }) {
  const { data, isLoading } = useQuery({
    queryKey: [...platformKey, 'logs', installationId],
    queryFn: () => studioPlatform.getAgentExecutionLogs({ installation_id: installationId, limit: 50 }),
    enabled: !!installationId,
  });

  if (isLoading) return <p className="text-xs dark:text-untold-muted">Loading logs…</p>;

  const items = data?.items || [];

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto">
      {items.map((log) => (
        <div key={log.id} className="text-xs py-2 border-b dark:border-white/5">
          <div className="flex justify-between gap-2">
            <span className={log.status === 'failed' ? 'text-red-400' : 'text-emerald-400'}>{log.status}</span>
            <span className="dark:text-untold-muted">{log.created_at?.slice(0, 16)}</span>
          </div>
          {log.message && <p className="dark:text-untold-muted mt-1">{log.message}</p>}
          {log.duration_ms != null && <p className="dark:text-untold-muted">{log.duration_ms}ms</p>}
        </div>
      ))}
      {items.length === 0 && <p className="text-xs dark:text-untold-muted">No execution logs yet.</p>}
    </div>
  );
}

export function AgentAnalyticsPanel({ installationId }) {
  const { data, isLoading } = useQuery({
    queryKey: [...platformKey, 'analytics', installationId],
    queryFn: () => studioPlatform.getAgentInstallationAnalytics(installationId),
    enabled: !!installationId,
  });

  if (isLoading) return <p className="text-xs dark:text-untold-muted">Loading analytics…</p>;
  if (!data) return null;

  return (
    <div className="grid grid-cols-2 gap-3">
      <StatCard label="Total runs" value={data.total_runs ?? 0} />
      <StatCard label="Total cost" value={`$${(data.total_cost_usd ?? 0).toFixed(4)}`} />
      <StatCard label="Input tokens" value={data.total_input_tokens ?? 0} />
      <StatCard label="Output tokens" value={data.total_output_tokens ?? 0} />
    </div>
  );
}
