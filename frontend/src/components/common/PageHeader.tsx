import React from 'react';

export interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  badge,
  actions,
  breadcrumbs,
}) => {
  return (
    <div className="flex flex-col gap-2 pb-6 border-b border-border/40">
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={crumb.label}>
              {idx > 0 && <span className="opacity-40">/</span>}
              {crumb.href ? (
                <a
                  href={crumb.href}
                  className="hover:text-foreground transition-colors"
                >
                  {crumb.label}
                </a>
              ) : (
                <span className="text-foreground font-medium">{crumb.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {title}
          </h1>
          {badge}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      {description && (
        <p className="text-sm text-muted-foreground max-w-3xl leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
};
