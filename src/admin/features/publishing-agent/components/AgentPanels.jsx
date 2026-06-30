import { useState } from 'react';
import PublishingQueueTable from '../../publishing/components/PublishingQueueTable';
import { RUN_STATUS_STYLES, APPROVAL_STYLES, formatPlatform } from '../constants';
import { WEBHOOK_EVENTS } from '../constants';

function ProgressBar({ progress }) {
  const pct = Math.min(100, Math.max(0, progress || 0));
  return (
    <div className="h-1.5 rounded-full bg-black/40 overflow-hidden">
      <div className="h-full bg-untold-gold transition-all" style={{ width: `${pct}%` }} />
    </div>
  );
}

export function AgentQueuePanel({ queue, mutations }) {
  const runs = queue?.runs || [];
  const jobs = queue?.jobs || [];

  return (
    <div className="space-y-6">
      {runs.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold dark:text-white uppercase tracking-wide">Agent runs</h3>
          {runs.map((run) => (
            <div key={run.id} className="rounded-lg border dark:border-white/10 p-4 space-y-2 text-xs">
              <div className="flex justify-between gap-2">
                <div>
                  <p className="font-medium dark:text-white">{run.project_title}</p>
                  <p className="dark:text-untold-muted">
                    {run.platforms?.map(formatPlatform).join(' · ')}
                  </p>
                </div>
                <div className="text-right">
                  <p className={RUN_STATUS_STYLES[run.status] || ''}>{run.status.replace('_', ' ')}</p>
                  <p className={APPROVAL_STYLES[run.approval_status] || ''}>{run.approval_status}</p>
                </div>
              </div>
              <ProgressBar progress={run.progress} />
              {run.approval_status === 'pending' && (
                <div className="flex gap-2">
                  <button type="button" onClick={() => mutations.approveRun.mutate({ id: run.id })} className="text-emerald-400 hover:underline">Approve</button>
                  <button type="button" onClick={() => mutations.rejectRun.mutate({ id: run.id })} className="text-red-400 hover:underline">Reject</button>
                </div>
              )}
              {(run.status === 'failed' || run.status === 'partial') && (
                <button type="button" onClick={() => mutations.retryRun.mutate({ id: run.id })} className="text-untold-gold hover:underline">Retry failed</button>
              )}
            </div>
          ))}
        </div>
      )}
      <div>
        <h3 className="text-xs font-semibold dark:text-white uppercase tracking-wide mb-3">Publishing jobs</h3>
        <PublishingQueueTable
          jobs={jobs}
          onApprove={(id) => mutations.approveJob.mutate(id)}
          onReject={(id) => mutations.rejectJob.mutate(id)}
          onRetry={(id) => mutations.retryJob.mutate(id)}
          compact
        />
      </div>
      {!runs.length && !jobs.length && (
        <p className="text-sm dark:text-untold-muted text-center py-8">Publishing queue is empty</p>
      )}
    </div>
  );
}

export function AgentHistoryPanel({ history, mutations }) {
  const items = history?.items || [];
  if (!items.length) {
    return <p className="text-sm dark:text-untold-muted text-center py-8">No agent runs yet</p>;
  }

  return (
    <div className="space-y-4">
      {items.map((run) => (
        <article key={run.id} className="rounded-xl border dark:border-white/10 p-4 space-y-2 text-xs">
          <div className="flex justify-between">
            <p className="font-medium dark:text-white">{run.project_title}</p>
            <span className={RUN_STATUS_STYLES[run.status] || ''}>{run.status}</span>
          </div>
          <p className="dark:text-untold-muted">{run.platforms?.map(formatPlatform).join(', ')}</p>
          {run.jobs?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {run.jobs.map((j) => (
                <span key={j.id} className="px-2 py-0.5 rounded bg-black/30 capitalize">
                  {formatPlatform(j.platform)}: {j.status}
                </span>
              ))}
            </div>
          )}
          {run.error_message && <p className="text-red-400">{run.error_message}</p>}
          {(run.status === 'failed' || run.status === 'partial') && (
            <button type="button" onClick={() => mutations.retryRun.mutate({ id: run.id })} className="text-untold-gold hover:underline">Retry</button>
          )}
        </article>
      ))}
    </div>
  );
}

export function AnalyticsPanel({ analytics }) {
  const byPlatform = analytics?.by_platform || {};
  const recent = analytics?.recent_events || [];

  return (
    <div className="space-y-6">
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {Object.entries(byPlatform).map(([plat, events]) => (
          <div key={plat} className="rounded-lg border dark:border-white/10 p-3 text-xs">
            <p className="font-medium dark:text-white capitalize mb-2">{formatPlatform(plat)}</p>
            {Object.entries(events).map(([evt, count]) => (
              <p key={evt} className="dark:text-untold-muted flex justify-between">
                <span>{evt.replace('publish.', '')}</span>
                <span className="text-untold-gold">{count}</span>
              </p>
            ))}
          </div>
        ))}
        {!Object.keys(byPlatform).length && (
          <p className="text-sm dark:text-untold-muted col-span-full text-center py-4">No publish analytics yet</p>
        )}
      </div>
      {recent.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold dark:text-white mb-2">Recent events</h3>
          <ul className="space-y-1 text-[10px] dark:text-untold-muted">
            {recent.map((e) => (
              <li key={e.id}>
                {formatPlatform(e.platform)} · {e.event_type} · project #{e.project_id}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function WebhooksPanel({ webhooks, mutations, webhookEvents }) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [events, setEvents] = useState(['publish.success', 'publish.failed']);
  const eventsList = webhookEvents || WEBHOOK_EVENTS;

  const toggleEvent = (evt) => {
    setEvents((prev) => (prev.includes(evt) ? prev.filter((e) => e !== evt) : [...prev, evt]));
  };

  return (
    <div className="space-y-6 max-w-xl">
      <p className="text-sm dark:text-untold-muted">
        Register HTTPS endpoints to receive publish lifecycle events with HMAC signatures.
      </p>
      <div className="space-y-3 rounded-lg border dark:border-white/10 p-4">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Webhook name" className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://your-server.com/webhooks/untold" className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white" />
        <div className="flex flex-wrap gap-1">
          {eventsList.map((evt) => (
            <button key={evt} type="button" onClick={() => toggleEvent(evt)}
              className={`text-[10px] px-2 py-0.5 rounded border ${events.includes(evt) ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10'}`}>
              {evt}
            </button>
          ))}
        </div>
        <button type="button" disabled={!name.trim() || !url.trim() || mutations.createWebhook.isPending}
          onClick={() => { mutations.createWebhook.mutate({ name: name.trim(), url: url.trim(), events }); setName(''); setUrl(''); }}
          className="text-xs px-3 py-1.5 rounded bg-untold-gold text-black font-semibold disabled:opacity-50">
          Add webhook
        </button>
      </div>
      <ul className="space-y-2 text-xs">
        {(webhooks || []).map((w) => (
          <li key={w.id} className="flex justify-between items-center rounded border dark:border-white/10 p-3">
            <div>
              <p className="dark:text-white font-medium">{w.name}</p>
              <p className="dark:text-untold-muted truncate max-w-xs">{w.url}</p>
            </div>
            <button type="button" onClick={() => mutations.deleteWebhook.mutate(w.id)} className="text-red-400 hover:underline shrink-0">Remove</button>
          </li>
        ))}
        {!webhooks?.length && <p className="dark:text-untold-muted text-center py-4">No webhooks configured</p>}
      </ul>
    </div>
  );
}
