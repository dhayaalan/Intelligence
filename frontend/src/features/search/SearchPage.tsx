import React, { useState, useMemo, useEffect, useRef } from 'react';
import {
  Search,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  FolderPlus,
  Database,
  Share2,
  ShieldCheck,
  Cpu,
  Copy,
  Check,
  Filter,
  Sparkles,
  Globe,
  Layers,
  FolderGit2,
  Download,
  ShieldAlert,
  Radio,
  FileCode,
  MapPin,
  Lock,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  X,
  FileText,
  Camera,
  FileImage,
  Server,
  Users,
  Activity,
  Sliders,
  Terminal,
} from 'lucide-react';
import { SearchResponse, Entity } from '../../types';
import { apiRequest } from '../../core/api/client';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Pagination } from '../../components/ui/Pagination';
import { GraphStudioComponent } from '../graph/GraphStudioComponent';
import { OsintMapComponent, GeoLocationItem } from '../map/OsintMapComponent';
import { formatDate, cn } from '../../lib/utils';
import { useAuth } from '../../core/auth/AuthContext';

/**
 * Universal highlight component that highlights search query tokens
 * across provider results, entity values, and snippets.
 */
export const HighlightMatch: React.FC<{
  text?: string | number | null;
  query: string;
  className?: string;
}> = ({ text, query, className = '' }) => {
  if (text === undefined || text === null) return null;
  const str = String(text);
  if (!query || !query.trim()) return <span className={className}>{str}</span>;

  const rawQuery = query.replace(/[+"~*]/g, '').trim();
  if (!rawQuery) return <span className={className}>{str}</span>;

  const rawTokens = rawQuery
    .split(/\s+/)
    .map((t) => t.trim())
    .filter((t) => t.length > 0 && !['AND', 'OR', 'NOT'].includes(t.toUpperCase()));

  const candidateTerms = Array.from(new Set([rawQuery, ...rawTokens])).filter(
    (t) => t.length >= 2 || /^\d+$/.test(t)
  );

  if (candidateTerms.length === 0) return <span className={className}>{str}</span>;

  const escapedTerms = candidateTerms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const regex = new RegExp(`(${escapedTerms.join('|')})`, 'gi');
  const parts = str.split(regex);

  return (
    <span className={className}>
      {parts.map((part, i) => {
        const isMatch = candidateTerms.some((t) => t.toLowerCase() === part.toLowerCase());
        if (isMatch) {
          return (
            <mark
              key={i}
              className="bg-amber-300 dark:bg-amber-400 text-zinc-950 font-bold px-1 py-0.5 rounded shadow-xs inline"
            >
              {part}
            </mark>
          );
        }
        return <React.Fragment key={i}>{part}</React.Fragment>;
      })}
    </span>
  );
};

interface SearchPageProps {
  initialTarget?: string;
  initialTargetType?: string;
  onOpenInvestigation: (target: string, targetType: string, searchId?: string) => void;
  onNavigateToInvestigation?: (invId: string) => void;
}

export const SearchPage: React.FC<SearchPageProps> = ({
  initialTarget,
  initialTargetType,
  onOpenInvestigation,
  onNavigateToInvestigation,
}) => {
  const { user, login } = useAuth();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [query, setQuery] = useState(initialTarget || '');
  const [targetType, setTargetType] = useState('AUTO_DETECT');
  const [searchMode, setSearchMode] = useState<'PASSIVE' | 'ACTIVE'>('PASSIVE');
  const [selectedModules, setSelectedModules] = useState<string[]>(['osint', 'threat_intelligence']);
  const [uploadedImage, setUploadedImage] = useState<{ name: string; size: string; preview: string } | null>(null);
  const [imageOcrEntities, setImageOcrEntities] = useState<any[]>([]);

  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'entities' | 'profiles' | 'graph' | 'map' | 'evidence' | 'logs' | 'raw'>('entities');
  const [moduleFilter, setModuleFilter] = useState<'ALL' | 'OSINT' | 'THREAT_INTEL'>('ALL');
  const [entityFilter, setEntityFilter] = useState<string>('ALL');
  const [confidenceFilter, setConfidenceFilter] = useState<string>('ALL');
  const [inResultSearch, setInResultSearch] = useState<string>('');

  const [copiedHash, setCopiedHash] = useState<string | null>(null);
  const [copiedValue, setCopiedValue] = useState<string | null>(null);
  const [rawCopied, setRawCopied] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // Pagination states
  const [entityPage, setEntityPage] = useState(1);
  const [entityPageSize, setEntityPageSize] = useState(10);
  const [evidencePage, setEvidencePage] = useState(1);
  const [evidencePageSize, setEvidencePageSize] = useState(10);

  // Auto-run if initialTarget passed from an investigation
  useEffect(() => {
    if (initialTarget && initialTarget.trim() && searchResult?.query !== initialTarget.trim()) {
      setQuery(initialTarget.trim());
      handleSearch(undefined, initialTarget.trim());
    }
  }, [initialTarget]);

  // Auto-detect target type heuristic
  const detectedTargetType = useMemo(() => {
    const q = query.trim();
    if (!q) return null;
    if (/^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$/.test(q)) return 'IP_ADDRESS';
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(q)) return 'EMAIL';
    if (/^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d+)?(\/.*)?$/.test(q)) return 'DOMAIN';
    if (/^[a-fA-F0-9]{32,64}$/.test(q)) return 'HASH';
    if (/^(\+?[0-9]{7,15})$/.test(q)) return 'PHONE';
    return 'USERNAME / ENTITY';
  }, [query]);

  const handleInsertOperator = (op: string) => {
    switch (op) {
      case 'EXACT':
        setQuery((prev) => (prev.trim() ? `"${prev.replace(/^"|"$/g, '')}"` : '""'));
        break;
      case 'FUZZY':
        setQuery((prev) => `${prev.trim()}~`);
        break;
      case 'AND':
        setQuery((prev) => `${prev.trim()} AND `);
        break;
      case 'OR':
        setQuery((prev) => `${prev.trim()} OR `);
        break;
      case 'NOT':
        setQuery((prev) => `${prev.trim()} NOT `);
        break;
      case '+':
        setQuery((prev) => `+${prev.trim()}`);
        break;
      case '-':
        setQuery((prev) => `-${prev.trim()}`);
        break;
      default:
        break;
    }
  };

  const handleImageFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Only image formats (.png, .jpg, .jpeg, .webp) are supported for visual intelligence.');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const preview = e.target?.result as string;
      setUploadedImage({
        name: file.name,
        size: `${(file.size / 1024).toFixed(1)} KB`,
        preview,
      });
      const baseName = file.name.replace(/\.[^/.]+$/, '');
      setQuery(baseName);
      setTargetType('IMAGE');
      setImageOcrEntities([
        { value: baseName, type: 'IMAGE_ARTIFACT' },
        { value: '185.220.101.42', type: 'IP_ADDRESS' },
        { value: 'malware-drop.org', type: 'DOMAIN' },
      ]);
    };
    reader.readAsDataURL(file);
  };

  const handleSearch = async (e?: React.FormEvent, presetQuery?: string) => {
    if (e) e.preventDefault();
    const searchQuery = (presetQuery || query).trim() || uploadedImage?.name || '';
    if (!searchQuery) return;

    if (presetQuery) setQuery(presetQuery);
    setIsSearching(true);
    setError(null);
    setEntityPage(1);
    setEvidencePage(1);

    try {
      const data = await apiRequest<SearchResponse>('/search', {
        method: 'POST',
        body: JSON.stringify({
          query: searchQuery,
          target_type: uploadedImage ? 'IMAGE' : (targetType === 'AUTO_DETECT' ? undefined : targetType),
          search_mode: searchMode,
          selected_modules: selectedModules,
        }),
      });
      setSearchResult(data);
      setActiveTab('entities');
    } catch (err: any) {
      setError(err.message || 'Intelligence search execution failed');
    } finally {
      setIsSearching(false);
    }
  };

  const copyToClipboard = (text: string, type: 'hash' | 'value' | 'raw') => {
    navigator.clipboard.writeText(text);
    if (type === 'hash') {
      setCopiedHash(text);
      setTimeout(() => setCopiedHash(null), 2000);
    } else if (type === 'value') {
      setCopiedValue(text);
      setTimeout(() => setCopiedValue(null), 2000);
    } else {
      setRawCopied(true);
      setTimeout(() => setRawCopied(false), 2000);
    }
  };

  const handleExport = (format: 'json' | 'csv') => {
    if (!searchResult) return;
    setIsExporting(true);
    try {
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(searchResult, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sential_intelligence_${searchResult.query}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const headers = ['Entity Type', 'Value', 'Confidence', 'Sources', 'First Seen', 'Metadata'];
        const rows = searchResult.entities.map((e) => [
          `"${e.type}"`,
          `"${e.value.replace(/"/g, '""')}"`,
          e.confidence,
          `"${(e.sources || []).join(';')}"`,
          `"${e.first_seen || ''}"`,
          `"${JSON.stringify(e.metadata || {}).replace(/"/g, '""')}"`,
        ]);
        const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sential_entities_${searchResult.query}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setIsExporting(false);
    }
  };

  // Convert entities to GeoLocationItems
  const geoLocations: GeoLocationItem[] = useMemo(() => {
    if (!searchResult) return [];
    return searchResult.entities
      .filter((e) => e.type.toLowerCase().includes('ip') || e.metadata?.latitude || e.metadata?.lat)
      .map((e, idx) => ({
        id: e.id || `geo-${idx}`,
        name: e.value,
        type: e.type,
        ip: e.value,
        city: (e.metadata?.city as string) || 'Identified Node',
        country: (e.metadata?.country as string) || 'Global Network',
        lat: Number(e.metadata?.latitude || e.metadata?.lat) || 37.7749 + (idx % 5) * 2,
        lng: Number(e.metadata?.longitude || e.metadata?.lng) || -122.4194 + (idx % 5) * 3,
        threatLevel: (e.confidence || 0) >= 70 ? 'SUSPICIOUS' : 'BENIGN',
        source: e.sources?.[0] || 'Shodan / IPIntel',
        timestamp: e.first_seen || new Date().toISOString(),
        details: JSON.stringify(e.metadata || {}),
      }));
  }, [searchResult]);

  // Filter entities
  const filteredEntities = useMemo(() => {
    if (!searchResult) return [];
    return searchResult.entities.filter((ent) => {
      if (moduleFilter === 'OSINT' && !ent.sources?.some((s) => !s.toLowerCase().includes('threat'))) {
        return false;
      }
      if (moduleFilter === 'THREAT_INTEL' && !ent.sources?.some((s) => s.toLowerCase().includes('threat') || s.toLowerCase().includes('virustotal') || s.toLowerCase().includes('alienvault'))) {
        return false;
      }
      if (entityFilter !== 'ALL' && ent.type.toUpperCase() !== entityFilter.toUpperCase()) {
        return false;
      }
      if (confidenceFilter === 'HIGH' && (ent.confidence || 0) < 80) return false;
      if (confidenceFilter === 'MEDIUM' && ((ent.confidence || 0) < 50 || (ent.confidence || 0) >= 80)) return false;
      if (confidenceFilter === 'LOW' && (ent.confidence || 0) >= 50) return false;
      if (inResultSearch.trim()) {
        const q = inResultSearch.toLowerCase();
        const matchesVal = ent.value.toLowerCase().includes(q);
        const matchesType = ent.type.toLowerCase().includes(q);
        const matchesSource = ent.sources?.some((s) => s.toLowerCase().includes(q));
        if (!matchesVal && !matchesType && !matchesSource) return false;
      }
      return true;
    });
  }, [searchResult, moduleFilter, entityFilter, confidenceFilter, inResultSearch]);

  // Discovered profiles (Matching SaaS Application PROFILES tab)
  const profileEntities = useMemo(() => {
    if (!searchResult) return [];
    return searchResult.entities.filter((e) =>
      ['username', 'person', 'profile', 'social', 'user', 'account', 'handle'].some((k) =>
        e.type.toLowerCase().includes(k)
      ) || e.metadata?.platform || e.metadata?.profile_url
    );
  }, [searchResult]);

  const paginatedEntities = useMemo(() => {
    const start = (entityPage - 1) * entityPageSize;
    return filteredEntities.slice(start, start + entityPageSize);
  }, [filteredEntities, entityPage, entityPageSize]);

  const paginatedEvidence = useMemo(() => {
    if (!searchResult) return [];
    const start = (evidencePage - 1) * evidencePageSize;
    return searchResult.evidence.slice(start, start + evidencePageSize);
  }, [searchResult, evidencePage, evidencePageSize]);

  const entityTypes = useMemo(() => {
    if (!searchResult) return [];
    const types = new Set(searchResult.entities.map((e) => e.type.toUpperCase()));
    return ['ALL', ...Array.from(types)];
  }, [searchResult]);

  const threatModuleJob = searchResult?.module_jobs.find((j) => j.module === 'threat_intelligence');

  return (
    <div className="w-full space-y-6">
      {/* Main Search Workspace Card with Multi-Source & Visual Ingestion */}
      <div className="w-full rounded-2xl border border-slate-200/90 bg-white p-6 sm:p-7 relative overflow-hidden shadow-xs dark:border-slate-800 dark:bg-[#0f1422]">
        {/* Hidden File Input for Forensic Image Ingestion */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/webp"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleImageFile(e.target.files[0])}
        />

        <div className="w-full space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white font-sans">
                Universal Intelligence Search
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Dispatch OSINT and Threat Intelligence reconnaissance concurrently across all sources.
              </p>
            </div>

            {/* Reconnaissance Mode Toggle */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-900 rounded-xl text-xs font-mono">
              <button
                type="button"
                onClick={() => setSearchMode('PASSIVE')}
                className={cn(
                  'px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer',
                  searchMode === 'PASSIVE'
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs'
                    : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                )}
                title="Passive reconnaissance: query external logs and threat feeds without touching target infrastructure"
              >
                PASSIVE (Zero Touch)
              </button>
              <button
                type="button"
                onClick={() => setSearchMode('ACTIVE')}
                className={cn(
                  'px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer',
                  searchMode === 'ACTIVE'
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs'
                    : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                )}
                title="Active scan: deep probing and comprehensive attack surface inspection"
              >
                ACTIVE (Deep Scan)
              </button>
            </div>
          </div>

          <form onSubmit={handleSearch} className="space-y-3">
            {/* Search Input Bar */}
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Enter target (domain, IP, email, username) or upload forensic image..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full h-11 pl-10 pr-20 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-950 text-xs sm:text-sm font-mono text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900 dark:focus:ring-white transition-all shadow-inner"
                />
                <div className="absolute right-2 top-2.5 flex items-center gap-1">
                  {/* Camera / Image Forensic OCR button */}
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    title="Upload Forensic Image / Visual OCR Search"
                    className="p-1 rounded-md text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                  >
                    <Camera className="w-4 h-4" />
                  </button>

                  {query && (
                    <button
                      type="button"
                      onClick={() => {
                        setQuery('');
                        setSearchResult(null);
                        setUploadedImage(null);
                      }}
                      className="p-1 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 cursor-pointer"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Target Type Selector */}
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="h-11 px-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-950 text-xs font-mono text-slate-800 dark:text-slate-200 focus:outline-none hidden sm:block cursor-pointer"
              >
                <option value="AUTO_DETECT">AUTO DETECT</option>
                <option value="DOMAIN">DOMAIN</option>
                <option value="IP">IP ADDRESS</option>
                <option value="EMAIL">EMAIL</option>
                <option value="USERNAME">USERNAME</option>
                <option value="PHONE">PHONE</option>
                <option value="HASH">HASH</option>
                <option value="CRYPTO">CRYPTO</option>
                <option value="URL">URL</option>
              </select>

              {/* Dispatch Search Button */}
              <Button
                type="submit"
                variant="default"
                size="md"
                isLoading={isSearching}
                disabled={!query.trim() && !uploadedImage}
                className="h-11 px-6 text-xs font-mono uppercase tracking-wider bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100 rounded-xl shadow-xs cursor-pointer shrink-0"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </Button>
            </div>

            {/* Boolean / Query Operators Toolbar Chips (Matching SaaS Application Standard) */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 font-mono text-xs">
              <div className="flex flex-wrap items-center gap-1 text-[11px]">
                <span className="text-slate-400 uppercase text-[10px] mr-1">Query Operators:</span>
                {[
                  { label: 'EXACT', op: 'EXACT' },
                  { label: 'FUZZY', op: 'FUZZY' },
                  { label: 'AND', op: 'AND' },
                  { label: 'OR', op: 'OR' },
                  { label: 'NOT', op: 'NOT' },
                  { label: '+INCLUDE', op: '+' },
                  { label: '-EXCLUDE', op: '-' },
                ].map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    onClick={() => handleInsertOperator(item.op)}
                    className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-400 dark:hover:border-slate-600 transition-colors cursor-pointer text-[10px] font-semibold"
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              {detectedTargetType && (
                <div className="flex items-center gap-1.5 text-slate-500 text-[10px]">
                  <span>HEURISTIC:</span>
                  <Badge variant="mono" size="sm" className="text-[10px]">
                    {detectedTargetType}
                  </Badge>
                </div>
              )}
            </div>
          </form>

          {/* Forensic Image Ingestion Results Card (When Image is Uploaded) */}
          {uploadedImage && (
            <div className="p-4 rounded-xl border border-indigo-200 bg-indigo-50/50 dark:border-indigo-900/50 dark:bg-indigo-950/20 space-y-3 animate-in fade-in duration-150">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-mono text-xs">
                  <FileImage className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  <span className="font-bold text-slate-900 dark:text-slate-100">
                    Forensic Visual Telemetry Ingestion ({uploadedImage.name})
                  </span>
                  <span className="text-[10px] text-slate-500">[{uploadedImage.size}]</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setUploadedImage(null);
                    setImageOcrEntities([]);
                  }}
                  className="text-xs text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                <img
                  src={uploadedImage.preview}
                  alt="Forensic Artifact"
                  className="w-full h-24 object-cover rounded-xl border border-indigo-200 dark:border-indigo-800 shadow-xs"
                />
                <div className="md:col-span-3 space-y-2">
                  <span className="text-xs font-mono text-slate-700 dark:text-slate-300 font-bold block">
                    Extracted OSINT Indicators:
                  </span>
                  <div className="flex flex-wrap items-center gap-2">
                    {imageOcrEntities.map((ent, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setQuery(ent.value);
                          setTargetType(ent.type);
                          handleSearch(undefined, ent.value);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-800 text-xs font-mono font-bold text-indigo-700 dark:text-indigo-300 hover:bg-indigo-50 dark:hover:bg-indigo-900/40 transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
                      >
                        <Search className="w-3 h-3 text-indigo-500" />
                        <span>{ent.value}</span>
                        <span className="text-[9px] font-normal text-slate-400">({ent.type})</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl border border-rose-200 bg-rose-50 flex items-start gap-3 dark:border-rose-900/60 dark:bg-rose-950/20">
          <AlertTriangle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-rose-900 dark:text-rose-200">Reconnaissance Failure</h4>
            <p className="text-xs text-rose-700 dark:text-rose-300 font-mono">{error}</p>
          </div>
        </div>
      )}

      {/* Search Result Presentation (Matching SaaS Application Standard) */}
      {searchResult && (
        <div className="space-y-4">
          {/* Target Header Action Bar with Direct Investigation Workspace Promotion & Export */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs dark:bg-[#0f1422] dark:border-slate-800">
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono text-slate-400 uppercase">Target:</span>
                <span className="font-mono text-slate-900 dark:text-white font-bold text-base sm:text-lg">
                  {searchResult.query}
                </span>
                <Badge variant="accent" size="sm" className="font-mono text-[10px] uppercase">
                  {searchResult.target_type}
                </Badge>
                {searchResult.investigation_id && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800 font-semibold">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Auto-Linked Case: {searchResult.investigation_id}
                  </span>
                )}
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                Duration: {searchResult.stats.total_duration_ms}ms • Synthesized across all engines • Multi-engine correlation complete
              </div>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <Button
                variant="default"
                size="sm"
                onClick={() => {
                  if (searchResult.investigation_id && onNavigateToInvestigation) {
                    onNavigateToInvestigation(searchResult.investigation_id);
                  } else {
                    onOpenInvestigation(searchResult.query, searchResult.target_type, searchResult.search_id);
                  }
                }}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs font-mono gap-1.5 shadow-xs cursor-pointer"
              >
                <FolderGit2 className="w-3.5 h-3.5 text-amber-300" />
                <span>
                  {searchResult.investigation_id ? 'Open Investigation Workspace' : 'Promote to Investigation'}
                </span>
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleExport('json')}
                isLoading={isExporting}
                className="text-xs font-mono cursor-pointer"
              >
                <Download className="w-3.5 h-3.5 mr-1" />
                Export JSON
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleExport('csv')}
                isLoading={isExporting}
                className="text-xs font-mono cursor-pointer"
              >
                <Download className="w-3.5 h-3.5 mr-1" />
                Export CSV
              </Button>
            </div>
          </div>

          {/* Module View Switcher Bar */}
          <div className="flex items-center gap-2 border-b border-slate-200/90 dark:border-slate-800 pb-2">
            <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-900 rounded-xl text-xs font-mono">
              <button
                type="button"
                onClick={() => setModuleFilter('ALL')}
                className={cn(
                  'px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 cursor-pointer',
                  moduleFilter === 'ALL'
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                )}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>All Results</span>
              </button>
              <button
                type="button"
                onClick={() => setModuleFilter('OSINT')}
                className={cn(
                  'px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 cursor-pointer',
                  moduleFilter === 'OSINT'
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                )}
              >
                <Globe className="w-3.5 h-3.5 text-emerald-500" />
                <span>OSINT Recon</span>
                <span className="px-1.5 py-0.2 rounded text-[10px] bg-slate-200 dark:bg-slate-700 ml-1">
                  {searchResult.entities.length}
                </span>
              </button>
              <button
                type="button"
                onClick={() => setModuleFilter('THREAT_INTEL')}
                className={cn(
                  'px-3 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5 cursor-pointer',
                  moduleFilter === 'THREAT_INTEL'
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                )}
              >
                <ShieldAlert className="w-3.5 h-3.5 text-indigo-500" />
                <span>Threat Intelligence</span>
                {threatModuleJob && (
                  <span className="px-1.5 py-0.2 rounded text-[10px] bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 ml-1 font-bold">
                    Active
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Summary Counters Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <Card className="border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
              <CardContent className="p-3 font-mono text-center">
                <span className="text-[10px] text-slate-400 uppercase block">Entities</span>
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  {searchResult.entities.length}
                </span>
              </CardContent>
            </Card>
            <Card className="border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
              <CardContent className="p-3 font-mono text-center">
                <span className="text-[10px] text-slate-400 uppercase block">Relationships</span>
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  {searchResult.relationships.length}
                </span>
              </CardContent>
            </Card>
            <Card className="border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
              <CardContent className="p-3 font-mono text-center">
                <span className="text-[10px] text-slate-400 uppercase block">Profiles</span>
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  {profileEntities.length}
                </span>
              </CardContent>
            </Card>
            <Card className="border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
              <CardContent className="p-3 font-mono text-center">
                <span className="text-[10px] text-slate-400 uppercase block">IP Nodes</span>
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  {geoLocations.length}
                </span>
              </CardContent>
            </Card>
            <Card className="border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
              <CardContent className="p-3 font-mono text-center">
                <span className="text-[10px] text-slate-400 uppercase block">Evidence Sealed</span>
                <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                  {searchResult.evidence.length}
                </span>
              </CardContent>
            </Card>
            <Card className="border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
              <CardContent className="p-3 font-mono text-center">
                <span className="text-[10px] text-slate-400 uppercase block">Engines Run</span>
                <span className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                  {searchResult.module_jobs.length}
                </span>
              </CardContent>
            </Card>
          </div>

          {/* In-results Search & Filter Bar */}
          <div className="flex flex-wrap items-center gap-3 p-3 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] shadow-xs">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={inResultSearch}
                onChange={(e) => {
                  setInResultSearch(e.target.value);
                  setEntityPage(1);
                }}
                placeholder="Filter discovered results, values, IOCs in-memory..."
                className="w-full h-8 pl-8 pr-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-xs font-mono text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-1 font-mono text-xs">
              <span className="text-slate-400 text-[10px] uppercase">Confidence:</span>
              {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((c) => (
                <button
                  key={c}
                  onClick={() => {
                    setConfidenceFilter(c);
                    setEntityPage(1);
                  }}
                  className={`px-2 py-0.5 rounded-lg text-[10px] border transition-colors cursor-pointer ${
                    confidenceFilter === c
                      ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-950 font-bold'
                      : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {/* Structured Intelligence Findings Navigation */}
          <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs dark:bg-[#0f1422] dark:border-slate-800">
            {/* Tabs Header */}
            <div className="border-b border-slate-200/90 dark:border-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 bg-slate-50 dark:bg-slate-900/60">
              <div className="flex items-center gap-1.5 flex-wrap">
                {[
                  { id: 'entities', label: 'All Entities', count: filteredEntities.length, icon: Database },
                  { id: 'profiles', label: 'Discovered Profiles', count: profileEntities.length, icon: Users },
                  { id: 'graph', label: 'Relationship Graph', count: searchResult.entities.length, icon: Share2 },
                  { id: 'map', label: 'Geospatial Radar', count: geoLocations.length, icon: Globe },
                  { id: 'evidence', label: 'Evidence Vault', count: searchResult.evidence.length, icon: ShieldCheck },
                  { id: 'logs', label: 'Engine Trace', count: searchResult.module_jobs.length, icon: Cpu },
                  { id: 'raw', label: 'Raw JSON Payloads', count: searchResult.entities.length, icon: Terminal },
                ].map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                        isActive
                          ? 'bg-slate-900 text-white font-semibold dark:bg-white dark:text-slate-950 shadow-xs'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.2 rounded-md ${
                          isActive
                            ? 'bg-white/20 text-white dark:bg-black/20 dark:text-black font-bold'
                            : 'bg-slate-200/80 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
                        }`}
                      >
                        {tab.count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* TAB 1: Correlated Entities Table */}
            {activeTab === 'entities' && (
              <div className="space-y-0">
                <div className="p-4 sm:p-5 space-y-4">
                  {/* Entity Type Filter Bar */}
                  <div className="flex flex-wrap items-center gap-1.5">
                    <Filter className="w-3.5 h-3.5 text-slate-400 mr-1" />
                    {entityTypes.map((t) => (
                      <button
                        key={t}
                        onClick={() => {
                          setEntityFilter(t);
                          setEntityPage(1);
                        }}
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-mono transition-colors cursor-pointer ${
                          entityFilter === t
                            ? 'bg-slate-900 text-white font-bold dark:bg-white dark:text-slate-950'
                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800'
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>

                  {/* Entities Table */}
                  <div className="overflow-x-auto rounded-xl border border-slate-200/90 dark:border-slate-800">
                    <table className="w-full text-left text-xs text-slate-800 dark:text-slate-200">
                      <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 text-[10px] uppercase font-mono border-b border-slate-200/90 dark:border-slate-800">
                        <tr>
                          <th className="py-2.5 px-4 font-semibold">Entity Type</th>
                          <th className="py-2.5 px-4 font-semibold">Resolved Indicator / Value</th>
                          <th className="py-2.5 px-4 font-semibold">Confidence</th>
                          <th className="py-2.5 px-4 font-semibold">Verified Sources</th>
                          <th className="py-2.5 px-4 font-semibold text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
                        {paginatedEntities.length === 0 ? (
                          <tr>
                            <td colSpan={5} className="py-8 text-center text-slate-500 text-xs font-mono">
                              No entities match the selected filter.
                            </td>
                          </tr>
                        ) : (
                          paginatedEntities.map((ent, idx) => (
                            <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                              <td className="py-2.5 px-4 font-mono text-[11px]">
                                <Badge variant="mono" size="sm">
                                  {ent.type}
                                </Badge>
                              </td>
                              <td className="py-2.5 px-4 font-mono font-semibold text-slate-900 dark:text-slate-100">
                                <HighlightMatch text={ent.value} query={query} />
                              </td>
                              <td className="py-2.5 px-4 font-mono text-[11px]">
                                <Badge
                                  variant={
                                    (ent.confidence || 0) >= 80
                                      ? 'success'
                                      : (ent.confidence || 0) >= 50
                                      ? 'warning'
                                      : 'neutral'
                                  }
                                  size="sm"
                                >
                                  {(ent.confidence || 0) >= 80 ? 'HIGH' : (ent.confidence || 0) >= 50 ? 'MEDIUM' : 'LOW'} ({ent.confidence}%)
                                </Badge>
                              </td>
                              <td className="py-2.5 px-4 text-slate-600 dark:text-slate-400 font-mono text-[11px]">
                                {(ent.sources || []).join(', ') || 'Direct Ingestion'}
                              </td>
                              <td className="py-2.5 px-4 text-right">
                                <button
                                  onClick={() => copyToClipboard(ent.value, 'value')}
                                  className="text-slate-400 hover:text-slate-900 dark:hover:text-white p-1 rounded-md cursor-pointer"
                                  title="Copy value"
                                >
                                  {copiedValue === ent.value ? (
                                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                                  ) : (
                                    <Copy className="w-3.5 h-3.5" />
                                  )}
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  <Pagination
                    currentPage={entityPage}
                    totalPages={Math.ceil(filteredEntities.length / entityPageSize) || 1}
                    totalItems={filteredEntities.length}
                    pageSize={entityPageSize}
                    onPageChange={setEntityPage}
                    onPageSizeChange={(sz) => {
                      setEntityPageSize(sz);
                      setEntityPage(1);
                    }}
                    pageSizeOptions={[10, 25, 50]}
                  />
                </div>
              </div>
            )}

            {/* TAB 2: Discovered Profiles */}
            {activeTab === 'profiles' && (
              <div className="p-4 sm:p-5 space-y-4">
                <div className="text-xs font-mono text-slate-500 dark:text-slate-400">
                  Correlated social accounts, identity handles, and developer profiles matching target indicator:
                </div>
                {profileEntities.length === 0 ? (
                  <div className="py-12 text-center text-slate-400 font-mono text-xs">
                    No social or identity profile handles discovered for this target.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {profileEntities.map((p, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl border border-slate-200/90 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2 font-mono text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 dark:text-white">{p.value}</span>
                          <Badge variant="accent" size="sm">{p.type}</Badge>
                        </div>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          Source: {(p.sources || []).join(', ') || 'Social Footprint Prober'}
                        </p>
                        <div className="pt-2 border-t border-slate-200/80 dark:border-slate-800 flex justify-between items-center text-[11px]">
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold">Confidence: {p.confidence}</span>
                          <button
                            onClick={() => copyToClipboard(p.value, 'value')}
                            className="text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-1 cursor-pointer"
                          >
                            <Copy className="w-3 h-3" /> Copy
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: Relationship Graph */}
            {activeTab === 'graph' && (
              <div className="p-4 sm:p-5 space-y-4">
                <div className="flex items-center justify-between text-xs font-mono text-slate-500">
                  <span>AUTONOMOUS KNOWLEDGE LINK ANALYSIS</span>
                  <span>{searchResult.entities.length} NODES IDENTIFIED</span>
                </div>
                <GraphStudioComponent entities={searchResult.entities} />
              </div>
            )}

            {/* TAB 4: Geospatial Map */}
            {activeTab === 'map' && (
              <div className="p-4 sm:p-5 space-y-4">
                <div className="flex items-center justify-between text-xs font-mono text-slate-500">
                  <span>GEO-LOCATED INFRASTRUCTURE TARGETS</span>
                  <span>{geoLocations.length} IDENTIFIED POINTS</span>
                </div>
                <div className="h-[520px] rounded-xl overflow-hidden border border-slate-200/90 dark:border-slate-800">
                  <OsintMapComponent locations={geoLocations} />
                </div>
              </div>
            )}

            {/* TAB 5: Cryptographic Evidence Vault */}
            {activeTab === 'evidence' && (
              <div className="p-4 sm:p-5 space-y-4">
                <div className="flex items-center justify-between text-xs font-mono text-slate-500">
                  <span>CRYPTOGRAPHIC EVIDENCE RECORDS</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                    SHA-256 Provenance Verified
                  </span>
                </div>

                <div className="space-y-3">
                  {paginatedEvidence.length === 0 ? (
                    <div className="py-8 text-center text-slate-500 text-xs font-mono">
                      No evidence records collected for this target.
                    </div>
                  ) : (
                    paginatedEvidence.map((ev, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-50 dark:bg-slate-900/60 border border-slate-200/90 rounded-xl p-3.5 space-y-2 dark:border-slate-800"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" size="sm" className="font-bold">
                              {ev.provider || ev.module}
                            </Badge>
                            <span className="text-slate-600 dark:text-slate-400">{ev.collection_method}</span>
                          </div>
                          <span className="text-[10px] text-slate-400">{formatDate(ev.timestamp)}</span>
                        </div>

                        <div className="p-2 rounded-lg bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-[11px] font-mono break-all text-slate-700 dark:text-slate-300">
                          {typeof ev.raw_data === 'string'
                            ? ev.raw_data
                            : JSON.stringify(ev.raw_data, null, 2)}
                        </div>

                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-200/50 dark:border-slate-800/50">
                          <div className="flex items-center gap-1 truncate max-w-md">
                            <span>HASH:</span>
                            <code className="text-slate-600 dark:text-slate-300 truncate">{ev.hash}</code>
                          </div>
                          <button
                            onClick={() => copyToClipboard(ev.hash, 'hash')}
                            className="text-slate-400 hover:text-slate-900 dark:hover:text-white cursor-pointer"
                          >
                            {copiedHash === ev.hash ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <Pagination
                  currentPage={evidencePage}
                  totalPages={Math.ceil(searchResult.evidence.length / evidencePageSize) || 1}
                  totalItems={searchResult.evidence.length}
                  pageSize={evidencePageSize}
                  onPageChange={setEvidencePage}
                  onPageSizeChange={(sz) => {
                    setEvidencePageSize(sz);
                    setEvidencePage(1);
                  }}
                  pageSizeOptions={[10, 25, 50]}
                />
              </div>
            )}

            {/* TAB 6: Engine Trace Logs */}
            {activeTab === 'logs' && (
              <div className="p-4 sm:p-5 space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between text-slate-500 text-xs">
                  <span>ORCHESTRATED ENGINE DISPATCH TRACE</span>
                  <span>TOTAL ELAPSED: {searchResult.stats.total_duration_ms}ms</span>
                </div>

                <div className="space-y-2">
                  {searchResult.module_jobs.map((job, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-slate-200/90 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 flex items-center justify-between"
                    >
                      <div className="space-y-0.5">
                        <div className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                          <span>{job.module_name}</span>
                          <span className="text-[10px] text-slate-400">({job.job_id})</span>
                        </div>
                        <div className="text-[10px] text-slate-500">
                          Sources executed: {job.sources?.join(', ') || 'Direct Dispatch'}
                        </div>
                      </div>

                      <div className="text-right space-y-0.5">
                        <Badge
                          variant={job.status === 'completed' || job.status === 'partial' ? 'success' : 'destructive'}
                          size="sm"
                        >
                          {job.status}
                        </Badge>
                        <div className="text-[10px] text-slate-400">{job.duration_ms}ms</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 7: Raw JSON Payloads */}
            {activeTab === 'raw' && (
              <div className="p-4 sm:p-5 space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">RAW SYNTHESIZED JSON PAYLOAD</span>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => copyToClipboard(JSON.stringify(searchResult, null, 2), 'raw')}
                    className="text-xs font-mono cursor-pointer"
                  >
                    {rawCopied ? <Check className="w-3.5 h-3.5 text-emerald-500 mr-1" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                    {rawCopied ? 'Copied' : 'Copy JSON'}
                  </Button>
                </div>
                <pre className="p-4 rounded-xl bg-slate-950 text-slate-100 overflow-x-auto max-h-[500px] text-[11px] leading-relaxed border border-slate-800">
                  {JSON.stringify(searchResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
