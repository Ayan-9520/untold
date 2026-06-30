import { useState } from 'react';
import { PUBLISH_PLATFORMS } from '../constants';

export default function DispatchPanel({ projects, onDispatch, dispatching }) {
  const [projectId, setProjectId] = useState(projects?.[0]?.id || '');
  const [platforms, setPlatforms] = useState(['originals', 'youtube']);
  const [scheduledAt, setScheduledAt] = useState('');
  const [requiresApproval, setRequiresApproval] = useState(true);
  const [seoTitle, setSeoTitle] = useState('');
  const [seoDescription, setSeoDescription] = useState('');

  const togglePlatform = (id) => {
    setPlatforms((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <p className="text-sm dark:text-untold-muted">
        Dispatch to UNTOLD Originals, YouTube, Instagram, Facebook, X, and Threads in one agent run.
        Schedule, require approval, and track via webhooks and analytics.
      </p>
      <label className="text-xs dark:text-untold-muted block">
        Project
        <select
          value={projectId}
          onChange={(e) => setProjectId(Number(e.target.value))}
          className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
        >
          {projects?.map((p) => (
            <option key={p.id} value={p.id}>{p.title}</option>
          ))}
        </select>
      </label>
      <div>
        <p className="text-xs dark:text-untold-muted mb-2">Platforms</p>
        <div className="flex flex-wrap gap-2">
          {PUBLISH_PLATFORMS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => togglePlatform(p.id)}
              className={`text-xs px-3 py-1.5 rounded-full border ${
                platforms.includes(p.id) ? 'border-untold-gold text-untold-gold' : 'dark:border-white/10 dark:text-untold-muted'
              }`}
            >
              {p.icon} {p.label}
            </button>
          ))}
        </div>
      </div>
      <div className="grid sm:grid-cols-2 gap-4">
        <label className="text-xs dark:text-untold-muted block">
          Schedule (optional)
          <input
            type="datetime-local"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
            className="w-full mt-1 rounded border dark:border-white/10 dark:bg-black/30 px-2 py-1.5 text-sm dark:text-white"
          />
        </label>
        <label className="flex items-end gap-2 text-xs dark:text-untold-muted pb-2 cursor-pointer">
          <input type="checkbox" checked={requiresApproval} onChange={(e) => setRequiresApproval(e.target.checked)} />
          Require approval before publish
        </label>
      </div>
      <input
        value={seoTitle}
        onChange={(e) => setSeoTitle(e.target.value)}
        placeholder="SEO title (optional)"
        className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />
      <textarea
        value={seoDescription}
        onChange={(e) => setSeoDescription(e.target.value)}
        rows={2}
        placeholder="Description / caption (optional)"
        className="w-full rounded border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />
      <button
        type="button"
        disabled={!projectId || platforms.length === 0 || dispatching}
        onClick={() => onDispatch({
          project_id: projectId,
          platforms,
          scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : undefined,
          requires_approval: requiresApproval,
          seo_title: seoTitle.trim() || undefined,
          seo_description: seoDescription.trim() || undefined,
        })}
        className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-semibold disabled:opacity-50"
      >
        {dispatching ? 'Dispatching…' : 'Dispatch publishing agent'}
      </button>
    </div>
  );
}
