const ACCENTS = {
  gold: 'bg-untold-gold/10 text-untold-gold border-untold-gold/20',
  blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
};

export default function StatCard({ label, value, icon: Icon, hint, accent = 'gold', className = '' }) {
  return (
    <div
      className={`studio-card p-5 card-hover ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider studio-muted">
            {label}
          </p>
          <p className="mt-2 text-2xl sm:text-3xl font-bold text-untold-gold tabular-nums">
            {value}
          </p>
          {hint && (
            <p className="mt-1 text-[10px] studio-muted">{hint}</p>
          )}
        </div>
        {Icon && (
          <div className={`shrink-0 p-2.5 rounded-lg border ${ACCENTS[accent] || ACCENTS.gold}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
    </div>
  );
}
