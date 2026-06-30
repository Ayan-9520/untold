import { useState } from 'react';
import { useAdminOverview, useAdminSection, useAdminMutations } from '../hooks/useAdminPanel';
import { studioPlatform } from '../../../api/adminApi';
import { formatRelativeTime } from '../../dashboard/utils';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'rbac', label: 'RBAC' },
  { id: 'users', label: 'Users' },
  { id: 'audit', label: 'Audit logs' },
  { id: 'ai', label: 'AI usage' },
  { id: 'storage', label: 'Storage' },
  { id: 'billing', label: 'Billing' },
  { id: 'api-keys', label: 'API keys' },
  { id: 'health', label: 'System health' },
  { id: 'security', label: 'Security' },
  { id: 'flags', label: 'Feature flags' },
  { id: 'settings', label: 'Settings' },
  { id: 'backups', label: 'Backups' },
];

function formatBytes(b) {
  if (!b) return '0 B';
  const u = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0;
  let n = b;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i += 1; }
  return `${n.toFixed(1)} ${u[i]}`;
}

const HEALTH_COLORS = { healthy: 'text-emerald-400', degraded: 'text-yellow-400', down: 'text-red-400' };

export default function AdminPanelDashboard() {
  const [tab, setTab] = useState('overview');
  const [newKeyName, setNewKeyName] = useState('');
  const [createdSecret, setCreatedSecret] = useState(null);
  const { data: overview } = useAdminOverview();
  const mutations = useAdminMutations();

  const rbac = useAdminSection('rbac', () => studioPlatform.getAdminRbac());
  const users = useAdminSection('users', () => studioPlatform.getAdminUsers());
  const audit = useAdminSection('audit', () => studioPlatform.getAdminAuditLogs());
  const ai = useAdminSection('ai', () => studioPlatform.getAdminAIUsage());
  const storage = useAdminSection('storage', () => studioPlatform.getAdminStorage());
  const billing = useAdminSection('billing', () => studioPlatform.getAdminBilling());
  const apiKeys = useAdminSection('api-keys', () => studioPlatform.getAdminApiKeys());
  const health = useAdminSection('health', () => studioPlatform.getAdminHealth());
  const security = useAdminSection('security', () => studioPlatform.getAdminSecurityLogs());
  const flags = useAdminSection('flags', () => studioPlatform.getAdminFeatureFlags());
  const settings = useAdminSection('settings', () => studioPlatform.getAdminSettings());
  const backups = useAdminSection('backups', () => studioPlatform.getAdminBackups());

  const sectionData = { rbac, users, audit, ai, storage, billing, apiKeys, health, security, flags, settings, backups };
  const loading = sectionData[tab]?.isLoading;

  return (
    <div className="space-y-6">
      {overview && tab === 'overview' && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Users', value: overview.users_count },
              { label: 'Active', value: overview.active_users },
              { label: 'API keys', value: overview.api_keys },
              { label: 'Pending approvals', value: overview.pending_approvals },
            ].map((s) => (
              <div key={s.label} className="ai-stat-card text-center">
                <p className="text-xl font-bold text-untold-gold">{s.value}</p>
                <p className="text-xs dark:text-untold-muted mt-1">{s.label}</p>
              </div>
            ))}
          </div>
          {overview.health && (
            <div className="flex flex-wrap gap-2">
              {Object.entries(overview.health).filter(([k]) => !['uptime_pct', 'version'].includes(k)).map(([k, v]) => (
                <span key={k} className={`text-xs px-2 py-1 rounded-full border dark:border-white/10 ${HEALTH_COLORS[v] || ''}`}>
                  {k}: {v}
                </span>
              ))}
              <span className="text-xs dark:text-untold-muted">uptime {overview.health.uptime_pct}% · v{overview.health.version}</span>
            </div>
          )}
        </>
      )}

      <div className="flex gap-1 overflow-x-auto border-b dark:border-white/10 pb-px">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-3 py-2 text-xs whitespace-nowrap border-b-2 -mb-px ${
              tab === t.id ? 'border-untold-gold text-untold-gold' : 'border-transparent dark:text-untold-muted'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && tab !== 'overview' ? <div className="h-48 skeleton rounded-xl" /> : null}

      {tab === 'rbac' && rbac.data && (
        <table className="w-full text-xs">
          <thead><tr className="dark:text-untold-muted border-b dark:border-white/10"><th className="text-left py-2">Permission</th><th className="text-left py-2">Roles</th></tr></thead>
          <tbody>
            {rbac.data.map((r) => (
              <tr key={r.permission} className="border-b dark:border-white/5">
                <td className="py-2 font-mono text-untold-gold">{r.permission}</td>
                <td className="py-2 dark:text-untold-muted">{r.roles.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === 'users' && users.data && (
        <table className="w-full text-xs">
          <thead><tr className="dark:text-untold-muted border-b dark:border-white/10"><th className="text-left py-2">User</th><th className="text-left py-2">Role</th><th className="text-left py-2">Status</th></tr></thead>
          <tbody>
            {users.data.map((u) => (
              <tr key={u.id} className="border-b dark:border-white/5">
                <td className="py-2"><p className="dark:text-white">{u.full_name}</p><p className="dark:text-untold-muted">{u.email}</p></td>
                <td className="py-2 capitalize">{u.studio_role}</td>
                <td className="py-2">{u.is_active ? <span className="text-emerald-400">Active</span> : <span className="text-red-400">Inactive</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === 'audit' && audit.data && (
        <ul className="space-y-2 max-h-96 overflow-y-auto text-xs">
          {audit.data.map((l) => (
            <li key={l.id} className="flex justify-between dark:text-untold-muted border-b dark:border-white/5 py-2">
              <span><span className="text-untold-gold">{l.action}</span> · user #{l.user_id}</span>
              <span>{formatRelativeTime(l.created_at)}</span>
            </li>
          ))}
          {!audit.data.length && <li className="dark:text-untold-muted">No audit logs yet</li>}
        </ul>
      )}

      {tab === 'ai' && ai.data && (
        <div className="grid sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-2">
            {['total_generations', 'running', 'queued', 'completed', 'failed'].map((k) => (
              <p key={k} className="flex justify-between dark:text-untold-muted"><span className="capitalize">{k.replace('_', ' ')}</span><span className="dark:text-white">{ai.data[k]}</span></p>
            ))}
            <p className="flex justify-between"><span>Tokens (est.)</span><span className="text-untold-gold">{ai.data.tokens_estimated?.toLocaleString()}</span></p>
          </div>
          <div>
            <p className="font-semibold dark:text-white mb-2">By module</p>
            {Object.entries(ai.data.by_module || {}).map(([m, c]) => (
              <p key={m} className="flex justify-between dark:text-untold-muted py-1"><span className="capitalize">{m}</span><span>{c}</span></p>
            ))}
          </div>
        </div>
      )}

      {tab === 'storage' && storage.data && (
        <div className="text-xs space-y-3">
          <p className="dark:text-white">Total: <span className="text-untold-gold">{formatBytes(storage.data.total_bytes)}</span> · {storage.data.total_assets} assets</p>
          {Object.entries(storage.data.by_folder || {}).map(([f, b]) => (
            <div key={f} className="flex justify-between dark:text-untold-muted"><span className="capitalize">{f}</span><span>{formatBytes(b)}</span></div>
          ))}
        </div>
      )}

      {tab === 'billing' && billing.data && (
        <div className="text-xs space-y-2">
          <p className="dark:text-white">MRR: <span className="text-untold-gold">${billing.data.mrr}</span> · ARR: ${billing.data.arr}</p>
          <p className="dark:text-untold-muted">{billing.data.active_subscriptions} active subscriptions</p>
          {Object.entries(billing.data.revenue_by_plan || {}).map(([p, v]) => (
            <div key={p} className="flex justify-between dark:text-untold-muted"><span className="capitalize">{p}</span><span>${v}</span></div>
          ))}
        </div>
      )}

      {tab === 'api-keys' && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="Key name…" className="flex-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-xs dark:text-white" />
            <button
              type="button"
              disabled={!newKeyName.trim() || mutations.createApiKey.isPending}
              onClick={() => mutations.createApiKey.mutate({ name: newKeyName.trim(), permissions: ['studio.access'] }, {
                onSuccess: (d) => { setCreatedSecret(d.secret_key); setNewKeyName(''); },
              })}
              className="text-xs px-3 py-1 rounded-lg bg-untold-gold text-black font-medium disabled:opacity-40"
            >
              Create key
            </button>
          </div>
          {createdSecret && (
            <p className="text-xs text-emerald-400 break-all">Copy now: <code className="bg-black/40 px-1 rounded">{createdSecret}</code></p>
          )}
          <ul className="space-y-2 text-xs">
            {(apiKeys.data || []).map((k) => (
              <li key={k.id} className="flex justify-between items-center dark:text-untold-muted border-b dark:border-white/5 py-2">
                <span>{k.name} · <code>{k.key_prefix}…</code></span>
                {k.is_active ? (
                  <button type="button" onClick={() => mutations.revokeApiKey.mutate(k.id)} className="text-red-400 hover:underline">Revoke</button>
                ) : <span className="text-gray-500">Revoked</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === 'health' && health.data && (
        <div className="grid sm:grid-cols-2 gap-3 text-xs">
          {Object.entries(health.data).map(([k, v]) => (
            <div key={k} className="rounded-lg border dark:border-white/10 p-3 flex justify-between">
              <span className="capitalize dark:text-untold-muted">{k.replace('_', ' ')}</span>
              <span className={typeof v === 'string' ? (HEALTH_COLORS[v] || 'dark:text-white') : 'text-untold-gold'}>{String(v)}</span>
            </div>
          ))}
        </div>
      )}

      {tab === 'security' && security.data && (
        <ul className="space-y-2 max-h-96 overflow-y-auto text-xs">
          {security.data.map((l) => (
            <li key={l.id} className="border-b dark:border-white/5 py-2">
              <span className={l.severity === 'warning' ? 'text-yellow-400' : 'text-untold-muted'}>[{l.severity}]</span>{' '}
              <span className="dark:text-white">{l.message}</span>
              <span className="dark:text-untold-muted ml-2">{formatRelativeTime(l.created_at)}</span>
            </li>
          ))}
        </ul>
      )}

      {tab === 'flags' && flags.data && (
        <ul className="space-y-2">
          {flags.data.map((f) => (
            <li key={f.id} className="flex items-center justify-between text-xs border-b dark:border-white/5 py-2">
              <div>
                <p className="dark:text-white font-medium">{f.label}</p>
                <p className="dark:text-untold-muted">{f.description}</p>
              </div>
              <button
                type="button"
                onClick={() => mutations.toggleFlag.mutate({ id: f.id, enabled: !f.enabled })}
                className={`px-2 py-1 rounded-full text-xs ${f.enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/5 dark:text-untold-muted'}`}
              >
                {f.enabled ? 'ON' : 'OFF'}
              </button>
            </li>
          ))}
        </ul>
      )}

      {tab === 'settings' && settings.data && (
        <div className="space-y-4 text-xs">
          {settings.data.map((s) => (
            <div key={s.key} className="rounded-lg border dark:border-white/10 p-3">
              <p className="font-semibold dark:text-white capitalize mb-2">{s.key}</p>
              <pre className="dark:text-untold-muted overflow-x-auto">{JSON.stringify(s.value, null, 2)}</pre>
            </div>
          ))}
        </div>
      )}

      {tab === 'backups' && (
        <div className="space-y-3">
          <button
            type="button"
            onClick={() => mutations.createBackup.mutate()}
            disabled={mutations.createBackup.isPending}
            className="text-xs px-3 py-1.5 rounded-lg border dark:border-white/10 text-untold-gold"
          >
            + Run backup now
          </button>
          <ul className="text-xs space-y-2">
            {(backups.data || []).map((b) => (
              <li key={b.id} className="flex justify-between dark:text-untold-muted border-b dark:border-white/5 py-2">
                <span className="dark:text-white">{b.label}</span>
                <span>{formatBytes(b.size_bytes)} · {b.status} · {formatRelativeTime(b.created_at)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
