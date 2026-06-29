const pillBase =
  'shrink-0 inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors duration-150';

function FilterPills({ label, options, active, onChange }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
      {label && (
        <span className="shrink-0 text-[9px] font-bold uppercase tracking-[0.22em] text-untold-gold/60">
          {label}
        </span>
      )}
      {options.map((opt) => {
        const value = opt.value ?? opt.label;
        const isActive = active === value;
        return (
          <button
            key={value}
            type="button"
            onClick={() => onChange(value)}
            className={`${pillBase}
              ${isActive
                ? 'bg-untold-gold text-untold-dark'
                : 'dark:bg-white/[0.05] light:bg-gray-100 dark:text-untold-muted light:text-gray-600 hover:text-untold-gold'
              }
              ${opt.dashed && !isActive ? 'border border-dashed dark:border-white/10 light:border-gray-300' : ''}
            `}
          >
            {opt.label ?? value}
            {opt.badge && (
              <span className={`text-[8px] font-bold uppercase ${isActive ? 'opacity-70' : 'text-untold-gold'}`}>
                {opt.badge}
              </span>
            )}
            {opt.count != null && value !== 'All' && value !== 'all' && !opt.badge && (
              <span className={`text-[10px] tabular-nums ${isActive ? 'opacity-60' : 'opacity-40'}`}>
                {opt.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

function FilterSegmented({ label, options, active, onChange, ariaLabel }) {
  return (
    <div className="flex items-center gap-2 min-w-0 overflow-x-auto scrollbar-hide">
      {label && (
        <span className="shrink-0 text-[9px] font-bold uppercase tracking-[0.22em] text-untold-gold/60">
          {label}
        </span>
      )}
      <div
        className="inline-flex p-0.5 rounded-lg dark:bg-black/20 light:bg-gray-100
          border dark:border-white/[0.05] light:border-gray-200"
        role="tablist"
        aria-label={ariaLabel || label}
      >
        {options.map((opt) => {
          const value = opt.value ?? opt.label;
          const isActive = active === value;
          return (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={isActive}
              onClick={() => onChange(value)}
              className={`shrink-0 px-2 py-1 rounded-md text-[11px] font-medium whitespace-nowrap transition-colors
                ${isActive
                  ? 'bg-untold-gold text-untold-dark'
                  : 'dark:text-untold-muted light:text-gray-600 hover:dark:text-untold-white'
                }`}
            >
              {opt.label ?? value}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function FilterMeta({ resultCount, resultLabel, hasFilters, onClear, trailing }) {
  if (resultCount == null && !trailing && !(hasFilters && onClear)) return null;

  return (
    <div className="flex items-center gap-3 shrink-0">
      {trailing}
      {resultCount != null && (
        <span className="text-[11px] dark:text-untold-muted light:text-gray-500 tabular-nums">
          <span className="font-semibold dark:text-untold-white light:text-black">{resultCount}</span>
          {' '}
          {resultLabel}
        </span>
      )}
      {hasFilters && onClear && (
        <button
          type="button"
          onClick={onClear}
          className="text-[11px] font-semibold text-untold-gold hover:underline"
        >
          Clear
        </button>
      )}
    </div>
  );
}

/**
 * Compact OTT-style filter bar — shared across content pillar pages.
 */
export default function ContentFilterBar({
  sticky = true,
  className = '',
  primary,
  secondary,
  resultCount,
  resultLabel = 'titles',
  onClear,
  footer,
  trailing,
  showClear,
}) {
  const primaryDefault = primary?.defaultValue ?? 'All';
  const secondaryDefault = secondary?.defaultValue ?? 'All';
  const hasFilters = showClear ?? Boolean(
    (primary && primary.active !== primaryDefault)
    || (secondary && secondary.active !== secondaryDefault)
  );

  const showMeta = resultCount != null || trailing || (hasFilters && onClear);

  return (
    <div className={`${sticky ? 'sticky top-16 sm:top-20 z-30' : ''} mb-5 ${className}`}>
      <div
        className="rounded-xl border dark:border-white/10 light:border-gray-200
          dark:bg-untold-surface/95 light:bg-white/95 backdrop-blur-md
          shadow-md shadow-black/5 px-3 py-2 space-y-2"
      >
        {primary && (
          <FilterPills
            label={primary.label}
            options={primary.options}
            active={primary.active}
            onChange={primary.onChange}
          />
        )}

        {footer ? (
          <p className="text-[11px] text-untold-gold/90">{footer}</p>
        ) : (secondary || showMeta) && (
          <div className={`flex items-center gap-2 flex-wrap ${secondary ? 'justify-between' : 'justify-end'}`}>
            {secondary ? (
              <FilterSegmented
                label={secondary.label}
                options={secondary.options}
                active={secondary.active}
                onChange={secondary.onChange}
                ariaLabel={secondary.ariaLabel}
              />
            ) : null}
            {showMeta && (
              <FilterMeta
                resultCount={resultCount}
                resultLabel={resultLabel}
                hasFilters={hasFilters}
                onClear={onClear}
                trailing={trailing}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
