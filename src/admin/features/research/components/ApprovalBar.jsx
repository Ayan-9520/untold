export default function ApprovalBar({ status, rejectionNotes, onRequest, onApprove, onReject, pending }) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border dark:border-white/10 p-3">
      <span className="text-xs dark:text-untold-muted">Approval workflow</span>
      {status === 'pending_approval' && (
        <>
          <button type="button" disabled={pending} onClick={onApprove} className="text-xs px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-400">Approve</button>
          <button type="button" disabled={pending} onClick={onReject} className="text-xs px-3 py-1 rounded-lg bg-red-500/20 text-red-400">Reject</button>
        </>
      )}
      {status !== 'pending_approval' && status !== 'approved' && (
        <button type="button" disabled={pending} onClick={onRequest} className="text-xs px-3 py-1 rounded-lg border dark:border-white/10 text-untold-gold">Submit for approval</button>
      )}
      {status === 'approved' && <span className="text-xs text-emerald-400">✓ Approved for scripting</span>}
      {rejectionNotes && <span className="text-xs text-red-400">Rejected: {rejectionNotes}</span>}
    </div>
  );
}
