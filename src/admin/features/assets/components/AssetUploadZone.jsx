export default function AssetUploadZone({ folder, onUpload, uploading, tags = '' }) {
  const targetFolder = ['all', 'favorites', 'trash'].includes(folder) ? 'images' : folder;
  return (
    <label className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed dark:border-white/15 hover:border-untold-gold/40 px-6 py-10 cursor-pointer transition-colors">
      <span className="text-2xl mb-2">⬆️</span>
      <p className="text-sm font-medium dark:text-white">{uploading ? 'Uploading…' : 'Upload assets'}</p>
      <p className="text-xs dark:text-untold-muted mt-1">Drop files or click · folder: {targetFolder}</p>
      <input
        type="file"
        multiple
        className="hidden"
        disabled={uploading}
        onChange={(e) => {
          const files = Array.from(e.target.files || []);
          files.forEach((file) => {
            const fd = new FormData();
            fd.append('file', file);
            fd.append('folder', targetFolder);
            fd.append('filename', file.name);
            if (tags) fd.append('tags', tags);
            onUpload(fd);
          });
          e.target.value = '';
        }}
      />
    </label>
  );
}
