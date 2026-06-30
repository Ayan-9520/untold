import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';

const costKey = ['ai-cost'];

const TABS = ['overview', 'budgets', 'policies', 'alerts', 'reports'];
const TAB_LABELS = {
  overview: 'Overview',
  budgets: 'Budgets',
  policies: 'Model Policies',
  alerts: 'Alerts',
  reports: 'Monthly Reports',
};

function StatCard({ label, value, sub, tone }) {
  const tones = { default: '', gold: 'text-untold-gold', green: 'text-emerald-400', sky: 'text-sky-400' };
  return (
    <div className="studio-card p-4">
      <div className="text-[10px] uppercase tracking-wider dark:text-untold-muted">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${tones[tone] || ''}`}>{value}</div>
      {sub && <div className="text-[10px] dark:text-untold-muted mt-1">{sub}</div>}
    </div>
  );
}

function BreakdownChart({ title, data }) {
  if (!data?.length) return null;
  return (
    <div className="studio-card p-4">
      <h3 className="text-sm font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data.slice(0, 8)} margin={{ top: 4, right: 8, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="label" tick={{ fontSize: 9, fill: '#888' }} angle={-25} textAnchor="end" interval={0} />
          <YAxis tick={{ fontSize: 10, fill: '#888' }} tickFormatter={(v) => `$${v}`} />
          <Tooltip
            formatter={(v) => [`$${Number(v).toFixed(4)}`, 'Cost']}
            contentStyle={{ background: '#111', border: '1px solid #333', fontSize: 12 }}
          />
          <Bar dataKey="cost_usd" fill="#d4af37" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function BudgetsPanel({ budgets, onCreate }) {
  const [form, setForm] = useState({
    name: '',
    scope_type: 'global',
    scope_id: '',
    monthly_limit_usd: 500,
    alert_threshold_pct: 80,
    hard_limit: false,
  });

  return (
    <div className="space-y-4">
      <div className="studio-card p-4">
        <h3 className="text-sm font-semibold mb-3">Create budget</h3>
        <div className="grid sm:grid-cols-2 gap-3">
          <input className="studio-input" placeholder="Budget name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <select className="studio-input" value={form.scope_type} onChange={(e) => setForm({ ...form, scope_type: e.target.value })}>
            <option value="global">Global</option>
            <option value="user">Per user</option>
            <option value="project">Per project</option>
          </select>
          {form.scope_type !== 'global' && (
            <input className="studio-input" placeholder="Scope ID" value={form.scope_id} onChange={(e) => setForm({ ...form, scope_id: e.target.value })} />
          )}
          <input type="number" className="studio-input" placeholder="Monthly limit USD" value={form.monthly_limit_usd} onChange={(e) => setForm({ ...form, monthly_limit_usd: Number(e.target.value) })} />
          <input type="number" className="studio-input" placeholder="Alert at %" value={form.alert_threshold_pct} onChange={(e) => setForm({ ...form, alert_threshold_pct: Number(e.target.value) })} />
          <label className="flex items-center gap-2 text-xs">
            <input type="checkbox" checked={form.hard_limit} onChange={(e) => setForm({ ...form, hard_limit: e.target.checked })} />
            Hard limit (block generations)
          </label>
        </div>
        <button
          type="button"
          className="studio-btn studio-btn--primary text-xs mt-3"
          disabled={!form.name}
          onClick={() =>
            onCreate({
              name: form.name,
              scope_type: form.scope_type,
              scope_id: form.scope_id ? Number(form.scope_id) : null,
              monthly_limit_usd: form.monthly_limit_usd,
              alert_threshold_pct: form.alert_threshold_pct,
              hard_limit: form.hard_limit,
            })
          }
        >
          Create budget
        </button>
      </div>

      <div className="studio-card p-4">
        <h3 className="text-sm font-semibold mb-3">Active budgets</h3>
        {!budgets?.length ? (
          <p className="text-xs dark:text-untold-muted">No budgets configured.</p>
        ) : (
          budgets.map((b) => (
            <div key={b.id} className="py-3 border-b dark:border-white/5 last:border-0">
              <div className="flex justify-between gap-2">
                <span className="text-sm font-medium">{b.name}</span>
                <span className="text-xs dark:text-untold-muted uppercase">{b.scope_type}</span>
              </div>
              <div className="flex justify-between text-xs mt-1">
                <span>${b.current_spend_usd?.toFixed(2)} / ${b.monthly_limit_usd}</span>
                <span className={b.utilization_pct >= b.alert_threshold_pct ? 'text-amber-400' : 'text-emerald-400'}>
                  {b.utilization_pct}%
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-white/10 mt-2 overflow-hidden">
                <div
                  className={`h-full rounded-full ${b.utilization_pct >= 100 ? 'bg-red-500' : b.utilization_pct >= b.alert_threshold_pct ? 'bg-amber-500' : 'bg-untold-gold'}`}
                  style={{ width: `${Math.min(100, b.utilization_pct)}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function PoliciesPanel({ policies, onSave }) {
  const [editing, setEditing] = useState(null);
  const [draft, setDraft] = useState({});

  const startEdit = (p) => {
    setEditing(p.module);
    setDraft({ ...p });
  };

  return (
    <div className="studio-card p-4 space-y-3">
      <h3 className="text-sm font-semibold">Automatic model selection & fallback</h3>
      {policies?.map((p) => (
        <div key={p.module} className="py-3 border-b dark:border-white/5 last:border-0">
          <div className="flex justify-between items-start gap-2">
            <div>
              <span className="text-sm font-medium font-mono">{p.module}</span>
              <p className="text-[10px] dark:text-untold-muted mt-0.5">
                {p.selection_mode} · cache {p.cache_enabled ? 'on' : 'off'} · {p.fallback_chain?.length || 0} fallbacks
              </p>
            </div>
            <button type="button" className="studio-btn studio-btn--ghost text-xs" onClick={() => startEdit(p)}>
              Edit
            </button>
          </div>
          {editing === p.module && (
            <div className="mt-3 space-y-2 p-3 rounded-lg bg-white/[0.03]">
              <select className="studio-input text-xs" value={draft.selection_mode} onChange={(e) => setDraft({ ...draft, selection_mode: e.target.value })}>
                <option value="auto">Auto</option>
                <option value="cheapest">Cheapest</option>
                <option value="quality">Quality</option>
                <option value="fixed">Fixed</option>
              </select>
              <input className="studio-input text-xs" placeholder="Primary model" value={draft.primary_model || ''} onChange={(e) => setDraft({ ...draft, primary_model: e.target.value })} />
              <label className="flex items-center gap-2 text-xs">
                <input type="checkbox" checked={draft.cache_enabled} onChange={(e) => setDraft({ ...draft, cache_enabled: e.target.checked })} />
                Response caching
              </label>
              <input type="number" className="studio-input text-xs" placeholder="Cache TTL hours" value={draft.cache_ttl_hours} onChange={(e) => setDraft({ ...draft, cache_ttl_hours: Number(e.target.value) })} />
              <button type="button" className="studio-btn studio-btn--primary text-xs" onClick={() => { onSave(p.module, draft); setEditing(null); }}>
                Save policy
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function AICostOptimizationPage() {
  const qc = useQueryClient();
  const [tab, setTab] = useState('overview');
  const now = new Date();

  const invalidate = () => qc.invalidateQueries({ queryKey: costKey });

  const { data: dashboard, isLoading } = useQuery({
    queryKey: [...costKey, 'dashboard'],
    queryFn: () => studioPlatform.getAICostDashboard(),
  });

  const { data: budgets } = useQuery({
    queryKey: [...costKey, 'budgets'],
    queryFn: () => studioPlatform.listAICostBudgets(),
    enabled: tab === 'budgets' || tab === 'overview',
  });

  const { data: policies } = useQuery({
    queryKey: [...costKey, 'policies'],
    queryFn: () => studioPlatform.listAICostPolicies(),
    enabled: tab === 'policies',
  });

  const { data: alerts } = useQuery({
    queryKey: [...costKey, 'alerts'],
    queryFn: () => studioPlatform.listAICostAlerts({ acknowledged: false }),
    enabled: tab === 'alerts' || tab === 'overview',
  });

  const { data: reports } = useQuery({
    queryKey: [...costKey, 'reports'],
    queryFn: () => studioPlatform.listAICostReports(),
    enabled: tab === 'reports',
  });

  const { data: cacheStats } = useQuery({
    queryKey: [...costKey, 'cache'],
    queryFn: () => studioPlatform.getAICostCacheStats(),
    enabled: tab === 'overview',
  });

  const createBudget = useMutation({
    mutationFn: (data) => studioPlatform.createAICostBudget(data),
    onSuccess: invalidate,
  });

  const updatePolicy = useMutation({
    mutationFn: ({ module, data }) => studioPlatform.updateAICostPolicy(module, data),
    onSuccess: invalidate,
  });

  const ackAlert = useMutation({
    mutationFn: (id) => studioPlatform.acknowledgeAICostAlert(id),
    onSuccess: invalidate,
  });

  const generateReport = useMutation({
    mutationFn: () =>
      studioPlatform.generateAICostReport({
        year: now.getFullYear(),
        month: now.getMonth() + 1,
      }),
    onSuccess: invalidate,
  });

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="AI Cost Optimization"
        description="Token usage, cost tracking, automatic model selection, caching, budgets, alerts, and monthly reports"
        actions={
          <button type="button" className="studio-btn studio-btn--secondary text-sm" onClick={() => generateReport.mutate()}>
            Generate report
          </button>
        }
      />

      <div className="flex gap-1 mt-4 flex-wrap">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            className={`px-3 py-1.5 rounded-full text-xs capitalize ${tab === t ? 'bg-untold-gold/20 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'}`}
            onClick={() => setTab(t)}
          >
            {TAB_LABELS[t]}
            {t === 'alerts' && alerts?.length > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-red-500/30 text-red-300 text-[9px]">{alerts.length}</span>
            )}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading cost data…</p>
      ) : (
        <div className="mt-6">
          {tab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <StatCard label="Total cost" value={`$${dashboard?.total_cost_usd?.toFixed(2) ?? '0'}`} tone="gold" />
                <StatCard label="Input tokens" value={(dashboard?.total_input_tokens ?? 0).toLocaleString()} />
                <StatCard label="Output tokens" value={(dashboard?.total_output_tokens ?? 0).toLocaleString()} />
                <StatCard label="Requests" value={dashboard?.total_requests ?? 0} />
                <StatCard label="Cache savings" value={`$${dashboard?.cache_savings_usd?.toFixed(2) ?? '0'}`} tone="green" sub={`${cacheStats?.total_hits ?? 0} hits`} />
                <StatCard label="Open alerts" value={dashboard?.unacknowledged_alerts ?? 0} tone={dashboard?.unacknowledged_alerts ? 'sky' : 'default'} />
              </div>
              <div className="grid lg:grid-cols-2 gap-4">
                <BreakdownChart title="Cost per project" data={dashboard?.by_project?.map((d) => ({ ...d, label: d.label || d.key }))} />
                <BreakdownChart title="Cost per model" data={dashboard?.by_model?.map((d) => ({ ...d, label: d.key }))} />
                <BreakdownChart title="Cost per provider" data={dashboard?.by_provider?.map((d) => ({ ...d, label: d.key }))} />
                <BreakdownChart title="Cost per user" data={dashboard?.by_user?.map((d) => ({ ...d, label: d.label || d.key }))} />
              </div>
            </div>
          )}

          {tab === 'budgets' && <BudgetsPanel budgets={budgets} onCreate={(data) => createBudget.mutate(data)} />}

          {tab === 'policies' && (
            <PoliciesPanel policies={policies} onSave={(module, data) => updatePolicy.mutate({ module, data })} />
          )}

          {tab === 'alerts' && (
            <div className="studio-card p-4 space-y-2">
              {!alerts?.length ? (
                <p className="text-xs dark:text-untold-muted">No active alerts.</p>
              ) : (
                alerts.map((a) => (
                  <div key={a.id} className="flex justify-between gap-3 py-3 border-b dark:border-white/5">
                    <div>
                      <p className="text-sm">{a.message}</p>
                      <p className="text-[10px] dark:text-untold-muted mt-1">{a.budget_name} · {a.created_at?.slice(0, 10)}</p>
                    </div>
                    <button type="button" className="studio-btn studio-btn--ghost text-xs shrink-0" onClick={() => ackAlert.mutate(a.id)}>
                      Acknowledge
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === 'reports' && (
            <div className="studio-card p-4 space-y-3">
              {!reports?.length ? (
                <p className="text-xs dark:text-untold-muted">No reports yet. Click Generate report above.</p>
              ) : (
                reports.map((r) => (
                  <div key={r.id} className="py-3 border-b dark:border-white/5">
                    <div className="flex justify-between">
                      <span className="font-medium">{r.year}-{String(r.month).padStart(2, '0')}</span>
                      <span className="text-untold-gold">${r.report_data?.total_cost_usd?.toFixed(2)}</span>
                    </div>
                    <p className="text-[10px] dark:text-untold-muted mt-1">
                      {r.report_data?.total_requests} requests · {r.report_data?.total_input_tokens?.toLocaleString()} input tokens
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
