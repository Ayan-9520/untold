import { formatBytes } from '../constants';

function isImage(asset) {
  return asset.mime_type?.startsWith('image/') || asset.folder === 'images' || asset.folder === 'thumbnails' || asset.folder === 'posters';
}

export default function AssetCard({ asset, onPreview, onFavorite, onDelete, onRestore, trash }) {
  const thumb = asset.preview_url || asset.url;

  return (
    <article className="group rounded-xl border dark:border-white/10 overflow-hidden dark:bg-untold-card/40 hover:border-untold-gold/30 transition-colors">
      <button type="button" onClick={() => onPreview(asset)} className="block w-full aspect-video bg-black/40 relative">
        {isImage(asset) && thumb ? (
          <img src={thumb} alt={asset.title} className="w-full h-full object-cover" />
        ) : (
          <div className="flex items-center justify-center h-full text-3xl opacity-60">
            {asset.folder === 'videos' ? '🎬' : asset.folder === 'audio' ? '🎵' : '📄'}
          </div>
        )}
        {asset.is_favorite && <span className="absolute top-2 right-2 text-sm">⭐</span>}
      </button>
      <div className="p-3 space-y-2">
        <p className="text-sm font-medium dark:text-white truncate">{asset.title}</p>
        <p className="text-[10px] dark:text-untold-muted">{formatBytes(asset.size_bytes)} · v{asset.version}</p>
        {asset.tags?.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {asset.tags.slice(0, 3).map((t) => (
              <span key={t} className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 dark:text-untold-muted">{t}</span>
            ))}
          </div>
        )}
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {!trash && (
            <button type="button" onClick={() => onFavorite(asset.id)} className="text-[10px] text-untold-gold hover:underline">
              {asset.is_favorite ? 'Unfavorite' : 'Favorite'}
            </button>
          )}
          {trash ? (
            <button type="button" onClick={() => onRestore(asset.id)} className="text-[10px] text-emerald-400 hover:underline">Restore</button>
          ) : (
            <button type="button" onClick={() => onDelete(asset.id)} className="text-[10px] text-red-400 hover:underline">Delete</button>
          )}
        </div>
      </div>
    </article>
  );
}
