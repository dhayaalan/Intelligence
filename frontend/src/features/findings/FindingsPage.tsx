import React, { useState, useEffect, useMemo } from 'react';
import { ShieldAlert, AlertTriangle, Clock, ChevronDown, ChevronUp, Filter } from 'lucide-react';
import { apiRequest } from '../../core/api/client';
import { Badge } from '../../components/ui/Badge';
import { Card, CardContent } from '../../components/ui/Card';
import { Pagination } from '../../components/ui/Pagination';
import { formatDate } from '../../lib/utils';

interface Finding {
  id: string;
  title: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  confidence: number;
  status: string;
  mitigation?: string;
  evidence_ids: string[];
  investigation_id?: string;
  created_at: string;
}

export const FindingsPage: React.FC = () => {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    const fetchFindings = async () => {
      try {
        const data = await apiRequest<Finding[]>('/findings');
        setFindings(data);
      } catch (err) {
        console.error('Failed to load findings', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFindings();
  }, []);

  const filteredFindings = useMemo(() => {
    if (severityFilter === 'ALL') return findings;
    return findings.filter((f) => f.severity === severityFilter);
  }, [findings, severityFilter]);

  const paginatedFindings = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredFindings.slice(start, start + pageSize);
  }, [filteredFindings, currentPage, pageSize]);

  const getSeverityBadgeVariant = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'critical';
      case 'HIGH':
        return 'high';
      case 'MEDIUM':
        return 'medium';
      case 'LOW':
        return 'low';
      default:
        return 'mono';
    }
  };

  const criticalCount = findings.filter((f) => f.severity === 'CRITICAL' || f.severity === 'HIGH').length;

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="h-6 w-48 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
        <div className="h-4 w-96 bg-zinc-100 dark:bg-zinc-800/60 rounded animate-pulse" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-28 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-200 dark:border-zinc-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">INTELLIGENCE</span>
            <span className="text-zinc-300 dark:text-zinc-700">//</span>
            <span className="text-xs font-mono text-black dark:text-white font-bold">FINDINGS</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-950 dark:text-white flex items-center gap-2 font-sans">
            <ShieldAlert className="w-6 h-6 text-zinc-700 dark:text-zinc-300" />
            <span>Threat Findings & IOC Manifest</span>
          </h1>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
            Actionable security discoveries, adversary infrastructure patterns, and defensive remediation guidance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {criticalCount > 0 && (
            <Badge variant="destructive" size="md">
              <AlertTriangle className="w-3.5 h-3.5 mr-1" />
              {criticalCount} High Severity
            </Badge>
          )}
          <Badge variant="default" size="md">{findings.length} Total</Badge>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-3.5 h-3.5 text-zinc-400 dark:text-zinc-500" />
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].map((sev) => (
          <button
            key={sev}
            onClick={() => {
              setSeverityFilter(sev);
              setCurrentPage(1);
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
              severityFilter === sev
                ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800'
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Findings List */}
      <div className="space-y-3">
        {filteredFindings.length === 0 ? (
          <div className="text-center py-16 text-zinc-500 text-xs font-mono border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl">
            <ShieldAlert className="w-8 h-8 mx-auto mb-3 text-zinc-400 dark:text-zinc-600" />
            {findings.length === 0
              ? 'No findings recorded. Execute an intelligence search to generate findings.'
              : 'No findings match the current severity filter.'}
          </div>
        ) : (
          <>
            {paginatedFindings.map((finding) => (
              <Card key={finding.id} className="hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
                <CardContent className="p-0">
                  <button
                    className="w-full p-4 sm:p-5 flex items-start justify-between gap-4 text-left"
                    onClick={() => setExpandedId(expandedId === finding.id ? null : finding.id)}
                  >
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant={getSeverityBadgeVariant(finding.severity)} size="sm">
                          {finding.severity}
                        </Badge>
                        <Badge variant="outline" size="sm">{finding.status}</Badge>
                        <span className="text-[11px] font-mono font-semibold text-zinc-600 dark:text-zinc-400">
                          {finding.confidence}% Analytic Confidence
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-zinc-950 dark:text-white leading-snug">{finding.title}</h3>
                      <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed line-clamp-2">{finding.description}</p>
                    </div>

                    <div className="shrink-0 text-zinc-400 mt-1">
                      {expandedId === finding.id ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </div>
                  </button>

                  {/* Expanded Details */}
                  {expandedId === finding.id && (
                    <div className="px-5 pb-5 space-y-3 border-t border-zinc-100 dark:border-zinc-800 pt-3">
                      {finding.mitigation && (
                        <div className="p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200 text-xs font-mono text-emerald-900 dark:bg-emerald-950/30 dark:border-emerald-800/40 dark:text-emerald-300">
                          <strong className="text-emerald-800 dark:text-emerald-200 block mb-1 text-[11px] uppercase tracking-wider">
                            Remediation Policy
                          </strong>
                          {finding.mitigation}
                        </div>
                      )}

                      <div className="flex items-center gap-4 text-[11px] font-mono text-zinc-500 dark:text-zinc-400 flex-wrap">
                        <span className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5" />
                          {formatDate(finding.created_at)}
                        </span>
                        {finding.evidence_ids.length > 0 && (
                          <span>{finding.evidence_ids.length} Evidence Items Linked</span>
                        )}
                        {finding.investigation_id && (
                          <span>Investigation: {finding.investigation_id.slice(0, 12)}...</span>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}

            {/* Pagination Controls */}
            <Card className="p-0 overflow-hidden">
              <Pagination
                currentPage={currentPage}
                totalPages={Math.ceil(filteredFindings.length / pageSize)}
                totalItems={filteredFindings.length}
                pageSize={pageSize}
                onPageChange={setCurrentPage}
                onPageSizeChange={(sz) => {
                  setPageSize(sz);
                  setCurrentPage(1);
                }}
                pageSizeOptions={[10, 25, 50]}
              />
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default FindingsPage;
