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
  SocialPost,
  SocialPlatformType,
  CibCluster,
  CredibilityScore,
  YouTubeInvestigationResult
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
  const [activeTab, setActiveTab] = useState<'feed' | 'cib' | 'youtube'>('feed');

  // YouTube modal / inspection
  const [inspectingVideoId, setInspectingVideoId] = useState<string | null>(null);
  const [selectedPostCredibility, setSelectedPostCredibility] = useState<CredibilityScore | null>(null);

  // Mutations
  const searchMutation = useSocialSearch();
  const ytMutation = useYouTubeInvestigation();
  const credMutation = useCredibilityAnalysis();

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
      </div>

      {/* 1. SOCIAL POSTS FEED TAB */}
      {activeTab === 'feed' && (
        <div className="space-y-4">
          {posts.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-500 dark:border-slate-800">
              <Share2 className="w-10 h-10 mx-auto text-slate-400 mb-2" />
              <p className="text-sm font-semibold">No social media dispatches collected yet.</p>
              <p className="text-xs text-slate-400 mt-1">Enter a query above and dispatch collectors.</p>
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
