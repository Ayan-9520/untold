import { JOB_STATUS_COLORS, formatPlatform } from '../constants';
import { formatRelativeTime } from '../../dashboard/utils';

export default function PublishingQueueTable({ jobs, onApprove, onReject, onRetry, compact }) {
  if (!jobs?.length) {
    return <p className="text-xs dark:text-untold-muted text-center py-6">Queue is empty</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="dark:text-untold-muted border-b dark:border-white/10">
            <th className="text-left py-2 pr-3 font-medium">Project</th>
            <th className="text-left py-2 pr-3 font-medium">Platform</th>
            <th className="text-left py-2 pr-3 font-medium">Status</th>
            {!compact && <th className="text-left py-2 pr-3 font-medium">SEO</th>}
            <th className="text-left py-2 pr-3 font-medium">Scheduled</th>
            <th className="text-right py-2 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id} className="border-b dark:border-white/5 hover:bg-white/[0.02]">
              <td className="py-2.5 pr-3 dark:text-white max-w-[140px] truncate">{job.project_title}</td>
              <td className="py-2.5 pr-3 capitalize">{formatPlatform(job.platform)}</td>
              <td className="py-2.5 pr-3">
                <span className={JOB_STATUS_COLORS[job.status] || ''}>{job.status.replace('_', ' ')}</span>
                {job.approval_status === 'pending' && (
                  <span className="ml-1 text-yellow-500">· approval</span>
                )}
                {job.error_message && (
                  <p className="text-[10px] text-red-400 mt-0.5 truncate max-w-[160px]" title={job.error_message}>
                    {job.error_message}
                  </p>
                )}
              </td>
              {!compact && (
                <td className="py-2.5 pr-3 dark:text-untold-muted max-w-[120px] truncate">
                  {job.seo_title || '—'}
                </td>
              )}
              <td className="py-2.5 pr-3 dark:text-untold-muted whitespace-nowrap">
                {job.scheduled_at ? formatRelativeTime(job.scheduled_at) : 'ASAP'}
              </td>
              <td className="py-2.5 text-right whitespace-nowrap">
                {job.approval_status === 'pending' && (
                  <>
                    <button type="button" onClick={() => onApprove?.(job.id)} className="text-emerald-400 hover:underline mr-2">Approve</button>
                    <button type="button" onClick={() => onReject?.(job.id)} className="text-red-400 hover:underline mr-2">Reject</button>
                  </>
                )}
                {job.status === 'failed' && (
                  <button type="button" onClick={() => onRetry?.(job.id)} className="text-untold-gold hover:underline">
                    Retry ({job.retry_count})
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
