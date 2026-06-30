import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';
import { studioPath } from '../../config/ecosystem';

const dashboardKey = ['workflow-dashboard'];

function StatCard({ label, value, tone }) {
  const tones = {
    default: 'text-white',
    active: 'text-untold-gold',
    success: 'text-emerald-400',
    danger: 'text-red-400',
  };
  return (
    <div className="studio-card p-4">
      <div className="text-[10px] uppercase tracking-wider dark:text-untold-muted">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${tones[tone] || tones.default}`}>{value}</div>
    </div>
  );
}

function RunRow({ run }) {
  const statusClass =
    run.status === 'completed'
      ? 'text-emerald-400'
      : run.status === 'running'
        ? 'text-untold-gold'
        : run.status === 'failed'
          ? 'text-red-400'
          : 'dark:text-untold-muted';

  return (
    <Link
      to={studioPath(`workflows/runs/${run.id}`)}
      className="flex items-center gap-3 py-3 border-b dark:border-white/5 last:border-0 hover:bg-white/[0.02] px-2 -mx-2 rounded"
    >
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">{run.topic}</div>
        <div className="text-[10px] dark:text-untold-muted">
          #{run.id}
          {run.trigger_type ? ` · ${run.trigger_type}` : ''}
          {run.workflow_definition_id ? ` · def ${run.workflow_definition_id}` : ''}
        </div>
      </div>
      <div className="text-right shrink-0">
        <div className={`text-[10px] uppercase ${statusClass}`}>{run.status}</div>
        <div className="text-[10px] dark:text-untold-muted">{run.progress}%</div>
      </div>
    </Link>
  );
}

export default function WorkflowDashboardPage() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: dashboardKey,
    queryFn: () => studioPlatform.getWorkflowDashboard(),
    refetchInterval: 5000,
  });

  const { data: definitions } = useQuery({
    queryKey: [...dashboardKey, 'definitions'],
    queryFn: () => studioPlatform.listWorkflowDefinitions(),
  });

  const { data: templates } = useQuery({
    queryKey: [...dashboardKey, 'templates'],
    queryFn: () => studioPlatform.listWorkflowTemplates(),
  });

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="Workflow Engine"
        description="Execution dashboard, visual pipelines, templates, triggers, and run history"
        actions={
          <Link to={studioPath('workflows/builder/new')} className="studio-btn studio-btn--primary text-sm">
            + New workflow
          </Link>
        }
      />

      {isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading dashboard…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-6">
            <StatCard label="Definitions" value={dashboard?.total_definitions ?? 0} />
            <StatCard label="Templates" value={dashboard?.total_templates ?? 0} />
            <StatCard label="Runs today" value={dashboard?.runs_today ?? 0} tone="active" />
            <StatCard label="Active" value={dashboard?.runs_active ?? 0} tone="active" />
            <StatCard label="Completed" value={dashboard?.runs_completed ?? 0} tone="success" />
            <StatCard label="Failed" value={dashboard?.runs_failed ?? 0} tone="danger" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-6">
            <section className="studio-card p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">Recent runs</h2>
                <Link to={studioPath('pipeline')} className="text-[10px] text-untold-gold">
                  Quick run →
                </Link>
              </div>
              {(dashboard?.recent_runs || []).map((run) => (
                <RunRow key={run.id} run={run} />
              ))}
            </section>

            <section className="studio-card p-4">
              <h2 className="text-sm font-semibold mb-3">Your workflows</h2>
              {(definitions?.items || []).length === 0 ? (
                <p className="text-xs dark:text-untold-muted">No custom workflows yet.</p>
              ) : (
                definitions.items.map((def) => (
                  <Link
                    key={def.id}
                    to={studioPath(`workflows/builder/${def.id}`)}
                    className="flex items-center justify-between py-2 border-b dark:border-white/5 last:border-0 hover:text-untold-gold"
                  >
                    <span className="text-sm">{def.name}</span>
                    <span className="text-[10px] dark:text-untold-muted uppercase">{def.status}</span>
                  </Link>
                ))
              )}
            </section>
          </div>

          <section className="studio-card p-4 mt-4">
            <h2 className="text-sm font-semibold mb-3">Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {(templates?.items || []).map((tpl) => (
                <div key={tpl.id} className="border dark:border-white/10 rounded-lg p-3">
                  <div className="text-sm font-medium">{tpl.name}</div>
                  <p className="text-xs dark:text-untold-muted mt-1 line-clamp-2">{tpl.description}</p>
                  <button
                    type="button"
                    className="studio-btn studio-btn--ghost text-xs mt-2"
                    onClick={async () => {
                      const cloned = await studioPlatform.cloneWorkflowTemplate(tpl.id);
                      window.location.href = studioPath(`workflows/builder/${cloned.id}`);
                    }}
                  >
                    Use template
                  </button>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
