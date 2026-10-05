import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { Button } from '../ui/Button';

export interface ErrorStateProps {
  title?: string;
  error?: string | Error;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Encountered an operational error',
  error,
  onRetry,
  className = '',
}) => {
  const errorMessage =
    typeof error === 'string'
      ? error
      : error?.message || 'An unexpected condition prevented data retrieval.';

  return (
    <div
      className={`flex flex-col items-center justify-center py-16 px-6 text-center rounded-xl border border-destructive/30 bg-destructive/5 ${className}`}
    >
      <div className="h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center mb-4 text-destructive">
        <AlertCircle className="h-6 w-6 stroke-[1.75]" />
      </div>
      <h3 className="text-base font-semibold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-6 leading-relaxed">
        {errorMessage}
      </p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="gap-2">
          <RotateCcw className="h-4 w-4" />
          Retry Operation
        </Button>
      )}
    </div>
  );
};
