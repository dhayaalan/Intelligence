import React from 'react';
import { ToolItem } from '../../core/api/hooks';
import { StatusBadge } from '../common/StatusBadge';
import { Button } from '../ui/Button';
import { Play, Key, Clock, ShieldCheck, Zap } from 'lucide-react';

export interface ToolCardProps {
  tool: ToolItem;
  onRun?: (tool: ToolItem) => void;
  onConfigure?: (tool: ToolItem) => void;
  onViewDetails?: (tool: ToolItem) => void;
  className?: string;
}

export const ToolCard: React.FC<ToolCardProps> = ({
  tool,
  onRun,
  onConfigure,
  onViewDetails,
  className = '',
}) => {
  const isAvailable = tool.status === 'AVAILABLE';
  const isConfigRequired = tool.status === 'CONFIG_REQUIRED';

  return (
    <div
      className={`group relative flex flex-col justify-between rounded-xl border border-border/70 bg-card p-5 transition-all duration-200 hover:border-border hover:shadow-md ${className}`}
    >
      <div>
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground bg-muted/60 px-2 py-0.5 rounded">
              {tool.category}
            </span>
            <span className="text-[11px] text-muted-foreground">
              v{tool.version}
            </span>
          </div>
          <StatusBadge status={tool.status} />
        </div>

        <h3
          onClick={() => onViewDetails && onViewDetails(tool)}
          className={`text-base font-semibold text-foreground group-hover:text-primary transition-colors ${
            onViewDetails ? 'cursor-pointer' : ''
          }`}
        >
          {tool.name}
        </h3>

        <p className="text-xs text-muted-foreground mt-1.5 line-clamp-2 leading-relaxed">
          {tool.description}
        </p>
      </div>

      <div className="mt-4 pt-3.5 border-t border-border/50 flex flex-col gap-2.5">
        <div className="flex items-center justify-between text-[11px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <ShieldCheck className="h-3 w-3" />
            {tool.provider}
          </span>
          <span className="flex items-center gap-1 font-mono">
            {tool.execution_type === 'REAL_TIME' ? (
              <Zap className="h-3 w-3 text-emerald-400" />
            ) : (
              <Clock className="h-3 w-3 text-blue-400" />
            )}
            {tool.execution_type}
          </span>
        </div>

        <div className="flex items-center gap-2 mt-1">
          {isAvailable ? (
            <Button
              size="sm"
              variant="primary"
              className="w-full gap-1.5 text-xs h-8"
              onClick={() => onRun && onRun(tool)}
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              Run Tool
            </Button>
          ) : isConfigRequired ? (
            <Button
              size="sm"
              variant="outline"
              className="w-full gap-1.5 text-xs h-8 border-amber-500/40 text-amber-400 hover:bg-amber-500/10"
              onClick={() => onConfigure ? onConfigure(tool) : onRun && onRun(tool)}
            >
              <Key className="h-3.5 w-3.5" />
              Configure API Key
            </Button>
          ) : (
            <Button
              size="sm"
              variant="secondary"
              disabled
              className="w-full text-xs h-8 opacity-60 cursor-not-allowed"
            >
              Coming Soon
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
