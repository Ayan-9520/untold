/** Inline error state for admin pages that fetch from API. */
export default function AdminErrorBanner({ message, onRetry }) {
  return (
    <div className="admin-error-banner" role="alert">
      <p className="text-sm font-medium text-red-400">{message || 'Failed to load data'}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className="admin-error-banner-retry">
          Retry
        </button>
      )}
    </div>
  );
}
