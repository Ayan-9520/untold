import { useState } from 'react';

const STATUS_STYLES = {
  pending: 'text-amber-400',
  approved: 'text-emerald-400',
  rejected: 'text-red-400',
};

export default function ApprovalPanel({
  workspace,
  approval,
  onRequest,
  onApprove,
  onReject,
  busy,
}) {
  const [notes, setNotes] = useState('');

  return (
    <div className="space-y-4 max-w-lg">
      <div className="rounded-lg border dark:border-white/10 p-4">
        <p className="text-xs dark:text-untold-muted">Script status</p>
        <p className="text-lg font-semibold dark:text-white capitalize mt-1">{workspace.status}</p>
        {workspace.approved_at && (
          <p className="text-xs text-emerald-400 mt-1">Approved {new Date(workspace.approved_at).toLocaleDateString()}</p>
        )}
        {approval && (
          <p className={`text-xs mt-2 capitalize ${STATUS_STYLES[approval.status] || 'dark:text-untold-muted'}`}>
            Approval: {approval.status}
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
        {workspace.status !== 'review' && workspace.status !== 'approved' && (
          <button
            type="button"
            disabled={busy}
            onClick={() => onRequest({ notes: notes || null })}
            className="px-4 py-2 text-sm rounded-lg bg-untold-gold text-black font-medium disabled:opacity-50"
          >
            Submit for approval
          </button>
        )}
        {workspace.status === 'review' && (
          <>
            <button
              type="button"
              disabled={busy}
              onClick={() => onApprove({ notes: notes || null })}
              className="px-4 py-2 text-sm rounded-lg bg-emerald-600 text-white font-medium disabled:opacity-50"
            >
              Approve
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => onReject({ notes: notes || null })}
              className="px-4 py-2 text-sm rounded-lg border border-red-500/50 text-red-400 disabled:opacity-50"
            >
              Request changes
            </button>
          </>
        )}
      </div>
    </div>
  );
}
