import React from 'react';
import { ShieldCheck, ArrowRight, Layers, FileSearch } from 'lucide-react';
import { MediaForensicsPanel } from '../investigations/components/MediaForensicsPanel';
import { PageHeader } from '../../components/common/PageHeader';

interface MediaForensicsPageProps {
  onNavigateToSearch?: (query: string, targetType?: string) => void;
  onNavigateToInvestigation?: (id: string) => void;
}

export const MediaForensicsPage: React.FC<MediaForensicsPageProps> = ({
  onNavigateToSearch,
  onNavigateToInvestigation,
}) => {
  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#070b13] p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <PageHeader
        title="Media & Digital Forensics"
        description="Tamper-evident forensic analysis across images, video, and audio assets. Includes cryptographic SHA-256 verification, dual perceptual hashing (dHash/pHash), C2PA Content Credentials, EXIF/GPS extraction, and OCR text mining."
      />

      {/* Capabilities Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-2xs">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 flex items-center justify-center font-bold">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Authenticity & Provenance</h3>
              <p className="text-[11px] text-slate-500 font-mono">C2PA / JUMBF Manifests</p>
            </div>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Extracts Content Credentials metadata to identify provenance, editing tools, and generative indicators with zero false positives.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-2xs">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-500 flex items-center justify-center font-bold">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Dual Perceptual Hashing</h3>
              <p className="text-[11px] text-slate-500 font-mono">dHash + 2D DCT pHash</p>
            </div>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Computes 64-bit difference and discrete cosine transform hashes. Calculates Hamming distance for near-duplicate and compression detection.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-2xs">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-500 flex items-center justify-center font-bold">
              <FileSearch className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">OCR & Metadata</h3>
              <p className="text-[11px] text-slate-500 font-mono">EXIF, GPS & Plate Mining</p>
            </div>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            Extracts camera parameters, sanitized GPS coordinates (rejecting 0,0 sentinels), and OCR text with automatic license plate recognition.
          </p>
        </div>
      </div>

      {/* Main Interactive Forensics Intake & Comparator */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-xs">
        <MediaForensicsPanel
          onNavigateToSearch={onNavigateToSearch}
          onAnalysisLinked={() => {
            if (onNavigateToInvestigation) {
              onNavigateToInvestigation('latest');
            }
          }}
        />
      </div>
    </div>
  );
};
