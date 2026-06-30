import { useState } from 'react';
import { formatBytes } from '../constants';
import { formatRelativeTime } from '../../dashboard/utils';

function isMedia(asset, type) {
  if (type === 'video') return asset.mime_type?.startsWith('video/') || asset.folder === 'videos';
  if (type === 'audio') return asset.mime_type?.startsWith('audio/') || asset.folder === 'audio';
  return asset.mime_type?.startsWith('image/') || ['images', 'thumbnails', 'posters'].includes(asset.folder);
}

export default function AssetPreviewModal({
  asset,
  versions,
  permissions,
  onClose,
  onRestoreVersion,
  onAddPermission,
  onUpdateTags,
}) {
  const [tagInput, setTagInput] = useState('');
  if (!asset) return null;
  const preview = asset.preview_url || asset.url;

  const addTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (!tag || asset.tags?.includes(tag)) return;
    onUpdateTags?.(asset.id, [...(asset.tags || []), tag]);
    setTagInput('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70" onClick={onClose}>
      <div
        className="w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-xl border dark:border-white/10 dark:bg-untold-card p-6 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold dark:text-white">{asset.title}</h3>
            <p className="text-xs dark:text-untold-muted mt-1 capitalize">
              {asset.folder} · {formatBytes(asset.size_bytes)} · {asset.cloud_provider}
            </p>
          </div>
          <button type="button" onClick={onClose} className="text-untold-muted hover:text-white">✕</button>
        </div>

        {preview && isMedia(asset, 'image') && (
          <img src={preview} alt={asset.title} className="w-full max-h-64 object-contain rounded-lg bg-black/30" />
        )}
        {preview && isMedia(asset, 'video') && (
          <video src={preview} controls className="w-full max-h-64 rounded-lg bg-black/30" />
        )}
        {preview && isMedia(asset, 'audio') && (
          <audio src={preview} controls className="w-full" />
        )}

        <div>
          <p className="text-xs font-semibold dark:text-white mb-2">Tags</p>
          <div className="flex flex-wrap gap-1 mb-2">
            {(asset.tags || []).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => onUpdateTags?.(asset.id, asset.tags.filter((x) => x !== t))}
                className="text-xs px-2 py-0.5 rounded-full bg-untold-gold/10 text-untold-gold hover:bg-red-500/20"
                title="Remove tag"
              >
                {t} ×
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              placeholder="Add tag…"
              className="flex-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-xs dark:text-white"
            />
            <button type="button" onClick={addTag} className="text-xs text-untold-gold hover:underline">Add</button>
          </div>
        </div>

        {versions?.length > 0 && (
          <div>
            <p className="text-xs font-semibold dark:text-white mb-2">Version history</p>
            <ul className="space-y-1 max-h-32 overflow-y-auto">
              {versions.map((v) => (
                <li key={v.id} className="flex justify-between text-xs dark:text-untold-muted">
                  <span>v{v.version} — {v.filename}</span>
                  <button type="button" onClick={() => onRestoreVersion(asset.id, v.id)} className="text-untold-gold hover:underline">Restore</button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <p className="text-xs font-semibold dark:text-white mb-2">Permissions</p>
          <ul className="text-xs dark:text-untold-muted space-y-1 mb-2">
            {(permissions || []).map((p) => (
              <li key={p.id}>{p.permission} — {p.role || `user #${p.user_id}`}</li>
            ))}
            {!permissions?.length && <li>No custom permissions (team defaults apply)</li>}
          </ul>
          <button
            type="button"
            onClick={() => onAddPermission(asset.id, { role: 'editor', permission: 'read' })}
            className="text-xs text-untold-gold hover:underline"
          >
            + Add editor read access
          </button>
        </div>

        <p className="text-[10px] dark:text-untold-muted">
          Uploaded {formatRelativeTime(asset.created_at)} · {asset.uploader_name || 'System'}
        </p>
      </div>
    </div>
  );
}
