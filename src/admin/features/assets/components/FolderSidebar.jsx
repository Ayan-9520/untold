import { ASSET_FOLDERS } from '../constants';

export default function FolderSidebar({ active, counts, onSelect, favoritesCount, trashCount }) {
  return (
    <nav className="space-y-1">
      {ASSET_FOLDERS.map((f) => (
        <button
          key={f.id}
          type="button"
          onClick={() => onSelect(f.id)}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
            active === f.id ? 'bg-untold-gold/15 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'
          }`}
        >
          <span><span className="mr-2">{f.icon}</span>{f.label}</span>
          <span className="text-xs opacity-70">{counts?.[f.id] ?? 0}</span>
        </button>
      ))}
      <div className="pt-3 mt-3 border-t dark:border-white/10 space-y-1">
        <button
          type="button"
          onClick={() => onSelect('favorites')}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm ${
            active === 'favorites' ? 'bg-untold-gold/15 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'
          }`}
        >
          <span>⭐ Favorites</span>
          <span className="text-xs">{favoritesCount}</span>
        </button>
        <button
          type="button"
          onClick={() => onSelect('trash')}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm ${
            active === 'trash' ? 'bg-untold-gold/15 text-untold-gold' : 'dark:text-untold-muted hover:bg-white/5'
          }`}
        >
          <span>🗑️ Trash</span>
          <span className="text-xs">{trashCount}</span>
        </button>
      </div>
    </nav>
  );
}
