import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { Button } from '../ui/Button';
import { CheckCircle2, AlertTriangle, Clock, RefreshCw, Copy, Check, ExternalLink, Play, Video } from 'lucide-react';

export interface ToolResultDetailsProps {
  result: {
    tool_id: string;
    target: string;
    target_type?: string;
    status: string;
    duration_ms?: number;
    results?: any[];
    raw_output?: any;
    config_help?: string;
    error_message?: string;
  };
  toolName?: string;
  onRunAnother?: () => void;
  className?: string;
}

export const ToolResultDetails: React.FC<ToolResultDetailsProps> = ({
  result,
  toolName,
  onRunAnother,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isSuccess = result.status === 'SUCCESS';
  const isConfigRequired = result.status === 'CONFIG_REQUIRED';

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Result Status Banner */}
      <div className="flex items-center justify-between p-3.5 rounded-lg border border-border/70 bg-card/60">
        <div className="flex items-center gap-2.5">
          {isSuccess ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
          ) : isConfigRequired ? (
            <AlertTriangle className="h-5 w-5 text-amber-400" />
          ) : (
            <AlertTriangle className="h-5 w-5 text-rose-400" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-foreground">
                {result.target}
              </span>
              <StatusBadge status={result.status} />
            </div>
            {result.duration_ms !== undefined && (
              <span className="text-[11px] text-muted-foreground flex items-center gap-1 mt-0.5 font-mono">
                <Clock className="h-3 w-3" />
                {Math.round(result.duration_ms)}ms execution time
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <Button
            size="sm"
            variant="ghost"
            className="h-8 px-2 text-xs"
            onClick={handleCopyJson}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-emerald-400 mr-1" />
            ) : (
              <Copy className="h-3.5 w-3.5 mr-1" />
            )}
            {copied ? 'Copied' : 'Copy JSON'}
          </Button>
          {onRunAnother && (
            <Button
              size="sm"
              variant="outline"
              className="h-8 px-2 text-xs gap-1"
              onClick={onRunAnother}
            >
              <RefreshCw className="h-3.5 w-3.5" />
              New Run
            </Button>
          )}
        </div>
      </div>

      {/* Config Required Notice */}
      {isConfigRequired && result.config_help && (
        <div className="p-3.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 leading-relaxed">
          <p className="font-semibold mb-1">Configuration Required:</p>
          <p>{result.config_help}</p>
        </div>
      )}

      {/* Structured Findings / Items */}
      {result.results && result.results.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <span>Discovered Records ({result.results.length})</span>
            <button
              type="button"
              onClick={() => setShowRaw(!showRaw)}
              className="text-primary hover:underline lowercase font-normal"
            >
              {showRaw ? 'hide raw' : 'view raw telemetry'}
            </button>
          </div>

          <div className="divide-y divide-border/40 rounded-lg border border-border/60 bg-card overflow-hidden">
            {result.results.map((item, idx) => {
              const avatar = item.metadata?.avatar_url || item.metadata?.image_url || item.metadata?.thumbnail_url || item.metadata?.hero_image;
              const profileUrl = item.metadata?.profile_url || item.metadata?.watch_url || item.metadata?.url;
              const isVideo = item.metadata?.is_video || item.type === 'VIDEO';
              const embedUrl = item.metadata?.embed_url;
              const platform = item.metadata?.platform;

              return (
                <div key={idx} className="p-3.5 text-xs space-y-2 hover:bg-muted/20 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {platform && (
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-primary/10 text-primary">
                          {platform}
                        </span>
                      )}
                      <span className="font-semibold text-foreground">
                        {item.title || item.type || `Record #${idx + 1}`}
                      </span>
                    </div>
                    {item.severity && (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-muted text-muted-foreground">
                        {item.severity}
                      </span>
                    )}
                  </div>

                  <div className="flex items-start gap-3">
                    {avatar && (
                      <div className="relative shrink-0">
                        <img
                          src={avatar}
                          alt="Extracted Media"
                          className={isVideo ? "w-24 h-16 rounded-lg object-cover border border-border" : "w-10 h-10 rounded-xl object-cover border border-border"}
                          onError={(e) => {
                            (e.target as any).style.display = 'none';
                          }}
                        />
                        {isVideo && (
                          <div className="absolute inset-0 bg-black/30 rounded-lg flex items-center justify-center">
                            <Play className="w-4 h-4 fill-white text-white" />
                          </div>
                        )}
                      </div>
                    )}
                    <div className="flex-1 min-w-0 space-y-1">
                      {item.value && (
                        <p className="font-mono text-muted-foreground break-all">
                          {item.value}
                        </p>
                      )}
                      {profileUrl && (
                        <div className="pt-1">
                          <a
                            href={profileUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] font-sans text-primary hover:underline font-medium"
                          >
                            {isVideo ? "Open YouTube Video" : "Open Public Profile"} <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      )}
                    </div>
                  </div>

                  {embedUrl && (
                    <div className="aspect-video w-full max-w-md rounded-lg overflow-hidden border border-border bg-black mt-2">
                      <iframe
                        src={embedUrl}
                        title="Embedded Media Player"
                        allowFullScreen
                        className="w-full h-full border-0"
                      />
                    </div>
                  )}

                  {item.raw && typeof item.raw === 'object' && (
                    <pre className="p-2 rounded bg-muted/40 font-mono text-[11px] overflow-x-auto text-muted-foreground">
                      {JSON.stringify(item.raw, null, 2)}
                    </pre>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Raw Output Inspector */}
      {(showRaw || (!result.results || result.results.length === 0)) && (
        <div className="space-y-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Raw Operational Telemetry
          </span>
          <pre className="p-3 rounded-lg border border-border/60 bg-muted/30 font-mono text-xs overflow-x-auto max-h-64 text-foreground/90">
            {JSON.stringify(result.raw_output || result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
