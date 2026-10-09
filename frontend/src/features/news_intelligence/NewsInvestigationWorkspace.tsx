import React, { useState, useRef } from 'react';
import {
  ArrowLeft, RefreshCw, Briefcase, FileText, CheckCircle2, AlertTriangle,
  XCircle, HelpCircle, Shield, Share2, Clock, Video, Image as ImageIcon,
  ExternalLink, Layers, GitFork, Copy, Check, Download, Eye, Hash,
  ChevronDown, ChevronRight, MessageSquare, AlertOctagon, Sparkles, User, Globe
} from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { AddToCaseModal } from './AddToCaseModal';
import {
  NewsInvestigationRecord,
  useNewsInvestigation,
  useReanalyzeNewsInvestigation,
  useNewsInvestigationReport,
  ExtractedClaim,
  NewsEvidenceItem,
  VideoTimelineSegment
} from '../../core/api/newsHooks';
import { cn } from '../../lib/utils';

interface NewsInvestigationWorkspaceProps {
  investigationId: string;
  onBack: () => void;
}

export const NewsInvestigationWorkspace: React.FC<NewsInvestigationWorkspaceProps> = ({
  investigationId,
  onBack,
}) => {
  const { data: inv, isLoading, refetch } = useNewsInvestigation(investigationId);
  const reanalyzeMutation = useReanalyzeNewsInvestigation();
  const { data: report, refetch: fetchReport } = useNewsInvestigationReport(investigationId);

  const [activeTab, setActiveTab] = useState<
    'overview' | 'claims' | 'evidence' | 'lineage' | 'media' | 'timeline' | 'narratives' | 'report'
  >('overview');

  const [isCaseModalOpen, setIsCaseModalOpen] = useState(false);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [selectedVideoSegment, setSelectedVideoSegment] = useState<VideoTimelineSegment | null>(null);
  const [highlightedText, setHighlightedText] = useState<string>('');
  const [copiedReport, setCopiedReport] = useState(false);

  const evidenceRefs = useRef<Record<string, HTMLDivElement | null>>({});

  if (isLoading || !inv) {
    return (
      <div className="flex-1 flex items-center justify-center h-full">
        <div className="text-center space-y-3">
          <RefreshCw className="w-6 h-6 animate-spin text-emerald-500 mx-auto" />
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Synthesizing news intelligence pipeline...
          </p>
        </div>
      </div>
    );
  }

  const assessment = inv.assessment;
  const verdict = assessment?.verdict || 'UNVERIFIED';

  const getVerdictBadge = (v: string) => {
    switch (v) {
      case 'VERIFIED':
      case 'LIKELY TRUE':
        return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 text-xs px-2.5 py-1 font-bold">{v}</Badge>;
      case 'MISLEADING':
      case 'OUT OF CONTEXT':
        return <Badge variant="outline" className="bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30 text-xs px-2.5 py-1 font-bold">{v}</Badge>;
      case 'FALSE':
      case 'MANIPULATED':
        return <Badge variant="outline" className="bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30 text-xs px-2.5 py-1 font-bold">{v}</Badge>;
      default:
        return <Badge variant="outline" className="bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/30 text-xs px-2.5 py-1 font-bold">{v}</Badge>;
    }
  };

  const handleReasonClick = (evidenceId?: string) => {
    if (!evidenceId) return;
    setActiveTab('evidence');
    setSelectedEvidenceId(evidenceId);
    setTimeout(() => {
      const el = evidenceRefs.current[evidenceId];
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 150);
  };

  const handleTextSelection = () => {
    const sel = window.getSelection();
    if (sel && sel.toString().trim().length > 10) {
      setHighlightedText(sel.toString().trim());
    }
  };

  const copyReportToClipboard = () => {
    if (!report) return;
    const text = `
SENTIAL NEWS INTELLIGENCE REPORT
TITLE: ${report.title}
VERDICT: ${report.final_verdict}
ROOT QUERY: ${report.original_query}

EXECUTIVE ASSESSMENT:
${report.executive_assessment}

WHAT WAS CLAIMED:
${report.what_was_claimed}

WHAT EVIDENCE SHOWS:
${report.what_evidence_shows}

CONFIDENCE FACTORS:
- Evidence Quality: ${report.confidence_metrics.evidence_quality}%
- Source Independence: ${report.confidence_metrics.source_independence}%
- Temporal Consistency: ${report.confidence_metrics.temporal_consistency}%
- Media Verification: ${report.confidence_metrics.media_verification}%
- Cross-Source Corroboration: ${report.confidence_metrics.cross_source_corroboration}%
- Contradiction Strength: ${report.confidence_metrics.contradiction_strength}%
- Overall Confidence: ${report.confidence_metrics.overall_confidence}%

LIMITATIONS:
${report.limitations}
    `.trim();
    navigator.clipboard.writeText(text);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50/50 dark:bg-[#090d16]">
      {/* Top Header */}
      <div className="shrink-0 border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-[#0d121f]/95 backdrop-blur-md px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2.5">
            <button
              onClick={onBack}
              className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
              title="Return to Search"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <h1 className="text-base font-bold text-slate-900 dark:text-slate-100 font-sans tracking-tight">
              {inv.title || inv.artifact.title}
            </h1>
            {getVerdictBadge(verdict)}
            <Badge variant="outline" className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">
              {inv.status}
            </Badge>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center space-x-1">
              <span className="font-semibold text-slate-700 dark:text-slate-300">Root Query:</span>
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono font-bold">
                "{inv.original_query}"
              </span>
            </span>
            <span>•</span>
            <span>Source: <strong className="text-slate-700 dark:text-slate-300">{inv.artifact.publisher || inv.artifact.domain || 'External Wire'}</strong></span>
            <span>•</span>
            <span>Investigator: <strong className="text-slate-700 dark:text-slate-300">{inv.investigator_name}</strong></span>
            {assessment && (
              <>
                <span>•</span>
                <span className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 font-semibold">
                  <Shield className="w-3.5 h-3.5" />
                  <span>Explainable Confidence: {assessment.confidence_breakdown.overall_confidence.toFixed(0)}%</span>
                </span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <Button
            size="sm"
            variant="outline"
            onClick={() => reanalyzeMutation.mutate(inv.id)}
            disabled={reanalyzeMutation.isPending}
            className="text-xs"
          >
            <RefreshCw className={cn("w-3.5 h-3.5 mr-1.5", reanalyzeMutation.isPending && "animate-spin")} />
            Re-Analyze
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsCaseModalOpen(true)}
            className="text-xs text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10"
          >
            <Briefcase className="w-3.5 h-3.5 mr-1.5" />
            Add to Case
          </Button>

          <Button
            size="sm"
            variant="default"
            onClick={() => {
              setActiveTab('report');
              fetchReport();
            }}
            className="text-xs bg-slate-900 hover:bg-slate-800 text-white dark:bg-emerald-600 dark:hover:bg-emerald-700"
          >
            <FileText className="w-3.5 h-3.5 mr-1.5" />
            Executive Report
          </Button>
        </div>
      </div>

      {/* Prominent "Why is this misleading?" Banner */}
      {assessment && assessment.why_misleading_reasons.length > 0 && (
        <div className="shrink-0 bg-amber-500/10 border-b border-amber-500/20 px-6 py-3">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <div className="p-1 rounded bg-amber-500/20 text-amber-600 dark:text-amber-400 mt-0.5">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300">
                    Why is this content misleading / out of context?
                  </h3>
                  <span className="text-[11px] font-semibold text-amber-700 dark:text-amber-400">
                    ({assessment.confidence_breakdown.overall_confidence.toFixed(0)}% Confidence)
                  </span>
                </div>
                <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                  {assessment.primary_reason}
                </p>
                <div className="flex flex-wrap gap-2 pt-1">
                  {assessment.why_misleading_reasons.map((reason) => (
                    <button
                      key={reason.id}
                      onClick={() => handleReasonClick(reason.linked_evidence_id)}
                      className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-amber-500/20 hover:bg-amber-500/30 text-amber-900 dark:text-amber-200 border border-amber-500/30 transition-colors flex items-center space-x-1.5 cursor-pointer text-left"
                    >
                      <Eye className="w-3 h-3 text-amber-600 dark:text-amber-400 shrink-0" />
                      <span>{reason.summary_text}</span>
                      <ChevronRight className="w-3 h-3 opacity-60 shrink-0" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="shrink-0 px-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0c101c] flex space-x-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Overview & Context Verification', icon: Eye },
          { id: 'claims', label: `Claims Matrix (${inv.claims.length})`, icon: MessageSquare },
          { id: 'evidence', label: `Evidence Vault (${inv.evidence_vault.length})`, icon: Shield },
          { id: 'lineage', label: 'Source Lineage & Copycats', icon: GitFork },
          { id: 'media', label: 'Media Forensics & Video Timeline', icon: Video },
          { id: 'timeline', label: `Temporal Timeline (${inv.timeline.length})`, icon: Clock },
          { id: 'narratives', label: `Narrative Clusters (${inv.narratives.length})`, icon: Layers },
          { id: 'report', label: '16-Section Executive Report', icon: FileText },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                'flex items-center space-x-2 py-3 px-3.5 text-xs font-semibold border-b-2 transition-colors whitespace-nowrap cursor-pointer',
                isActive
                  ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5'
                  : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: In-App Article Reader */}
        <div className="w-1/2 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0b0f19] flex flex-col overflow-hidden">
          <div className="shrink-0 px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/40 flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5 text-emerald-500" />
              <span>In-App Article & Artifact Reader</span>
            </span>
            {inv.artifact.canonical_url && (
              <span className="text-[11px] font-mono text-slate-400 truncate max-w-xs">
                {inv.artifact.domain || inv.artifact.canonical_url}
              </span>
            )}
          </div>

          <div
            className="flex-1 p-6 overflow-y-auto space-y-4 select-text"
            onMouseUp={handleTextSelection}
          >
            {highlightedText && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-700 dark:text-emerald-300 flex items-center justify-between animate-in fade-in">
                <div className="truncate mr-2">
                  <span className="font-bold">Investigate Selected Claim:</span> "{highlightedText}"
                </div>
                <Button
                  size="sm"
                  variant="default"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] h-6 px-2 shrink-0"
                  onClick={() => {
                    setActiveTab('claims');
                    setHighlightedText('');
                  }}
                >
                  Analyze Claim
                </Button>
              </div>
            )}

            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 font-sans leading-tight">
                {inv.artifact.title}
              </h2>
              {inv.artifact.subtitle && (
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 italic">
                  {inv.artifact.subtitle}
                </p>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3 py-2 border-y border-slate-100 dark:border-slate-800/80 text-xs text-slate-500">
              {inv.artifact.author && (
                <span>By <strong className="text-slate-700 dark:text-slate-300">{inv.artifact.author}</strong></span>
              )}
              {inv.artifact.publication_date && (
                <span>Published: {inv.artifact.publication_date}</span>
              )}
              <span>Publisher: <strong className="text-slate-700 dark:text-slate-300">{inv.artifact.publisher || 'Unknown'}</strong></span>
            </div>

            {/* Extracted Media Preview */}
            {inv.artifact.extracted_videos.length > 0 && (
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-900 text-slate-100 space-y-2">
                <div className="flex items-center space-x-2 text-xs text-emerald-400 font-bold">
                  <Video className="w-4 h-4" />
                  <span>Associated Media Feed</span>
                </div>
                <div className="h-44 bg-slate-800/80 rounded-lg flex flex-col items-center justify-center text-center p-4">
                  <Video className="w-10 h-10 text-slate-500 mb-2" />
                  <span className="text-xs text-slate-300 font-medium font-mono">
                    {inv.artifact.extracted_videos[0]}
                  </span>
                  <span className="text-[10px] text-slate-400 mt-1">
                    Frame-by-frame forensics available in Media Forensics tab
                  </span>
                </div>
              </div>
            )}

            {/* Article Body Paragraphs */}
            <div className="space-y-3.5 text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
              {inv.artifact.paragraphs && inv.artifact.paragraphs.length > 0 ? (
                inv.artifact.paragraphs.map((p, idx) => (
                  <p key={idx} className="relative group p-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-900/60 transition-colors">
                    {p}
                  </p>
                ))
              ) : (
                <p className="whitespace-pre-wrap">{inv.artifact.article_body}</p>
              )}
            </div>

            {/* Extracted quotes & stats summary */}
            {(inv.artifact.quoted_individuals.length > 0 || inv.artifact.cited_statistics.length > 0) && (
              <div className="pt-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
                {inv.artifact.quoted_individuals.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Attributed Quotes & Key Speakers
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {inv.artifact.quoted_individuals.map((q, i) => (
                        <span key={i} className="px-2 py-0.5 rounded text-[11px] bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          "{q}"
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {inv.artifact.cited_statistics.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Cited Statistics
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {inv.artifact.cited_statistics.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 rounded text-[11px] bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20 font-mono">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: Specialized Investigation Tabs */}
        <div className="w-1/2 bg-slate-50/50 dark:bg-[#0c101d] flex flex-col overflow-hidden">
          <div className="flex-1 p-6 overflow-y-auto">
            {/* TAB 1: OVERVIEW & CONTEXT VERIFICATION */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* 8 Core Context Verification Questions */}
                <div className="space-y-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                    <Shield className="w-4 h-4 text-emerald-500" />
                    <span>Context Verification Matrix (8 Core Questions)</span>
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {[
                      { q: 'WHAT IS CLAIMED?', key: 'what_is_claimed', val: assessment?.context_verification?.what_is_claimed || 'Content asserts event took place as described.' },
                      { q: 'WHAT ACTUALLY HAPPENED?', key: 'what_actually_happened', val: assessment?.context_verification?.what_actually_happened || 'Archived records confirm earlier origin.' },
                      { q: 'WHEN DID IT OCCUR?', key: 'when_did_it_occur', val: assessment?.context_verification?.when_did_it_occur || 'Chronological mismatch identified.' },
                      { q: 'WHERE DID IT OCCUR?', key: 'where_did_it_occur', val: assessment?.context_verification?.where_did_it_occur || 'Location mismatch detected against claim.' },
                      { q: 'WHO IS INVOLVED?', key: 'who_is_involved', val: assessment?.context_verification?.who_is_involved || 'Entities verified against registry.' },
                      { q: 'ORIGINAL SOURCE?', key: 'original_source', val: assessment?.context_verification?.original_source || 'First recorded instance traced in archive.' },
                      { q: 'WHAT SUPPORTS IT?', key: 'what_supports_it', val: assessment?.context_verification?.what_supports_it || 'Cross-source corroboration evaluated.' },
                      { q: 'WHAT CONTRADICTS IT?', key: 'what_contradicts_it', val: assessment?.context_verification?.what_contradicts_it || 'Documented timeline & metadata discrepancies.' },
                    ].map((item, i) => (
                      <div key={i} className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] space-y-1">
                        <span className="text-[10px] font-mono font-bold text-emerald-600 dark:text-emerald-400">
                          {item.q}
                        </span>
                        <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                          {item.val}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Explainable Confidence Factors */}
                {assessment && (
                  <div className="space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                      <Sparkles className="w-4 h-4 text-emerald-500" />
                      <span>Measurable Confidence Factors</span>
                    </h3>

                    <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                        <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          Overall Assessment Confidence
                        </span>
                        <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                          {assessment.confidence_breakdown.overall_confidence.toFixed(0)}%
                        </span>
                      </div>

                      <div className="space-y-2 text-xs">
                        {[
                          { label: 'Evidence Quality', score: assessment.confidence_breakdown.evidence_quality },
                          { label: 'Source Independence', score: assessment.confidence_breakdown.source_independence },
                          { label: 'Temporal Consistency', score: assessment.confidence_breakdown.temporal_consistency },
                          { label: 'Media Verification', score: assessment.confidence_breakdown.media_verification },
                          { label: 'Cross-Source Corroboration', score: assessment.confidence_breakdown.cross_source_corroboration },
                          { label: 'Contradiction Strength', score: assessment.confidence_breakdown.contradiction_strength },
                        ].map((row, idx) => (
                          <div key={idx} className="space-y-1">
                            <div className="flex justify-between text-[11px] text-slate-600 dark:text-slate-400">
                              <span>{row.label}</span>
                              <span className="font-mono font-bold text-slate-900 dark:text-slate-200">{row.score.toFixed(0)}%</span>
                            </div>
                            <div className="h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                              <div
                                className="h-full bg-emerald-500 rounded-full transition-all duration-300"
                                style={{ width: `${Math.min(100, Math.max(0, row.score))}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: CLAIMS MATRIX */}
            {activeTab === 'claims' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                    Extracted Factual Claims ({inv.claims.length})
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    Each claim is independently verifiable
                  </span>
                </div>

                <div className="space-y-3">
                  {inv.claims.map((claim) => (
                    <div
                      key={claim.id}
                      className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] space-y-2.5 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-[10px] font-mono uppercase bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {claim.claim_type}
                          </Badge>
                          <span className="text-[10px] font-mono text-slate-400">{claim.id}</span>
                        </div>
                        <Badge
                          variant="outline"
                          className={cn(
                            "text-[10px] font-bold",
                            claim.status === 'VERIFIED' ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30' :
                            claim.status === 'MISLEADING' ? 'bg-amber-500/10 text-amber-600 border-amber-500/30' :
                            'bg-slate-500/10 text-slate-600 border-slate-500/30'
                          )}
                        >
                          {claim.status} ({claim.confidence.toFixed(0)}%)
                        </Badge>
                      </div>

                      <p className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                        "{claim.claim_text}"
                      </p>

                      <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-800/80">
                        {claim.provenance_reference && (
                          <span>Provenance: <strong className="text-slate-700 dark:text-slate-300 font-mono">{claim.provenance_reference}</strong></span>
                        )}
                        <span>Supporting Ev.: <strong className="text-emerald-600">{claim.supporting_evidence_ids.length}</strong></span>
                        <span>Contradicting Ev.: <strong className="text-rose-600">{claim.contradicting_evidence_ids.length}</strong></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 3: EVIDENCE VAULT */}
            {activeTab === 'evidence' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                    Evidence Vault Items ({inv.evidence_vault.length})
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    Unified with platform Evidence Vault
                  </span>
                </div>

                <div className="space-y-3">
                  {inv.evidence_vault.map((ev) => {
                    const isSelected = selectedEvidenceId === ev.id;
                    return (
                      <div
                        key={ev.id}
                        ref={(el) => { evidenceRefs.current[ev.id] = el; }}
                        className={cn(
                          "p-4 rounded-xl border transition-all space-y-2.5",
                          isSelected
                            ? "border-emerald-500 bg-emerald-500/5 shadow-md ring-2 ring-emerald-500/20"
                            : "border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424]"
                        )}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-0.5">
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline" className="text-[10px] font-mono bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20">
                                {ev.evidence_type}
                              </Badge>
                              <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                                {ev.title}
                              </span>
                            </div>
                            <span className="text-[11px] text-slate-500 dark:text-slate-400">
                              Source: <strong>{ev.source}</strong> {ev.publisher ? `(${ev.publisher})` : ''}
                            </span>
                          </div>

                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[10px] font-mono",
                              ev.claim_relationship === 'DIRECTLY_RELEVANT' ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30' :
                              ev.claim_relationship === 'RELATED' ? 'bg-sky-500/10 text-sky-600 border-sky-500/30' :
                              'bg-slate-500/10 text-slate-500'
                            )}
                          >
                            {ev.claim_relationship}
                          </Badge>
                        </div>

                        {/* Critical Explanation: WHY WAS THIS EVIDENCE FOUND? */}
                        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 space-y-1">
                          <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center space-x-1">
                            <Sparkles className="w-3 h-3" />
                            <span>Why was this evidence found?</span>
                          </div>
                          <p className="font-mono text-[11px] text-slate-800 dark:text-slate-200">
                            {ev.retrieval_reason}
                          </p>
                        </div>

                        <p className="text-xs text-slate-600 dark:text-slate-400 italic">
                          "{ev.extracted_text}"
                        </p>

                        <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-800/80">
                          <span className="font-mono flex items-center space-x-1">
                            <Hash className="w-3 h-3" />
                            <span>SHA256: {ev.hash_value.substring(0, 16)}...</span>
                          </span>
                          <span>Reliability: <strong className="text-slate-700 dark:text-slate-300">{ev.reliability_score.toFixed(0)}%</strong></span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 4: SOURCE LINEAGE & DUPLICATION */}
            {activeTab === 'lineage' && (
              <div className="space-y-4">
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300 flex items-start space-x-2">
                  <AlertOctagon className="w-4 h-4 mt-0.5 shrink-0" />
                  <div>
                    <span className="font-bold">Source Independence Principle:</span> Ten websites copying or rewriting the same syndicated press release are NOT ten independent confirmations. Lineage detection traces origin to prevent artificial amplification.
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                    Lineage Nodes & Amplification Paths
                  </h4>
                  <div className="space-y-2">
                    {inv.source_lineage_nodes.map((node) => (
                      <div
                        key={node.id}
                        className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] flex items-center justify-between"
                      >
                        <div className="flex items-center space-x-3">
                          <div className={cn(
                            "w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold font-mono",
                            node.node_type === 'ORIGINAL_SOURCE' ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/30" :
                            node.node_type === 'PRIMARY_ARTICLE' ? "bg-sky-500/10 text-sky-600 border border-sky-500/30" :
                            "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                          )}>
                            {node.amplification_rank}
                          </div>
                          <div>
                            <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                              {node.label}
                            </span>
                            <div className="flex items-center space-x-2 text-[11px] text-slate-500">
                              <span>Type: {node.node_type}</span>
                              {node.published_at && <span>• {node.published_at}</span>}
                            </div>
                          </div>
                        </div>

                        <Badge
                          variant="outline"
                          className={cn(
                            "text-[10px] font-bold",
                            node.is_independent ? "text-emerald-600 border-emerald-500/30" : "text-amber-600 border-amber-500/30"
                          )}
                        >
                          {node.is_independent ? 'INDEPENDENT' : 'SYNDICATED / REPRINT'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 5: MEDIA FORENSICS & VIDEO TIMELINE */}
            {activeTab === 'media' && (
              <div className="space-y-5">
                {inv.video_forensics ? (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                          Video Contextual Verification
                        </span>
                        <Badge
                          variant="outline"
                          className={cn(
                            "text-xs font-bold",
                            inv.video_forensics.is_authentic_media_false_context
                              ? "bg-amber-500/10 text-amber-600 border-amber-500/30"
                              : "bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
                          )}
                        >
                          {inv.video_forensics.is_authentic_media_false_context
                            ? "AUTHENTIC MEDIA + FALSE CONTEXT"
                            : inv.video_forensics.is_manipulated_media
                            ? "MANIPULATED MEDIA"
                            : "AUTHENTIC VERIFIED"}
                        </Badge>
                      </div>

                      <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                        {inv.video_forensics.contextual_verdict}
                      </p>

                      <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
                        <div>Earliest Appearance: <strong>{inv.video_forensics.earliest_known_appearance || 'N/A'}</strong></div>
                        <div>Original Source: <strong>{inv.video_forensics.earliest_source || 'N/A'}</strong></div>
                        <div className="font-mono text-[11px]">Perceptual Hash: {inv.video_forensics.perceptual_fingerprint.substring(0, 16)}...</div>
                        <div className="font-mono text-[11px]">SHA256: {inv.video_forensics.sha256_hash.substring(0, 16)}...</div>
                      </div>
                    </div>

                    {/* Interactive Video Evidence Timeline */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                        Interactive Video Evidence Timeline
                      </h4>
                      <p className="text-[11px] text-slate-400">
                        Clicking a timeline section reveals detected scene attributes, OCR text, and reused archival segments.
                      </p>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-1">
                        {inv.video_forensics.timeline_segments.map((seg, idx) => {
                          const isSel = selectedVideoSegment?.start_timestamp === seg.start_timestamp;
                          return (
                            <button
                              key={idx}
                              onClick={() => setSelectedVideoSegment(seg)}
                              className={cn(
                                "p-3 rounded-xl border text-left transition-all cursor-pointer space-y-1.5",
                                isSel
                                  ? "border-emerald-500 bg-emerald-500/10 shadow-sm"
                                  : "border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] hover:border-slate-300"
                              )}
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-[11px] font-mono font-bold text-emerald-600 dark:text-emerald-400">
                                  {seg.start_timestamp} – {seg.end_timestamp}
                                </span>
                                <Badge variant="outline" className="text-[9px] font-mono">
                                  {seg.detection_type}
                                </Badge>
                              </div>
                              <span className="text-xs font-bold text-slate-900 dark:text-slate-100 block">
                                {seg.segment_title}
                              </span>
                              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                                {seg.description}
                              </p>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="py-12 text-center text-xs text-slate-400">
                    No video media associated with this investigation artifact.
                  </div>
                )}
              </div>
            )}

            {/* TAB 6: TEMPORAL TIMELINE */}
            {activeTab === 'timeline' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                    Chronological Intelligence Timeline ({inv.timeline.length} Events)
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    Detects recycled content presented as new
                  </span>
                </div>

                <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
                  {inv.timeline.map((event) => (
                    <div key={event.id} className="relative space-y-1">
                      <div className={cn(
                        "absolute -left-6 top-1 w-3 h-3 rounded-full border-2 bg-white dark:bg-slate-900",
                        event.is_contradiction ? "border-rose-500" :
                        event.event_category === 'FIRST_KNOWN_APPEARANCE' ? "border-emerald-500" :
                        "border-slate-400"
                      )} />
                      <div className="flex items-center space-x-2">
                        <span className="text-[11px] font-mono font-bold text-emerald-600 dark:text-emerald-400">
                          {event.timestamp_label}
                        </span>
                        <Badge variant="outline" className="text-[10px] font-mono">
                          {event.event_category}
                        </Badge>
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        {event.title}
                      </h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        {event.description}
                      </p>
                      <span className="text-[10px] text-slate-400 block">
                        Source/Actor: {event.actor_or_source}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 7: NARRATIVE CLUSTERS */}
            {activeTab === 'narratives' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                    Detected Narrative Clusters ({inv.narratives.length})
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    Scoped strictly to original query
                  </span>
                </div>

                <div className="space-y-3">
                  {inv.narratives.map((nar) => (
                    <div
                      key={nar.id}
                      className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0e1424] space-y-2.5"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                            {nar.narrative_title}
                          </h4>
                          <span className="text-[11px] text-slate-500">
                            Framing: <strong>{nar.framing_angle}</strong>
                          </span>
                        </div>
                        <Badge variant="outline" className="text-[10px] text-emerald-600 border-emerald-500/30">
                          Velocity: {nar.amplification_speed}
                        </Badge>
                      </div>

                      <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                        "{nar.core_assertion}"
                      </p>

                      {nar.counter_evidence_summary && (
                        <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300">
                          <strong>Counter-Evidence Summary:</strong> {nar.counter_evidence_summary}
                        </div>
                      )}

                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        {nar.associated_entities.map((e, idx) => (
                          <span key={idx} className="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {e}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 8: 16-SECTION EXECUTIVE REPORT */}
            {activeTab === 'report' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      16-Section Evidence-First Investigation Report
                    </h3>
                    <span className="text-[11px] text-slate-400">
                      Objective, structured dossier ready for intelligence dissemination
                    </span>
                  </div>

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={copyReportToClipboard}
                    className="text-xs text-emerald-600 dark:text-emerald-400"
                  >
                    {copiedReport ? (
                      <>
                        <Check className="w-3.5 h-3.5 mr-1 text-emerald-500" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 mr-1" />
                        Copy Report
                      </>
                    )}
                  </Button>
                </div>

                {report ? (
                  <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0d121f] space-y-4 text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
                    <div className="border-b border-slate-100 dark:border-slate-800 pb-3">
                      <span className="text-[10px] font-mono uppercase text-slate-400">Section 1: Executive Assessment</span>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1">
                        {report.title}
                      </h4>
                      <p className="mt-1 text-slate-700 dark:text-slate-300">
                        {report.executive_assessment}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
                      <div>
                        <span className="text-[10px] font-mono uppercase text-slate-400">Section 5: What Was Claimed</span>
                        <p className="mt-1 font-medium">{report.what_was_claimed}</p>
                      </div>
                      <div>
                        <span className="text-[10px] font-mono uppercase text-slate-400">Section 6: What Evidence Shows</span>
                        <p className="mt-1 font-medium text-emerald-600 dark:text-emerald-400">{report.what_evidence_shows}</p>
                      </div>
                    </div>

                    <div className="space-y-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                      <span className="text-[10px] font-mono uppercase text-slate-400">Section 7 & 8: Source and Media Forensics</span>
                      <p>{report.source_analysis}</p>
                      <p>{report.media_analysis}</p>
                    </div>

                    <div className="space-y-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                      <span className="text-[10px] font-mono uppercase text-slate-400">Section 9 & 10: Timeline & Narrative Analysis</span>
                      <p>{report.timeline_summary}</p>
                      <p>{report.narrative_analysis}</p>
                    </div>

                    <div className="border-b border-slate-100 dark:border-slate-800 pb-3">
                      <span className="text-[10px] font-mono uppercase text-slate-400">Section 15: Limitations & Gaps</span>
                      <p className="mt-1 text-slate-500 italic">{report.limitations}</p>
                    </div>

                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-400">Section 16: Final Assessment</span>
                      <div className="mt-1.5 flex items-center space-x-2">
                        {getVerdictBadge(report.final_verdict)}
                        <span className="font-semibold text-slate-700 dark:text-slate-300">
                          Backed by {report.supporting_evidence.length} supporting and {report.contradicting_evidence.length} contradicting evidence records.
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="py-8 text-center text-xs text-slate-400">
                    Generating report dossier...
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add To Case Modal */}
      <AddToCaseModal
        isOpen={isCaseModalOpen}
        onClose={() => setIsCaseModalOpen(false)}
        investigationId={inv.id}
        investigationTitle={inv.title || inv.artifact.title}
      />
    </div>
  );
};
