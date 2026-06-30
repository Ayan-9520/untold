import JobStatusBadge from '../../ai-studio/components/JobStatusBadge';
import { JOB_STATUS_STYLES, APPROVAL_STYLES } from '../constants';

function ProgressBar({ progress, stage }) {
  const pct = Math.min(100, Math.max(0, progress || 0));
  return (
    <div className="space-y-1">
      <div className="h-1.5 rounded-full bg-black/40 overflow-hidden">
        <div className="h-full bg-untold-gold transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      {stage && (
        <p className="text-[10px] dark:text-untold-muted capitalize">
          {stage.replace(/_/g, ' ')} · {pct}%
        </p>
      )}
    </div>
  );
}

function langLabel(code, languages) {
  return languages?.find((l) => l.code === code)?.label || code?.toUpperCase();
}

export function TranslationHistoryPanel({ jobs, mutations, languages }) {
  if (!jobs?.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No translations yet</p>;
  }

  const downloadBlob = (content, filename, mime) => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {jobs.map((job) => {
        const statusClass = JOB_STATUS_STYLES[job.status] || JOB_STATUS_STYLES.queued;
        const approvalClass = APPROVAL_STYLES[job.approval_status] || APPROVAL_STYLES.none;

        return (
          <article
            key={job.id}
            className={`rounded-xl border p-4 space-y-3 ${statusClass.split(' ').slice(1).join(' ') || 'dark:border-white/10'}`}
          >
            <div className="flex justify-between gap-2">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium dark:text-white capitalize">{job.content_type}</p>
                <p className="text-[10px] dark:text-untold-muted">
                  {langLabel(job.source_lang, languages)} → {langLabel(job.target_lang, languages)}
                  {job.tm_hit ? ' · TM hit' : ''}
                  {job.auto_sync ? ' · Auto-sync' : ''}
                </p>
                <p className="text-xs dark:text-untold-muted mt-1 line-clamp-2">{job.source_text}</p>
              </div>
              <div className="text-right space-y-1 shrink-0">
                <JobStatusBadge status={job.status} />
                <p className={`text-[10px] capitalize ${approvalClass}`}>Approval: {job.approval_status}</p>
              </div>
            </div>

            {job.status === 'completed' && job.translated_text && (
              <div className="rounded-lg dark:bg-black/30 p-3 text-xs dark:text-white whitespace-pre-wrap font-mono max-h-40 overflow-y-auto">
                {job.translated_text}
              </div>
            )}

            {job.status === 'completed' && (
              <div className="flex flex-wrap gap-2 text-[10px]">
                {(job.srt_content || job.srt_url) && (
                  <button
                    type="button"
                    onClick={() => {
                      if (job.srt_content) {
                        downloadBlob(job.srt_content, `translation-${job.id}.srt`, 'text/plain');
                      } else {
                        window.open(mutations.getSrtUrl(job.id), '_blank');
                      }
                    }}
                    className="text-untold-gold hover:underline"
                  >
                    Download SRT
                  </button>
                )}
                {(job.vtt_content || job.vtt_url) && (
                  <button
                    type="button"
                    onClick={() => {
                      if (job.vtt_content) {
                        downloadBlob(job.vtt_content, `translation-${job.id}.vtt`, 'text/vtt');
                      } else {
                        window.open(mutations.getVttUrl(job.id), '_blank');
                      }
                    }}
                    className="text-untold-gold hover:underline"
                  >
                    Download VTT
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => mutations.requestApproval.mutate({ id: job.id, data: { project_id: job.project_id } })}
                  className="text-untold-gold hover:underline"
                >
                  Request approval
                </button>
                <button
                  type="button"
                  onClick={() => mutations.approve.mutate({ id: job.id, data: {} })}
                  className="text-emerald-400 hover:underline"
                >
                  Approve
                </button>
                <button
                  type="button"
                  onClick={() => mutations.reject.mutate({ id: job.id, data: {} })}
                  className="text-red-400 hover:underline"
                >
                  Reject
                </button>
              </div>
            )}

            {(job.status === 'failed' || job.status === 'cancelled') && (
              <button
                type="button"
                onClick={() => mutations.retryJob.mutate(job.id)}
                className="text-[10px] text-untold-gold hover:underline"
              >
                Retry
              </button>
            )}
          </article>
        );
      })}
    </div>
  );
}

export function TranslationQueuePanel({ queue, mutations }) {
  const items = [...(queue?.queued || []), ...(queue?.running || [])];
  if (!items.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">Queue is empty</p>;
  }

  return (
    <div className="space-y-4">
      {items.map((job) => (
        <div key={job.id} className="rounded-lg border dark:border-white/10 p-4 space-y-2">
          <div className="flex justify-between items-center">
            <p className="text-sm dark:text-white capitalize">{job.content_type}</p>
            <JobStatusBadge status={job.status} />
          </div>
          <p className="text-[10px] dark:text-untold-muted">
            {job.source_lang} → {job.target_lang}
          </p>
          <ProgressBar progress={job.progress} stage={job.stage} />
          {job.status === 'queued' && (
            <button
              type="button"
              onClick={() => mutations.cancelJob.mutate(job.id)}
              className="text-[10px] text-red-400 hover:underline"
            >
              Cancel
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

export function TranslationMemoryPanel({ memory, mutations, languages }) {
  const items = memory?.items || [];
  if (!items.length) {
    return (
      <p className="text-sm dark:text-untold-muted text-center py-8">
        Translation memory is empty — completed jobs will populate matches automatically.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((entry) => (
        <div key={entry.id} className="rounded-lg border dark:border-white/10 p-3 text-xs space-y-2">
          <div className="flex justify-between gap-2">
            <span className="dark:text-untold-muted capitalize">
              {entry.content_type} · {langLabel(entry.source_lang, languages)} → {langLabel(entry.target_lang, languages)}
            </span>
            <span className="text-untold-gold">{entry.usage_count}× used</span>
          </div>
          <p className="dark:text-white line-clamp-2">{entry.source_text}</p>
          <p className="dark:text-untold-muted line-clamp-2">{entry.translated_text}</p>
          <button
            type="button"
            onClick={() => mutations.deleteMemory.mutate(entry.id)}
            className="text-[10px] text-red-400 hover:underline"
          >
            Remove from memory
          </button>
        </div>
      ))}
    </div>
  );
}
