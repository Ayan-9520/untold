import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { developerApi } from '../api/developerApi';

export default function WebhooksPage() {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [events, setEvents] = useState(['video.updated']);
  const [signingSecret, setSigningSecret] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const queryClient = useQueryClient();

  const { data: catalog } = useQuery({
    queryKey: ['developer-scopes'],
    queryFn: developerApi.scopes,
    staleTime: 300_000,
  });

  const eventOptions = catalog?.webhook_events || ['video.updated', 'api_key.used'];

  const { data: webhooks = [] } = useQuery({
    queryKey: ['developer-webhooks'],
    queryFn: developerApi.listWebhooks,
    retry: false,
  });

  const { data: deliveries = [], isFetching: deliveriesLoading } = useQuery({
    queryKey: ['developer-webhook-deliveries', expandedId],
    queryFn: () => developerApi.webhookDeliveries(expandedId),
    enabled: expandedId != null,
  });

  const create = useMutation({
    mutationFn: (body) => developerApi.createWebhook(body),
    onSuccess: (res) => {
      setSigningSecret(res.signing_secret);
      setName('');
      setUrl('');
      queryClient.invalidateQueries({ queryKey: ['developer-webhooks'] });
    },
  });

  const remove = useMutation({
    mutationFn: (id) => developerApi.deleteWebhook(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['developer-webhooks'] }),
  });

  const test = useMutation({
    mutationFn: (id) => developerApi.testWebhook(id),
    onSuccess: (res) => {
      setTestResult(res);
      if (expandedId) {
        queryClient.invalidateQueries({ queryKey: ['developer-webhook-deliveries', expandedId] });
      }
    },
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Webhooks</h2>
      <p className="text-sm text-neutral-400">
        Receive signed HTTP POST callbacks when events occur in UNTOLD. Production endpoints must use HTTPS.
      </p>

      <div className="rounded-xl border border-neutral-800 p-4">
        <input
          className="mb-2 w-full rounded-lg border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm"
          placeholder="Webhook name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="mb-2 w-full rounded-lg border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm"
          placeholder="https://your-app.com/webhooks/untold"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          {eventOptions.map((ev) => (
            <button
              key={ev}
              type="button"
              onClick={() =>
                setEvents((prev) => (prev.includes(ev) ? prev.filter((e) => e !== ev) : [...prev, ev]))
              }
              className={`rounded px-2 py-1 text-xs ${events.includes(ev) ? 'bg-rose-600' : 'bg-neutral-800'}`}
            >
              {ev}
            </button>
          ))}
        </div>
        <button
          type="button"
          disabled={!name || !url || !events.length}
          onClick={() => create.mutate({ name, url, events })}
          className="mt-3 rounded-lg bg-rose-600 px-4 py-2 text-sm"
        >
          Add webhook
        </button>
        {create.error && <p className="mt-2 text-sm text-red-400">{create.error.message}</p>}
        {signingSecret && (
          <div className="mt-3 rounded-lg border border-amber-800/50 bg-amber-950/30 p-3 text-sm">
            Signing secret: <code className="break-all">{signingSecret}</code>
          </div>
        )}
      </div>

      {testResult && (
        <div className="rounded-lg border border-neutral-700 bg-neutral-900/50 p-3 text-xs">
          <div className="font-medium text-neutral-300">Last test delivery</div>
          <pre className="mt-2 overflow-auto text-neutral-400">{JSON.stringify(testResult, null, 2)}</pre>
        </div>
      )}

      <ul className="space-y-2">
        {webhooks.map((w) => (
          <li key={w.id} className="rounded-lg border border-neutral-800 p-4 text-sm">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">{w.name}</div>
                <div className="text-neutral-400">{w.url}</div>
                <div className="mt-1 text-xs text-neutral-500">{(w.events || []).join(', ')}</div>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setExpandedId(expandedId === w.id ? null : w.id);
                    setTestResult(null);
                  }}
                  className="text-neutral-400 hover:text-white"
                >
                  {expandedId === w.id ? 'Hide' : 'Deliveries'}
                </button>
                <button type="button" onClick={() => test.mutate(w.id)} className="text-rose-400">
                  Test
                </button>
                <button type="button" onClick={() => remove.mutate(w.id)} className="text-red-400">
                  Delete
                </button>
              </div>
            </div>
            {expandedId === w.id && (
              <div className="mt-3 border-t border-neutral-800 pt-3">
                {deliveriesLoading && <p className="text-xs text-neutral-500">Loading deliveries…</p>}
                {!deliveriesLoading && !deliveries.length && (
                  <p className="text-xs text-neutral-500">No deliveries yet.</p>
                )}
                <ul className="space-y-1">
                  {deliveries.map((d) => (
                    <li key={d.id} className="flex justify-between text-xs text-neutral-400">
                      <span>{d.event_type}</span>
                      <span>
                        {d.status} · HTTP {d.http_status ?? '—'} · {d.attempts} attempt(s)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
