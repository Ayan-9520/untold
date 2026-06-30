export default function CollaboratorAvatars({ collaborators = [], className = '' }) {
  if (!collaborators.length) return null;
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-[10px] uppercase tracking-wider dark:text-untold-muted">Editing</span>
      <div className="flex -space-x-2">
        {collaborators.slice(0, 5).map((c) => (
          <span
            key={c.user_id}
            title={c.name}
            className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-untold-gold/20 text-[10px] font-semibold text-untold-gold border-2 border-untold-card"
          >
            {(c.name || '?').slice(0, 2).toUpperCase()}
          </span>
        ))}
      </div>
    </div>
  );
}
