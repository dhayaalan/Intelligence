import React, { useState, useEffect, useMemo } from 'react';
import {
  FileText, Download, Clock, Shield, AlertTriangle, Hash, Layers,
  ChevronDown, ChevronRight
} from 'lucide-react';
import { apiRequest } from '../../core/api/client';
import { Badge } from '../../components/ui/Badge';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Pagination } from '../../components/ui/Pagination';
import { formatDate } from '../../lib/utils';

interface Report {
  id: string;
  tenant_id: string;
  investigation_id: string;
  title: string;
  type: string;
  status: string;
  author: string;
  created_at: string;
  executive_summary: string;
  classification: string;
  finding_ids: string[];
  evidence_citations: string[];
  entity_ids: string[];
  markdown_content?: string;
}

interface Investigation {
  id: string;
  title: string;
  target: string;
  target_type: string;
  status: string;
}

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedReport, setExpandedReport] = useState<string | null>(null);
  const [selectedInvId, setSelectedInvId] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const totalPages = Math.max(1, Math.ceil(reports.length / pageSize));
  const paginatedReports = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return reports.slice(start, start + pageSize);
  }, [reports, currentPage, pageSize]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [reportsData, invData] = await Promise.all([
          apiRequest<Report[]>('/reports'),
          apiRequest<Investigation[]>('/investigations'),
        ]);
        setReports(reportsData);
        setInvestigations(invData);
      } catch (err) {
        console.error('Failed to load reports data', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleGenerateReport = async () => {
    if (!selectedInvId) return;
    setIsGenerating(true);
    const inv = investigations.find((i) => i.id === selectedInvId);
    try {
      const newReport = await apiRequest<Report>('/reports', {
        method: 'POST',
        body: JSON.stringify({
          investigation_id: selectedInvId,
          title: `Dossier: ${inv?.title || 'Unknown Investigation'}`,
          type: 'COURT_ADMISSIBLE_DOSSIER',
          executive_summary: `Intelligence dossier compiled from investigation "${inv?.title || selectedInvId}" targeting ${inv?.target || 'unknown target'} (${inv?.target_type || 'UNKNOWN'}).`,
          classification: 'RESTRICTED // TLP:AMBER+STRICT',
          finding_ids: [],
          evidence_citations: [],
          entity_ids: [],
        }),
      });
      setReports((prev) => [newReport, ...prev]);
      setSelectedInvId('');
    } catch (err) {
      console.error('Failed to generate report', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportMarkdown = async (reportId: string) => {
    try {
      const response = await fetch(`/api/v1/reports/${reportId}/export`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('sential_token')}`,
        },
      });
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dossier_${reportId}.md`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed', err);
    }
  };

  const getStatusBadge = (status: string): 'success' | 'warning' | 'info' | 'mono' => {
    switch (status) {
      case 'READY':
      case 'EXPORTED':
        return 'success';
      case 'GENERATING':
        return 'warning';
      case 'DRAFT':
        return 'info';
      case 'ARCHIVED':
        return 'mono';
      default:
        return 'mono';
    }
  };

  const getTypeBadge = (type: string): 'purple' | 'info' | 'warning' => {
    switch (type) {
      case 'COURT_ADMISSIBLE_DOSSIER':
        return 'purple';
      case 'EXECUTIVE_THREAT_SUMMARY':
        return 'info';
      case 'TECHNICAL_IOC_MANIFEST':
        return 'warning';
      default:
        return 'purple';
    }
  };

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="h-6 w-48 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
        <div className="h-4 w-96 bg-zinc-100 dark:bg-zinc-800/60 rounded animate-pulse" />
        {[1, 2].map((i) => (
          <div key={i} className="h-44 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl animate-pulse" />
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
            <span className="text-xs font-mono text-black dark:text-white font-bold">DOSSIERS</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-950 dark:text-white flex items-center gap-2 font-sans">
            <FileText className="w-6 h-6 text-zinc-700 dark:text-zinc-300" />
            <span>Intelligence Dossier Studio</span>
          </h1>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
            Compile, review, and export court-admissible dossiers and executive briefings.
          </p>
        </div>

        <Badge variant="purple" size="md">
          <Shield className="w-3.5 h-3.5 mr-1" />
          Court-Admissible Standards
        </Badge>
      </div>

      {/* Report Builder: Generate from Investigation */}
      {investigations.length > 0 && (
        <Card className="border-zinc-200 dark:border-zinc-800">
          <CardContent className="p-4 sm:p-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <h3 className="text-xs font-bold text-zinc-900 dark:text-white">Generate New Dossier</h3>
                <p className="text-[11px] text-zinc-500 dark:text-zinc-400 font-mono">
                  Select an active investigation to compile a comprehensive intelligence dossier.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <select
                  className="h-9 px-3 rounded-md bg-white border border-zinc-200 text-xs text-zinc-800 focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white font-mono max-w-xs dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-200 shadow-2xs"
                  value={selectedInvId}
                  onChange={(e) => setSelectedInvId(e.target.value)}
                >
                  <option value="" disabled>
                    Select Investigation...
                  </option>
                  {investigations.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      {inv.title}
                    </option>
                  ))}
                </select>

                <Button
                  variant="primary"
                  size="sm"
                  isLoading={isGenerating}
                  disabled={!selectedInvId}
                  onClick={handleGenerateReport}
                >
                  <FileText className="w-3.5 h-3.5 mr-1" />
                  Generate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reports List */}
      <div className="space-y-3">
        {reports.length === 0 ? (
          <div className="text-center py-16 text-zinc-500 text-xs font-mono border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl">
            <FileText className="w-8 h-8 mx-auto mb-3 text-zinc-400 dark:text-zinc-600" />
            No dossiers generated. Create an investigation and generate a comprehensive dossier.
          </div>
        ) : (
          <>
            {paginatedReports.map((report) => (
              <Card key={report.id} className="hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
                <CardContent className="p-0">
                  {/* Report Summary Row */}
                  <button
                    className="w-full p-4 sm:p-5 flex items-start justify-between gap-4 text-left"
                    onClick={() => setExpandedReport(expandedReport === report.id ? null : report.id)}
                  >
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant={getStatusBadge(report.status)} size="sm">{report.status}</Badge>
                        <Badge variant={getTypeBadge(report.type)} size="sm">
                          {report.type.replace(/_/g, ' ')}
                        </Badge>
                        <Badge variant="mono" size="sm">{report.classification}</Badge>
                      </div>
                      <h3 className="text-sm font-bold text-zinc-950 dark:text-white">{report.title}</h3>
                      <div className="flex items-center gap-4 text-[11px] font-mono text-zinc-500 dark:text-zinc-400">
                        <span className="flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3 text-zinc-400" />
                          {report.finding_ids.length} Findings
                        </span>
                        <span className="flex items-center gap-1">
                          <Hash className="w-3 h-3 text-zinc-400" />
                          {report.evidence_citations.length} Evidence
                        </span>
                        <span className="flex items-center gap-1">
                          <Layers className="w-3 h-3 text-zinc-400" />
                          {report.entity_ids.length} Entities
                        </span>
                      </div>
                    </div>

                    <div className="shrink-0 text-zinc-400 mt-1">
                      {expandedReport === report.id ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </div>
                  </button>

                  {/* Expanded Dossier Detail */}
                  {expandedReport === report.id && (
                    <div className="px-5 pb-5 space-y-3 border-t border-zinc-100 dark:border-zinc-800 pt-3">
                      {/* Executive Summary */}
                      <div>
                        <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-1.5">
                          Executive Summary
                        </span>
                        <p className="text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed bg-zinc-50 border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800 p-3.5 rounded-lg">
                          {report.executive_summary}
                        </p>
                      </div>

                      {/* Author & Metadata */}
                      <div className="flex items-center gap-4 text-[11px] font-mono text-zinc-500 dark:text-zinc-400">
                        <span>Author: <strong className="text-zinc-800 dark:text-zinc-200">{report.author}</strong></span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-zinc-400" />
                          {formatDate(report.created_at)}
                        </span>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 pt-2 border-t border-zinc-100 dark:border-zinc-800">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleExportMarkdown(report.id);
                          }}
                        >
                          <Download className="w-3.5 h-3.5 mr-1" />
                          Export Markdown
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}

            {reports.length > pageSize && (
              <div className="pt-2">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  totalItems={reports.length}
                  pageSize={pageSize}
                  pageSizeOptions={[5, 10, 20, 50]}
                  onPageChange={setCurrentPage}
                  onPageSizeChange={(newSize) => {
                    setPageSize(newSize);
                    setCurrentPage(1);
                  }}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
