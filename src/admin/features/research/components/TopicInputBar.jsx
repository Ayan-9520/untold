export default function TopicInputBar({ topic, status, onSave }) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl border dark:border-white/10 p-3 dark:bg-black/20">
      <label className="text-xs dark:text-untold-muted shrink-0">Research topic</label>
      <input
        defaultValue={topic}
        onBlur={(e) => {
          if (e.target.value.trim() && e.target.value !== topic) onSave(e.target.value.trim());
        }}
        className="flex-1 min-w-[200px] rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white font-medium"
      />
      <span className={`text-[10px] uppercase px-2 py-0.5 rounded-full border ${
        status === 'approved' ? 'border-emerald-500/40 text-emerald-400'
          : status === 'pending_approval' ? 'border-yellow-500/40 text-yellow-400'
            : status === 'rejected' ? 'border-red-500/40 text-red-400'
              : 'border-white/10 dark:text-untold-muted'
      }`}>
        {status?.replace('_', ' ') || 'active'}
      </span>
    </div>
  );
}
