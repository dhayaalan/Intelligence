import React, { useState } from 'react';
import { ToolItem, useRunTool } from '../../core/api/hooks';
import { Dialog } from '../ui/Dialog';
import { Button } from '../ui/Button';
import { StatusBadge } from '../common/StatusBadge';
import { ToolResultDetails } from './ToolResultDetails';
import { Play, Loader2, AlertCircle } from 'lucide-react';

export interface ToolRunModalProps {
  tool: ToolItem | null;
  isOpen: boolean;
  onClose: () => void;
  defaultTarget?: string;
  investigationId?: string;
}

export const ToolRunModal: React.FC<ToolRunModalProps> = ({
  tool,
  isOpen,
  onClose,
  defaultTarget = '',
  investigationId,
}) => {
  const [target, setTarget] = useState(defaultTarget);
  const [targetType, setTargetType] = useState('DOMAIN');
  const [result, setResult] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const runMutation = useRunTool();

  if (!tool) return null;

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return;

    setErrorMessage(null);
    setResult(null);

    try {
      const data = await runMutation.mutateAsync({
        toolId: tool.id,
        payload: {
          target: target.trim(),
          target_type: targetType,
          investigation_id: investigationId,
        },
      });
      setResult(data);
    } catch (err: any) {
      setErrorMessage(
        err?.message || 'Tool execution encountered an unexpected network error.'
      );
    }
  };

  const handleReset = () => {
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={() => {
        handleReset();
        onClose();
      }}
      title={`Run ${tool.name}`}
    >
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between text-xs pb-3 border-b border-border/50">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-muted-foreground uppercase">
              {tool.category}
            </span>
            <span className="text-muted-foreground">|</span>
            <span className="text-muted-foreground">{tool.provider}</span>
          </div>
          <StatusBadge status={tool.status} />
        </div>

        {!result ? (
          <form onSubmit={handleRun} className="space-y-4">
            <p className="text-xs text-muted-foreground leading-relaxed">
              {tool.description}
            </p>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-foreground">
                Target Input
              </label>
              <input
                type="text"
                required
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="e.g. example.com, 1.1.1.1, username, admin@example.com"
                className="w-full h-9 px-3 text-sm rounded-lg bg-background border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <span className="text-[11px] text-muted-foreground">
                Supported inputs: {tool.supported_inputs.join(', ')}
              </span>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-foreground">
                Target Type
              </label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="w-full h-9 px-3 text-sm rounded-lg bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="DOMAIN">DOMAIN</option>
                <option value="IP">IP ADDRESS</option>
                <option value="USERNAME">USERNAME</option>
                <option value="EMAIL">EMAIL</option>
                <option value="HASH">HASH / IOC</option>
                <option value="URL">URL</option>
              </select>
            </div>

            {errorMessage && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-xs text-destructive flex items-start gap-2">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/40">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={runMutation.isPending || !target.trim()}
                className="gap-1.5"
              >
                {runMutation.isPending ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Play className="h-3.5 w-3.5 fill-current" />
                    Execute Tool
                  </>
                )}
              </Button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <ToolResultDetails
              result={result}
              toolName={tool.name}
              onRunAnother={handleReset}
            />
            <div className="flex items-center justify-end pt-3 border-t border-border/40">
              <Button size="sm" variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        )}
      </div>
    </Dialog>
  );
};
