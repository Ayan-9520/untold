import { cn } from '@/lib/utils';

const variants = {
  default: 'bg-studio-surface text-studio-muted border-studio-border',
  gold: 'bg-studio-gold/15 text-studio-gold border-studio-gold/30',
};

export function Badge({
  className,
  variant = 'default',
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide',
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
