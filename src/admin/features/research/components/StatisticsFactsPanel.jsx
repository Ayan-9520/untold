export default function StatisticsFactsPanel({ statistics, publicFacts }) {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div>
        <h3 className="text-xs font-semibold dark:text-white mb-3">Statistics</h3>
        {!statistics?.length ? (
          <p className="text-xs dark:text-untold-muted">Run AI agent → Statistics to populate</p>
        ) : (
          <ul className="space-y-2">
            {statistics.map((s, i) => (
              <li key={i} className="rounded-lg border dark:border-white/10 px-3 py-2 text-sm">
                <p className="dark:text-white font-medium">{s.label}: <span className="text-untold-gold">{s.value}</span></p>
                <p className="text-[10px] dark:text-untold-muted mt-0.5">{s.source} · {Math.round((s.confidence || 0) * 100)}% confidence</p>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <h3 className="text-xs font-semibold dark:text-white mb-3">Publicly available facts</h3>
        {!publicFacts?.length ? (
          <p className="text-xs dark:text-untold-muted">Run AI agent → Public facts to populate</p>
        ) : (
          <ul className="space-y-2">
            {publicFacts.map((f, i) => (
              <li key={i} className="rounded-lg border dark:border-white/10 px-3 py-2 text-sm">
                <p className="dark:text-white">{f.fact}</p>
                <p className="text-[10px] dark:text-untold-muted mt-1">{f.source} · {f.verified ? '✓ verified' : 'needs check'}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
