function fmtNum(n) {
  if (n == null) return '—';
  return Number(n).toLocaleString();
}

function fmtCost(n) {
  if (n == null) return '—';
  return `$${Number(n).toFixed(4)}`;
}

function fmtLatency(ms) {
  if (ms == null) return '—';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function approvalClass(status) {
  if (status === 'approved') return 'text-emerald-400';
  if (status === 'pending') return 'text-amber-400';
  if (status === 'rejected') return 'text-red-400';
  return 'dark:text-untold-muted';
}

export default function AITelemetryTable({ data, loading }) {
  const items = data?.items || [];
  const totals = data?.totals;

  if (loading) return <div className="h-48 skeleton rounded-xl" />;

  if (!items.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-12">No generation telemetry yet.</p>;
  }

  return (
    <div className="space-y-4">
      {totals && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
          {[
            { label: 'Input tokens', value: fmtNum(totals.input_tokens) },
            { label: 'Output tokens', value: fmtNum(totals.output_tokens) },
            { label: 'Cost', value: fmtCost(totals.cost_usd) },
            { label: 'Failures', value: totals.failures },
            { label: 'Retries', value: totals.retries },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border dark:border-white/10 px-3 py-2 text-center">
              <p className="text-sm font-semibold text-untold-gold">{s.value}</p>
              <p className="text-[10px] dark:text-untold-muted mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border dark:border-white/10">
        <table className="w-full text-xs min-w-[1200px]">
          <thead>
            <tr className="border-b dark:border-white/10 dark:bg-black/30">
              {[
                'Prompt',
                'Model',
                'Provider',
                'Input Tokens',
                'Output Tokens',
                'Latency',
                'Cost',
                'Failures',
                'Retries',
                'Approval',
                'Version',
                'Temperature',
                'Project',
                'User',
              ].map((h) => (
                <th key={h} className="px-3 py-2 text-left font-semibold dark:text-untold-muted whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.id} className="border-b dark:border-white/5 hover:bg-white/[0.02]">
                <td className="px-3 py-2 max-w-[200px]">
                  <p className="truncate dark:text-white" title={row.prompt}>{row.prompt}</p>
                  <p className="text-[10px] dark:text-untold-muted capitalize">{row.module} · {row.status}</p>
                </td>
                <td className="px-3 py-2 font-mono dark:text-untold-muted whitespace-nowrap">{row.model || '—'}</td>
                <td className="px-3 py-2 dark:text-untold-muted whitespace-nowrap">{row.provider}</td>
                <td className="px-3 py-2 text-right tabular-nums">{fmtNum(row.input_tokens)}</td>
                <td className="px-3 py-2 text-right tabular-nums">{fmtNum(row.output_tokens)}</td>
                <td className="px-3 py-2 text-right tabular-nums whitespace-nowrap">{fmtLatency(row.latency_ms)}</td>
                <td className="px-3 py-2 text-right tabular-nums whitespace-nowrap">{fmtCost(row.cost_usd)}</td>
                <td className="px-3 py-2 text-center tabular-nums">{row.failure_count || 0}</td>
                <td className="px-3 py-2 text-center tabular-nums">{row.retries ?? row.retry_count ?? 0}</td>
                <td className={`px-3 py-2 capitalize whitespace-nowrap ${approvalClass(row.approval_status)}`}>
                  {row.approval_status || 'none'}
                </td>
                <td className="px-3 py-2 dark:text-untold-muted whitespace-nowrap">{row.prompt_version || '—'}</td>
                <td className="px-3 py-2 text-right tabular-nums">{row.temperature ?? '—'}</td>
                <td className="px-3 py-2 dark:text-untold-muted max-w-[120px] truncate" title={row.project_title}>
                  {row.project_title || (row.project_id ? `#${row.project_id}` : '—')}
                </td>
                <td className="px-3 py-2 dark:text-untold-muted whitespace-nowrap">{row.author_name || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
