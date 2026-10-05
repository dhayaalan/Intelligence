import React from 'react';

export type OperationalStatus =
  | 'AVAILABLE'
  | 'CONFIG_REQUIRED'
  | 'COMING_SOON'
  | 'DISABLED'
  | 'RUNNING'
  | 'COMPLETED'
  | 'SUCCESS'
  | 'FAILED'
  | 'ACTIVE'
  | 'SUSPENDED'
  | 'READY'
  | 'DEGRADED'
  | string;

export interface StatusBadgeProps {
  status: OperationalStatus;
  className?: string;
  showDot?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className = '',
  showDot = true,
}) => {
  const norm = (status || '').toUpperCase().trim();

  let styles = 'bg-zinc-800 text-zinc-300 border-zinc-700';
  let dotColor = 'bg-zinc-400';
  let label = status;

  switch (norm) {
    case 'AVAILABLE':
    case 'READY':
    case 'ACTIVE':
    case 'SUCCESS':
    case 'COMPLETED':
      styles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      dotColor = 'bg-emerald-400';
      label = norm === 'AVAILABLE' ? 'Available' : norm === 'ACTIVE' ? 'Active' : 'Operational';
      break;

    case 'CONFIG_REQUIRED':
      styles = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      dotColor = 'bg-amber-400';
      label = 'Config Required';
      break;

    case 'RUNNING':
      styles = 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse';
      dotColor = 'bg-blue-400';
      label = 'Running';
      break;

    case 'COMING_SOON':
      styles = 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      dotColor = 'bg-purple-400';
      label = 'Coming Soon';
      break;

    case 'FAILED':
    case 'SUSPENDED':
    case 'DEGRADED':
    case 'DISABLED':
      styles = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      dotColor = 'bg-rose-400';
      label = norm === 'FAILED' ? 'Failed' : norm === 'SUSPENDED' ? 'Suspended' : 'Degraded';
      break;

    default:
      styles = 'bg-zinc-800 text-zinc-300 border-zinc-700';
      dotColor = 'bg-zinc-400';
      label = status;
      break;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles} ${className}`}
    >
      {showDot && (
        <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} />
      )}
      {label}
    </span>
  );
};
