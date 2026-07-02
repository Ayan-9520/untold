import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { developerApi } from '../api/developerApi';

const DEFAULT_SCOPES = ['videos.read', 'projects.read', 'graphql.query'];

export default function KeysPage() {
  const [name, setName] = useState('');
  const [environment, setEnvironment] = useState('production');
  const [selectedScopes, setSelectedScopes] = useState(DEFAULT_SCOPES);
  const [secret, setSecret] = useState(null);
  const queryClient = useQueryClient();

  const { data: catalog } = useQuery({
    queryKey: ['developer-scopes'],
    queryFn: developerApi.scopes,
    staleTime: 300_000,
  });

  const scopeOptions = catalog?.scopes ? Object.keys(catalog.scopes) : DEFAULT_SCOPES;

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ['developer-keys'],
    queryFn: developerApi.listKeys,
    retry: false,
  });

  const create = useMutation({
    mutationFn: (body) => developerApi.createKey(body),
    onSuccess: (res) => {
      setSecret(res.secret_key);
      setName('');
      queryClient.invalidateQueries({ queryKey: ['developer-keys'] });
    },
  });

  const revoke = useMutation({
    mutationFn: (id) => developerApi.revokeKey(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['developer-keys'] }),
  });

  const toggleScope = (scope) => {
    setSelectedScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">API Keys</h2>
      {catalog?.account_tiers && (
        <p className="text-sm text-neutral-400">
          Your plan limits active keys and rate tiers. Upgrade your developer account tier for higher limits.
        </p>
      )}

      <div className="rounded-xl border border-neutral-800 p-4">
        <h3 className="font-medium">Create key</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <input
            className="rounded-lg border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm"
            placeholder="Key name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <select
            className="rounded-lg border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm"
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
          >
            <option value="production">Production (unt_live_)</option>
            <option value="sandbox">Sandbox (unt_sandbox_)</option>
          </select>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {scopeOptions.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => toggleScope(s)}
              className={`rounded px-2 py-1 text-xs ${
                selectedScopes.includes(s) ? 'bg-rose-600' : 'bg-neutral-800'
              }`}
              title={catalog?.scopes?.[s]?.description}
            >
              {s}
            </button>
          ))}
        </div>
        <button
          type="button"
          disabled={!name || create.isPending}
          onClick={() => create.mutate({ name, environment, scopes: selectedScopes })}
          className="mt-4 rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium disabled:opacity-50"
        >
          Generate key
        </button>
        {create.error && (
          <p className="mt-2 text-sm text-red-400">{create.error.message}</p>
        )}
        {secret && (
          <div className="mt-4 rounded-lg border border-amber-800/50 bg-amber-950/30 p-3 text-sm">
            <div className="text-amber-200">Copy now — shown once:</div>
            <code className="mt-1 block break-all text-amber-100">{secret}</code>
          </div>
        )}
      </div>

      <div>
        <h3 className="font-medium">Your keys</h3>
        {isLoading && <p className="text-sm text-neutral-400">Loading…</p>}
        {!isLoading && !keys.length && (
          <p className="text-sm text-neutral-400">No keys yet. Register on the overview page first.</p>
        )}
        <ul className="mt-2 space-y-2">
          {keys.map((k) => (
            <li
              key={k.id}
              className="flex items-center justify-between rounded-lg border border-neutral-800 px-4 py-3 text-sm"
            >
              <div>
                <div className="font-medium">{k.name}</div>
                <div className="text-neutral-400">
                  {k.key_prefix}… · {k.environment} · {k.rate_limit_tier} · {k.total_requests} reqs
                </div>
              </div>
              {k.is_active && (
                <button
                  type="button"
                  onClick={() => revoke.mutate(k.id)}
                  className="text-red-400 hover:underline"
                >
                  Revoke
                </button>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
