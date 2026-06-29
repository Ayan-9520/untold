export default function StatCard({ title, value, change, icon: Icon, accent = 'gold' }) {
  const accents = {
    gold: 'bg-untold-gold/10 text-untold-gold',
    blue: 'bg-blue-500/10 text-blue-400',
    green: 'bg-emerald-500/10 text-emerald-400',
    purple: 'bg-purple-500/10 text-purple-400',
  };

  return (
    <div className="rounded-xl p-5 dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200 card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider dark:text-untold-muted light:text-gray-500">
            {title}
          </p>
          <p className="mt-2 text-2xl sm:text-3xl font-bold dark:text-untold-white light:text-black">
            {value}
          </p>
          {change !== undefined && (
            <p className={`mt-1 text-xs font-medium ${change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {change >= 0 ? '+' : ''}{change}% vs last month
            </p>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${accents[accent]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  );
}
