import { useQuery } from '@tanstack/react-query';
import { developerApi } from '../api/developerApi';

function Stat({ label, value }) {
  return (
    <div className="rounded-xl border border-neutral-800 p-4">
      <div className="text-xs text-neutral-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value ?? '—'}</div>
    </div>
  );
}

export default function UsagePage() {
  const { data: overview } = useQuery({
    queryKey: ['developer-usage'],
    queryFn: developerApi.usageOverview,
    retry: false,
  });

  const { data: timeseries = [] } = useQuery({
    queryKey: ['developer-usage-ts'],
    queryFn: () => developerApi.usageTimeseries(14),
    retry: false,
  });

  const { data: endpoints = [] } = useQuery({
    queryKey: ['developer-usage-endpoints'],
    queryFn: developerApi.usageEndpoints,
    retry: false,
  });

  const maxReq = Math.max(...timeseries.map((d) => d.requests || 0), 1);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Usage Analytics</h2>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Requests (24h)" value={overview?.requests_24h} />
        <Stat label="Requests (7d)" value={overview?.requests_7d} />
        <Stat label="Avg latency" value={overview?.avg_latency_ms != null ? `${overview.avg_latency_ms}ms` : null} />
        <Stat label="Error rate (24h)" value={overview?.error_rate_24h_pct != null ? `${overview.error_rate_24h_pct}%` : null} />
      </div>

      {timeseries.length > 0 && (
        <section>
          <h3 className="font-medium">Daily requests</h3>
          <div className="mt-3 flex h-32 items-end gap-1">
            {timeseries.map((d) => (
              <div
                key={d.date}
                title={`${d.date}: ${d.requests}`}
                className="flex-1 rounded-t bg-rose-600/80"
                style={{ height: `${((d.requests || 0) / maxReq) * 100}%`, minHeight: 4 }}
              />
            ))}
          </div>
        </section>
      )}

      {endpoints.length > 0 && (
        <section>
          <h3 className="font-medium">Top endpoints (7d)</h3>
          <table className="mt-2 w-full text-sm">
            <thead>
              <tr className="text-left text-neutral-500">
                <th className="py-2">Method</th>
                <th>Path</th>
                <th>Requests</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map((e) => (
                <tr key={`${e.method}-${e.path}`} className="border-t border-neutral-800">
                  <td className="py-2 font-mono text-xs">{e.method}</td>
                  <td className="font-mono text-xs">{e.path}</td>
                  <td>{e.requests}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {!overview && (
        <p className="text-sm text-neutral-400">Create API keys and make gateway requests to see usage data.</p>
      )}
    </div>
  );
}
