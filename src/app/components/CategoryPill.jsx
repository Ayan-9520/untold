export default function CategoryPill({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`shrink-0 px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-200
        active:scale-95
        ${active
          ? 'bg-untold-gold text-untold-dark'
          : 'dark:bg-white/8 light:bg-black/5 dark:text-untold-muted light:text-gray-500'
        }`}
    >
      {label}
    </button>
  );
}
