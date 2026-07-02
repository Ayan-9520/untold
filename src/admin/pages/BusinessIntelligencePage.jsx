import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';

const biKey = ['business-intelligence'];

const TABS = [
  'executive',
  'revenue',
  'ai-costs',
  'usage',
  'performance',
  'projects',
  'teams',
  'organizations',
  'retention',
  'growth',
  'reports',
  'scheduled',
];

const TAB_LABELS = {
  executive: 'Executive',
  revenue: 'Revenue',
  'ai-costs': 'AI Costs',
  usage: 'Usage',
  performance: 'Performance',
  projects: 'Projects',
  teams: 'Teams',
  organizations: 'Organizations',
  retention: 'Retention',
  growth: 'Growth',
  reports: 'Custom Reports',
  scheduled: 'Scheduled',
};

function StatCard({ label, value, sub, tone }) {
  const tones = { default: '', gold: 'text-untold-gold', green: 'text-emerald-400', sky: 'text-sky-400', red: 'text-red-400' };
  return (
    <div className="studio-card p-4">
      <div className="text-[10px] uppercase tracking-wider dark:text-untold-muted">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${tones[tone] || ''}`}>{value}</div>
      {sub && <div className="text-[10px] dark:text-untold-muted mt-1">{sub}</div>}
    </div>
  );
}

function KpiGrid({ kpis, labels }) {
  if (!kpis) return null;
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      {Object.entries(labels).map(([key, label]) => (
        <StatCard key={key} label={label} value={formatKpi(key, kpis[key])} tone={key.includes('cost') || key.includes('failed') ? 'red' : key.includes('mrr') || key.includes('growth') ? 'gold' : 'green'} />
      ))}
    </div>
  );
}

function formatKpi(key, val) {
  if (val == null) return '—';
  if (key.includes('usd') || key.includes('mrr') || key.includes('arr') || key.includes('cost')) return `$${Number(val).toFixed(2)}`;
  if (key.includes('pct') || key.includes('rate')) return `${Number(val).toFixed(1)}%`;
  if (typeof val === 'number') return Number(val).toLocaleString();
  return String(val);
}

function TimeseriesChart({ data, dataKey = 'value', title, valueFormatter }) {
  if (!data?.length) return null;
  const fmt = valueFormatter || ((v) => v);
  return (
    <div className="studio-card p-4 mt-4">
      <h3 className="text-sm font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#888' }} />
          <YAxis tick={{ fontSize: 10, fill: '#888' }} tickFormatter={fmt} />
          <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', fontSize: 12 }} formatter={(v) => [fmt(v), '']} />
          <Line type="monotone" dataKey={dataKey} stroke="#d4af37" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function BreakdownBar({ title, data, labelKey = 'label', valueKey = 'cost_usd' }) {
  if (!data?.length) return null;
  return (
    <div className="studio-card p-4 mt-4">
      <h3 className="text-sm font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data.slice(0, 8)} margin={{ top: 4, right: 8, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey={labelKey} tick={{ fontSize: 9, fill: '#888' }} angle={-25} textAnchor="end" interval={0} />
          <YAxis tick={{ fontSize: 10, fill: '#888' }} />
          <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', fontSize: 12 }} />
          <Bar dataKey={valueKey} fill="#d4af37" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function ExecutivePanel({ data }) {
  if (!data) return null;
  return (
    <div className="space-y-4 mt-4">
      <KpiGrid
        kpis={data.kpis}
        labels={{
          mrr_usd: 'MRR',
          arr_usd: 'ARR',
          ai_cost_usd: 'AI Cost',
          active_projects: 'Active Projects',
          organizations: 'Organizations',
          mrr_growth_pct: 'MRR Growth',
          ai_generations: 'AI Generations',
          seat_utilization_pct: 'Seat Utilization',
        }}
      />
      {data.highlights?.length > 0 && (
        <div className="studio-card p-4">
          <h3 className="text-sm font-semibold mb-3">Highlights</h3>
          <div className="grid sm:grid-cols-3 gap-3">
            {data.highlights.map((h) => (
              <div key={h.label} className="text-xs">
                <div className="dark:text-untold-muted">{h.label}</div>
                <div className="text-lg font-semibold text-untold-gold mt-1">{h.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      <TimeseriesChart data={data.timeseries?.revenue} title="Revenue trend" />
      <TimeseriesChart data={data.timeseries?.ai_cost} dataKey="cost_usd" title="AI cost trend" valueFormatter={(v) => `$${Number(v).toFixed(4)}`} />
    </div>
  );
}

function ReportsPanel({ reports, onRun, onExport, onCreate }) {
  const [form, setForm] = useState({ name: '', report_type: 'custom', metrics: '', chart_type: 'bar' });
  return (
    <div className="space-y-4 mt-4">
      <div className="studio-card p-4">
        <h3 className="text-sm font-semibold mb-3">Create custom report</h3>
        <div className="grid sm:grid-cols-2 gap-3">
          <input className="studio-input text-xs" placeholder="Report name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="studio-input text-xs" value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })}>
            {['custom', 'executive', 'revenue', 'ai_cost', 'usage', 'projects'].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input className="studio-input text-xs sm:col-span-2" placeholder="Metrics (comma-separated, e.g. revenue.mrr_cents)" value={form.metrics} onChange={(e) => setForm({ ...form, metrics: e.target.value })} />
        </div>
        <button
          type="button"
          className="studio-btn studio-btn--primary text-xs mt-3"
          disabled={!form.name}
          onClick={() => onCreate({ name: form.name, report_type: form.report_type, metrics: form.metrics.split(',').map((s) => s.trim()).filter(Boolean), chart_type: form.chart_type })}
        >
          Create report
        </button>
      </div>
      <div className="space-y-2">
        {(reports || []).map((r) => (
          <div key={r.id} className="studio-card p-4 flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="font-semibold text-sm">{r.name}</div>
              <div className="text-[10px] dark:text-untold-muted uppercase">{r.report_type} · {r.chart_type}{r.is_system ? ' · system' : ''}</div>
            </div>
            <div className="flex gap-2">
              <button type="button" className="studio-btn studio-btn--ghost text-xs" onClick={() => onRun(r.id)}>Run</button>
              <button type="button" className="studio-btn studio-btn--secondary text-xs" onClick={() => onExport(r.id, 'csv')}>CSV</button>
              <button type="button" className="studio-btn studio-btn--secondary text-xs" onClick={() => onExport(r.id, 'json')}>JSON</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ScheduledPanel({ schedules, reports, onCreate, onDelete }) {
  const [form, setForm] = useState({ name: '', report_id: '', cron_expression: '0 8 * * 1', export_format: 'csv' });
  return (
    <div className="space-y-4 mt-4">
      <div className="studio-card p-4">
        <h3 className="text-sm font-semibold mb-3">Schedule report delivery</h3>
        <div className="grid sm:grid-cols-2 gap-3">
          <input className="studio-input text-xs" placeholder="Schedule name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="studio-input text-xs" value={form.report_id} onChange={(e) => setForm({ ...form, report_id: e.target.value })}>
            <option value="">Select report</option>
            {(reports || []).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
          <input className="studio-input text-xs font-mono" placeholder="Cron" value={form.cron_expression} onChange={(e) => setForm({ ...form, cron_expression: e.target.value })} />
          <select className="studio-input text-xs" value={form.export_format} onChange={(e) => setForm({ ...form, export_format: e.target.value })}>
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
        </div>
        <button
          type="button"
          className="studio-btn studio-btn--primary text-xs mt-3"
          disabled={!form.name || !form.report_id}
          onClick={() => onCreate({ ...form, report_id: Number(form.report_id) })}
        >
          Add schedule
        </button>
      </div>
      <div className="space-y-2">
        {(schedules || []).map((s) => (
          <div key={s.id} className="studio-card p-4 flex justify-between gap-2 text-xs">
            <div>
              <div className="font-semibold">{s.name}</div>
              <div className="font-mono dark:text-untold-muted mt-1">{s.cron_expression}</div>
              {s.next_run_at && <div className="dark:text-untold-muted">Next: {s.next_run_at.slice(0, 16)}</div>}
            </div>
            <button type="button" className="text-red-400" onClick={() => onDelete(s.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BusinessIntelligencePage() {
  const [tab, setTab] = useState('executive');
  const [runResult, setRunResult] = useState(null);
  const qc = useQueryClient();

  const fetchers = {
    executive: () => studioPlatform.getBIExecutive(),
    revenue: () => studioPlatform.getBIRevenue(),
    'ai-costs': () => studioPlatform.getBIAICosts(),
    usage: () => studioPlatform.getBIUsage(),
    performance: () => studioPlatform.getBIPerformance(),
    projects: () => studioPlatform.getBIProjects(),
    teams: () => studioPlatform.getBITeams(),
    organizations: () => studioPlatform.getBIOrganizations(),
    retention: () => studioPlatform.getBIRetention(),
    growth: () => studioPlatform.getBIGrowth(),
  };

  const { data, isLoading } = useQuery({
    queryKey: [...biKey, tab],
    queryFn: fetchers[tab],
    enabled: !!fetchers[tab],
  });

  const { data: reports } = useQuery({
    queryKey: [...biKey, 'reports'],
    queryFn: () => studioPlatform.listBIReports(),
    enabled: tab === 'reports' || tab === 'scheduled',
  });

  const { data: schedules } = useQuery({
    queryKey: [...biKey, 'scheduled'],
    queryFn: () => studioPlatform.listBIScheduledReports(),
    enabled: tab === 'scheduled',
  });

  const createReport = useMutation({
    mutationFn: (payload) => studioPlatform.createBIReport(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [...biKey, 'reports'] }),
  });

  const runReport = useMutation({
    mutationFn: (id) => studioPlatform.runBIReport(id),
    onSuccess: (res) => setRunResult(res),
  });

  const exportReport = async (id, format) => {
    const blob = await studioPlatform.exportBIReport(id, format);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${id}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const createSchedule = useMutation({
    mutationFn: (payload) => studioPlatform.createBIScheduledReport(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [...biKey, 'scheduled'] }),
  });

  const deleteSchedule = useMutation({
    mutationFn: (id) => studioPlatform.deleteBIScheduledReport(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [...biKey, 'scheduled'] }),
  });

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="Business Intelligence"
        description="Executive dashboards, revenue, AI costs, usage, performance, and scheduled reports"
      />

      <div className="flex gap-1 mt-4 flex-wrap">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            className={`px-3 py-1.5 rounded text-xs ${tab === t ? 'bg-untold-gold/20 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'}`}
            onClick={() => { setTab(t); setRunResult(null); }}
          >
            {TAB_LABELS[t]}
          </button>
        ))}
      </div>

      {tab === 'executive' && <ExecutivePanel data={data} />}

      {tab === 'reports' && (
        <ReportsPanel
          reports={reports}
          onRun={(id) => runReport.mutate(id)}
          onExport={exportReport}
          onCreate={(payload) => createReport.mutate(payload)}
        />
      )}

      {tab === 'scheduled' && (
        <ScheduledPanel
          schedules={schedules}
          reports={reports}
          onCreate={(payload) => createSchedule.mutate(payload)}
          onDelete={(id) => deleteSchedule.mutate(id)}
        />
      )}

      {runResult && tab === 'reports' && (
        <div className="studio-card p-4 mt-4 text-xs">
          <h3 className="text-sm font-semibold mb-2">Last run result</h3>
          <pre className="overflow-auto max-h-64 dark:text-untold-muted">{JSON.stringify(runResult.result, null, 2)}</pre>
        </div>
      )}

      {!['executive', 'reports', 'scheduled'].includes(tab) && (
        isLoading ? (
          <p className="text-sm dark:text-untold-muted mt-6">Loading…</p>
        ) : (
          <div className="space-y-4 mt-4">
            <KpiGrid kpis={data?.kpis} labels={Object.fromEntries(Object.keys(data?.kpis || {}).map((k) => [k, k.replace(/_/g, ' ')]))} />
            {data?.timeseries && (
              <TimeseriesChart
                data={Array.isArray(data.timeseries) ? data.timeseries : data.timeseries?.new_orgs || data.timeseries?.revenue}
                dataKey={data.timeseries?.[0]?.cost_usd != null ? 'cost_usd' : 'value'}
                title="Trend"
              />
            )}
            {data?.by_modality && <BreakdownBar title="By modality" data={data.by_modality} />}
            {data?.by_provider && <BreakdownBar title="By provider" data={data.by_provider} />}
            {data?.by_plan && <BreakdownBar title="By plan" data={data.by_plan} labelKey="plan" valueKey="mrr_usd" />}
            {data?.by_module && <BreakdownBar title="By module" data={data.by_module} labelKey="module" valueKey="count" />}
            {data?.by_stage && <BreakdownBar title="By stage" data={data.by_stage} labelKey="stage" valueKey="count" />}
            {data?.teams && (
              <div className="studio-card p-4">
                <h3 className="text-sm font-semibold mb-3">Teams</h3>
                <div className="space-y-2 text-xs">
                  {data.teams.map((t) => (
                    <div key={t.id} className="flex justify-between border-b dark:border-white/5 py-2">
                      <span>{t.name}</span>
                      <span className="dark:text-untold-muted">{t.member_count} members</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {data?.organizations && (
              <div className="studio-card p-4">
                <h3 className="text-sm font-semibold mb-3">Organizations</h3>
                <div className="space-y-2 text-xs max-h-80 overflow-y-auto">
                  {data.organizations.map((o) => (
                    <div key={o.id} className="flex justify-between border-b dark:border-white/5 py-2">
                      <span>{o.name}</span>
                      <span className="dark:text-untold-muted">{o.seats_used}/{o.seat_limit} seats</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {data?.by_organization && (
              <div className="studio-card p-4">
                <h3 className="text-sm font-semibold mb-3">Usage by organization</h3>
                <div className="space-y-2 text-xs">
                  {data.by_organization.map((o) => (
                    <div key={o.organization_id} className="flex justify-between border-b dark:border-white/5 py-2">
                      <span>{o.name}</span>
                      <span className="dark:text-untold-muted">{o.storage_gb} GB</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      )}
    </div>
  );
}
