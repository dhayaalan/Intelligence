import React, { useState } from 'react';
import { StatusBadge } from '../common/StatusBadge';
import { Button } from '../ui/Button';
import {
  CheckCircle2, AlertTriangle, Clock, RefreshCw, Copy, Check,
  ExternalLink, Play, Video, UserCheck, ShieldCheck, Database, FileText
} from 'lucide-react';
import { apiRequest } from '../../core/api/client';

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
  const [refreshingIdx, setRefreshingIdx] = useState<number | null>(null);
  const [refreshedItems, setRefreshedItems] = useState<Record<number, any>>({});

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRefreshProfile = async (platformId: string, username: string, idx: number) => {
    setRefreshingIdx(idx);
    try {
      const res = await apiRequest<{ status: string; result: any; changes: any[] }>(
        '/tools/profile/refresh',
        {
          method: 'POST',
          body: JSON.stringify({ platform_id: platformId.toLowerCase(), username }),
        }
      );
      if (res && res.result) {
        setRefreshedItems((prev) => ({
          ...prev,
          [idx]: {
            ...res.result,
            changes: res.changes,
          },
        }));
      }
    } catch (err) {
      console.error('Failed to refresh profile:', err);
    } finally {
      setRefreshingIdx(null);
    }
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
              const refreshed = refreshedItems[idx];
              const meta = refreshed ? { ...item.metadata, ...refreshed } : item.metadata;
              const avatar = meta?.avatar_url || meta?.image_url || meta?.thumbnail_url || meta?.hero_image;
              const profileUrl = meta?.profile_url || meta?.canonical_url || meta?.watch_url || meta?.url;
              const isVideo = meta?.is_video || item.type === 'VIDEO';
              const embedUrl = meta?.embed_url;
              const platform = meta?.platform || meta?.platform_id;
              const extractionStatus = meta?.status || (meta?.is_metadata_extracted ? 'METADATA_EXTRACTED' : 'PROFILE_VALIDATED');
              const bio = meta?.bio || meta?.description;
              const displayName = meta?.display_name || meta?.name;
              const fieldsExtracted = meta?.fields_extracted || [];

              return (
                <div key={idx} className="p-3.5 text-xs space-y-2.5 hover:bg-muted/20 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 flex-wrap">
                      {platform && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-primary/10 text-primary uppercase">
                          {platform}
                        </span>
                      )}
                      <span className="font-semibold text-foreground">
                        {displayName || item.metadata?.title || item.title || item.type || `Record #${idx + 1}`}
                      </span>
                      {extractionStatus && (
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold ${
                            extractionStatus === 'METADATA_EXTRACTED'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : extractionStatus === 'PARTIAL_EXTRACTION'
                              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                              : extractionStatus === 'CONFIG_REQUIRED'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-muted text-muted-foreground border border-border/60'
                          }`}
                        >
                          {extractionStatus}
                        </span>
                      )}
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
                          className={isVideo ? "w-24 h-16 rounded-lg object-cover border border-border" : "w-11 h-11 rounded-xl object-cover border border-border"}
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
                      {bio && (
                        <p className="text-foreground/90 text-xs leading-relaxed bg-muted/20 p-2 rounded border border-border/40">
                          {bio}
                        </p>
                      )}
                      {item.value && (
                        <p className="font-mono text-muted-foreground break-all text-[11px]">
                          {item.value}
                        </p>
                      )}

                      {/* Fields Extracted Chips */}
                      {fieldsExtracted.length > 0 && (
                        <div className="flex items-center gap-1 flex-wrap pt-1">
                          <span className="text-[10px] text-muted-foreground font-mono">Parsed:</span>
                          {fieldsExtracted.map((f: string, fIdx: number) => (
                            <span key={fIdx} className="px-1.5 py-0.2 rounded text-[9px] bg-secondary text-secondary-foreground font-mono">
                              {f}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center gap-3 pt-1">
                        {profileUrl && (
                          <a
                            href={profileUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] text-primary hover:underline font-medium"
                          >
                            {isVideo ? "Open YouTube Video" : "Open Public Source"} <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                        {platform && result.target && (
                          <button
                            type="button"
                            disabled={refreshingIdx === idx}
                            onClick={() => handleRefreshProfile(platform, result.target, idx)}
                            className="inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground hover:underline font-mono"
                          >
                            <RefreshCw className={`w-3 h-3 ${refreshingIdx === idx ? 'animate-spin' : ''}`} />
                            {refreshingIdx === idx ? 'Refreshing...' : 'Live Refresh'}
                          </button>
                        )}
                      </div>

                      {/* Refreshed change alert */}
                      {refreshed?.changes && refreshed.changes.length > 0 && (
                        <div className="mt-2 p-1.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-[10px] text-emerald-300">
                          <span className="font-semibold">Recent Changes Detected: </span>
                          {refreshed.changes.map((c: any, cIdx: number) => (
                            <span key={cIdx} className="mr-2">
                              {c.field_name}: {String(c.previous_value)} → {String(c.new_value)}
                            </span>
                          ))}
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
