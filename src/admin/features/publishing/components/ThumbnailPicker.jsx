export default function ThumbnailPicker({ url, onChange }) {
  return (
    <div className="space-y-2">
      <label className="text-xs dark:text-untold-muted block">Thumbnail</label>
      <div className="flex gap-3 items-start">
        <div className="w-32 aspect-video rounded-lg border dark:border-white/10 bg-black/40 overflow-hidden shrink-0">
          {url ? (
            <img src={url} alt="Thumbnail" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-2xl opacity-40">🖼️</div>
          )}
        </div>
        <input
          value={url || ''}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-xs dark:text-white"
          placeholder="https://… thumbnail URL"
        />
      </div>
    </div>
  );
}
