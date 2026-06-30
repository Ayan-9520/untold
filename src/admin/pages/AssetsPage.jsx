import { useState } from 'react';
import StudioPageHeader from '../components/StudioPageHeader';
import StudioLiveBadge from '../components/StudioLiveBadge';
import FolderSidebar from '../features/assets/components/FolderSidebar';
import AssetCard from '../features/assets/components/AssetCard';
import AssetUploadZone from '../features/assets/components/AssetUploadZone';
import AssetPreviewModal from '../features/assets/components/AssetPreviewModal';
import {
  useAssetsOverview,
  useAssetsList,
  useAssetCollections,
  useAssetMutations,
  useAssetVersions,
  useAssetPermissions,
} from '../features/assets/hooks/useAssets';
import { formatBytes } from '../features/assets/constants';

export default function AssetsPage() {
  const [folder, setFolder] = useState('all');
  const [search, setSearch] = useState('');
  const [tagFilter, setTagFilter] = useState('');
  const [collectionId, setCollectionId] = useState(null);
  const [preview, setPreview] = useState(null);
  const [newCollection, setNewCollection] = useState('');

  const listParams = {
    folder: folder === 'all' || folder === 'favorites' || folder === 'trash' ? undefined : folder,
    search: search || undefined,
    tags: tagFilter || undefined,
    collection_id: collectionId || undefined,
    favorites_only: folder === 'favorites',
    trash: folder === 'trash',
  };

  const { data: overview, isError } = useAssetsOverview();
  const { data: list, isLoading } = useAssetsList(listParams);
  const { data: collections } = useAssetCollections();
  const mutations = useAssetMutations();
  const { data: versions } = useAssetVersions(preview?.id);
  const { data: permissions } = useAssetPermissions(preview?.id);

  const counts = overview?.folder_counts || {};
  const allCount = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      <StudioPageHeader
        section="Asset Library"
        title="Asset Library"
        description="Images, footage, audio, documents, thumbnails & posters — cloud-ready with versions & permissions."
      >
        <StudioLiveBadge live={!isError} />
      </StudioPageHeader>

      {overview && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Total assets', value: overview.total_assets },
              { label: 'Storage', value: formatBytes(overview.total_bytes) },
              { label: 'Collections', value: overview.collections_count },
              { label: 'Favorites', value: overview.favorites_count },
            ].map((s) => (
              <div key={s.label} className="ai-stat-card text-center">
                <p className="text-xl font-bold text-untold-gold">{s.value}</p>
                <p className="text-xs dark:text-untold-muted mt-1">{s.label}</p>
              </div>
            ))}
          </div>
          {overview.storage_providers?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {overview.storage_providers.map((p) => (
                <span
                  key={p.id}
                  className={`text-xs px-2 py-1 rounded-full border ${
                    p.available ? 'border-emerald-500/40 text-emerald-400' : 'border-white/10 dark:text-untold-muted'
                  }`}
                >
                  ☁ {p.label}{p.available ? '' : ' (configure)'}
                </span>
              ))}
            </div>
          )}
        </>
      )}

      <div className="grid lg:grid-cols-[200px_1fr] gap-6">
        <FolderSidebar
          active={folder}
          counts={{ all: allCount, ...counts }}
          favoritesCount={overview?.favorites_count ?? 0}
          trashCount={overview?.trash_count ?? 0}
          onSelect={setFolder}
        />

        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search assets…"
              className="flex-1 min-w-[200px] rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
            />
            <input
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
              placeholder="Filter by tag…"
              className="w-40 rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
            />
          </div>

          {folder !== 'trash' && (
            <AssetUploadZone
              folder={folder}
              uploading={mutations.upload.isPending}
              onUpload={(fd) => mutations.upload.mutate(fd)}
            />
          )}

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setCollectionId(null)}
              className={`text-xs px-2 py-1 rounded-full border ${
                !collectionId ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
              }`}
            >
              All collections
            </button>
            {(collections || []).map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setCollectionId(c.id)}
                className={`text-xs px-2 py-1 rounded-full border ${
                  collectionId === c.id ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
                }`}
              >
                {c.name} ({c.asset_count})
              </button>
            ))}
            <input
              value={newCollection}
              onChange={(e) => setNewCollection(e.target.value)}
              placeholder="New collection…"
              className="w-36 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1 text-xs dark:text-white"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && newCollection.trim()) {
                  mutations.createCollection.mutate(
                    { name: newCollection.trim() },
                    { onSuccess: () => setNewCollection('') },
                  );
                }
              }}
            />
            <button
              type="button"
              disabled={!newCollection.trim() || mutations.createCollection.isPending}
              onClick={() => mutations.createCollection.mutate(
                { name: newCollection.trim() },
                { onSuccess: () => setNewCollection('') },
              )}
              className="text-xs text-untold-gold hover:underline disabled:opacity-40"
            >
              + Create
            </button>
          </div>

          {isLoading ? (
            <div className="h-48 skeleton rounded-xl" />
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-4">
              {(list?.items || []).map((asset) => (
                <AssetCard
                  key={asset.id}
                  asset={asset}
                  trash={folder === 'trash'}
                  onPreview={setPreview}
                  onFavorite={(id) => mutations.toggleFavorite.mutate(id)}
                  onDelete={(id) => mutations.remove.mutate(id)}
                  onRestore={(id) => mutations.restore.mutate(id)}
                />
              ))}
            </div>
          )}

          {!isLoading && !list?.items?.length && (
            <p className="text-sm dark:text-untold-muted text-center py-8">No assets in this folder.</p>
          )}
        </div>
      </div>

      <AssetPreviewModal
        asset={preview}
        versions={versions}
        permissions={permissions}
        onClose={() => setPreview(null)}
        onRestoreVersion={(assetId, versionId) => mutations.restoreVersion.mutate({ assetId, versionId })}
        onAddPermission={(assetId, data) => mutations.addPermission.mutate({ assetId, data })}
        onUpdateTags={(id, tags) => mutations.update.mutate(
          { id, data: { tags } },
          { onSuccess: (updated) => setPreview(updated) },
        )}
      />
    </div>
  );
}
