import React, { useState, useEffect, useMemo } from 'react';
import {
  FolderGit2,
  Plus,
  Search,
  ArrowRight,
  ShieldAlert,
  Clock,
  Layers,
  FileText,
  Globe,
  Radio,
  CheckCircle2,
  LayoutGrid,
  List,
  Copy,
  Check,
  Target,
  Shield,
  Activity,
  User,
  Send,
  Lock,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  X,
  Zap,
  Flame,
  Hash,
} from 'lucide-react';
import { Investigation, Evidence, Entity } from '../../types';
import { apiRequest } from '../../core/api/client';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Dialog } from '../../components/ui/Dialog';
import { formatDate, cn } from '../../lib/utils';
import { InvestigationDetailPage } from './InvestigationDetailPage';

interface InvestigationsPageProps {
  onNavigateToSearch?: (target: string, targetType?: string) => void;
  selectedInvestigationId?: string | null;
}

export const InvestigationsPage: React.FC<InvestigationsPageProps> = ({
  onNavigateToSearch,
  selectedInvestigationId,
}) => {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModuleTab, setSelectedModuleTab] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  // Pagination
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [moduleCounts, setModuleCounts] = useState<Record<string, number>>({
    all: 0,
    osint: 0,
    threat_intelligence: 0,
  });

  // Modals & Details
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedInv, setSelectedInv] = useState<Investigation | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailTab, setDetailTab] = useState<'overview' | 'entities' | 'evidence' | 'notes'>('overview');
  const [copiedTarget, setCopiedTarget] = useState<string | null>(null);

  // Linked items for selected investigation
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [entityList, setEntityList] = useState<Entity[]>([]);
  const [newNote, setNewNote] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);

  // New Investigation Form
  const [title, setTitle] = useState('');
  const [target, setTarget] = useState('');
  const [targetType, setTargetType] = useState('DOMAIN');
  const [priority, setPriority] = useState<'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'>('HIGH');
  const [summary, setSummary] = useState('');
  const [selectedModules, setSelectedModules] = useState<string[]>(['osint', 'threat_intelligence']);
  const [isCreating, setIsCreating] = useState(false);

  const fetchInvestigations = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      if (selectedModuleTab !== 'ALL') queryParams.append('module', selectedModuleTab);
      if (statusFilter !== 'ALL') queryParams.append('status', statusFilter);
      if (priorityFilter !== 'ALL') queryParams.append('priority', priorityFilter);
      if (searchTerm.trim()) queryParams.append('search', searchTerm.trim());

      const data = await apiRequest<{
        items: Investigation[];
        total: number;
        page: number;
        page_size: number;
        total_pages: number;
        module_counts: Record<string, number>;
      }>(`/investigations/paginated?${queryParams.toString()}`);

      if (data && Array.isArray(data.items)) {
        setInvestigations(data.items);
        setTotalItems(data.total);
        setTotalPages(data.total_pages);
        if (data.module_counts) {
          setModuleCounts(data.module_counts);
        }
      } else {
        // Fallback to plain list
        const fallback = await apiRequest<Investigation[]>('/investigations');
        setInvestigations(fallback || []);
        setTotalItems((fallback || []).length);
        setTotalPages(Math.ceil((fallback || []).length / pageSize) || 1);
      }
    } catch (err) {
      console.error('Failed to load investigations:', err);
      // Fallback
      try {
        const fallback = await apiRequest<Investigation[]>('/investigations');
        setInvestigations(fallback || []);
        setTotalItems((fallback || []).length);
      } catch (e) {
        console.error('Complete fallback failure', e);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigations();
  }, [page, pageSize, selectedModuleTab, statusFilter, priorityFilter, searchTerm]);

  // If a specific investigation was requested from navigation, open it in full workspace
  useEffect(() => {
    if (selectedInvestigationId) {
      const match = investigations.find((i) => i.id === selectedInvestigationId);
      if (match) {
        setSelectedInv(match);
      } else {
        apiRequest<Investigation>(`/investigations/${selectedInvestigationId}`)
          .then((inv) => setSelectedInv(inv))
          .catch((err) => console.error('Failed to load selected investigation', err));
      }
    }
  }, [selectedInvestigationId, investigations]);

  const fetchInvestigationDetails = (inv: Investigation) => {
    setSelectedInv(inv);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return;
    setIsCreating(true);

    try {
      const newInv = await apiRequest<Investigation>('/investigations', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim() || `Target Investigation: ${target.trim()}`,
          target: target.trim(),
          target_type: targetType,
          priority,
          summary: summary.trim(),
          description: summary.trim() || `Multi-engine intelligence investigation for ${target.trim()}`,
          selected_modules: selectedModules,
        }),
      });

      setIsCreateOpen(false);
      setTitle('');
      setTarget('');
      setSummary('');
      setPriority('HIGH');

      await fetchInvestigations();

      if (onNavigateToSearch) {
        onNavigateToSearch(newInv.target, newInv.target_type);
      } else {
        fetchInvestigationDetails(newInv);
      }
    } catch (err) {
      console.error('Failed to create investigation:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInv || !newNote.trim()) return;
    setIsSubmittingNote(true);

    try {
      const updated = await apiRequest<Investigation>(`/investigations/${selectedInv.id}/notes`, {
        method: 'POST',
        body: JSON.stringify({ content: newNote.trim() }),
      });
      setSelectedInv(updated);
      setInvestigations((prev) =>
        prev.map((inv) => (inv.id === updated.id ? updated : inv))
      );
      setNewNote('');
    } catch (err) {
      console.error('Failed to add note:', err);
    } finally {
      setIsSubmittingNote(false);
    }
  };

  const handleCopyTarget = (e: React.MouseEvent, text: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedTarget(text);
    setTimeout(() => setCopiedTarget(null), 2000);
  };

  const activeCasesCount = investigations.filter(
    (i) => i.status === 'open' || i.status === 'in_progress'
  ).length;

  if (selectedInv) {
    return (
      <InvestigationDetailPage
        investigationId={selectedInv.id}
        onBack={() => {
          setSelectedInv(null);
          fetchInvestigations();
        }}
        onNavigateToSearch={onNavigateToSearch}
      />
    );
  }

  return (
    <div className="w-full pb-12 space-y-6">
      {/* 1. HERO HEADER WITH ELEVATED BRANDING (SAAS APPLICATION INVESTIGATION) */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 shadow-xl border border-indigo-900/40">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 -mb-12 w-64 h-64 bg-rose-500/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-[11px] font-mono font-semibold text-indigo-200">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>UNIFIED INTELLIGENCE ORCHESTRATION</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
              <FolderGit2 className="w-8 h-8 text-indigo-400 shrink-0" />
              <span>Threat & Security Investigations</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Unified evidentiary workspace correlating OSINT reconnaissance findings, Cyber Threat Intelligence IOCs, Attack Surface discovery, and Vulnerability telemetry.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <Button
              variant="default"
              size="lg"
              onClick={() => setIsCreateOpen(true)}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/30 border border-indigo-400/30 transition-all flex items-center gap-2 px-5 py-2.5 h-auto rounded-xl cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>New Investigation</span>
            </Button>
          </div>
        </div>

        {/* 2. STATS KPI STRIP */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-6 border-t border-white/10">
          <div className="bg-white/5 backdrop-blur-md rounded-xl p-3 border border-white/10 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300">
              <FolderGit2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-mono font-bold text-white">
                {moduleCounts.all || totalItems}
              </div>
              <div className="text-[11px] text-slate-400 font-medium">Total Cases</div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-md rounded-xl p-3 border border-white/10 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-emerald-300">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-mono font-bold text-white">
                {moduleCounts.threat_intelligence ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 font-medium">Threat Intel Cases</div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-md rounded-xl p-3 border border-white/10 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-sky-500/20 border border-sky-400/30 flex items-center justify-center text-sky-300">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-mono font-bold text-white">
                {moduleCounts.osint ?? totalItems}
              </div>
              <div className="text-[11px] text-slate-400 font-medium">OSINT Recon Cases</div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-md rounded-xl p-3 border border-white/10 flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-mono font-bold text-white">
                {activeCasesCount || totalItems}
              </div>
              <div className="text-[11px] text-slate-400 font-medium">Active Operations</div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. DYNAMIC MODULE TABS BAR */}
      <div className="w-full bg-white dark:bg-[#0f1422] p-1.5 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs">
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-0.5 w-full">
          <button
            type="button"
            onClick={() => {
              setSelectedModuleTab('ALL');
              setPage(1);
            }}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold font-mono transition-all whitespace-nowrap border select-none cursor-pointer',
              selectedModuleTab === 'ALL'
                ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-950 dark:border-white shadow-md'
                : 'bg-white text-slate-700 border-slate-200/90 hover:border-slate-300 hover:text-slate-950 dark:bg-slate-950 dark:border-slate-800 dark:text-slate-300 dark:hover:text-white'
            )}
          >
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>All Investigations</span>
            <span
              className={cn(
                'text-[10px] px-1.5 py-0.2 rounded-md font-mono font-bold ml-0.5',
                selectedModuleTab === 'ALL'
                  ? 'bg-white/20 text-white dark:bg-black/20 dark:text-slate-950'
                  : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
              )}
            >
              {moduleCounts.all || totalItems}
            </span>
          </button>

          <button
            type="button"
            onClick={() => {
              setSelectedModuleTab('OSINT');
              setPage(1);
            }}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold font-mono transition-all whitespace-nowrap border select-none cursor-pointer',
              selectedModuleTab === 'OSINT'
                ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-600/20'
                : 'bg-white text-slate-700 border-slate-200/90 hover:border-slate-300 hover:text-slate-950 dark:bg-slate-950 dark:border-slate-800 dark:text-slate-300 dark:hover:text-white'
            )}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Open-Source Intelligence (OSINT)</span>
            <span
              className={cn(
                'text-[10px] px-1.5 py-0.2 rounded-md font-mono font-bold ml-0.5',
                selectedModuleTab === 'OSINT'
                  ? 'bg-white/20 text-white'
                  : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
              )}
            >
              {moduleCounts.osint ?? totalItems}
            </span>
          </button>

          <button
            type="button"
            onClick={() => {
              setSelectedModuleTab('THREAT_INTEL');
              setPage(1);
            }}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold font-mono transition-all whitespace-nowrap border select-none cursor-pointer',
              selectedModuleTab === 'THREAT_INTEL'
                ? 'bg-rose-600 text-white border-rose-600 shadow-md shadow-rose-600/20'
                : 'bg-white text-slate-700 border-slate-200/90 hover:border-slate-300 hover:text-slate-950 dark:bg-slate-950 dark:border-slate-800 dark:text-slate-300 dark:hover:text-white'
            )}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Cyber Threat Intelligence (CTI)</span>
            <span
              className={cn(
                'text-[10px] px-1.5 py-0.2 rounded-md font-mono font-bold ml-0.5',
                selectedModuleTab === 'THREAT_INTEL'
                  ? 'bg-white/20 text-white'
                  : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
              )}
            >
              {moduleCounts.threat_intelligence ?? 0}
            </span>
          </button>
        </div>
      </div>

      {/* 4. SEARCH, FILTER & VIEW CONTROLS */}
      <div className="w-full flex flex-col md:flex-row items-center justify-between gap-3 bg-white dark:bg-[#0f1422] p-3 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search targets, campaigns, infrastructure, IOCs..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full h-10 pl-10 pr-9 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 font-mono transition-colors"
          />
          {searchTerm && (
            <button
              onClick={() => {
                setSearchTerm('');
                setPage(1);
              }}
              className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2.5 w-full md:w-auto justify-between md:justify-end">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="h-10 px-3 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 focus:outline-none font-mono cursor-pointer"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active Cases</option>
            <option value="CLOSED">Closed Cases</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => {
              setPriorityFilter(e.target.value);
              setPage(1);
            }}
            className="h-10 px-3 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 focus:outline-none font-mono cursor-pointer"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">Critical Priority</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          {/* View Toggle */}
          <div className="flex items-center p-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-1.5 rounded-md transition-all cursor-pointer',
                viewMode === 'grid'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              )}
              title="Grid View"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={cn(
                'p-1.5 rounded-md transition-all cursor-pointer',
                viewMode === 'table'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              )}
              title="Dense Table View"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 5. LOADING STATE */}
      {loading && (
        <div className="flex flex-col items-center justify-center min-h-[30vh] gap-3 text-slate-500 font-mono text-xs">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
          <span>SYNCHRONIZING TENANT INVESTIGATIONS REGISTRY...</span>
        </div>
      )}

      {/* 6. EMPTY STATE */}
      {!loading && investigations.length === 0 && (
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 max-w-md mx-auto space-y-4 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto">
            <FolderGit2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">No Investigations Found</h3>
            <p className="text-xs text-slate-500 mt-1">
              Search any target from the top search bar or create a new case to initialize multi-engine telemetry.
            </p>
          </div>
          <Button
            variant="default"
            size="sm"
            onClick={() => setIsCreateOpen(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl"
          >
            <Plus className="w-3.5 h-3.5 mr-1" />
            Initialize Investigation
          </Button>
        </div>
      )}

      {/* 7. INVESTIGATION CARDS GRID VIEW */}
      {!loading && viewMode === 'grid' && investigations.length > 0 && (
        <div className="w-full grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {investigations.map((inv) => {
            const isCritical = inv.priority === 'CRITICAL';
            const isHigh = inv.priority === 'HIGH' || !inv.priority;
            const invModules = inv.selected_modules || ['osint', 'threat_intelligence'];

            return (
              <Card
                key={inv.id}
                onClick={() => fetchInvestigationDetails(inv)}
                className={cn(
                  'group relative overflow-hidden bg-white dark:bg-slate-900 cursor-pointer transition-all duration-200 rounded-2xl border shadow-xs hover:shadow-xl hover:-translate-y-0.5',
                  isCritical
                    ? 'border-rose-200 dark:border-rose-900/50 hover:border-rose-500'
                    : isHigh
                      ? 'border-amber-200 dark:border-amber-900/50 hover:border-amber-500'
                      : 'border-slate-200/80 dark:border-slate-800 hover:border-indigo-500'
                )}
              >
                {/* Accent Top Bar */}
                <div
                  className={cn(
                    'h-1.5 w-full transition-all duration-300',
                    isCritical
                      ? 'bg-rose-500'
                      : isHigh
                        ? 'bg-amber-500'
                        : 'bg-indigo-500'
                  )}
                />

                <CardContent className="p-5 flex flex-col justify-between h-full space-y-4">
                  <div className="space-y-3">
                    {/* Header Badges */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <Badge
                          variant={isCritical ? 'destructive' : isHigh ? 'warning' : 'outline'}
                          className="font-mono text-[10px] font-bold tracking-wider"
                        >
                          {inv.priority || 'HIGH'}
                        </Badge>
                        <Badge variant="outline" className="font-mono text-[10px] bg-slate-50 dark:bg-slate-800 uppercase">
                          {inv.target_type}
                        </Badge>

                        {/* Active Capability Tags */}
                        {invModules.map((mid) => {
                          const isTI = mid.toLowerCase().includes('threat') || mid.toLowerCase().includes('ti');
                          return (
                            <span
                              key={mid}
                              className={cn(
                                'text-[9px] font-mono font-bold px-2 py-0.5 rounded-md border flex items-center gap-1 tracking-tight',
                                isTI
                                  ? 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800'
                                  : 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-800'
                              )}
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-current" />
                              {isTI ? 'CTI' : 'OSINT'}
                            </span>
                          );
                        })}
                      </div>

                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[10px] font-mono font-bold uppercase text-slate-600 dark:text-slate-400">
                          {inv.status}
                        </span>
                      </div>
                    </div>

                    {/* Title & Target */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
                        {inv.title}
                      </h3>
                      <div className="flex items-center gap-1.5 mt-1">
                        <span className="text-[11px] font-mono text-slate-500">Target:</span>
                        <code className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                          {inv.target}
                        </code>
                        <button
                          onClick={(e) => handleCopyTarget(e, inv.target)}
                          className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-0.5 rounded transition-colors"
                          title="Copy target indicator"
                        >
                          {copiedTarget === inv.target ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed font-sans">
                      {inv.summary || inv.description || 'Unified intelligence workspace correlating reconnaissance observations with threat telemetry.'}
                    </p>
                  </div>

                  {/* Card Footer Telemetry */}
                  <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 font-mono">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1" title="Correlated Entities">
                        <Layers className="w-3.5 h-3.5 text-indigo-500" />
                        <strong className="text-slate-800 dark:text-slate-200">{inv.entity_ids?.length || 0}</strong> Ent
                      </span>
                      <span className="flex items-center gap-1" title="Cryptographic Evidence Items">
                        <Shield className="w-3.5 h-3.5 text-sky-500" />
                        <strong className="text-slate-800 dark:text-slate-200">{inv.evidence_ids?.length || 0}</strong> Ev
                      </span>
                      <span className="flex items-center gap-1" title="Investigation Notes">
                        <FileText className="w-3.5 h-3.5 text-emerald-500" />
                        <strong className="text-slate-800 dark:text-slate-200">{inv.notes?.length || 0}</strong> Notes
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {onNavigateToSearch && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onNavigateToSearch(inv.target, inv.target_type);
                          }}
                          className="px-2.5 py-1 rounded bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 text-[10px] font-bold border border-indigo-200 dark:border-indigo-800 flex items-center gap-1 transition-colors"
                          title="Run search on this target across 368 engines"
                        >
                          <Search className="w-3 h-3" />
                          <span>Investigate</span>
                        </button>
                      )}
                      <div className="flex items-center gap-1 text-slate-700 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors text-[11px] font-semibold">
                        <span>Details</span>
                        <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* 8. SOC ANALYST DENSE TABLE VIEW */}
      {!loading && viewMode === 'table' && investigations.length > 0 && (
        <div className="w-full bg-white dark:bg-[#0f1422] rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-slate-500 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4 font-bold">Investigation & Target</th>
                  <th className="py-3 px-3 font-bold">Capabilities</th>
                  <th className="py-3 px-3 font-bold">Priority</th>
                  <th className="py-3 px-3 font-bold">Entities</th>
                  <th className="py-3 px-3 font-bold">Evidence</th>
                  <th className="py-3 px-3 font-bold">Status</th>
                  <th className="py-3 px-4 font-bold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {investigations.map((inv) => {
                  const invModules = inv.selected_modules || ['osint', 'threat_intelligence'];
                  return (
                    <tr
                      key={inv.id}
                      onClick={() => fetchInvestigationDetails(inv)}
                      className="hover:bg-indigo-50/40 dark:hover:bg-indigo-950/20 cursor-pointer transition-colors"
                    >
                      <td className="py-3.5 px-4">
                        <div className="font-sans font-bold text-slate-900 dark:text-white text-xs">{inv.title}</div>
                        <div className="text-[11px] text-slate-500 font-mono mt-0.5 flex items-center gap-1.5">
                          <span className="uppercase">{inv.target_type}:</span>
                          <span className="font-semibold text-slate-800 dark:text-slate-200">{inv.target}</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-3">
                        <div className="flex items-center gap-1 flex-wrap">
                          {invModules.map((mid) => (
                            <span
                              key={mid}
                              className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
                            >
                              {mid.toLowerCase().includes('threat') ? 'CTI' : 'OSINT'}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3.5 px-3">
                        <Badge
                          variant={inv.priority === 'CRITICAL' ? 'destructive' : inv.priority === 'HIGH' ? 'warning' : 'outline'}
                          className="text-[10px]"
                        >
                          {inv.priority || 'HIGH'}
                        </Badge>
                      </td>
                      <td className="py-3.5 px-3 font-semibold text-slate-800 dark:text-slate-200">
                        {inv.entity_ids?.length || 0}
                      </td>
                      <td className="py-3.5 px-3 font-semibold text-slate-800 dark:text-slate-200">
                        {inv.evidence_ids?.length || 0}
                      </td>
                      <td className="py-3.5 px-3">
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase text-emerald-600 dark:text-emerald-400">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          {inv.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {onNavigateToSearch && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                onNavigateToSearch(inv.target, inv.target_type);
                              }}
                              className="text-xs h-7 px-2.5 rounded-lg"
                            >
                              <Search className="w-3 h-3 mr-1" />
                              <span>Search</span>
                            </Button>
                          )}
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              fetchInvestigationDetails(inv);
                            }}
                            className="text-xs h-7 px-2.5 rounded-lg"
                          >
                            <span>Open</span>
                            <ArrowRight className="w-3 h-3 ml-1" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 9. RESPONSIVE BACKEND PAGINATION BAR */}
      {!loading && totalItems > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200 dark:border-slate-800 text-xs font-mono">
          <div className="text-slate-500">
            Showing <strong className="text-slate-800 dark:text-slate-200">{(page - 1) * pageSize + 1}</strong> to{' '}
            <strong className="text-slate-800 dark:text-slate-200">{Math.min(page * pageSize, totalItems)}</strong> of{' '}
            <strong className="text-slate-800 dark:text-slate-200">{totalItems}</strong> cases
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-slate-500">
              <span className="text-[11px]">Rows:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="h-8 px-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-mono text-slate-800 dark:text-slate-200 cursor-pointer"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="h-8 px-2.5 rounded-lg text-xs"
              >
                <ChevronLeft className="w-3.5 h-3.5 mr-1" />
                <span>Prev</span>
              </Button>

              <div className="px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 font-bold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                {page} / {totalPages}
              </div>

              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="h-8 px-2.5 rounded-lg text-xs"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 10. ENHANCED MULTI-CAPABILITY INITIALIZATION MODAL */}
      <Dialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Initialize Multi-Capability Investigation"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Case / Operation Title
            </label>
            <input
              required
              type="text"
              placeholder="e.g. Operation Sovereign Trace: Target Recon"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Target Type
              </label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="w-full h-9 px-2 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs font-mono cursor-pointer"
              >
                <option value="DOMAIN">DOMAIN</option>
                <option value="IP">IP ADDRESS</option>
                <option value="EMAIL">EMAIL</option>
                <option value="USERNAME">USERNAME</option>
                <option value="HASH">MALWARE HASH</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Priority Level
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as any)}
                className="w-full h-9 px-2 rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs font-mono cursor-pointer"
              >
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Primary Target Indicator
            </label>
            <input
              required
              type="text"
              placeholder="e.g. target-c2.org, 185.220.101.42, or admin@target.com"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="w-full h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1.5">
              Capabilities To Dispatch
            </label>
            <div className="grid grid-cols-2 gap-2">
              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50">
                <input
                  type="checkbox"
                  checked={selectedModules.includes('osint')}
                  onChange={(e) => {
                    if (e.target.checked) setSelectedModules((prev) => [...prev, 'osint']);
                    else setSelectedModules((prev) => prev.filter((m) => m !== 'osint'));
                  }}
                  className="rounded text-indigo-600"
                />
                <span>OSINT (335 Engines)</span>
              </label>
              <label className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50">
                <input
                  type="checkbox"
                  checked={selectedModules.includes('threat_intelligence')}
                  onChange={(e) => {
                    if (e.target.checked) setSelectedModules((prev) => [...prev, 'threat_intelligence']);
                    else setSelectedModules((prev) => prev.filter((m) => m !== 'threat_intelligence'));
                  }}
                  className="rounded text-indigo-600"
                />
                <span>Threat Intel (33 Engines)</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Case Brief / Hypothesis
            </label>
            <textarea
              rows={3}
              placeholder="Case objectives, threat attribution hypotheses, and scope..."
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              className="w-full p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
            <Button type="button" variant="secondary" size="sm" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="default"
              size="sm"
              isLoading={isCreating}
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
            >
              Launch Case & Investigate
            </Button>
          </div>
        </form>
      </Dialog>

      {/* 11. CASE WORKSPACE DETAILS MODAL / DRAWER */}
      <Dialog
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title={selectedInv ? `${selectedInv.title}` : 'Investigation Workspace'}
      >
        {selectedInv && (
          <div className="space-y-4 max-h-[75vh] overflow-y-auto pr-1">
            {/* Target Header Bar */}
            <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="uppercase font-mono text-[10px]">
                  {selectedInv.target_type}
                </Badge>
                <code className="text-xs font-mono font-bold text-slate-900 dark:text-slate-100">
                  {selectedInv.target}
                </code>
              </div>

              {onNavigateToSearch && (
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => {
                    setDetailModalOpen(false);
                    onNavigateToSearch(selectedInv.target, selectedInv.target_type);
                  }}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-mono gap-1"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>Launch Full 368-Engine Reconnaissance →</span>
                </Button>
              )}
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-1 border-b border-slate-200 dark:border-slate-800 text-xs font-mono pb-1">
              {[
                { id: 'overview', label: 'Overview & Hypotheses' },
                { id: 'entities', label: `Correlated Entities (${selectedInv.entity_ids?.length || entityList.length})` },
                { id: 'evidence', label: `Evidence Vault (${selectedInv.evidence_ids?.length || evidenceList.length})` },
                { id: 'notes', label: `Case Notes (${selectedInv.notes?.length || 0})` },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setDetailTab(tab.id as any)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer',
                    detailTab === tab.id
                      ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-950 shadow-xs'
                      : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-100'
                  )}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab: Overview */}
            {detailTab === 'overview' && (
              <div className="space-y-3 font-mono text-xs">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <span className="text-[10px] text-slate-400 block uppercase">Status</span>
                    <strong className="text-emerald-600 uppercase">{selectedInv.status}</strong>
                  </div>
                  <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <span className="text-[10px] text-slate-400 block uppercase">Priority</span>
                    <strong className="text-amber-500 uppercase">{selectedInv.priority || 'HIGH'}</strong>
                  </div>
                  <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <span className="text-[10px] text-slate-400 block uppercase">Created By</span>
                    <span className="truncate block font-semibold text-slate-700 dark:text-slate-300">
                      {selectedInv.created_by}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <span className="text-[10px] text-slate-400 block uppercase">Created</span>
                    <span className="text-slate-500 text-[10px] block">
                      {formatDate(selectedInv.created_at)}
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Scope & Hypothesis</span>
                  <p className="text-slate-700 dark:text-slate-300 font-sans text-xs leading-relaxed">
                    {selectedInv.summary || selectedInv.description || 'No detailed scope provided.'}
                  </p>
                </div>
              </div>
            )}

            {/* Tab: Entities */}
            {detailTab === 'entities' && (
              <div className="space-y-2 font-mono text-xs">
                {entityList.length === 0 ? (
                  <div className="p-6 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-lg text-slate-400">
                    <span>No entities linked to this case file yet. Run an investigation search to correlate indicators.</span>
                  </div>
                ) : (
                  <div className="space-y-1.5 max-h-60 overflow-y-auto">
                    {entityList.map((ent, idx) => (
                      <div
                        key={idx}
                        className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-[9px] uppercase">
                            {ent.type}
                          </Badge>
                          <span className="font-semibold text-slate-900 dark:text-white break-all">
                            {ent.value}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400">
                          {ent.sources?.join(', ') || 'Correlated'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab: Evidence */}
            {detailTab === 'evidence' && (
              <div className="space-y-2 font-mono text-xs">
                {evidenceList.length === 0 ? (
                  <div className="p-6 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-lg text-slate-400">
                    <span>No cryptographic evidence items sealed in this case yet.</span>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {evidenceList.map((ev, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 dark:text-white uppercase text-[10px]">
                            {ev.provider || ev.module} • {ev.collection_method}
                          </span>
                          <span className="text-[9px] text-slate-400">{formatDate(ev.timestamp)}</span>
                        </div>
                        <div className="text-[10px] text-slate-500 truncate">
                          SHA256: <code>{ev.hash}</code>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab: Notes */}
            {detailTab === 'notes' && (
              <div className="space-y-3 font-mono text-xs">
                <form onSubmit={handleAddNote} className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Record analyst observation or lead..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    className="flex-1 h-9 px-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs"
                  />
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    isLoading={isSubmittingNote}
                    className="h-9 px-3 text-xs"
                  >
                    Add Note
                  </Button>
                </form>

                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {(selectedInv.notes || []).length === 0 ? (
                    <div className="p-4 text-center text-slate-400 text-xs">
                      No analyst notes recorded yet.
                    </div>
                  ) : (
                    (selectedInv.notes || []).map((n) => (
                      <div
                        key={n.id}
                        className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 space-y-1"
                      >
                        <div className="flex items-center justify-between text-[10px] text-slate-400">
                          <strong className="text-slate-700 dark:text-slate-300">{n.author_name}</strong>
                          <span>{formatDate(n.created_at)}</span>
                        </div>
                        <p className="text-slate-900 dark:text-slate-100 font-sans text-xs">{n.content}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
};
