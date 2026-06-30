import { useState } from 'react';

export default function StoryboardApprovalPanel({ approvalStatus, approval, onRequest, onApprove, onReject, busy }) {
  const [notes, setNotes] = useState('');

  return (
    <div className="space-y-4 max-w-lg">
      <div className="rounded-lg border dark:border-white/10 p-4">
        <p className="text-xs dark:text-untold-muted">Storyboard approval</p>
        <p className="text-lg font-semibold dark:text-white capitalize mt-1">{approvalStatus || 'draft'}</p>
        {approval && (
          <p className="text-xs dark:text-untold-muted mt-2 capitalize">
            Latest: {approval.status}
            {approval.notes ? ` — ${approval.notes}` : ''}
          </p>
        )}
      </div>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        rows={3}
        placeholder="Notes for approvers (optional)"
        className="w-full rounded-lg border dark:border-white/10 dark:bg-black/30 px-3 py-2 text-sm dark:text-white"
      />
      <div className="flex flex-wrap gap-2">
        {approvalStatus !== 'pending' && approvalStatus !== 'approved' && (
          <button
            type="button"
            disabled={busy}
            onClick={() => onRequest({ notes: notes || null })}
            className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50"
          >
            Submit for approval
          </button>
        )}
        {approvalStatus === 'pending' && (
          <>
            <button type="button" disabled={busy} onClick={() => onApprove({ notes: notes || null })} className="px-4 py-2 text-sm rounded-lg bg-emerald-600 text-white font-medium disabled:opacity-50">
              Approve storyboard
            </button>
            <button type="button" disabled={busy} onClick={() => onReject({ notes: notes || null })} className="px-4 py-2 text-sm rounded-lg border border-red-500/50 text-red-400 disabled:opacity-50">
              Request changes
            </button>
          </>
        )}
      </div>
    </div>
  );
}
