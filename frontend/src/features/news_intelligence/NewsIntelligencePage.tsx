import React, { useState, useEffect } from 'react';
import {
  Search, Sliders, Calendar, MapPin, Globe, Filter, Video, Play,
  Image as ImageIcon, Newspaper, MessageSquare, Layers, Shield,
  ArrowRight, RefreshCw, ExternalLink, Eye, Clock, CheckCircle2,
  FolderPlus, Sparkles, ChevronRight, X, AlertTriangle, Link2,
  FolderGit2, Briefcase, BookOpen
} from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import {
  useNewsSearch,
  useNewsSearchHistory,
  useNewsInvestigations,
  useCreateNewsInvestigation,
  NewsSearchResultItem,
  SearchMode,
  ContentCategory,
} from '../../core/api/newsHooks';
import { NewsInvestigationWorkspace } from './NewsInvestigationWorkspace';
import { NewsArticleReaderView } from './NewsArticleReaderView';
import { WatchlistsModal } from './WatchlistsModal';
import { AddToCaseModal } from './AddToCaseModal';
import { cn } from '../../lib/utils';

export const NewsIntelligencePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<SearchMode>('SEMANTIC');
  const [minRelevance, setMinRelevance] = useState<number>(60);
  const [selectedCategory, setSelectedCategory] = useState<ContentCategory>('all');
  const [dateFilter, setDateFilter] = useState<string>('');
  const [locationFilter, setLocationFilter] = useState<string>('');
  const [sourceFilter, setSourceFilter] = useState<string>('');
  const [languageFilter, setLanguageFilter] = useState<string>('en');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Direct URL ingestion modal state
  const [directUrl, setDirectUrl] = useState('');
  const [directUrlTitle, setDirectUrlTitle] = useState('');
  const [isDirectUrlOpen, setIsDirectUrlOpen] = useState(false);

  // Active investigation viewing
  const [activeInvestigationId, setActiveInvestigationId] = useState<string | null>(null);

  // Selected article for internal DisInfoLab-style long-form reading
  const [selectedArticleId, setSelectedArticleId] = useState<string | null>(null);
  const [playingVideoId, setPlayingVideoId] = useState<string | null>(null);

  // Watchlists modal
  const [isWatchlistsOpen, setIsWatchlistsOpen] = useState(false);

  // Add to case modal for search result
  const [caseModalItem, setCaseModalItem] = useState<{ id: string; title: string } | null>(null);

  // Comparison drawer state
  const [compareItems, setCompareItems] = useState<NewsSearchResultItem[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  // Evidence preview modal
  const [previewItem, setPreviewItem] = useState<NewsSearchResultItem | null>(null);

  // Hooks
  const searchMutation = useNewsSearch();
  const { data: searchHistory = [], refetch: refetchHistory } = useNewsSearchHistory();
  const { data: activeInvestigations = [], refetch: refetchInvestigations } = useNewsInvestigations();
  const createInvestigationMutation = useCreateNewsInvestigation();

  const handleSearch = (customQuery?: string) => {
    const q = (customQuery || query).trim();
    if (!q) return;

    if (customQuery) {
      setQuery(customQuery);
    }

    searchMutation.mutate(
      {
        query: q,
        search_mode: searchMode,
        min_relevance: minRelevance,
        category_filter: selectedCategory,
        date_filter: dateFilter || undefined,
        location_filter: locationFilter || undefined,
        source_filter: sourceFilter || undefined,
        language_filter: languageFilter || undefined,
      },
      {
        onSuccess: () => {
          refetchHistory();
        },
      }
    );
  };

  const handleInvestigateResult = async (item: NewsSearchResultItem) => {
    try {
      const inv = await createInvestigationMutation.mutateAsync({
        original_query: searchMutation.data?.original_query || query,
        target_input: item.summary || item.title,
        canonical_url: item.canonical_url,
        preset_title: item.title,
        search_id: searchMutation.data?.search_id,
      });
      setActiveInvestigationId(inv.id);
      refetchInvestigations();
    } catch (err) {
      console.error('Failed to create investigation', err);
    }
  };

  const handleDirectUrlInvestigate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!directUrl.trim()) return;

    try {
      const inv = await createInvestigationMutation.mutateAsync({
        original_query: directUrlTitle.trim() || directUrl.trim(),
        target_input: directUrl.trim(),
        canonical_url: directUrl.trim(),
        preset_title: directUrlTitle.trim() || `URL Verification: ${directUrl}`,
      });
      setDirectUrl('');
      setDirectUrlTitle('');
      setIsDirectUrlOpen(false);
      setActiveInvestigationId(inv.id);
      refetchInvestigations();
    } catch (err) {
      console.error('Failed to investigate URL', err);
    }
  };

  const toggleCompare = (item: NewsSearchResultItem) => {
    if (compareItems.some((i) => i.id === item.id)) {
      setCompareItems(compareItems.filter((i) => i.id !== item.id));
    } else {
      if (compareItems.length >= 3) {
        alert('You can compare up to 3 items at a time.');
        return;
      }
      setCompareItems([...compareItems, item]);
      setIsCompareOpen(true);
    }
  };

  // If viewing an active investigation workspace, render the workspace component!
  if (activeInvestigationId) {
    return (
      <NewsInvestigationWorkspace
        investigationId={activeInvestigationId}
        onBack={() => {
          setActiveInvestigationId(null);
          refetchInvestigations();
        }}
      />
    );
  }

  // If viewing an internal investigative article, render DisInfoLab-inspired reader!
  if (selectedArticleId) {
    return (
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-[#f8fafc] dark:bg-[#090d16]">
        <NewsArticleReaderView
          articleId={selectedArticleId}
          queryHint={query}
          onBack={() => setSelectedArticleId(null)}
          onPromoteToInvestigation={async (art) => {
            setSelectedArticleId(null);
            await handleInvestigateResult({
              id: art.id,
              title: art.title,
              summary: art.subtitle || art.title,
              canonical_url: art.canonical_url || '',
            } as any);
          }}
        />
      </div>
    );
  }

  const searchResults = searchMutation.data?.results || [];
  const categoryCounts = searchMutation.data?.category_counts || {};

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto bg-slate-50/50 dark:bg-[#090d16]">
      {/* Sticky Top Workstation Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-[#0d121f]/95 backdrop-blur-md px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Newspaper className="w-5 h-5 text-emerald-500" />
            <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100 font-sans tracking-tight">
              News Intelligence Investigation Engine
            </h1>
            <Badge variant="outline" className="text-[10px] text-emerald-600 dark:text-emerald-400 border-emerald-500/30">
              SEARCH-DRIVEN
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Query-bound multi-source retrieval, claim decomposition, source lineage, and media forensics.
          </p>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsDirectUrlOpen(true)}
            className="text-xs text-slate-700 dark:text-slate-300"
          >
            <Link2 className="w-3.5 h-3.5 mr-1 text-emerald-500" />
            Investigate URL / Media
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsWatchlistsOpen(true)}
            className="text-xs text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10"
          >
            <Eye className="w-3.5 h-3.5 mr-1" />
            Topic Watchlists
          </Button>

          {activeInvestigations.length > 0 && (
            <Button
              size="sm"
              variant="default"
              onClick={() => setActiveInvestigationId(activeInvestigations[0].id)}
              className="text-xs bg-slate-900 hover:bg-slate-800 text-white dark:bg-emerald-600 dark:hover:bg-emerald-700"
            >
              <FolderGit2 className="w-3.5 h-3.5 mr-1" />
              Active Investigations ({activeInvestigations.length})
            </Button>
          )}
        </div>
      </div>

      <div className="p-6 max-w-7xl mx-auto w-full space-y-6">
        {/* HERO SECTION: SEARCH-FIRST INTERACTION */}
        <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0c101c] shadow-xs space-y-4">
          <div className="space-y-1">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 font-mono">
              WHAT DO YOU WANT TO INVESTIGATE?
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Your search query anchors and scopes the entire investigation. Downstream forensics and evidence strictly maintain this context.
            </p>
          </div>

          {/* Search Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSearch();
            }}
            className="flex items-center gap-2"
          >
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search a topic, claim, article, video, person, organization, event or narrative... (e.g. 'Chennai flood viral video' or 'India election EVM')"
                className="w-full pl-10 pr-4 py-2.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/60 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-sans"
              />
            </div>

            <Button
              type="submit"
              size="md"
              disabled={searchMutation.isPending || !query.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-6 shrink-0 h-10 rounded-xl"
            >
              {searchMutation.isPending ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin mr-1.5" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5 mr-1.5" />
                  SEARCH
                </>
              )}
            </Button>
          </form>

          {/* Search Controls & Mode Selector */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-slate-100 dark:border-slate-800/80">
            {/* Search Modes */}
            <div className="flex items-center space-x-1">
              <span className="text-[11px] font-semibold text-slate-400 mr-1.5">Mode:</span>
              {[
                { id: 'SEMANTIC', label: 'Semantic' },
                { id: 'EXACT', label: 'Exact ("quotes")' },
                { id: 'BOOLEAN', label: 'Boolean (AND/OR/NOT)' },
                { id: 'ENTITY', label: 'Entity Match' },
                { id: 'TEMPORAL', label: 'Temporal' },
                { id: 'GEOGRAPHIC', label: 'Geographic' },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setSearchMode(m.id as SearchMode)}
                  className={cn(
                    'px-2.5 py-1 text-[11px] rounded-lg font-medium transition-colors cursor-pointer',
                    searchMode === m.id
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                      : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                  )}
                >
                  {m.label}
                </button>
              ))}
            </div>

            {/* Relevance Slider & Advanced toggle */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-[11px] text-slate-500 dark:text-slate-400">
                <span>Min Relevance:</span>
                <input
                  type="range"
                  min="30"
                  max="95"
                  value={minRelevance}
                  onChange={(e) => setMinRelevance(Number(e.target.value))}
                  className="w-20 accent-emerald-500 cursor-pointer"
                />
                <span className="font-mono font-bold text-slate-700 dark:text-slate-300 w-8">
                  {minRelevance}%
                </span>
              </div>

              <button
                type="button"
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className="flex items-center space-x-1 text-[11px] font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 cursor-pointer"
              >
                <Sliders className="w-3 h-3" />
                <span>Filters</span>
              </button>
            </div>
          </div>

          {/* Advanced Filters Expandable Drawer */}
          {showAdvancedFilters && (
            <div className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/40 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs animate-in fade-in">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                  Temporal Filter
                </label>
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                >
                  <option value="">Any Time</option>
                  <option value="today">Past 24 Hours</option>
                  <option value="week">Past Week</option>
                  <option value="month">Past Month</option>
                  <option value="year">Past Year</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                  Location / Region
                </label>
                <input
                  type="text"
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                  placeholder="e.g. Chennai, India, Geneva"
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                  Source / Outlet
                </label>
                <input
                  type="text"
                  value={sourceFilter}
                  onChange={(e) => setSourceFilter(e.target.value)}
                  placeholder="e.g. Reuters, NDTV, Twitter"
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                  Language
                </label>
                <select
                  value={languageFilter}
                  onChange={(e) => setLanguageFilter(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                >
                  <option value="en">English (en)</option>
                  <option value="ta">Tamil (ta)</option>
                  <option value="hi">Hindi (hi)</option>
                  <option value="es">Spanish (es)</option>
                  <option value="all">Any Language</option>
                </select>
              </div>
            </div>
          )}

          {/* Search History Pills */}
          {searchHistory.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1 mr-1">
                <Clock className="w-3 h-3" />
                <span>Recent Scopes:</span>
              </span>
              {searchHistory.slice(0, 5).map((h) => (
                <button
                  key={h.search_id}
                  onClick={() => handleSearch(h.query)}
                  className="px-2 py-0.5 rounded-md text-[11px] bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono transition-colors cursor-pointer"
                  title={`Ran at ${new Date(h.timestamp).toLocaleTimeString()}`}
                >
                  "{h.query}"
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Query Expansions Indicator */}
        {searchMutation.data?.query_expansions && searchMutation.data.query_expansions.length > 0 && (
          <div className="p-3.5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-emerald-800 dark:text-emerald-300 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
                <span>Strict Provenance Query Expansions (Root Scope Preserved)</span>
              </span>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400">
                {searchMutation.data.query_expansions.length} bound variations
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {searchMutation.data.query_expansions.map((exp, i) => (
                <div
                  key={i}
                  className="px-2.5 py-1 rounded-md text-[11px] bg-white dark:bg-slate-900 border border-emerald-500/30 text-slate-800 dark:text-slate-200"
                >
                  <strong className="font-mono">{exp.generated_query}</strong>
                  <span className="text-slate-400 dark:text-slate-500 ml-1.5 italic">
                    ({exp.generated_reason})
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Result Categories Navigation Tabs */}
        {searchMutation.data && (
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
            <div className="flex items-center space-x-1 overflow-x-auto">
              {[
                { id: 'all', label: 'All', count: categoryCounts.all || searchResults.length },
                { id: 'articles', label: 'Articles', count: categoryCounts.articles },
                { id: 'videos', label: 'Videos', count: categoryCounts.videos },
                { id: 'images', label: 'Images', count: categoryCounts.images },
                { id: 'social', label: 'Social', count: categoryCounts.social },
                { id: 'claims', label: 'Claims', count: categoryCounts.claims },
                { id: 'sources', label: 'Sources', count: categoryCounts.sources },
                { id: 'entities', label: 'Entities', count: categoryCounts.entities },
                { id: 'narratives', label: 'Narratives', count: categoryCounts.narratives },
                { id: 'evidence', label: 'Evidence', count: categoryCounts.evidence },
              ].map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id as ContentCategory)}
                  className={cn(
                    'px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors flex items-center space-x-1.5 whitespace-nowrap cursor-pointer',
                    selectedCategory === cat.id
                      ? 'bg-slate-900 text-white dark:bg-emerald-600'
                      : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'
                  )}
                >
                  <span>{cat.label}</span>
                  {cat.count !== undefined && (
                    <span className="text-[10px] opacity-75 font-mono">({cat.count})</span>
                  )}
                </button>
              ))}
            </div>

            <div className="text-xs text-slate-400 shrink-0">
              Found {searchResults.length} relevant results in {searchMutation.data.duration_ms}ms
            </div>
          </div>
        )}

        {/* RESULTS GRID / LIST */}
        {searchMutation.isPending ? (
          <div className="py-20 flex flex-col items-center justify-center text-center space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin text-emerald-500" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Searching verified sources for "{query}"...
            </p>
            <p className="text-xs text-slate-400 max-w-sm">
              Executing live queries, scoring relevance against query tokens, and deduplicating wire copycats.
            </p>
          </div>
        ) : searchResults.length > 0 ? (
          <div className="space-y-4">
            {searchResults.map((item) => (
              <div
                key={item.id}
                className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0c101d] shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-all space-y-3.5"
              >
                {/* Story Cluster Syndicate Banner (Section 50/54) */}
                {item.story_cluster && (
                  <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs">
                    <div className="flex items-center space-x-2">
                      <Layers className="w-4 h-4 text-emerald-500 shrink-0" />
                      <span className="font-semibold text-emerald-800 dark:text-emerald-300">
                        STORY CLUSTER ({item.story_cluster.article_count} articles across {item.story_cluster.publishers_count} outlets in {item.story_cluster.countries_count} countries)
                      </span>
                      <span className="text-[11px] text-slate-500 font-mono hidden sm:inline">
                        Wire Syndicate: {item.story_cluster.primary_source_name}
                      </span>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedArticleId(item.id)}
                      className="h-7 text-xs font-semibold text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/20 px-2"
                    >
                      Explore Syndicate Coverage &rarr;
                    </Button>
                  </div>
                )}

                {/* Card Top: Type badge, status, source, country, relevance */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-[10px] font-bold uppercase",
                        item.content_type === 'video' ? 'bg-purple-500/10 text-purple-600 border-purple-500/30' :
                        item.content_type === 'image' ? 'bg-sky-500/10 text-sky-600 border-sky-500/30' :
                        'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                      )}
                    >
                      {item.content_type}
                    </Badge>

                    {/* Investigation Status */}
                    <Badge
                      variant="outline"
                      className="text-[10px] font-bold text-slate-500 dark:text-slate-400 border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 font-mono"
                    >
                      {item.investigation_status}
                    </Badge>

                    {item.country && (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-sky-500/10 text-sky-600 dark:text-sky-400 font-mono font-medium">
                        {item.country}
                      </span>
                    )}

                    <span className="text-xs text-slate-500">
                      Source: <strong className="text-slate-700 dark:text-slate-300">{item.source}</strong> ({item.publisher})
                    </span>

                    {item.author && (
                      <span className="text-xs text-slate-400 italic">
                        By {item.author}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold font-mono text-emerald-600 dark:text-emerald-400">
                      Relevance: {item.relevance_score.toFixed(0)}%
                    </span>
                    {item.publication_date && (
                      <span className="text-[11px] text-slate-400">
                        • {item.publication_date}
                      </span>
                    )}
                  </div>
                </div>

                {/* Title & Summary with optional thumbnail / video player */}
                {playingVideoId === item.id && (item.media_indicators?.embed_url) ? (
                  <div className="relative aspect-video w-full rounded-2xl overflow-hidden bg-black shadow-lg border border-slate-800 my-2">
                    <iframe
                      src={`${item.media_indicators.embed_url}?autoplay=1`}
                      title={item.title}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      className="w-full h-full border-0"
                    />
                    <button
                      onClick={() => setPlayingVideoId(null)}
                      className="absolute top-2.5 right-2.5 bg-black/80 hover:bg-black text-white p-1 rounded-full text-xs cursor-pointer shadow-md"
                      title="Close Video"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col sm:flex-row gap-4 items-start">
                    {item.hero_image && (
                      <div
                        onClick={() => {
                          if ((item.content_type === 'video' || item.media_indicators?.is_video) && item.media_indicators?.embed_url) {
                            setPlayingVideoId(item.id);
                          } else {
                            setSelectedArticleId(item.id);
                          }
                        }}
                        className="w-full sm:w-48 h-32 rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800 shrink-0 cursor-pointer border border-slate-200 dark:border-slate-800 group relative"
                      >
                        <img
                          src={item.hero_image}
                          alt={item.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          loading="lazy"
                        />
                        {(item.content_type === 'video' || item.media_indicators?.is_video) ? (
                          <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                            <div className="w-9 h-9 rounded-full bg-red-600/95 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                              <Play className="w-4 h-4 fill-white ml-0.5" />
                            </div>
                            <span className="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 bg-black/80 text-white text-[10px] rounded font-mono font-bold">
                              VIDEO
                            </span>
                          </div>
                        ) : (
                          <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                            <span className="text-[10px] bg-slate-900/90 text-white px-2 py-0.5 rounded font-medium">Read Article</span>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex-1 space-y-1">
                      <h3
                        onClick={() => {
                          if ((item.content_type === 'video' || item.media_indicators?.is_video) && item.media_indicators?.embed_url) {
                            setPlayingVideoId(item.id);
                          } else {
                            setSelectedArticleId(item.id);
                          }
                        }}
                        className="text-base font-bold text-slate-900 dark:text-slate-100 font-sans hover:text-emerald-600 transition-colors cursor-pointer leading-snug"
                      >
                        {item.title}
                      </h3>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed line-clamp-3">
                        {item.summary}
                      </p>
                    </div>
                  </div>
                )}

                {/* Explanation Bar: Why was this result returned? */}
                {item.search_explanation && (
                  <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-400 flex items-center space-x-2">
                    <span className="font-bold text-emerald-600 dark:text-emerald-400 shrink-0">
                      Match Rationale:
                    </span>
                    <span className="font-mono text-slate-700 dark:text-slate-300 truncate">
                      {item.search_explanation}
                    </span>
                  </div>
                )}

                {/* Entities & Indicators */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 dark:border-slate-800/80">
                  <div className="flex flex-wrap items-center gap-1.5">
                    {item.detected_entities.map((ent, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                      >
                        {ent}
                      </span>
                    ))}
                    {item.claim_indicators && item.claim_indicators.length > 0 && (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-medium">
                        {item.claim_indicators.length} Claim Indicators
                      </span>
                    )}
                  </div>

                  {/* Actions (Section 12): READ ARTICLE, INVESTIGATE, COMPARE, ADD TO CASE, VIEW EVIDENCE */}
                  <div className="flex flex-wrap items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setSelectedArticleId(item.id)}
                      className="text-xs h-8 border-slate-300 dark:border-slate-700 hover:border-emerald-500 hover:text-emerald-600 font-semibold text-slate-800 dark:text-slate-200"
                    >
                      <BookOpen className="w-3.5 h-3.5 mr-1 text-emerald-500" />
                      READ ARTICLE
                    </Button>

                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setPreviewItem(item)}
                      className="text-xs text-slate-600 dark:text-slate-400 h-8"
                    >
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      Evidence
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => toggleCompare(item)}
                      className="text-xs h-8"
                    >
                      {compareItems.some((i) => i.id === item.id) ? 'Remove Compare' : 'Compare'}
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setCaseModalItem({ id: item.id, title: item.title })}
                      className="text-xs h-8 text-slate-600 dark:text-slate-400"
                    >
                      <Briefcase className="w-3.5 h-3.5 mr-1" />
                      Add to Case
                    </Button>

                    <Button
                      size="sm"
                      variant="default"
                      onClick={() => handleInvestigateResult(item)}
                      disabled={createInvestigationMutation.isPending}
                      className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-bold h-8 px-4"
                    >
                      <ArrowRight className="w-3.5 h-3.5 mr-1" />
                      INVESTIGATE
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : searchMutation.data ? (
          <div className="py-16 text-center space-y-2">
            <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto" />
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
              No results found above {minRelevance}% relevance
            </h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Try adjusting the minimum relevance threshold or broadening search operators while maintaining your core inquiry scope.
            </p>
          </div>
        ) : (
          <div className="py-20 text-center space-y-3">
            <Newspaper className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto" />
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
              Ready for Investigation
            </h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
              Enter an investigative target above (topic, claim, viral video description, or person). The engine will search verified sources and initialize an evidence-backed dossier.
            </p>
          </div>
        )}
      </div>

      {/* Comparison Drawer */}
      {isCompareOpen && compareItems.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-[#0c101e]/95 border-t border-slate-200 dark:border-slate-800 p-4 shadow-2xl backdrop-blur-md">
          <div className="max-w-7xl mx-auto flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
              Side-by-Side Artifact Comparison ({compareItems.length} selected)
            </span>
            <button
              onClick={() => setIsCompareOpen(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-3">
            {compareItems.map((c) => (
              <div
                key={c.id}
                className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 text-xs space-y-1.5"
              >
                <div className="flex justify-between items-center">
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {c.content_type}
                  </Badge>
                  <span className="font-mono text-emerald-600 font-bold">{c.relevance_score.toFixed(0)}%</span>
                </div>
                <h4 className="font-bold truncate text-slate-900 dark:text-slate-100">{c.title}</h4>
                <p className="text-slate-500 text-[11px] line-clamp-2">{c.summary}</p>
                <div className="pt-1 flex justify-end">
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => handleInvestigateResult(c)}
                    className="text-[11px] h-6 bg-emerald-600 text-white"
                  >
                    Investigate
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Internal Evidence Preview Modal */}
      {previewItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-slate-900/40 dark:bg-black/70 backdrop-blur-xs"
            onClick={() => setPreviewItem(null)}
          />
          <div className="relative w-full max-w-xl rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f1422] p-6 z-10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Internal Evidence Snapshot
              </h3>
              <button
                onClick={() => setPreviewItem(null)}
                className="p-1 rounded text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                {previewItem.title}
              </h4>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                {previewItem.summary}
              </p>
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-900 font-mono text-[11px] text-slate-500 space-y-1">
                <div>Source: {previewItem.source}</div>
                <div>Publisher: {previewItem.publisher}</div>
                <div>Canonical URL: {previewItem.canonical_url}</div>
                <div>Relevance Score: {previewItem.relevance_score}%</div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button
                size="sm"
                variant="default"
                onClick={() => {
                  handleInvestigateResult(previewItem);
                  setPreviewItem(null);
                }}
                className="bg-emerald-600 text-white text-xs"
              >
                Launch Deep Investigation
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Direct URL Ingestion Modal */}
      {isDirectUrlOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-slate-900/40 dark:bg-black/70 backdrop-blur-xs"
            onClick={() => setIsDirectUrlOpen(false)}
          />
          <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f1422] p-6 z-10 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                  Investigate Target Article or Video URL
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Content will be extracted internally without redirecting investigators off-platform.
                </p>
              </div>
              <button
                onClick={() => setIsDirectUrlOpen(false)}
                className="p-1 rounded text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleDirectUrlInvestigate} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Target URL (Article, Video, Social Post) *
                </label>
                <input
                  type="url"
                  value={directUrl}
                  onChange={(e) => setDirectUrl(e.target.value)}
                  placeholder="https://example.com/investigative-report-or-video"
                  required
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Hypothesis / Investigation Title (Optional)
                </label>
                <input
                  type="text"
                  value={directUrlTitle}
                  onChange={(e) => setDirectUrlTitle(e.target.value)}
                  placeholder="e.g. Purported flood emergency verification"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => setIsDirectUrlOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  variant="default"
                  disabled={createInvestigationMutation.isPending}
                  className="bg-emerald-600 text-white text-xs"
                >
                  {createInvestigationMutation.isPending ? 'Extracting...' : 'Start Investigation'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Watchlists Modal */}
      <WatchlistsModal
        isOpen={isWatchlistsOpen}
        onClose={() => setIsWatchlistsOpen(false)}
        onSelectTopic={(topic) => handleSearch(topic)}
      />

      {/* Add To Case Modal */}
      {caseModalItem && (
        <AddToCaseModal
          isOpen={Boolean(caseModalItem)}
          onClose={() => setCaseModalItem(null)}
          investigationId={caseModalItem.id}
          investigationTitle={caseModalItem.title}
        />
      )}
    </div>
  );
};
