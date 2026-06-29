const variants = {
  primary:
    'bg-untold-gold text-untold-dark hover:bg-untold-gold-light font-semibold',
  secondary:
    'dark:bg-white/10 dark:text-untold-white dark:hover:bg-white/20 light:bg-black/5 light:text-black light:hover:bg-black/10 font-medium backdrop-blur-sm',
  outline:
    'border border-untold-gold text-untold-gold hover:bg-untold-gold hover:text-untold-dark font-medium',
  ghost:
    'dark:text-untold-white light:text-black dark:hover:bg-white/10 light:hover:bg-black/5',
};

const sizes = {
  sm: 'px-4 py-2 text-sm',
  md: 'px-6 py-2.5 text-sm',
  lg: 'px-8 py-3 text-base',
};

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  icon,
  ...props
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-md transition-all duration-300
        focus:outline-none focus-visible:ring-2 focus-visible:ring-untold-gold focus-visible:ring-offset-2
        dark:focus-visible:ring-offset-untold-dark light:focus-visible:ring-offset-white
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </button>
  );
}
