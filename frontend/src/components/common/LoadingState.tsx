import React from 'react';
import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  message?: string;
  submessage?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading platform telemetry...',
  submessage,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center py-20 px-6 text-center ${className}`}
    >
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-4 stroke-[1.75]" />
      <p className="text-sm font-medium text-foreground">{message}</p>
      {submessage && (
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">{submessage}</p>
      )}
    </div>
  );
};
