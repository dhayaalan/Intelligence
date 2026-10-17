import React, { useEffect } from 'react';
import { X, ExternalLink, Calendar, ShieldCheck, Tag, Info, Film, Image as ImageIcon } from 'lucide-react';
import { MediaRecord } from '../../../types';

interface MediaViewerModalProps {
  media: MediaRecord | null;
  onClose: () => void;
}

export const MediaViewerModal: React.FC<MediaViewerModalProps> = ({ media, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!media) return null;

  const isVideo = media.media_type === 'video';
  const youtubeMatch = media.url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([a-zA-Z0-9_-]{11})/);
  const youtubeId = youtubeMatch ? youtubeMatch[1] : (media.metadata?.video_id || null);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Media Preview"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div
        className="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-[#0f1422] border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              {isVideo ? <Film className="w-5 h-5" /> : <ImageIcon className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900 dark:text-white line-clamp-1">
                {media.title || (isVideo ? 'Video Media Evidence' : 'Visual Image Evidence')}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Source: <span className="font-medium text-slate-700 dark:text-slate-300">{media.source_provider}</span>
                {media.source_platform && ` (${media.source_platform})`}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close dialog"
            className="p-2 text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white rounded-xl hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Media Player / Image Display */}
          <div className="w-full flex items-center justify-center bg-slate-950 rounded-xl overflow-hidden min-h-[300px] max-h-[480px]">
            {isVideo ? (
              youtubeId ? (
                <iframe
                  src={`https://www.youtube.com/embed/${youtubeId}?autoplay=1`}
                  title={media.title || 'Video Player'}
                  className="w-full aspect-video border-0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : (
                <video
                  src={media.url}
                  controls
                  className="w-full max-h-[460px] object-contain"
                  poster={media.thumbnail_url}
                >
                  Your browser does not support the video tag.
                </video>
              )
            ) : (
              <img
                src={media.url}
                alt={media.title || 'Investigative Evidence'}
                className="w-full max-h-[460px] object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect fill="%231e293b" width="400" height="300"/><text fill="%2394a3b8" font-family="sans-serif" font-size="14" dy="10.5" font-weight="bold" x="50%" y="50%" text-anchor="middle">Image Unavailable / External Link Restricted</text></svg>';
                }}
              />
            )}
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                <span>Verification & Integrity</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 text-xs font-semibold rounded-md ${
                  media.verification_status === 'VERIFIED'
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-400'
                    : 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-400'
                }`}>
                  {media.verification_status}
                </span>
                <span className="text-xs text-slate-500">
                  {media.evidence_ids.length > 0 ? `${media.evidence_ids.length} Corroborating Evidence Records` : 'Direct Finding'}
                </span>
              </div>
              {media.description && (
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2">
                  {media.description}
                </p>
              )}
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <Calendar className="w-4 h-4 text-blue-500" />
                <span>Provenance & Dates</span>
              </div>
              <div className="text-xs text-slate-600 dark:text-slate-300 space-y-1">
                {media.publication_date && (
                  <div>
                    <span className="text-slate-400 font-medium">Published: </span>
                    {new Date(media.publication_date).toLocaleString()}
                  </div>
                )}
                {media.collection_date && (
                  <div>
                    <span className="text-slate-400 font-medium">Collected: </span>
                    {new Date(media.collection_date).toLocaleString()}
                  </div>
                )}
                {media.parent_title && (
                  <div>
                    <span className="text-slate-400 font-medium">Associated Target: </span>
                    <span className="font-semibold text-slate-900 dark:text-white">{media.parent_title}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Raw Metadata Details */}
          {media.metadata && Object.keys(media.metadata).length > 0 && (
            <details className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40 p-3 text-xs">
              <summary className="font-semibold text-slate-700 dark:text-slate-300 cursor-pointer flex items-center gap-2">
                <Info className="w-4 h-4 text-slate-400" />
                Technical Metadata & Cryptographic Hashes
              </summary>
              <pre className="mt-3 p-3 bg-white dark:bg-slate-950 rounded-lg overflow-x-auto text-[11px] font-mono text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800">
                {JSON.stringify(media.metadata, null, 2)}
              </pre>
            </details>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60">
          <span className="text-xs font-mono text-slate-400">ID: {media.id}</span>
          <div className="flex items-center gap-3">
            {media.canonical_source_url && (
              <a
                href={media.canonical_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-xs transition-colors"
              >
                <span>Open Original Source</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-300 bg-slate-200/80 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
