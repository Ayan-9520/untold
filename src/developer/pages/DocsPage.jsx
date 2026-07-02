import { useEffect, useState } from 'react';
import { apiUrl } from '../../config/runtime';
import { developerApi } from '../api/developerApi';

export default function DocsPage() {
  const [docs, setDocs] = useState(null);
  const [scopes, setScopes] = useState(null);

  useEffect(() => {
    developerApi.docs().then(setDocs);
    developerApi.scopes().then(setScopes);
  }, []);

  if (!docs) return <p className="text-neutral-400">Loading documentation…</p>;

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">API Documentation</h2>

      <section>
        <h3 className="text-lg font-semibold">Authentication</h3>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-neutral-950 p-4 text-sm">
{`curl -H "X-API-Key: unt_live_YOUR_KEY" \\
  ${apiUrl('/gateway/v1/videos')}`}
        </pre>
        <p className="mt-2 text-sm text-neutral-400">
          Headers: <code className="text-rose-300">X-API-Key</code>,{' '}
          <code className="text-rose-300">Authorization: Bearer</code>,{' '}
          <code className="text-rose-300">X-API-Version</code> (v1 | v2)
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold">Versioning</h3>
        <ul className="mt-2 list-inside list-disc text-sm text-neutral-300">
          {Object.entries(docs.versions || {}).map(([ver, meta]) => (
            <li key={ver}>
              <strong>{ver}</strong> — {meta.status}, base {meta.base_path}
              {meta.envelope ? ' (envelope responses)' : ''}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold">GraphQL</h3>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-neutral-950 p-4 text-sm">
{`POST /gateway/graphql
{
  videos(page: 1, page_size: 10) {
    total
    items { id title views_count }
  }
}`}
        </pre>
      </section>

      <section>
        <h3 className="text-lg font-semibold">Webhooks</h3>
        <p className="text-sm text-neutral-400">Events are signed with HMAC-SHA256 using your signing secret.</p>
        <ul className="mt-2 flex flex-wrap gap-2">
          {(scopes?.webhook_events || docs.webhook_events || []).map((ev) => (
            <span key={ev} className="rounded bg-neutral-800 px-2 py-1 text-xs">
              {ev}
            </span>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold">Rate limits</h3>
        <div className="mt-2 grid gap-2 sm:grid-cols-3">
          {Object.entries(scopes?.rate_limit_tiers || docs.rate_limit_tiers || {}).map(([tier, meta]) => (
            <div key={tier} className="rounded-lg border border-neutral-800 p-3 text-sm">
              <div className="font-medium capitalize">{tier}</div>
              <div className="text-neutral-400">{meta.limit}</div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3 className="text-lg font-semibold">SDK</h3>
        <pre className="mt-2 rounded-lg bg-neutral-950 p-4 text-sm">
{`import { UntoldClient } from '@untold/developer-sdk';

const client = new UntoldClient({
  apiKey: 'unt_live_...',
  environment: 'production',
  version: 'v2',
});

const { items } = await client.videos.list({ page: 1 });
const data = await client.graphql(\`{ me { email scopes } }\`);`}
        </pre>
      </section>

      <section>
        <h3 className="text-lg font-semibold">OpenAPI</h3>
        <a
          href="/gateway/openapi.json"
          target="_blank"
          rel="noreferrer"
          className="text-rose-400 hover:underline"
        >
          /gateway/openapi.json
        </a>
        {' · '}
        <a href="/gateway/docs" target="_blank" rel="noreferrer" className="text-rose-400 hover:underline">
          Swagger UI
        </a>
      </section>
    </div>
  );
}
