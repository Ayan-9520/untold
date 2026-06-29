export default function ChartCard({ title, subtitle, children, action }) {
  return (
    <div className="rounded-xl p-5 sm:p-6 dark:bg-untold-surface light:bg-white border dark:border-white/5 light:border-gray-200">
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="text-sm font-semibold dark:text-untold-white light:text-black">{title}</h3>
          {subtitle && (
            <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-0.5">{subtitle}</p>
          )}
        </div>
        {action}
      </div>
      <div className="h-[280px]">{children}</div>
    </div>
  );
}
