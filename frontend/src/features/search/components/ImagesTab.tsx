import React, { useState } from 'react';
import { Image as ImageIcon, ExternalLink, Calendar, ShieldCheck, Search, Filter } from 'lucide-react';
import { MediaRecord } from '../../../types';

interface ImagesTabProps {
  images: MediaRecord[];
  query: string;
  onSelectImage: (media: MediaRecord) => void;
  sourcesEvaluated?: number;
}

export const ImagesTab: React.FC<ImagesTabProps> = ({
  images,
  query,
  onSelectImage,
  sourcesEvaluated = 0,
}) => {
  const [filterPlatform, setFilterPlatform] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const platforms = Array.from(new Set(images.map((img) => img.source_platform || img.source_provider))).filter(Boolean);

  const filteredImages = images.filter((img) => {
    const matchesPlatform =
      filterPlatform === 'ALL' ||
      (img.source_platform && img.source_platform === filterPlatform) ||
      img.source_provider === filterPlatform;

    const matchesSearch =
      !searchTerm.trim() ||
      (img.title && img.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (img.description && img.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (img.parent_title && img.parent_title.toLowerCase().includes(searchTerm.toLowerCase()));

    return matchesPlatform && matchesSearch;
  });

  if (images.length === 0) {
    return (
      <div className="p-12 text-center bg-white dark:bg-[#0f1422] rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs">
        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-100 dark:bg-slate-800/80 flex items-center justify-center text-slate-400">
          <ImageIcon className="w-8 h-8" />
        </div>
        <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-2">
          No Visual Images Extracted
        </h4>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-4">
          Visual intelligence evaluated available providers for target "{query}". No source-backed image records, EXIF metadata, or open-source post images were discovered in authorized sources.
        </p>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs font-mono text-slate-600 dark:text-slate-400">
          <span>Sources evaluated: {sourcesEvaluated || 'Active OSINT & Media Engines'}</span>
          <span>•</span>
          <span>Status: SUCCESSFUL_NO_MEDIA</span>
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
              placeholder="Filter images..."
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
                <option value="ALL">All Sources ({images.length})</option>
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
          Showing <span className="font-semibold text-slate-900 dark:text-white">{filteredImages.length}</span> of {images.length} verified image findings
        </div>
      </div>

      {/* Responsive Images Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredImages.map((img) => (
          <div
            key={img.id}
            onClick={() => onSelectImage(img)}
            className="group relative flex flex-col bg-white dark:bg-[#0f1422] rounded-2xl border border-slate-200/90 dark:border-slate-800 overflow-hidden shadow-xs hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500/50 transition-all cursor-pointer"
          >
            {/* Image Thumbnail Container */}
            <div className="relative aspect-4/3 w-full bg-slate-950 overflow-hidden">
              <img
                src={img.thumbnail_url || img.url}
                alt={img.title || 'Evidence Image'}
                loading="lazy"
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="300" height="225" viewBox="0 0 300 225"><rect fill="%230f172a" width="300" height="225"/><text fill="%2364748b" font-family="sans-serif" font-size="12" dy="4" font-weight="bold" x="50%" y="50%" text-anchor="middle">Image Preview Unavailable</text></svg>';
                }}
              />
              <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
                <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-black/70 backdrop-blur-xs text-white border border-white/20">
                  {img.source_platform || img.source_provider}
                </span>
              </div>
              <div className="absolute top-2.5 right-2.5">
                <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold border ${
                  img.verification_status === 'VERIFIED'
                    ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40'
                    : 'bg-amber-950/80 text-amber-400 border-amber-500/40'
                }`}>
                  {img.verification_status}
                </span>
              </div>
            </div>

            {/* Card Content */}
            <div className="p-3.5 flex flex-col flex-1 justify-between gap-2.5">
              <div>
                <h5 className="text-xs font-semibold text-slate-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {img.title || 'Source Image Finding'}
                </h5>
                {img.parent_title && (
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1 mt-1">
                    Context: <span className="text-slate-700 dark:text-slate-300 font-medium">{img.parent_title}</span>
                  </p>
                )}
              </div>

              {/* Card Footer */}
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  <span>
                    {img.publication_date
                      ? new Date(img.publication_date).toLocaleDateString()
                      : new Date(img.collection_date || Date.now()).toLocaleDateString()}
                  </span>
                </div>
                {img.canonical_source_url && (
                  <a
                    href={img.canonical_source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="p-1 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                    title="Open original source"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
