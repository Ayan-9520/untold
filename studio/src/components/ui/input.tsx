import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'w-full rounded-lg border border-studio-border bg-studio-surface px-3 py-2.5 text-sm text-white',
        'placeholder:text-studio-muted focus:border-studio-gold/50 focus:outline-none focus:ring-1 focus:ring-studio-gold/30',
        className
      )}
      {...props}
    />
  )
);
Input.displayName = 'Input';
