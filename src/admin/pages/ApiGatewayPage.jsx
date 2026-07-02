import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import StudioPageHeader from '../components/StudioPageHeader';
import { studioPlatform } from '../api/adminApi';

const gatewayKey = ['api-gateway'];

const TIERS = ['free', 'standard', 'enterprise'];
const SCOPES = [
  'videos.read',
  'videos.write',
  'projects.read',
  'projects.write',
  'analytics.read',
  'webhooks.manage',
  'graphql.query',
];

function StatCard({ label, value, hint }) {
  return (
    <div className="studio-card p-4">
      <div className="text-[10px] uppercase dark:text-untold-muted">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
      {hint && <div className="text-[10px] dark:text-untold-muted mt-1">{hint}</div>}
    </div>
  );
}

export default function ApiGatewayPage() {
  const [tab, setTab] = useState('overview');
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyTier, setNewKeyTier] = useState('standard');
  const [newKeyScopes, setNewKeyScopes] = useState(['videos.read', 'projects.read', 'graphql.query']);
  const [createdSecret, setCreatedSecret] = useState(null);
  const [webhookName, setWebhookName] = useState('');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookEvents, setWebhookEvents] = useState(['video.updated']);
  const [createdWebhookSecret, setCreatedWebhookSecret] = useState(null);
  const queryClient = useQueryClient();

  const { data: overview, isLoading } = useQuery({
    queryKey: gatewayKey,
    queryFn: async () => {
      const [ov, keys, webhooks, timeseries, endpoints, docs] = await Promise.all([
        studioPlatform.getApiGatewayOverview(),
        studioPlatform.listApiGatewayKeys(),
        studioPlatform.listApiGatewayWebhooks(),
        studioPlatform.getApiGatewayUsageTimeseries(),
        studioPlatform.getApiGatewayUsageEndpoints(),
        studioPlatform.getApiGatewayDocs(),
      ]);
      return { overview: ov, keys, webhooks, timeseries, endpoints, docs };
    },
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: gatewayKey });

  const createKey = useMutation({
    mutationFn: (data) => studioPlatform.createApiGatewayKey(data),
    onSuccess: (res) => {
      setCreatedSecret(res.secret_key);
      setNewKeyName('');
      invalidate();
    },
  });

  const revokeKey = useMutation({
    mutationFn: (id) => studioPlatform.revokeApiGatewayKey(id),
    onSuccess: invalidate,
  });

  const createWebhook = useMutation({
    mutationFn: (data) => studioPlatform.createApiGatewayWebhook(data),
    onSuccess: (res) => {
      setCreatedWebhookSecret(res.signing_secret);
      setWebhookName('');
      setWebhookUrl('');
      invalidate();
    },
  });

  const deleteWebhook = useMutation({
    mutationFn: (id) => studioPlatform.deleteApiGatewayWebhook(id),
    onSuccess: invalidate,
  });

  const testWebhook = useMutation({
    mutationFn: (id) => studioPlatform.testApiGatewayWebhook(id),
  });

  const toggleScope = (scope) => {
    setNewKeyScopes((prev) => (prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]));
  };

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'keys', label: 'API Keys' },
    { id: 'webhooks', label: 'Webhooks' },
    { id: 'docs', label: 'OpenAPI & Docs' },
  ];

  return (
    <div className="studio-page">
      <StudioPageHeader
        title="API Gateway"
        description="REST API, GraphQL, webhooks, rate limiting, API keys, and usage analytics for third-party integrations"
      >
        <a href="/gateway/docs" target="_blank" rel="noreferrer" className="studio-btn studio-btn--ghost text-xs">
          OpenAPI Docs
        </a>
        <a href="/gateway/graphql" target="_blank" rel="noreferrer" className="studio-btn studio-btn--ghost text-xs">
          GraphQL
        </a>
      </StudioPageHeader>

      <div className="flex gap-2 mt-6 flex-wrap">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`studio-tab ${tab === t.id ? 'studio-tab--active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-sm dark:text-untold-muted mt-6">Loading API Gateway…</p>
      ) : (
        <div className="mt-6">
          {tab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <StatCard label="Active API Keys" value={overview?.overview?.active_api_keys ?? 0} />
                <StatCard label="Requests (24h)" value={overview?.overview?.requests_24h ?? 0} />
                <StatCard label="Avg Latency" value={`${overview?.overview?.avg_latency_ms ?? 0}ms`} />
                <StatCard
                  label="Error Rate (24h)"
                  value={`${overview?.overview?.error_rate_24h_pct ?? 0}%`}
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="studio-card p-4">
                  <h3 className="text-sm font-semibold mb-3">Usage (7 days)</h3>
                  <div className="space-y-2 text-xs">
                    {(overview?.timeseries || []).map((row) => (
                      <div key={row.date} className="flex justify-between dark:text-untold-muted">
                        <span>{row.date}</span>
                        <span>
                          {row.requests} req · {row.avg_latency_ms}ms avg
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="studio-card p-4">
                  <h3 className="text-sm font-semibold mb-3">Top Endpoints</h3>
                  <div className="space-y-2 text-xs">
                    {(overview?.endpoints || []).map((row) => (
                      <div key={`${row.method}-${row.path}`} className="flex justify-between gap-2">
                        <code className="text-untold-gold truncate">
                          {row.method} {row.path}
                        </code>
                        <span className="dark:text-untold-muted shrink-0">{row.requests}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="studio-card p-4 text-xs dark:text-untold-muted">
                <p>
                  <strong className="text-white">Versions:</strong> v1 (direct JSON), v2 (envelope with meta)
                </p>
                <p className="mt-2">
                  <strong className="text-white">Auth:</strong> <code>Authorization: Bearer &lt;jwt&gt;</code> or{' '}
                  <code>X-API-Key: unt_...</code>
                </p>
                <p className="mt-2">
                  <strong className="text-white">Base URL:</strong> <code>/gateway/v1</code> · GraphQL at{' '}
                  <code>/gateway/graphql</code>
                </p>
              </div>
            </div>
          )}

          {tab === 'keys' && (
            <div className="space-y-6">
              <div className="studio-card p-4">
                <h3 className="text-sm font-semibold mb-3">Create API Key</h3>
                <div className="flex flex-wrap gap-2 mb-3">
                  <input
                    className="studio-input flex-1 min-w-[200px]"
                    placeholder="Key name"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                  />
                  <select
                    className="studio-input"
                    value={newKeyTier}
                    onChange={(e) => setNewKeyTier(e.target.value)}
                  >
                    {TIERS.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="studio-btn studio-btn--primary text-xs"
                    disabled={!newKeyName.trim() || createKey.isPending}
                    onClick={() =>
                      createKey.mutate({
                        name: newKeyName.trim(),
                        scopes: newKeyScopes,
                        rate_limit_tier: newKeyTier,
                        api_version: 'v1',
                      })
                    }
                  >
                    Create
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {SCOPES.map((s) => (
                    <label key={s} className="flex items-center gap-1 text-xs">
                      <input type="checkbox" checked={newKeyScopes.includes(s)} onChange={() => toggleScope(s)} />
                      <code>{s}</code>
                    </label>
                  ))}
                </div>
                {createdSecret && (
                  <div className="mt-3 p-3 rounded bg-emerald-500/10 text-xs">
                    <p className="text-emerald-400 font-medium">Copy your key now — it won&apos;t be shown again:</p>
                    <code className="block mt-2 break-all">{createdSecret}</code>
                  </div>
                )}
              </div>

              <div className="studio-card divide-y dark:divide-white/5">
                {(overview?.keys || []).map((k) => (
                  <div key={k.id} className="p-4 flex flex-wrap justify-between gap-2 text-sm">
                    <div>
                      <div className="font-medium">{k.name}</div>
                      <code className="text-xs dark:text-untold-muted">{k.key_prefix}…</code>
                      <div className="text-[10px] dark:text-untold-muted mt-1">
                        {k.rate_limit_tier} · {k.total_requests} requests
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={k.is_active ? 'text-emerald-400 text-xs' : 'text-red-400 text-xs'}>
                        {k.is_active ? 'Active' : 'Revoked'}
                      </span>
                      {k.is_active && (
                        <button
                          type="button"
                          className="text-xs text-red-400"
                          onClick={() => revokeKey.mutate(k.id)}
                        >
                          Revoke
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === 'webhooks' && (
            <div className="space-y-6">
              <div className="studio-card p-4">
                <h3 className="text-sm font-semibold mb-3">Register Webhook</h3>
                <div className="space-y-2">
                  <input
                    className="studio-input w-full"
                    placeholder="Webhook name"
                    value={webhookName}
                    onChange={(e) => setWebhookName(e.target.value)}
                  />
                  <input
                    className="studio-input w-full"
                    placeholder="https://your-server.com/webhooks/untold"
                    value={webhookUrl}
                    onChange={(e) => setWebhookUrl(e.target.value)}
                  />
                  <div className="flex flex-wrap gap-2 text-xs">
                    {(overview?.docs?.webhook_events || []).map((ev) => (
                      <label key={ev} className="flex items-center gap-1">
                        <input
                          type="checkbox"
                          checked={webhookEvents.includes(ev)}
                          onChange={() =>
                            setWebhookEvents((prev) =>
                              prev.includes(ev) ? prev.filter((e) => e !== ev) : [...prev, ev],
                            )
                          }
                        />
                        <code>{ev}</code>
                      </label>
                    ))}
                  </div>
                  <button
                    type="button"
                    className="studio-btn studio-btn--primary text-xs"
                    disabled={!webhookName.trim() || !webhookUrl.trim() || createWebhook.isPending}
                    onClick={() =>
                      createWebhook.mutate({ name: webhookName.trim(), url: webhookUrl.trim(), events: webhookEvents })
                    }
                  >
                    Create Webhook
                  </button>
                </div>
                {createdWebhookSecret && (
                  <div className="mt-3 p-3 rounded bg-emerald-500/10 text-xs">
                    <p className="text-emerald-400">Signing secret (save now):</p>
                    <code className="block mt-2 break-all">{createdWebhookSecret}</code>
                  </div>
                )}
              </div>

              <div className="studio-card divide-y dark:divide-white/5">
                {(overview?.webhooks || []).map((w) => (
                  <div key={w.id} className="p-4 flex justify-between gap-2 text-sm">
                    <div>
                      <div className="font-medium">{w.name}</div>
                      <div className="text-xs dark:text-untold-muted truncate max-w-md">{w.url}</div>
                      <div className="text-[10px] mt-1">{(w.events || []).join(', ')}</div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button
                        type="button"
                        className="text-xs text-untold-gold"
                        onClick={() => testWebhook.mutate(w.id)}
                      >
                        Test
                      </button>
                      <button
                        type="button"
                        className="text-xs text-red-400"
                        onClick={() => deleteWebhook.mutate(w.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === 'docs' && (
            <div className="space-y-4">
              <div className="studio-card p-4 text-sm dark:text-untold-muted space-y-3">
                <p>
                  <strong className="text-white">OpenAPI:</strong>{' '}
                  <a href="/gateway/openapi.json" className="text-untold-gold hover:underline" target="_blank" rel="noreferrer">
                    /gateway/openapi.json
                  </a>
                </p>
                <p>
                  <strong className="text-white">Swagger UI:</strong>{' '}
                  <a href="/gateway/docs" className="text-untold-gold hover:underline" target="_blank" rel="noreferrer">
                    /gateway/docs
                  </a>
                </p>
                <p>
                  <strong className="text-white">GraphQL:</strong> POST <code>/gateway/graphql</code>
                </p>
                <p>
                  <strong className="text-white">Rate limit tiers:</strong>{' '}
                  {Object.entries(overview?.docs?.rate_limit_tiers || {})
                    .map(([k, v]) => `${k}: ${v.limit}`)
                    .join(' · ')}
                </p>
              </div>
              <pre className="studio-card p-4 text-xs overflow-x-auto max-h-96">
                {JSON.stringify(overview?.docs, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
