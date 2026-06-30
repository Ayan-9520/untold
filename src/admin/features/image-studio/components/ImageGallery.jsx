import JobStatusBadge from '../../ai-studio/components/JobStatusBadge';
import { JOB_STATUS_STYLES } from '../constants';

function ImageCard({ job, onFavorite, onUpscale, onVary, onSave, onDownload, collections, onAddToCollection }) {
  const statusClass = JOB_STATUS_STYLES[job.status] || JOB_STATUS_STYLES.queued;

  return (
    <article className={`rounded-xl border p-3 space-y-3 ${statusClass.split(' ').slice(1).join(' ') || 'dark:border-white/10'}`}>
      {job.result_url && job.status === 'completed' ? (
        <img src={job.result_url} alt={job.prompt} className="w-full rounded-lg border dark:border-white/10 max-h-48 object-contain bg-black/40" />
      ) : (
        <div className="h-32 rounded-lg border dark:border-white/10 bg-black/30 flex items-center justify-center text-xs dark:text-untold-muted">
          {job.status === 'failed' ? job.error?.slice(0, 120) : job.status}
        </div>
      )}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs font-medium dark:text-white capitalize">{job.image_type?.replace('_', ' ')}</p>
          <p className="text-[10px] dark:text-untold-muted line-clamp-2 mt-0.5">{job.prompt}</p>
        </div>
        <JobStatusBadge status={job.status} />
      </div>
      <div className="flex flex-wrap gap-2 text-[10px]">
        <button type="button" onClick={() => onFavorite(job.id)} className="text-untold-gold hover:underline">
          {job.is_favorite ? '★ Favorited' : '☆ Favorite'}
        </button>
        {job.status === 'completed' && (
          <>
            <button type="button" onClick={() => onUpscale(job.id)} className="text-untold-gold hover:underline">Upscale</button>
            <button type="button" onClick={() => onVary(job.id)} className="text-untold-gold hover:underline">Variation</button>
            <button type="button" onClick={() => onSave(job.id)} className="text-untold-gold hover:underline">Save to assets</button>
            <a href={onDownload(job.id)} target="_blank" rel="noreferrer" className="text-untold-gold hover:underline">Download</a>
          </>
        )}
        {collections?.length > 0 && job.status === 'completed' && (
          <select
            className="text-[10px] rounded border dark:border-white/10 dark:bg-black/30 px-1 py-0.5 dark:text-white"
            defaultValue=""
            onChange={(e) => {
              if (e.target.value) onAddToCollection(Number(e.target.value), job.id);
              e.target.value = '';
            }}
          >
            <option value="">+ Collection</option>
            {collections.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        )}
      </div>
    </article>
  );
}

export function ImageGallery({ jobs, collections, mutations, getDownloadUrl }) {
  if (!jobs?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No images yet</p>;
  }
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {jobs.map((job) => (
        <ImageCard
          key={job.id}
          job={job}
          collections={collections}
          onFavorite={(id) => mutations.toggleFavorite.mutate(id)}
          onUpscale={(id) => mutations.upscale.mutate(id)}
          onVary={(id) => mutations.vary.mutate({ id })}
          onSave={(id) => mutations.saveToAsset.mutate(id)}
          onDownload={getDownloadUrl}
          onAddToCollection={(colId, genId) => mutations.addToCollection.mutate({ collectionId: colId, generationId: genId })}
        />
      ))}
    </div>
  );
}

export function ImageQueuePanel({ queue, mutations }) {
  const items = [...(queue?.queued || []), ...(queue?.running || [])];
  if (!items.length) return <p className="text-sm dark:text-untold-muted">Queue empty</p>;
  return (
    <ul className="space-y-2">
      {items.map((j) => (
        <li key={j.id} className="flex justify-between gap-2 text-xs rounded-lg border dark:border-white/10 px-3 py-2">
          <span className="dark:text-untold-muted truncate flex-1">{j.prompt}</span>
          <JobStatusBadge status={j.status} />
          {(j.status === 'queued' || j.status === 'running') && (
            <button type="button" onClick={() => mutations.cancelJob.mutate(j.id)} className="text-red-400 shrink-0">Cancel</button>
          )}
        </li>
      ))}
    </ul>
  );
}
