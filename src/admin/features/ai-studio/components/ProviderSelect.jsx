export default function ProviderSelect({ providers, value, onChange, moduleId }) {
  const available = (providers || []).filter(
    (p) => p.available && (p.modules.includes('*') || p.modules.includes(moduleId)),
  );
  if (!available.length) {
    return <p className="text-xs dark:text-untold-muted">No providers available for this module.</p>;
  }
  return (
    <select
      value={value || ''}
      onChange={(e) => onChange(e.target.value || null)}
      className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
    >
      <option value="">Auto-select provider</option>
      {available.map((p) => (
        <option key={p.id} value={p.id}>{p.label}</option>
      ))}
    </select>
  );
}
