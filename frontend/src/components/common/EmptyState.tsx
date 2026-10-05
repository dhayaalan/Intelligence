import React from 'react';
import { LucideIcon, Search } from 'lucide-react';

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Search,
  title,
  description,
  action,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center py-16 px-6 text-center rounded-xl border border-dashed border-border/60 bg-card/30 ${className}`}
    >
      <div className="h-12 w-12 rounded-full bg-muted/60 flex items-center justify-center mb-4 text-muted-foreground">
        <Icon className="h-6 w-6 stroke-[1.5]" />
      </div>
      <h3 className="text-base font-semibold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-6 leading-relaxed">
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
};
