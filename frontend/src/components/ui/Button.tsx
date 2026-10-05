import React from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'accent' | 'default' | 'emerald';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, children, disabled, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black disabled:pointer-events-none disabled:opacity-50 select-none rounded-md text-xs font-sans tracking-tight cursor-pointer';

    const variants = {
      primary: 'bg-black text-white hover:bg-zinc-800 shadow-sm dark:bg-white dark:text-black dark:hover:bg-zinc-200',
      default: 'bg-black text-white hover:bg-zinc-800 shadow-sm dark:bg-white dark:text-black dark:hover:bg-zinc-200',
      secondary:
        'bg-white text-zinc-900 border border-zinc-200 hover:bg-zinc-50 shadow-sm dark:bg-zinc-900 dark:text-zinc-100 dark:border-zinc-800 dark:hover:bg-zinc-800',
      outline:
        'border border-zinc-200 hover:bg-zinc-100 text-zinc-900 hover:text-black dark:border-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white',
      ghost:
        'hover:bg-zinc-100 text-zinc-600 hover:text-black dark:hover:bg-zinc-800/60 dark:text-zinc-400 dark:hover:text-zinc-100',
      destructive:
        'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100 dark:bg-red-950/40 dark:text-red-400 dark:border-red-900/50',
      accent:
        'bg-black text-white hover:bg-zinc-800 shadow-sm dark:bg-white dark:text-black dark:hover:bg-zinc-200',
      emerald:
        'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm dark:bg-emerald-500 dark:text-black dark:hover:bg-emerald-400',
    };

    const sizes = {
      sm: 'h-8 px-3 text-xs gap-1.5',
      md: 'h-9 px-4 text-xs gap-2',
      lg: 'h-10 px-5 text-sm gap-2.5',
      icon: 'h-8 w-8 p-0',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
