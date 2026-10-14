import React, { useState } from 'react';
import {
  Share2,
  Search,
  Radio,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
  Layers,
  Sparkles,
  RefreshCw,
  FolderPlus,
  Play,
  MessageSquare,
  Eye,
  Heart,
  Repeat2,
  Clock,
  UserCheck,
  Bot,
  Video,
  FileText,
  Activity,
  Flame,
  Globe
} from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import {
  useSocialSearch,
  useYouTubeInvestigation,
  useCredibilityAnalysis,
  useRegionalNarrativeComparison,
  SocialPost,
  SocialPlatformType,
  CibCluster,
  CredibilityScore,
  YouTubeInvestigationResult,
  RegionalGeography,
  RegionalPerspective,
} from '../../core/api/socialHooks';
import { formatDate, cn } from '../../lib/utils';

export const SocialIntelligencePage: React.FC = () => {
  const [query, setQuery] = useState('malware threat campaign');
  const [selectedPlatforms, setSelectedPlatforms] = useState<SocialPlatformType[]>([
    'bluesky',
    'telegram',
    'reddit',
    'mastodon',
    'youtube'
  ]);
  const [detectCib, setDetectCib] = useState(true);
  const [activeTab, setActiveTab] = useState<'feed' | 'cib' | 'youtube' | 'regional'>('feed');

  // Regional Narrative Comparison State
  const [regionalTopic, setRegionalTopic] = useState('defense aerospace readiness');
  const [selectedRegions, setSelectedRegions] = useState<RegionalGeography[]>([
    'SOUTH_INDIA',
    'NORTH_INDIA',
    'PAKISTAN'
  ]);
  const [egressRoute, setEgressRoute] = useState<'DIRECT' | 'REGIONAL_GATEWAY_APPROVED'>('REGIONAL_GATEWAY_APPROVED');
  const [failClosed, setFailClosed] = useState(true);

  // YouTube modal / inspection
  const [inspectingVideoId, setInspectingVideoId] = useState<string | null>(null);
  const [selectedPostCredibility, setSelectedPostCredibility] = useState<CredibilityScore | null>(null);

  // Mutations
  const searchMutation = useSocialSearch();
  const ytMutation = useYouTubeInvestigation();
  const credMutation = useCredibilityAnalysis();
  const regionalMutation = useRegionalNarrativeComparison();

  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    searchMutation.mutate({
      query: query.trim(),
      platforms: selectedPlatforms,
      limit: 25,
      detect_cib: detectCib,
    });
  };

  const togglePlatform = (p: SocialPlatformType) => {
    if (selectedPlatforms.includes(p)) {
      if (selectedPlatforms.length > 1) {
        setSelectedPlatforms(selectedPlatforms.filter((item) => item !== p));
      }
    } else {
      setSelectedPlatforms([...selectedPlatforms, p]);
    }
  };

  const handleInspectYouTube = (urlOrId: string) => {
    setInspectingVideoId(urlOrId);
    ytMutation.mutate({ video_url_or_id: urlOrId });
    setActiveTab('youtube');
  };

  const handleScoreAccount = (post: SocialPost) => {
    credMutation.mutate(
      {
        target: post.author,
        platform: post.platform,
        posts: searchMutation.data?.results.filter((p) => p.author === post.author) || [post],
      },
      {
        onSuccess: (data) => setSelectedPostCredibility(data),
      }
    );
  };

  const handleRegionalCompare = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!regionalTopic.trim()) return;
    regionalMutation.mutate({
      topic: regionalTopic.trim(),
      selected_regions: selectedRegions,
      egress_route: egressRoute,
      fail_closed: failClosed,
      collection_limit: 15,
    });
  };

  const toggleRegion = (reg: RegionalGeography) => {
    if (selectedRegions.includes(reg)) {
      if (selectedRegions.length > 1) {
        setSelectedRegions(selectedRegions.filter((r) => r !== reg));
      }
    } else {
      setSelectedRegions([...selectedRegions, reg]);
    }
  };

  const posts = searchMutation.data?.results || [];
  const cibClusters = searchMutation.data?.cib_clusters || [];

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Workspace Header */}
      <div className="rounded-2xl border border-slate-200/90 bg-white p-6 sm:p-7 relative overflow-hidden shadow-xs dark:border-slate-800 dark:bg-[#0f1422]">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
                <Share2 className="w-5 h-5" />
              </span>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white font-sans">
                Social Media Intelligence & Inauthentic Behavior Engine
              </h1>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
              Cross-platform OSINT harvesting across Bluesky, Telegram, Reddit, Mastodon, and YouTube.
              Detects Coordinated Inauthentic Behavior (CIB) bursts, bot indicators, and video transcripts.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-semibold uppercase">
              5 Collectors Live
            </span>
          </div>
        </div>

        {/* Search Input Bar */}
        <form onSubmit={handleSearch} className="mt-5 space-y-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search keywords, hashtags (#threat), Telegram channels (@wire), or YouTube URLs..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-cyan-500/40 dark:border-slate-800 dark:bg-slate-900 dark:text-white font-mono"
              />
            </div>

            <Button
              type="submit"
              disabled={searchMutation.isPending}
              className="px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-semibold text-xs tracking-wide uppercase transition-all shadow-sm"
            >
              {searchMutation.isPending ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 mr-2 animate-spin" />
                  HARVESTING INTELLIGENCE...
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5 mr-2" />
                  DISPATCH COLLECTORS
                </>
              )}
            </Button>
          </div>

          {/* Platform Filters and Options */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
            <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
              <span className="text-slate-400 mr-1 text-[11px]">PLATFORMS:</span>
              {(['bluesky', 'telegram', 'reddit', 'mastodon', 'youtube'] as SocialPlatformType[]).map((p) => {
                const active = selectedPlatforms.includes(p);
                return (
                  <button
                    key={p}
                    type="button"
                    onClick={() => togglePlatform(p)}
                    className={cn(
                      'px-2.5 py-1 rounded-lg border text-xs capitalize transition-all cursor-pointer font-medium',
                      active
                        ? 'bg-cyan-50 border-cyan-300 text-cyan-800 dark:bg-cyan-950/40 dark:border-cyan-800 dark:text-cyan-300'
                        : 'bg-slate-100 border-slate-200 text-slate-500 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400 opacity-60'
                    )}
                  >
                    {p === 'bluesky' && '🦋 Bluesky'}
                    {p === 'telegram' && '✈️ Telegram'}
                    {p === 'reddit' && '🤖 Reddit'}
                    {p === 'mastodon' && '🐘 Mastodon'}
                    {p === 'youtube' && '▶️ YouTube'}
                  </button>
                );
              })}
            </div>

            <div className="flex items-center gap-3 text-xs">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={detectCib}
                  onChange={(e) => setDetectCib(e.target.checked)}
                  className="rounded border-slate-300 text-cyan-600 focus:ring-cyan-500"
                />
                <span className="text-slate-600 dark:text-slate-300 font-medium">
                  Detect Coordinated Inauthentic Behavior (CIB)
                </span>
              </label>
            </div>
          </div>
        </form>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('feed')}
          className={cn(
            'px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono transition-colors cursor-pointer',
            activeTab === 'feed'
              ? 'bg-cyan-600 text-white'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
          )}
        >
          Social Posts Feed ({posts.length})
        </button>

        <button
          onClick={() => setActiveTab('cib')}
          className={cn(
            'px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono transition-colors flex items-center gap-1.5 cursor-pointer',
            activeTab === 'cib'
              ? 'bg-rose-600 text-white'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
          )}
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          CIB Anomaly Clusters ({cibClusters.length})
        </button>

        <button
          onClick={() => setActiveTab('youtube')}
          className={cn(
            'px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono transition-colors flex items-center gap-1.5 cursor-pointer',
            activeTab === 'youtube'
              ? 'bg-red-600 text-white'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
          )}
        >
          <Video className="w-3.5 h-3.5" />
          YouTube Video Forensics
        </button>

        <button
          onClick={() => {
            setActiveTab('regional');
            if (!regionalMutation.data && !regionalMutation.isPending) {
              handleRegionalCompare();
            }
          }}
          className={cn(
            'px-3.5 py-1.5 rounded-lg text-xs font-semibold font-mono transition-colors flex items-center gap-1.5 cursor-pointer',
            activeTab === 'regional'
              ? 'bg-emerald-600 text-white'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
          )}
        >
          <Globe className="w-3.5 h-3.5" />
          Regional Narrative Comparison
        </button>
      </div>

      {/* 1. SOCIAL POSTS FEED TAB */}
      {activeTab === 'feed' && (
        <div className="space-y-4">
          {posts.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500 dark:border-slate-800 space-y-3">
              <Share2 className="w-8 h-8 mx-auto text-slate-400" />
              <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                {searchMutation.data ? "No authentic social posts returned for this query" : "No social media dispatches collected yet"}
              </p>
              {searchMutation.data?.provider_statuses && Object.keys(searchMutation.data.provider_statuses).length > 0 && (
                <div className="max-w-md mx-auto pt-2 text-left space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono block text-center">
                    Collector Diagnostics & Platform Quota Status:
                  </span>
                  <div className="space-y-1.5 font-mono text-[11px]">
                    {Object.entries(searchMutation.data.provider_statuses).map(([plat, status_str]) => (
                      <div
                        key={plat}
                        className="p-2 rounded-lg border bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-between"
                      >
                        <strong className="capitalize text-slate-900 dark:text-white">{plat}:</strong>
                        <span className="text-right truncate ml-2 text-xs">{status_str}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <p className="text-xs text-slate-400">
                {searchMutation.data
                  ? "Zero synthetic data injected. External platforms restricting automated access require authenticated API credentials."
                  : "Enter a query above and dispatch collectors."}
              </p>
            </div>
          ) : (
            posts.map((post) => (
              <Card key={post.id} className="border-slate-200/90 dark:border-slate-800 dark:bg-[#0f1422] shadow-xs">
                <CardContent className="p-4 sm:p-5 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="neutral"
                        className={cn(
                          'uppercase font-mono text-[10px] px-2 py-0.5 font-bold',
                          post.platform === 'bluesky' && 'bg-cyan-50 text-cyan-700 border-cyan-200 dark:bg-cyan-950/40 dark:text-cyan-300',
                          post.platform === 'telegram' && 'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-950/40 dark:text-sky-300',
                          post.platform === 'reddit' && 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/40 dark:text-orange-300',
                          post.platform === 'mastodon' && 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300',
                          post.platform === 'youtube' && 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300'
                        )}
                      >
                        {post.platform}
                      </Badge>

                      <span className="font-bold text-slate-900 dark:text-white font-mono">{post.author}</span>
                      {post.channel_name && (
                        <span className="text-slate-400 font-mono text-[11px]">in {post.channel_name}</span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-slate-400 font-mono text-[11px]">
                      <span>{formatDate(post.created_at)}</span>
                      <a
                        href={post.url}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:text-cyan-600 dark:hover:text-cyan-400 flex items-center gap-1"
                      >
                        Source <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 whitespace-pre-line leading-relaxed font-sans">
                    {post.text}
                  </p>

                  {/* Links / Media preview */}
                  {post.links.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {post.links.map((link, idx) => (
                        <a
                          key={idx}
                          href={link}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] font-mono text-cyan-600 dark:text-cyan-400 hover:underline bg-cyan-50 dark:bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-200/50 dark:border-cyan-800/50 truncate max-w-xs"
                        >
                          🔗 {link}
                        </a>
                      ))}
                    </div>
                  )}

                  {/* Actions & Metrics */}
                  <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                      {post.views_count !== undefined && (
                        <span className="flex items-center gap-1">
                          <Eye className="w-3.5 h-3.5" /> {post.views_count.toLocaleString()}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Heart className="w-3.5 h-3.5" /> {post.likes_count}
                      </span>
                      <span className="flex items-center gap-1">
                        <Repeat2 className="w-3.5 h-3.5" /> {post.reposts_count}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleScoreAccount(post)}
                        className="text-[11px] font-mono cursor-pointer"
                      >
                        <UserCheck className="w-3 h-3 mr-1" /> Bot Check
                      </Button>

                      {post.platform === 'youtube' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleInspectYouTube(post.url)}
                          className="text-[11px] font-mono cursor-pointer bg-red-500/10 text-red-600 hover:bg-red-500/20 dark:text-red-400 border border-red-500/20"
                        >
                          <Play className="w-3 h-3 mr-1" /> Transcript
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* 2. CIB ANOMALY CLUSTERS TAB */}
      {activeTab === 'cib' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/70 dark:border-amber-900/60 dark:bg-amber-950/30 text-amber-900 dark:text-amber-200 text-xs">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
              <div>
                <strong className="font-semibold">Auditable CIB Disclaimer:</strong> These are algorithmic signals
                warranting analyst review, not a determination of inauthenticity. Legitimate public campaigns
                (emergency services, press releases, activist networks) exhibit similar burst synchronizations.
              </div>
            </div>
          </div>

          {cibClusters.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-500 dark:border-slate-800">
              <CheckCircle2 className="w-10 h-10 mx-auto text-emerald-500 mb-2" />
              <p className="text-sm font-semibold">No Coordinated Inauthentic Behavior clusters detected.</p>
              <p className="text-xs text-slate-400 mt-1">Cross-account publication timings conform to natural dispersion.</p>
            </div>
          ) : (
            cibClusters.map((cluster) => (
              <Card key={cluster.cluster_id} className="border-rose-200 dark:border-rose-900/60 dark:bg-[#120a14] shadow-xs">
                <CardContent className="p-5 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="p-1.5 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                        <Flame className="w-4 h-4" />
                      </span>
                      <h3 className="font-bold text-sm text-slate-900 dark:text-white font-mono">{cluster.primary_topic}</h3>
                    </div>

                    <Badge variant="destructive" className="font-mono text-xs font-bold">
                      Coordination Score: {cluster.coordination_confidence}%
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono pt-1">
                    <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                      <span className="text-slate-400 text-[10px] block">ACCOUNTS INVOLVED</span>
                      <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{cluster.account_count}</span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                      <span className="text-slate-400 text-[10px] block">BURST POSTS</span>
                      <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{cluster.post_count}</span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                      <span className="text-slate-400 text-[10px] block">BURST WINDOW</span>
                      <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{cluster.duration_seconds}s</span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                      <span className="text-slate-400 text-[10px] block">VELOCITY</span>
                      <span className="text-sm font-bold text-rose-600 dark:text-rose-400">{cluster.synchronization_velocity} /min</span>
                    </div>
                  </div>

                  {/* Accounts Involved */}
                  <div className="text-xs space-y-1 pt-1">
                    <span className="text-slate-400 font-mono text-[11px] block">AFFILIATED ACCOUNTS:</span>
                    <div className="flex flex-wrap gap-1.5 font-mono text-xs">
                      {cluster.accounts.map((acc, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-rose-50 border border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900/60 dark:text-rose-300">
                          {acc}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Shared URLs or Phrases */}
                  {cluster.shared_urls.length > 0 && (
                    <div className="text-xs space-y-1">
                      <span className="text-slate-400 font-mono text-[11px] block">SYNCHRONIZED DISSEMINATION TARGETS:</span>
                      {cluster.shared_urls.map((u, idx) => (
                        <div key={idx} className="text-cyan-600 dark:text-cyan-400 font-mono text-xs truncate">
                          🔗 {u}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* 3. YOUTUBE VIDEO FORENSICS TAB */}
      {activeTab === 'youtube' && (
        <div className="space-y-4">
          <Card className="border-slate-200/90 dark:border-slate-800 dark:bg-[#0f1422] p-5">
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  placeholder="Enter YouTube Video URL or ID (e.g. https://www.youtube.com/watch?v=wb_DPZnYx04)..."
                  value={inspectingVideoId || ''}
                  onChange={(e) => setInspectingVideoId(e.target.value)}
                  className="flex-1 px-3.5 py-2 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-900 font-mono dark:border-slate-800 dark:bg-slate-900 dark:text-white"
                />
                <Button
                  size="sm"
                  onClick={() => inspectingVideoId && handleInspectYouTube(inspectingVideoId)}
                  disabled={ytMutation.isPending}
                  className="bg-red-600 hover:bg-red-700 text-white font-mono text-xs uppercase"
                >
                  {ytMutation.isPending ? 'Extracting...' : 'Analyze Video'}
                </Button>
              </div>

              {ytMutation.data && (
                <div className="space-y-4 pt-3 border-t border-slate-200 dark:border-slate-800">
                  <div className="flex flex-col md:flex-row gap-4">
                    <img
                      src={ytMutation.data.metadata.thumbnail_url}
                      alt={ytMutation.data.metadata.title}
                      className="w-full md:w-64 h-36 object-cover rounded-xl border border-slate-200 dark:border-slate-800"
                    />
                    <div className="space-y-1.5 flex-1">
                      <h3 className="font-bold text-base text-slate-900 dark:text-white">{ytMutation.data.metadata.title}</h3>
                      <p className="text-xs text-slate-500 font-mono">
                        Channel: <strong>{ytMutation.data.metadata.channel_title}</strong> • Views: {ytMutation.data.metadata.view_count.toLocaleString()} • Likes: {ytMutation.data.metadata.like_count.toLocaleString()}
                      </p>
                      <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 leading-relaxed">
                        {ytMutation.data.metadata.description}
                      </p>
                    </div>
                  </div>

                  {/* Subtitles / Closed Captions */}
                  {ytMutation.data.subtitles && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-xs uppercase font-mono tracking-wider text-slate-400">
                        Timestamped Subtitles & Transcript Segments
                      </h4>
                      <div className="max-h-60 overflow-y-auto space-y-1.5 p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 font-mono text-xs">
                        {ytMutation.data.subtitles.segments.map((seg, idx) => (
                          <div key={idx} className="flex gap-3 hover:bg-slate-100 dark:hover:bg-slate-800/40 p-1.5 rounded transition-colors">
                            <span className="text-cyan-600 dark:text-cyan-400 font-bold shrink-0">
                              [{Math.floor(seg.start_seconds / 60)}:{(seg.start_seconds % 60).toFixed(0).padStart(2, '0')}]
                            </span>
                            <span className="text-slate-800 dark:text-slate-200">{seg.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Top Comments */}
                  {ytMutation.data.top_comments.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-xs uppercase font-mono tracking-wider text-slate-400">
                        Audience Sentiment & Comments
                      </h4>
                      <div className="space-y-2">
                        {ytMutation.data.top_comments.map((comm) => (
                          <div key={comm.id} className="p-3 rounded-lg border border-slate-100 dark:border-slate-800/60 bg-white dark:bg-slate-900/40 text-xs space-y-1">
                            <div className="flex justify-between font-mono text-[11px] text-slate-400">
                              <span className="font-bold text-slate-800 dark:text-slate-200">{comm.author}</span>
                              <span>Likes: {comm.likes}</span>
                            </div>
                            <p className="text-slate-700 dark:text-slate-300">{comm.text}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* 4. REGIONAL NARRATIVE COMPARISON TAB */}
      {activeTab === 'regional' && (
        <div className="space-y-6">
          {/* Query & Regional Scope Config Card */}
          <Card className="border-slate-200/90 dark:border-slate-800 dark:bg-[#0f1422] shadow-xs">
            <CardContent className="p-5 space-y-4">
              <form onSubmit={handleRegionalCompare} className="space-y-4">
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={regionalTopic}
                      onChange={(e) => setRegionalTopic(e.target.value)}
                      placeholder="Enter investigation topic or claim for cross-regional analysis..."
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50/50 dark:bg-slate-900/50 dark:border-slate-800 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 font-sans"
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={regionalMutation.isPending || !regionalTopic.trim()}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-mono text-xs uppercase px-5 py-2.5 rounded-xl flex items-center justify-center gap-2 cursor-pointer shadow-xs shrink-0"
                  >
                    {regionalMutation.isPending ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        Comparing...
                      </>
                    ) : (
                      <>
                        <Globe className="w-3.5 h-3.5" />
                        Compare Geographies
                      </>
                    )}
                  </Button>
                </div>

                {/* Region Selector Pills */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                      Target Geographies (Select to Compare):
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      {selectedRegions.length} selected
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { id: 'SOUTH_INDIA' as RegionalGeography, label: 'South India', sub: 'Tamil Nadu / Karnataka / Kerala' },
                      { id: 'NORTH_INDIA' as RegionalGeography, label: 'North India', sub: 'Delhi / Punjab / Northern Belt' },
                      { id: 'PAKISTAN' as RegionalGeography, label: 'Pakistan', sub: 'Federal & Provincial Press' },
                      { id: 'BANGLADESH' as RegionalGeography, label: 'Bangladesh', sub: 'National & Regional Wires' },
                      { id: 'INTERNATIONAL' as RegionalGeography, label: 'International', sub: 'Global Agencies & Wires' },
                    ].map((reg) => {
                      const isSel = selectedRegions.includes(reg.id);
                      return (
                        <button
                          key={reg.id}
                          type="button"
                          onClick={() => toggleRegion(reg.id)}
                          className={cn(
                            'px-3 py-1.5 rounded-xl border text-left text-xs transition-all cursor-pointer font-sans',
                            isSel
                              ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-800 dark:text-emerald-300 font-semibold'
                              : 'bg-slate-50 border-slate-200 text-slate-600 dark:bg-slate-900/50 dark:border-slate-800 dark:text-slate-400 hover:border-slate-300'
                          )}
                        >
                          <div className="flex items-center gap-1.5">
                            <span className={cn('w-2 h-2 rounded-full', isSel ? 'bg-emerald-500' : 'bg-slate-400')} />
                            <span>{reg.label}</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* OPSEC Egress Profile Selector */}
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800/60 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono text-[11px] uppercase">OPSEC Egress Route:</span>
                    <select
                      value={egressRoute}
                      onChange={(e) => setEgressRoute(e.target.value as any)}
                      className="px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-xs font-mono text-slate-700 dark:text-slate-300 focus:outline-hidden"
                    >
                      <option value="REGIONAL_GATEWAY_APPROVED">Approved Regional Gateway (Fail-Closed)</option>
                      <option value="DIRECT">Direct Network (Audited)</option>
                    </select>
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="flex items-center gap-1.5 cursor-pointer text-slate-600 dark:text-slate-300 font-mono text-[11px]">
                      <input
                        type="checkbox"
                        checked={failClosed}
                        onChange={(e) => setFailClosed(e.target.checked)}
                        className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                      />
                      Fail Closed (Prohibit Direct Fallback)
                    </label>
                  </div>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Loading State */}
          {regionalMutation.isPending && (
            <div className="rounded-xl border border-dashed border-emerald-500/30 p-10 text-center space-y-4 bg-emerald-500/5">
              <RefreshCw className="w-8 h-8 mx-auto text-emerald-500 animate-spin" />
              <div className="space-y-1">
                <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                  Orchestrating Regional Narrative Intelligence
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                  Applying multilingual query transliterations (Tamil, Hindi, Urdu, Bengali), verifying OPSEC network egress route, and harvesting authentic regional perspectives...
                </p>
              </div>
            </div>
          )}

          {/* Results State */}
          {regionalMutation.data && !regionalMutation.isPending && (
            <div className="space-y-6">
              {/* Telemetry & Advisory Banner */}
              <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 space-y-2">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div className="space-y-1 text-xs text-slate-700 dark:text-slate-300">
                    <strong className="text-amber-700 dark:text-amber-300 block font-mono text-[11px] uppercase tracking-wider">
                      Methodology & Sampling Limitation Advisory
                    </strong>
                    <p className="leading-relaxed">
                      {regionalMutation.data.investigator_advisory}
                    </p>
                    <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] font-mono text-slate-500">
                      <span>Comparison ID: <strong>{regionalMutation.data.comparison_id}</strong></span>
                      {regionalMutation.data.egress_status && (
                        <span>
                          Egress: <strong>{regionalMutation.data.egress_status.gateway_name}</strong> (Masked IP: {regionalMutation.data.egress_status.egress_ip_masked})
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Side-by-Side Regional Perspectives Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {regionalMutation.data.regions_compared.map((persp) => (
                  <Card key={persp.region} className="border-slate-200/90 dark:border-slate-800 dark:bg-[#0f1422] shadow-xs flex flex-col">
                    <CardContent className="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-4">
                      <div className="space-y-3">
                        {/* Region Header */}
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                              {persp.region_label}
                            </h3>
                            <span className="text-[10px] font-mono uppercase text-slate-400 block">
                              {persp.region}
                            </span>
                          </div>
                          <Badge variant="outline" className="font-mono text-[10px] shrink-0 font-bold bg-slate-50 dark:bg-slate-900">
                            N = {persp.sample_size} records
                          </Badge>
                        </div>

                        {/* Primary Framing */}
                        <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono block">
                            Observed Narrative Framing:
                          </span>
                          <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-snug">
                            {persp.primary_framing}
                          </p>
                        </div>

                        {/* Distinctive Regional Lexicon */}
                        {persp.distinctive_regional_terms.length > 0 && (
                          <div className="space-y-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono block">
                              Regional Terms & Transliteration:
                            </span>
                            <div className="flex flex-wrap gap-1">
                              {persp.distinctive_regional_terms.map((term, tIdx) => (
                                <Badge key={tIdx} variant="neutral" className="text-[10px] font-mono px-1.5 py-0.5">
                                  {term}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Extracted Claims */}
                        {persp.claims.length > 0 && (
                          <div className="space-y-2 pt-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono block">
                              Representative Dispatches:
                            </span>
                            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                              {persp.claims.map((claim, cIdx) => (
                                <div key={cIdx} className="p-2 rounded border border-slate-100 dark:border-slate-800/60 bg-white dark:bg-slate-900/40 text-xs space-y-1">
                                  <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                                    <span className="font-bold text-slate-700 dark:text-slate-300 truncate max-w-[140px]">
                                      {claim.publisher}
                                    </span>
                                    <span>{claim.publication_time}</span>
                                  </div>
                                  <p className="text-slate-800 dark:text-slate-200 font-medium line-clamp-2">
                                    "{claim.claim_text}"
                                  </p>
                                  {claim.translated_text && (
                                    <p className="text-[11px] text-emerald-600 dark:text-emerald-400 italic">
                                      {claim.translated_text}
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Footer: Sources & Limitation */}
                      <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2 text-[11px] font-mono text-slate-500">
                        <div className="flex justify-between">
                          <span>Evidence Balance:</span>
                          <span>
                            <strong className="text-emerald-600 dark:text-emerald-400">+{persp.supporting_evidence_count}</strong>
                            {' / '}
                            <strong className="text-rose-600 dark:text-rose-400">-{persp.conflicting_evidence_count}</strong>
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 italic">
                          {persp.collection_coverage_notes}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Cross-Regional Synthesis & Divergence Card */}
              <Card className="border-slate-200/90 dark:border-slate-800 dark:bg-[#0f1422] shadow-xs">
                <CardContent className="p-5 space-y-4">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    <h3 className="font-bold text-sm text-slate-900 dark:text-white font-mono uppercase tracking-wider">
                      Cross-Regional Narrative Synthesis & Divergences
                    </h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Key Similarities */}
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 space-y-2">
                      <span className="text-[11px] font-bold font-mono uppercase tracking-wider text-emerald-600 dark:text-emerald-400 block">
                        Observed Similarities Across Coverage:
                      </span>
                      <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
                        {regionalMutation.data.key_similarities.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-emerald-500 mt-0.5">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Key Divergences */}
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 space-y-2">
                      <span className="text-[11px] font-bold font-mono uppercase tracking-wider text-rose-600 dark:text-rose-400 block">
                        Distinct Framing Divergences:
                      </span>
                      <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
                        {regionalMutation.data.key_divergences.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-rose-500 mt-0.5">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Controlled Variables & Limitations */}
                  <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-4 text-xs font-mono text-slate-500">
                    <div>
                      <span className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                        Controlled Experimental Variables:
                      </span>
                      <ul className="space-y-0.5 list-disc list-inside">
                        {regionalMutation.data.controlled_variables.map((cv, idx) => (
                          <li key={idx}>{cv}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                        Uncontrolled Sampling Limitations:
                      </span>
                      <ul className="space-y-0.5 list-disc list-inside">
                        {regionalMutation.data.uncontrolled_limitations.map((ul, idx) => (
                          <li key={idx}>{ul}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* Account Credibility Modal */}
      {selectedPostCredibility && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#0f1422] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                <h3 className="font-bold text-sm text-slate-900 dark:text-white font-mono">
                  Credibility & Bot Audit
                </h3>
              </div>
              <button
                onClick={() => setSelectedPostCredibility(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex justify-between items-center font-mono">
              <div>
                <span className="text-[10px] text-slate-400 block">TARGET</span>
                <span className="font-bold text-xs text-slate-900 dark:text-white">{selectedPostCredibility.target}</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block">BAND</span>
                <Badge
                  variant={selectedPostCredibility.band === 'HIGH' ? 'success' : selectedPostCredibility.band === 'INAUTHENTIC' ? 'destructive' : 'warning'}
                  className="font-bold"
                >
                  {selectedPostCredibility.band} ({selectedPostCredibility.overall_score}%)
                </Badge>
              </div>
            </div>

            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
              {selectedPostCredibility.rationale}
            </p>

            <div className="space-y-1.5 text-xs font-mono">
              <span className="text-[11px] text-slate-400 block">AUDIT FACTORS:</span>
              {Object.entries(selectedPostCredibility.factors).map(([factor, pts]) => (
                <div key={factor} className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                  <span className="capitalize text-slate-500">{factor.replace('_', ' ')}</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{pts} pts</span>
                </div>
              ))}
            </div>

            <Button
              className="w-full text-xs font-mono uppercase"
              onClick={() => setSelectedPostCredibility(null)}
            >
              Close Assessment
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
