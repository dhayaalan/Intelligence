import React, { useState } from 'react';
import { Film, Play, ExternalLink, Calendar, ShieldCheck, Search, Filter, FileText } from 'lucide-react';
import { MediaRecord } from '../../../types';

interface VideosTabProps {
  videos: MediaRecord[];
  query: string;
  onSelectVideo: (media: MediaRecord) => void;
  sourcesEvaluated?: number;
}

export const VideosTab: React.FC<VideosTabProps> = ({
  videos,
  query,
  onSelectVideo,
  sourcesEvaluated = 0,
}) => {
  const [filterPlatform, setFilterPlatform] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const platforms = Array.from(new Set(videos.map((v) => v.source_platform || v.source_provider))).filter(Boolean);

  const filteredVideos = videos.filter((vid) => {
    const matchesPlatform =
      filterPlatform === 'ALL' ||
      (vid.source_platform && vid.source_platform === filterPlatform) ||
      vid.source_provider === filterPlatform;

    const matchesSearch =
      !searchTerm.trim() ||
      (vid.title && vid.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (vid.description && vid.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (vid.parent_title && vid.parent_title.toLowerCase().includes(searchTerm.toLowerCase()));

    return matchesPlatform && matchesSearch;
  });

  if (videos.length === 0) {
    return (
      <div className="p-12 text-center bg-white dark:bg-[#0f1422] rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-100 dark:bg-slate-800/80 flex items-center justify-center text-slate-400">
          <Film className="w-8 h-8" />
        </div>
        <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-2">
          No Video Evidence Records
        </h4>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-4">
          Video intelligence queried open video platforms (including YouTube and verified social feeds) for target "{query}". No matching video broadcasts or channel uploads were found.
        </p>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs font-mono text-slate-600 dark:text-slate-400">
          <span>Sources evaluated: {sourcesEvaluated || 'YouTube & Social Media Engines'}</span>
          <span>•</span>
          <span>Status: SUCCESSFUL_NO_VIDEO</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 shadow-xs">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter videos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {platforms.length > 1 && (
            <div className="flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={filterPlatform}
                onChange={(e) => setFilterPlatform(e.target.value)}
                className="text-xs py-1.5 px-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 focus:outline-hidden"
              >
                <option value="ALL">All Sources ({videos.length})</option>
                {platforms.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
        <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          Showing <span className="font-semibold text-slate-900 dark:text-white">{filteredVideos.length}</span> of {videos.length} verified video findings
        </div>
      </div>

      {/* Videos Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredVideos.map((vid) => {
          const hasTranscript = Boolean(vid.metadata?.transcript_available || vid.metadata?.has_transcript);
          const channelName = vid.metadata?.channel || vid.metadata?.author || vid.source_platform;

          return (
            <div
              key={vid.id}
              onClick={() => onSelectVideo(vid)}
              className="group relative flex flex-col bg-white dark:bg-[#0f1422] rounded-2xl border border-slate-200/90 dark:border-slate-800 overflow-hidden shadow-xs hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500/50 transition-all cursor-pointer"
            >
              {/* Video Thumbnail Container with Play Overlay */}
              <div className="relative aspect-video w-full bg-slate-950 overflow-hidden">
                <img
                  src={vid.thumbnail_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=60'}
                  alt={vid.title || 'Video Evidence'}
                  loading="lazy"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 opacity-90"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="225" viewBox="0 0 400 225"><rect fill="%230f172a" width="400" height="225"/><text fill="%2364748b" font-family="sans-serif" font-size="14" dy="5" font-weight="bold" x="50%" y="50%" text-anchor="middle">Video Thumbnail Unavailable</text></svg>';
                  }}
                />
                
                {/* Play Button Overlay */}
                <div className="absolute inset-0 flex items-center justify-center bg-black/30 group-hover:bg-black/10 transition-colors">
                  <div className="w-12 h-12 rounded-full bg-red-600 group-hover:bg-red-500 text-white flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform">
                    <Play className="w-5 h-5 fill-white ml-0.5" />
                  </div>
                </div>

                {/* Source Badge */}
                <div className="absolute top-3 left-3 flex items-center gap-1.5">
                  <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-black/75 backdrop-blur-xs text-white border border-white/20">
                    {vid.source_platform || vid.source_provider}
                  </span>
                </div>

                {/* Transcript Badge */}
                <div className="absolute bottom-3 right-3 flex items-center gap-1.5">
                  <span className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold backdrop-blur-xs ${
                    hasTranscript
                      ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/30'
                      : 'bg-slate-900/80 text-slate-300 border border-slate-700/50'
                  }`}>
                    <FileText className="w-3 h-3" />
                    <span>{hasTranscript ? 'Transcript Available' : 'No Transcript'}</span>
                  </span>
                </div>
              </div>

              {/* Video Info Body */}
              <div className="p-4 flex flex-col flex-1 justify-between gap-3">
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {vid.title || 'Video Finding'}
                  </h4>
                  {channelName && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium">
                      Channel: <span className="text-slate-700 dark:text-slate-200 font-semibold">{channelName}</span>
                    </p>
                  )}
                  {vid.parent_title && (
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1 mt-0.5">
                      Target Association: <span className="text-slate-700 dark:text-slate-300">{vid.parent_title}</span>
                    </p>
                  )}
                </div>

                {/* Card Footer */}
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>
                      {vid.publication_date
                        ? new Date(vid.publication_date).toLocaleDateString()
                        : new Date(vid.collection_date || Date.now()).toLocaleDateString()}
                    </span>
                  </div>
                  {vid.canonical_source_url && (
                    <a
                      href={vid.canonical_source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                    >
                      <span>Watch</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
