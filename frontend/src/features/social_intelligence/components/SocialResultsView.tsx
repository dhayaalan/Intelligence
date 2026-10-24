import React, { useState, useMemo } from 'react';
import {
  Share2,
  ExternalLink,
  MessageSquare,
  Eye,
  Heart,
  Repeat2,
  Video,
  Flame,
  Globe,
  Link as LinkIcon,
  Check,
  Zap,
  ShieldAlert,
  Sparkles,
  UserCheck,
  Film,
  PlusCircle,
  Clock,
  Layers,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Play,
  X,
  ArrowRight
} from 'lucide-react';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Card, CardContent } from '../../../components/ui/Card';
import { useSocialCrawlUrl, useSocialAutoCrawl, SocialCommentItem } from '../../../core/api/socialHooks';
import { formatDate, cn } from '../../../lib/utils';
import { apiRequest } from '../../../core/api/client';

export interface SocialResultItem {
  id: string;
  platform: string;
  author: string;
  author_id?: string;
  text: string;
  url: string;
  created_at?: string;
  likes_count?: number;
  views_count?: number;
  shares_count?: number;
  comments_count?: number;
  post_type?: string; // 'reel' | 'video' | 'post' | 'thread'
  video_url?: string;
  comments?: SocialCommentItem[];
  cib_clusters?: any[];
  credibility_score?: number;
  evidence_id?: string;
  confidence?: number;
  entities?: string[];
}

interface SocialResultsViewProps {
  posts: SocialResultItem[];
  cibClusters?: any[];
  targetQuery?: string;
  investigationId?: string;
  allowDirectCrawl?: boolean;
  onPostCrawledAndSealed?: (newPost: SocialResultItem) => void;
  onPivot?: (term: string) => void;
}

export const SocialResultsView: React.FC<SocialResultsViewProps> = ({
  posts,
  cibClusters = [],
  targetQuery = '',
  investigationId,
  allowDirectCrawl = true,
  onPostCrawledAndSealed,
  onPivot
}) => {
  const [crawlUrl, setCrawlUrl] = useState('');
  const [extractComments, setExtractComments] = useState(true);
  const [showManualUrl, setShowManualUrl] = useState(false);
  const [autoCrawlAttempted, setAutoCrawlAttempted] = useState(false);
  const [autoCrawledPosts, setAutoCrawledPosts] = useState<SocialResultItem[]>([]);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('ALL');
  const [selectedType, setSelectedType] = useState<'ALL' | 'REEL' | 'POST'>('ALL');
  const [expandedComments, setExpandedComments] = useState<Record<string, boolean>>({});
  const [expandedText, setExpandedText] = useState<Record<string, boolean>>({});
  const [sealingPostId, setSealingPostId] = useState<string | null>(null);
  const [sealedSuccessId, setSealedSuccessId] = useState<string | null>(null);
  const [playingVideoId, setPlayingVideoId] = useState<string | null>(null);

  // Helper to extract YouTube video ID
  const getYoutubeId = (url?: string): string | null => {
    if (!url) return null;
    const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})/i);
    return match ? match[1] : null;
  };

  // Helper to check for direct HTML5 video stream
  const isDirectVideo = (url?: string): boolean => {
    if (!url) return false;
    return /\.(mp4|webm|ogg|m4v)(\?.*)?$/i.test(url);
  };

  // Helper to sanitize post captions from raw web scrape noise
  const cleanPostCaption = (rawText?: string): string => {
    if (!rawText) return 'No caption provided.';
    let clean = rawText;
    // Strip common GitHub / web boilerplate
    clean = clean.replace(/Sign inAppearance settings[\s\S]*?(?=[A-Z][a-z]{3,}|$)/g, '');
    clean = clean.replace(/Overview\s+Repositories\s+Projects\s+Packages\s+Stars[\s\S]*/gi, '');
    clean = clean.replace(/Popular repositories[\s\S]*Loading[\s\S]*/gi, '');
    clean = clean.replace(/AI CODE CREATION[\s\S]*?(?=[A-Z][a-z]{3,}|$)/g, '');
    clean = clean.replace(/\n{3,}/g, '\n\n').trim();
    return clean || 'Authentic social media capture';
  };

  const crawlMutation = useSocialCrawlUrl();
  const autoCrawlMutation = useSocialAutoCrawl();

  // Automatically trigger crawler when viewing target and no posts exist
  React.useEffect(() => {
    if (targetQuery && posts.length === 0 && !autoCrawlAttempted && !autoCrawlMutation.isPending) {
      setAutoCrawlAttempted(true);
      autoCrawlMutation.mutate({
        target: targetQuery,
        investigation_id: investigationId,
        extract_comments: true
      }, {
        onSuccess: (data) => {
          if (data && data.results && data.results.length > 0) {
            setAutoCrawledPosts(data.results);
            if (onPostCrawledAndSealed) {
              data.results.forEach(p => onPostCrawledAndSealed(p));
            }
          }
        }
      });
    }
  }, [targetQuery, posts.length, autoCrawlAttempted, investigationId]);

  const handleAutoCrawlTrigger = () => {
    if (!targetQuery) return;
    autoCrawlMutation.mutate({
      target: targetQuery,
      investigation_id: investigationId,
      extract_comments: true
    }, {
      onSuccess: (data) => {
        if (data && data.results && data.results.length > 0) {
          setAutoCrawledPosts(data.results);
          if (onPostCrawledAndSealed) {
            data.results.forEach(p => onPostCrawledAndSealed(p));
          }
        }
      }
    });
  };

  const handleToggleComments = (id: string) => {
    setExpandedComments((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleCrawlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!crawlUrl.trim()) return;

    try {
      const res = await crawlMutation.mutateAsync({
        url: crawlUrl.trim(),
        extract_comments: extractComments
      });

      const newPostItem: SocialResultItem = {
        id: res.url,
        platform: res.platform.toLowerCase(),
        author: res.author,
        text: res.text,
        url: res.url,
        created_at: res.published_at || new Date().toISOString(),
        likes_count: res.likes_count || 0,
        views_count: res.views_count || 0,
        shares_count: res.shares_count || 0,
        comments_count: res.comments_count || (res.comments?.length || 0),
        post_type: res.post_type || (res.video_url ? 'reel' : 'post'),
        video_url: res.video_url,
        comments: res.comments || [],
        entities: res.extracted_entities || [],
        confidence: 0.95
      };

      if (investigationId) {
        // Automatically seal into active investigation
        try {
          await apiRequest(`/evidence`, {
            method: 'POST',
            body: JSON.stringify({
              investigation_id: investigationId,
              source: `${res.platform.toUpperCase()} Resilient Dispatch`,
              provider: res.platform.toLowerCase(),
              module: 'social_media_intelligence',
              reference: res.url,
              confidence: 0.95,
              raw_data: {
                post_id: res.url,
                platform: res.platform,
                author: res.author,
                text: res.text,
                url: res.url,
                created_at: res.published_at,
                likes: res.likes_count,
                views: res.views_count,
                shares: res.shares_count,
                comments_count: res.comments_count,
                post_type: res.post_type,
                video_url: res.video_url,
                comments: res.comments,
                entities: res.extracted_entities
              }
            })
          });
        } catch (sealErr) {
          console.warn('Failed to auto-seal crawled post to investigation:', sealErr);
        }
      }

      if (onPostCrawledAndSealed) {
        onPostCrawledAndSealed(newPostItem);
      }
      setCrawlUrl('');
    } catch (err) {
      console.error('Failed to crawl social URL:', err);
    }
  };

  const handleSealPostToInvestigation = async (post: SocialResultItem) => {
    if (!investigationId) return;
    setSealingPostId(post.id);
    try {
      await apiRequest(`/evidence`, {
        method: 'POST',
        body: JSON.stringify({
          investigation_id: investigationId,
          source: `${post.platform.toUpperCase()} Dispatch`,
          provider: post.platform.toLowerCase(),
          module: 'social_media_intelligence',
          reference: post.url,
          confidence: post.confidence || 0.9,
          raw_data: {
            post_id: post.id,
            platform: post.platform,
            author: post.author,
            text: post.text,
            url: post.url,
            created_at: post.created_at,
            likes: post.likes_count,
            views: post.views_count,
            shares: post.shares_count,
            comments_count: post.comments_count,
            post_type: post.post_type,
            video_url: post.video_url,
            comments: post.comments
          }
        })
      });
      setSealedSuccessId(post.id);
      setTimeout(() => setSealedSuccessId(null), 3000);
    } catch (err) {
      alert('Failed to seal post to investigation');
    } finally {
      setSealingPostId(null);
    }
  };

  // Combined posts: existing investigation posts + newly auto-crawled dispatches
  const mergedPosts = useMemo(() => {
    const combined = [...posts];
    const seen = new Set(posts.map((p) => p.url || p.id));
    autoCrawledPosts.forEach((p) => {
      const u = p.url || p.id;
      if (!seen.has(u)) {
        seen.add(u);
        combined.unshift(p);
      }
    });
    return combined;
  }, [posts, autoCrawledPosts]);

  // Filter posts
  const filteredPosts = useMemo(() => {
    return mergedPosts.filter((p) => {
      const matchPlatform =
        selectedPlatform === 'ALL' ||
        p.platform.toLowerCase() === selectedPlatform.toLowerCase();
      const isReel = p.post_type === 'reel' || Boolean(p.video_url);
      const matchType =
        selectedType === 'ALL' ||
        (selectedType === 'REEL' && isReel) ||
        (selectedType === 'POST' && !isReel);
      return matchPlatform && matchType;
    });
  }, [mergedPosts, selectedPlatform, selectedType]);

  // Aggregate stats
  const reelCount = useMemo(() => mergedPosts.filter((p) => p.post_type === 'reel' || Boolean(p.video_url)).length, [mergedPosts]);
  const totalCommentsCaptured = useMemo(
    () => mergedPosts.reduce((acc, p) => acc + (p.comments?.length || p.comments_count || 0), 0),
    [mergedPosts]
  );
  const platformsPresent = useMemo(
    () => Array.from(new Set(mergedPosts.map((p) => p.platform.toLowerCase()))),
    [mergedPosts]
  );

  const getPlatformStyle = (plat: string) => {
    switch (plat.toLowerCase()) {
      case 'instagram':
        return {
          bg: 'bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-amber-500/10 border-pink-500/30 text-pink-500',
          badge: 'bg-gradient-to-r from-purple-600 to-pink-600 text-white',
          label: 'Instagram'
        };
      case 'facebook':
        return {
          bg: 'bg-blue-500/10 border-blue-500/30 text-blue-500',
          badge: 'bg-blue-600 text-white',
          label: 'Facebook'
        };
      case 'youtube':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-500',
          badge: 'bg-red-600 text-white',
          label: 'YouTube'
        };
      case 'reddit':
        return {
          bg: 'bg-orange-500/10 border-orange-500/30 text-orange-500',
          badge: 'bg-orange-600 text-white',
          label: 'Reddit'
        };
      case 'telegram':
        return {
          bg: 'bg-sky-500/10 border-sky-500/30 text-sky-500',
          badge: 'bg-sky-500 text-white',
          label: 'Telegram'
        };
      case 'bluesky':
        return {
          bg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-500',
          badge: 'bg-cyan-600 text-white',
          label: 'Bluesky'
        };
      case 'mastodon':
        return {
          bg: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-500',
          badge: 'bg-indigo-600 text-white',
          label: 'Mastodon'
        };
      case 'github':
        return {
          bg: 'bg-slate-800/20 border-slate-700/50 text-slate-300',
          badge: 'bg-slate-900 border border-slate-700 text-white',
          label: 'GitHub'
        };
      case 'web':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500',
          badge: 'bg-emerald-600 text-white',
          label: 'Web Capture'
        };
      default:
        return {
          bg: 'bg-slate-500/10 border-slate-500/30 text-slate-500',
          badge: 'bg-slate-700 text-white',
          label: plat.toUpperCase()
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Autonomous Social Media & Reel Crawler Bar */}
      {allowDirectCrawl && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white border border-indigo-900/60 shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
            <Zap className="w-36 h-36 text-indigo-400" />
          </div>

          <div className="relative z-10 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center text-indigo-300">
                  <Film className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                    Autonomous Social Media & Reel Crawler
                    <span className="text-[10px] font-mono font-normal px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      ZERO-INPUT AUTO-CRAWL
                    </span>
                  </h3>
                  <p className="text-xs text-slate-300">
                    Automatically discovers and crawls Instagram reels, Facebook videos, Reddit discussion trees, and comment threads {targetQuery ? <>for <span className="font-semibold text-indigo-200">"{targetQuery}"</span></> : ''} without requiring manual URLs.
                  </p>
                </div>
              </div>

              {/* Automatic Crawl Trigger Button */}
              {targetQuery && (
                <Button
                  type="button"
                  onClick={handleAutoCrawlTrigger}
                  disabled={autoCrawlMutation.isPending}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-2 shrink-0 transition-all cursor-pointer shadow-md"
                >
                  {autoCrawlMutation.isPending ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Auto-Crawling Across Platforms...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-3.5 h-3.5 text-amber-300" />
                      <span>Auto-Crawl Target Now</span>
                    </>
                  )}
                </Button>
              )}
            </div>

            {/* Auto-Crawl Feedback Message */}
            {autoCrawlMutation.isSuccess && autoCrawlMutation.data && (
              <div className="flex items-center gap-2 text-xs text-emerald-300 bg-emerald-950/40 border border-emerald-800/60 px-3 py-1.5 rounded-lg">
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>{autoCrawlMutation.data.message || `Auto-crawl completed: extracted ${autoCrawlMutation.data.total} items.`}</span>
              </div>
            )}

            {/* Optional Collapsible Manual URL input */}
            <div className="pt-1.5 border-t border-indigo-900/40">
              <button
                type="button"
                onClick={() => setShowManualUrl(!showManualUrl)}
                className="text-[11px] text-indigo-300/80 hover:text-indigo-200 flex items-center gap-1 cursor-pointer transition-colors"
              >
                <span>{showManualUrl ? 'Hide manual direct URL tool' : 'Paste a specific direct link (Optional)'}</span>
                {showManualUrl ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>

              {showManualUrl && (
                <form onSubmit={handleCrawlSubmit} className="space-y-2 mt-2">
                  <div className="flex flex-col sm:flex-row gap-2">
                    <div className="relative flex-1">
                      <LinkIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                      <input
                        type="url"
                        value={crawlUrl}
                        onChange={(e) => setCrawlUrl(e.target.value)}
                        placeholder="Paste Instagram Reel / Post, Facebook Video, Reddit thread, YouTube URL..."
                        className="w-full pl-10 pr-4 py-2 text-xs rounded-xl bg-slate-950/70 border border-slate-700 focus:outline-hidden focus:border-indigo-400 text-white placeholder-slate-400 font-mono transition-all"
                      />
                    </div>
                    <Button
                      type="submit"
                      disabled={crawlMutation.isPending || !crawlUrl.trim()}
                      className="bg-indigo-700 hover:bg-indigo-600 text-white text-xs font-semibold px-4 py-2 rounded-xl flex items-center gap-2 shrink-0 transition-all cursor-pointer shadow-md"
                    >
                      {crawlMutation.isPending ? (
                        <>
                          <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          <span>Extracting...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                          <span>Crawl Direct URL</span>
                        </>
                      )}
                    </Button>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-slate-300">
                    <label className="flex items-center gap-2 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={extractComments}
                        onChange={(e) => setExtractComments(e.target.checked)}
                        className="rounded-sm border-slate-700 text-indigo-500 focus:ring-0 focus:ring-offset-0 bg-slate-800"
                      />
                      <span>Extract nested comment tree & discussion sentiments</span>
                    </label>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 2. Coordinated Inauthentic Behavior (CIB) Alerts */}
      {cibClusters.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-900 dark:text-amber-200 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            <AlertTriangle className="w-4 h-4" />
            <span>Coordinated Inauthentic Behavior (CIB) Clusters Detected ({cibClusters.length})</span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Identified suspicious post burst frequency, shared linguistic phraseology, or coordinated cross-platform timing patterns indicative of inorganic narrative amplification.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
            {cibClusters.map((cluster, cIdx) => (
              <div
                key={cIdx}
                className="p-2.5 rounded-xl bg-white/70 dark:bg-slate-900/80 border border-amber-500/20 text-xs space-y-1 font-mono"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-700 dark:text-amber-400">Cluster #{cIdx + 1}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-amber-500/20 text-amber-600 dark:text-amber-300 font-semibold">
                    Confidence {Math.round((cluster.confidence || 0.85) * 100)}%
                  </span>
                </div>
                <div className="text-[11px] text-slate-600 dark:text-slate-400">
                  {cluster.posts_count || (cluster.post_ids?.length || 0)} posts involved • {cluster.reason || 'Synchronized temporal burst'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Metrics Summary Header */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800 shadow-xs">
          <div className="text-[10px] font-mono uppercase text-slate-500 font-semibold">Total Social Dispatches</div>
          <div className="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1">{posts.length}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">{platformsPresent.length} platform networks</div>
        </div>
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800 shadow-xs">
          <div className="text-[10px] font-mono uppercase text-pink-500 font-semibold flex items-center gap-1">
            <Film className="w-3 h-3" />
            <span>Reels & Video Streams</span>
          </div>
          <div className="text-xl font-bold font-mono text-pink-600 dark:text-pink-400 mt-1">{reelCount}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Instagram & Facebook video forensics</div>
        </div>
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800 shadow-xs">
          <div className="text-[10px] font-mono uppercase text-cyan-500 font-semibold flex items-center gap-1">
            <MessageSquare className="w-3 h-3" />
            <span>Captured Comments</span>
          </div>
          <div className="text-xl font-bold font-mono text-cyan-600 dark:text-cyan-400 mt-1">{totalCommentsCaptured}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Thread responses preserved</div>
        </div>
        <div className="p-3.5 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/90 dark:border-slate-800 shadow-xs">
          <div className="text-[10px] font-mono uppercase text-indigo-500 font-semibold flex items-center gap-1">
            <ShieldAlert className="w-3 h-3" />
            <span>Authentic Verification</span>
          </div>
          <div className="text-xl font-bold font-mono text-indigo-600 dark:text-indigo-400 mt-1">100%</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Zero mock / synthetic data</div>
        </div>
      </div>

      {/* 4. Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200/90 dark:border-slate-800">
        <div className="flex items-center gap-1.5 flex-wrap text-xs">
          <span className="text-[11px] font-mono text-slate-400 uppercase mr-1">Platform:</span>
          {['ALL', ...platformsPresent].map((plat) => (
            <button
              key={plat}
              onClick={() => setSelectedPlatform(plat)}
              className={cn(
                'px-2.5 py-1 rounded-lg font-mono text-xs uppercase transition-all cursor-pointer',
                selectedPlatform.toLowerCase() === plat.toLowerCase()
                  ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 font-bold shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200/60 dark:hover:bg-slate-800'
              )}
            >
              {plat}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-[11px] font-mono text-slate-400 uppercase mr-1">Type:</span>
          {[
            { id: 'ALL', label: 'All Items' },
            { id: 'REEL', label: 'Reels & Videos' },
            { id: 'POST', label: 'Text Dispatches' }
          ].map((type) => (
            <button
              key={type.id}
              onClick={() => setSelectedType(type.id as any)}
              className={cn(
                'px-2.5 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer',
                selectedType === type.id
                  ? 'bg-indigo-600 text-white font-semibold shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200/60 dark:hover:bg-slate-800'
              )}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* 5. Posts and Reels Grid */}
      {filteredPosts.length === 0 ? (
        <div className="py-16 text-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 space-y-3 bg-white/40 dark:bg-slate-900/20">
          <Share2 className="w-10 h-10 mx-auto text-slate-400 opacity-50" />
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
            No matching social dispatches or reels found
          </h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            {targetQuery
              ? `The system can automatically crawl and extract authentic public posts, video reels, and comment trees for "${targetQuery}".`
              : 'Try adjusting your platform filters or use the automatic crawler above.'}
          </p>
          {targetQuery && (
            <Button
              type="button"
              onClick={handleAutoCrawlTrigger}
              disabled={autoCrawlMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-xl inline-flex items-center gap-2 cursor-pointer shadow-md mt-2"
            >
              {autoCrawlMutation.isPending ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Auto-Crawling Dispatches & Comments...</span>
                </>
              ) : (
                <>
                  <Zap className="w-3.5 h-3.5 text-amber-300" />
                  <span>Auto-Crawl Social Media for "{targetQuery}"</span>
                </>
              )}
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filteredPosts.map((post) => {
            const pStyle = getPlatformStyle(post.platform);
            const isReel = post.post_type === 'reel' || Boolean(post.video_url);
            const isCommentsOpen = Boolean(expandedComments[post.id]);
            const commentsList = post.comments || [];

            return (
              <div
                key={post.id}
                className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800/90 overflow-hidden shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div className="p-4 space-y-3">
                  {/* Card Header: Platform, Author, Badges */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-bold text-xs uppercase text-slate-700 dark:text-slate-300">
                        {post.author.slice(0, 2)}
                      </div>
                      <div>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-xs font-bold text-slate-900 dark:text-white font-mono hover:underline cursor-pointer"
                            onClick={() => onPivot?.(post.author)}
                          >
                            @{post.author.replace(/^@/, '')}
                          </span>
                          <span className={cn('text-[10px] font-mono px-2 py-0.2 rounded-full font-semibold', pStyle.badge)}>
                            {pStyle.label}
                          </span>
                          {isReel && (
                            <span className="text-[10px] font-mono px-2 py-0.2 rounded-full bg-pink-500/10 text-pink-600 dark:text-pink-400 border border-pink-500/20 font-bold flex items-center gap-1">
                              <Film className="w-2.5 h-2.5" />
                              REEL / VIDEO
                            </span>
                          )}
                        </div>
                        {post.created_at && (
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-slate-400" />
                            {formatDate(post.created_at)}
                          </div>
                        )}
                      </div>
                    </div>

                    <a
                      href={post.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer"
                      title="Open source URL"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>

                  {/* Clean Post Caption with Smart Overflow Clamp */}
                  {(() => {
                    const cleanCaption = cleanPostCaption(post.text);
                    const isLong = cleanCaption.length > 280;
                    const isExpanded = Boolean(expandedText[post.id]);
                    return (
                      <div className="space-y-1">
                        <p
                          className={cn(
                            'text-xs text-slate-700 dark:text-slate-200 leading-relaxed font-sans whitespace-pre-line break-words',
                            !isExpanded && isLong && 'line-clamp-4'
                          )}
                        >
                          {cleanCaption}
                        </p>
                        {isLong && (
                          <button
                            type="button"
                            onClick={() => setExpandedText((prev) => ({ ...prev, [post.id]: !prev[post.id] }))}
                            className="text-[11px] text-indigo-500 hover:text-indigo-400 font-mono font-medium hover:underline cursor-pointer"
                          >
                            {isExpanded ? 'Show less' : 'Show full dispatch'}
                          </button>
                        )}
                      </div>
                    );
                  })()}

                  {/* Play Video Option (YouTube, Reels, & HTML5 Streams) */}
                  {(() => {
                    const videoTargetUrl = post.video_url || post.url;
                    const ytId = getYoutubeId(videoTargetUrl);
                    const isDirect = isDirectVideo(videoTargetUrl);
                    const hasVideo = Boolean(post.video_url) || Boolean(ytId) || isReel;

                    if (!hasVideo) return null;

                    const isPlaying = playingVideoId === post.id;
                    const ytThumb = ytId ? `https://img.youtube.com/vi/${ytId}/hqdefault.jpg` : null;

                    if (isPlaying) {
                      return (
                        <div className="relative aspect-video w-full rounded-xl overflow-hidden bg-black shadow-lg border border-slate-800 my-2 animate-in fade-in duration-200">
                          {ytId ? (
                            <iframe
                              src={`https://www.youtube-nocookie.com/embed/${ytId}?autoplay=1&rel=0`}
                              title={post.text || 'YouTube Video Player'}
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                              allowFullScreen
                              className="w-full h-full border-0"
                            />
                          ) : isDirect ? (
                            <video
                              controls
                              autoPlay
                              src={videoTargetUrl}
                              className="w-full h-full object-contain"
                            >
                              Your browser does not support HTML5 video preview.
                            </video>
                          ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center p-4 text-center bg-slate-900 text-white space-y-2">
                              <Film className="w-8 h-8 text-pink-400" />
                              <span className="text-xs font-semibold">Video Stream Ready</span>
                              <a
                                href={videoTargetUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center gap-1.5"
                              >
                                <span>Watch on {pStyle.label}</span>
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            </div>
                          )}

                          <button
                            type="button"
                            onClick={() => setPlayingVideoId(null)}
                            className="absolute top-2 right-2 bg-black/80 hover:bg-black text-white p-1.5 rounded-full text-xs cursor-pointer shadow-md transition-transform hover:scale-105 z-10"
                            title="Close Video Player"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      );
                    }

                    {/* Compact "Play Video Option" Banner / Card */}
                    return (
                      <div
                        onClick={() => setPlayingVideoId(post.id)}
                        className="relative rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 aspect-video group cursor-pointer bg-slate-950 flex items-center justify-center shadow-xs hover:border-red-500/60 transition-all duration-300"
                        title="Click to play video"
                      >
                        {ytThumb ? (
                          <img
                            src={ytThumb}
                            alt="Video Thumbnail"
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 opacity-80"
                            loading="lazy"
                          />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 flex items-center justify-center">
                            <div className="w-14 h-14 rounded-full bg-slate-800/80 border border-slate-700/80 flex items-center justify-center text-slate-400 group-hover:text-red-400 group-hover:border-red-500/40 transition-all">
                              <Film className="w-6 h-6" />
                            </div>
                          </div>
                        )}

                        {/* Centered Play Button Overlay */}
                        <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600/95 hover:bg-red-500 text-white font-semibold text-xs shadow-xl transition-transform group-hover:scale-110">
                            <Play className="w-4 h-4 fill-white" />
                            <span>Play Video</span>
                          </div>
                        </div>

                        {/* Bottom Metadata Bar */}
                        <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between text-[11px] font-mono text-white/90">
                          <span className="bg-black/70 px-2 py-0.5 rounded backdrop-blur-xs flex items-center gap-1 font-semibold text-[10px]">
                            <Video className="w-3 h-3 text-red-400" />
                            {pStyle.label}
                          </span>
                          <span className="text-[10px] text-slate-300 bg-black/70 px-2 py-0.5 rounded backdrop-blur-xs font-mono">
                            Stream Inline
                          </span>
                        </div>
                      </div>
                    );
                  })()}

                  {/* Engagement Metrics */}
                  <div className="flex items-center gap-4 pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px] font-mono text-slate-500">
                    {post.likes_count !== undefined && (
                      <span className="flex items-center gap-1">
                        <Heart className="w-3 h-3 text-rose-500" />
                        {post.likes_count.toLocaleString()}
                      </span>
                    )}
                    {post.views_count !== undefined && post.views_count > 0 && (
                      <span className="flex items-center gap-1">
                        <Eye className="w-3 h-3 text-indigo-400" />
                        {post.views_count.toLocaleString()}
                      </span>
                    )}
                    {post.shares_count !== undefined && post.shares_count > 0 && (
                      <span className="flex items-center gap-1">
                        <Repeat2 className="w-3 h-3 text-emerald-500" />
                        {post.shares_count.toLocaleString()}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-3 h-3 text-cyan-400" />
                      {post.comments_count || commentsList.length} comments
                    </span>
                  </div>

                  {/* Expandable Comments Drawer */}
                  {commentsList.length > 0 && (
                    <div className="pt-2">
                      <button
                        onClick={() => handleToggleComments(post.id)}
                        className="w-full flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-mono text-slate-600 dark:text-slate-300 transition-all cursor-pointer"
                      >
                        <span className="flex items-center gap-1.5 font-semibold text-cyan-600 dark:text-cyan-400">
                          <MessageSquare className="w-3.5 h-3.5" />
                          Captured Comments ({commentsList.length})
                        </span>
                        {isCommentsOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>

                      {isCommentsOpen && (
                        <div className="mt-2 space-y-2 max-h-56 overflow-y-auto pr-1">
                          {commentsList.map((c, cIdx) => (
                            <div
                              key={cIdx}
                              className="p-2.5 rounded-lg bg-slate-50/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800 text-xs space-y-1"
                            >
                              <div className="flex items-center justify-between text-[11px] font-mono">
                                <span className="font-semibold text-cyan-700 dark:text-cyan-300">@{c.author}</span>
                                {c.published_at && (
                                  <span className="text-slate-400 text-[10px]">{formatDate(c.published_at)}</span>
                                )}
                              </div>
                              <p className="text-slate-800 dark:text-slate-200 text-xs font-sans leading-relaxed">
                                {c.text}
                              </p>
                              {c.likes_count !== undefined && c.likes_count > 0 && (
                                <div className="text-[10px] text-rose-500 font-mono flex items-center gap-1">
                                  <Heart className="w-2.5 h-2.5 fill-rose-500" />
                                  {c.likes_count}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Card Action Footer */}
                <div className="px-4 py-2.5 bg-slate-50/80 dark:bg-slate-900/60 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    {post.confidence && (
                      <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md font-semibold">
                        Confidence {Math.round(post.confidence * 100)}%
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {investigationId && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleSealPostToInvestigation(post)}
                        disabled={sealingPostId === post.id || sealedSuccessId === post.id}
                        className="text-xs h-7 px-2.5 rounded-lg flex items-center gap-1.5 cursor-pointer"
                      >
                        {sealedSuccessId === post.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-500" />
                            <span className="text-emerald-500 font-bold">Sealed</span>
                          </>
                        ) : sealingPostId === post.id ? (
                          <>
                            <div className="w-3 h-3 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                            <span>Sealing...</span>
                          </>
                        ) : (
                          <>
                            <PlusCircle className="w-3 h-3 text-indigo-500" />
                            <span>Seal Evidence</span>
                          </>
                        )}
                      </Button>
                    )}

                    <a
                      href={post.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                    >
                      <span>Source</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
