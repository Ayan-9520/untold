import { Link } from 'react-router-dom';

export default function DashboardSection({
  title,
  subtitle,
  actionLabel,
  actionTo,
  children,
  className = '',
}) {
  return (
    <section className={`space-y-3 ${className}`}>
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold dark:text-white light:text-black">{title}</h2>
          {subtitle && (
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">{subtitle}</p>
          )}
        </div>
        {actionLabel && actionTo && (
          <Link to={actionTo} className="text-xs font-medium text-untold-gold hover:underline shrink-0">
            {actionLabel}
          </Link>
        )}
      </div>
      <div className="studio-card p-5">
        {children}
      </div>
    </section>
  );
}

export function ChartPanel({ title, subtitle, children, className = '' }) {
  return (
    <div
      className={`studio-card p-5 sm:p-6 flex flex-col ${className}`}
    >
      <div className="mb-4">
        <h3 className="text-sm font-semibold">{title}</h3>
        {subtitle && (
          <p className="text-xs studio-muted mt-0.5">{subtitle}</p>
        )}
      </div>
      <div className="flex-1 min-h-[240px]">{children}</div>
    </div>
  );
}
