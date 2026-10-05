import React from 'react';

export type FindingSeverity =
  | 'CRITICAL'
  | 'HIGH'
  | 'MEDIUM'
  | 'LOW'
  | 'INFORMATIONAL'
  | string;

export interface SeverityBadgeProps {
  severity: FindingSeverity;
  className?: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  className = '',
}) => {
  const norm = (severity || '').toUpperCase().trim();

  let styles = 'bg-zinc-800 text-zinc-300 border-zinc-700';

  switch (norm) {
    case 'CRITICAL':
      styles = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      break;
    case 'HIGH':
      styles = 'bg-orange-500/15 text-orange-400 border-orange-500/30';
      break;
    case 'MEDIUM':
      styles = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      break;
    case 'LOW':
      styles = 'bg-blue-500/15 text-blue-400 border-blue-500/30';
      break;
    case 'INFORMATIONAL':
    case 'INFO':
      styles = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      break;
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider border ${styles} ${className}`}
    >
      {severity}
    </span>
  );
};
