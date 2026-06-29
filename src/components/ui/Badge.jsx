const variants = {
  gold: 'bg-untold-gold/90 text-untold-dark',
  live: 'bg-red-600 text-white',
  breaking: 'bg-red-600 text-white',
  muted: 'dark:bg-black/70 light:bg-gray-800/80 text-white backdrop-blur-sm',
  outline: 'border border-untold-gold/50 text-untold-gold bg-transparent',
  premium: 'bg-gradient-to-r from-untold-gold-dark to-untold-gold-light text-untold-dark',
};

const sizes = {
  sm: 'px-2 py-0.5 text-[10px]',
  md: 'px-2.5 py-0.5 text-xs',
  lg: 'px-3 py-1 text-sm',
};

export default function Badge({
  children,
  variant = 'gold',
  size = 'md',
  pulse = false,
  className = '',
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-semibold uppercase tracking-wide
        ${variants[variant] || variants.gold}
        ${sizes[size] || sizes.md}
        ${pulse ? 'animate-pulse' : ''}
        ${className}`}
    >
      {pulse && <span className="w-1.5 h-1.5 rounded-full bg-current opacity-90" />}
      {children}
    </span>
  );
}
