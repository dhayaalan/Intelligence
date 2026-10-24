import React, { useState, useEffect } from 'react';
import {
  Camera,
  Video,
  FileAudio,
  Upload,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  ShieldCheck,
  ShieldAlert,
  Search,
  Sparkles,
  MapPin,
  Clock,
  Cpu,
  Layers,
  FileText,
  RefreshCw,
  ExternalLink,
  SlidersHorizontal,
  GitCompare,
  ArrowRight
} from 'lucide-react';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { apiRequest } from '../../../core/api/client';
import { cn } from '../../../lib/utils';

interface MediaForensicsPanelProps {
  investigationId?: string;
  onAnalysisLinked?: () => void;
  onNavigateToSearch?: (query: string, targetType?: string) => void;
}

interface ImageAnalysisResult {
  sha256: string;
  md5: string;
  file_size_bytes: number;
  mime_type: string;
  dhash: string;
  phash: string;
  exif: {
    present: boolean;
    make?: string;
    model?: string;
    software?: string;
    datetime?: string;
    gps_lat?: number;
    gps_lon?: number;
    gps_precision?: string;
    raw_tags_count?: number;
  };
  c2pa: {
    status: string;
    signed_by?: string;
    generator?: string;
    ai_generated: boolean;
    ai_evidence?: string;
  };
  ocr: {
    text: string;
    words_count: number;
    confidence: number;
    detected_license_plate?: string;
    detected_urls?: string[];
    detected_emails?: string[];
  };
  quality: {
    width: number;
    height: number;
    megapixels: number;
    sharpness_score: number;
    is_blurry: boolean;
    quality_warning?: string;
  };
  analyzed_at: string;
}

interface VideoAnalysisResult {
  sha256: string;
  file_size_bytes: number;
  format: string;
  codec: string;
  duration_seconds: number;
  fps: number;
  resolution: string;
  frame_count: number;
  keyframes: Array<{
    time_seconds: number;
    frame_index: number;
    phash: string;
    dhash: string;
    preview_data_url?: string;
    ocr_text?: string;
  }>;
  scene_cuts: Array<{
    index: number;
    time_seconds: number;
    distance_from_previous: number;
  }>;
  ocr_findings: string[];
  transcript: Array<{
    start_seconds: number;
    end_seconds: number;
    text: string;
    confidence: number;
    lang?: string;
  }>;
  audio_present: boolean;
  analyzed_at: string;
}

interface AudioAnalysisResult {
  sha256: string;
  file_size_bytes: number;
  format: string;
  sample_rate: number;
  channels: number;
  duration_seconds: number;
  transcript: Array<{
    start_seconds: number;
    end_seconds: number;
    text: string;
    confidence: number;
    lang?: string;
  }>;
  detected_language?: string;
  analyzed_at: string;
}

export const MediaForensicsPanel: React.FC<MediaForensicsPanelProps> = ({
  investigationId,
  onAnalysisLinked,
  onNavigateToSearch
}) => {
  const [mediaType, setMediaType] = useState<'image' | 'video' | 'audio'>('image');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [linking, setLinking] = useState(false);
  const [linkedSuccess, setLinkedSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Analysis Results
  const [imageResult, setImageResult] = useState<ImageAnalysisResult | null>(null);
  const [videoResult, setVideoResult] = useState<VideoAnalysisResult | null>(null);
  const [audioResult, setAudioResult] = useState<AudioAnalysisResult | null>(null);

  // Attached Analyses history
  const [history, setHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Perceptual Comparison state
  const [compareHash1, setCompareHash1] = useState('');
  const [compareHash2, setCompareHash2] = useState('');
  const [compareResult, setCompareResult] = useState<any | null>(null);
  const [comparing, setComparing] = useState(false);

  const fetchHistory = async () => {
    if (!investigationId) return;
    setLoadingHistory(true);
    try {
      const res = await apiRequest<any[]>(
        `/media-intelligence/investigations/${investigationId}/media-analyses`
      );
      setHistory(res || []);
    } catch {
      // Non-blocking history load
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [investigationId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setImageResult(null);
      setVideoResult(null);
      setAudioResult(null);
      setLinkedSuccess(false);

      if (file.type.startsWith('image/')) {
        setMediaType('image');
        setPreviewUrl(URL.createObjectURL(file));
      } else if (file.type.startsWith('video/')) {
        setMediaType('video');
        setPreviewUrl(URL.createObjectURL(file));
      } else if (file.type.startsWith('audio/')) {
        setMediaType('audio');
        setPreviewUrl(null);
      }
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(label);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const runAnalysis = async () => {
    if (!selectedFile) {
      setError('Please select a media file to inspect.');
      return;
    }

    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('filename', selectedFile.name);

    try {
      if (mediaType === 'image') {
        const res = await apiRequest<ImageAnalysisResult>('/media-intelligence/analyze/image', {
          method: 'POST',
          body: formData,
        });
        setImageResult(res);
      } else if (mediaType === 'video') {
        const res = await apiRequest<VideoAnalysisResult>('/media-intelligence/analyze/video', {
          method: 'POST',
          body: formData,
        });
        setVideoResult(res);
      } else if (mediaType === 'audio') {
        const res = await apiRequest<AudioAnalysisResult>('/media-intelligence/analyze/audio', {
          method: 'POST',
          body: formData,
        });
        setAudioResult(res);
      }
    } catch (err: any) {
      setError(err?.message || 'Forensic analysis encountered an unhandled error.');
    } finally {
      setAnalyzing(false);
    }
  };

  const linkToInvestigation = async () => {
    if (!investigationId || (!imageResult && !videoResult && !audioResult)) return;

    setLinking(true);
    try {
      await apiRequest(`/media-intelligence/investigations/${investigationId}/media-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          investigation_id: investigationId,
          media_type: mediaType,
          filename: selectedFile?.name || 'media_asset',
          media_url: previewUrl || undefined,
          image_result: imageResult,
          video_result: videoResult,
          audio_result: audioResult,
        }),
      });
      setLinkedSuccess(true);
      fetchHistory();
      if (onAnalysisLinked) {
        onAnalysisLinked();
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to seal analysis to investigation evidence.');
    } finally {
      setLinking(false);
    }
  };

  const runHashComparison = async () => {
    if (!compareHash1 || !compareHash2) return;
    setComparing(true);
    try {
      const res = await apiRequest('/media-intelligence/compare-hash', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hash1: compareHash1.trim(),
          hash2: compareHash2.trim(),
          algorithm: 'phash',
        }),
      });
      setCompareResult(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to compute perceptual hash distance');
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Forensics Mission Header */}
      <div className="rounded-xl p-4 bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-bold text-white font-mono tracking-wide">
              FORENSIC MEDIA INTELLIGENCE & CHAIN OF CUSTODY
            </h3>
            <Badge variant="success" className="text-[10px] font-mono">
              TAMPER-EVIDENT
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Execute safe decoding, EXIF/GPS extraction, dual dHash/pHash perceptual hashing, C2PA Content Credentials provenance, and OCR text extraction.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs font-mono text-slate-300 border-slate-700">
            {history.length} ATTACHED ASSETS
          </Badge>
        </div>
      </div>

      {/* Main Grid: Upload & Inspection Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Upload & Controls */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="border-slate-800 bg-[#0f1422]">
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-xs font-mono font-bold text-slate-200 flex items-center justify-between">
                <span>1. SUBMIT MEDIA EVIDENCE</span>
                <span className="text-[10px] text-slate-500 font-mono">MAX 50 MB</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              {/* Type Switcher */}
              <div className="grid grid-cols-3 gap-2 p-1 bg-slate-950 rounded-lg border border-slate-800">
                <button
                  type="button"
                  onClick={() => setMediaType('image')}
                  className={cn(
                    'py-1.5 text-xs font-mono font-bold rounded-md flex items-center justify-center gap-1.5 transition-all cursor-pointer',
                    mediaType === 'image'
                      ? 'bg-emerald-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-white'
                  )}
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>IMAGE</span>
                </button>
                <button
                  type="button"
                  onClick={() => setMediaType('video')}
                  className={cn(
                    'py-1.5 text-xs font-mono font-bold rounded-md flex items-center justify-center gap-1.5 transition-all cursor-pointer',
                    mediaType === 'video'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-white'
                  )}
                >
                  <Video className="w-3.5 h-3.5" />
                  <span>VIDEO</span>
                </button>
                <button
                  type="button"
                  onClick={() => setMediaType('audio')}
                  className={cn(
                    'py-1.5 text-xs font-mono font-bold rounded-md flex items-center justify-center gap-1.5 transition-all cursor-pointer',
                    mediaType === 'audio'
                      ? 'bg-purple-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-white'
                  )}
                >
                  <FileAudio className="w-3.5 h-3.5" />
                  <span>AUDIO</span>
                </button>
              </div>

              {/* Upload Dropzone */}
              <label className="border-2 border-dashed border-slate-800 hover:border-slate-700 bg-slate-950/50 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-colors block text-center">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept={
                    mediaType === 'image'
                      ? 'image/jpeg,image/png,image/webp,image/gif'
                      : mediaType === 'video'
                      ? 'video/mp4,video/quicktime,video/x-msvideo,video/x-matroska'
                      : 'audio/wav,audio/mpeg,audio/mp3'
                  }
                  className="hidden"
                />
                <Upload className="w-8 h-8 text-slate-500 mb-2" />
                <span className="text-xs font-mono font-bold text-slate-200">
                  {selectedFile ? selectedFile.name : `Select ${mediaType.toUpperCase()} file`}
                </span>
                <span className="text-[11px] text-slate-500 mt-1">
                  {selectedFile
                    ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB · Click to replace`
                    : 'Click or drop file to start automated forensic analysis'}
                </span>
              </label>

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  onClick={runAnalysis}
                  disabled={!selectedFile || analyzing}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold"
                >
                  {analyzing ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin mr-2" />
                      ANALYZING RAW BYTES...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5 mr-2" />
                      RUN FORENSIC EXTRACTION
                    </>
                  )}
                </Button>
              </div>

              {error && (
                <div className="p-3 bg-red-950/40 border border-red-800/80 rounded-lg text-xs text-red-300 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Perceptual Duplicate Comparator */}
          <Card className="border-slate-800 bg-[#0f1422]">
            <CardHeader className="pb-3 border-b border-slate-800">
              <CardTitle className="text-xs font-mono font-bold text-slate-200 flex items-center gap-2">
                <SlidersHorizontal className="w-3.5 h-3.5 text-cyan-400" />
                <span>PERCEPTUAL HASH DUPLICATE COMPARATOR</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3">
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Hash A (dHash / pHash hex or binary)"
                  value={compareHash1}
                  onChange={(e) => setCompareHash1(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-1.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-hidden focus:border-cyan-500"
                />
                <input
                  type="text"
                  placeholder="Hash B (dHash / pHash hex or binary)"
                  value={compareHash2}
                  onChange={(e) => setCompareHash2(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-1.5 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-hidden focus:border-cyan-500"
                />
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={runHashComparison}
                disabled={!compareHash1 || !compareHash2 || comparing}
                className="w-full text-xs font-mono border-slate-700 text-cyan-300 hover:bg-slate-800"
              >
                {comparing ? 'COMPUTING DISTANCE...' : 'COMPUTE HAMMING DISTANCE'}
              </Button>
              {compareResult && (
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5 font-mono text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Hamming Distance:</span>
                    <span className="font-bold text-white">{compareResult.hamming_distance} / 64 bits</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Similarity:</span>
                    <span className="font-bold text-emerald-400">{compareResult.similarity_percentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Classification:</span>
                    <Badge
                      variant={compareResult.match_type === 'EXACT_MATCH' ? 'success' : compareResult.match_type === 'NEAR_DUPLICATE' ? 'warning' : 'outline'}
                      className="text-[10px]"
                    >
                      {compareResult.match_type}
                    </Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Deep Forensic Results Display */}
        <div className="lg:col-span-7 space-y-4">
          {imageResult && (
            <Card className="border-emerald-950/80 bg-[#0f1422] shadow-md">
              <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-2">
                    <Camera className="w-4 h-4" />
                    <span>IMAGE FORENSIC DOSSIER</span>
                  </CardTitle>
                  <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                    Analyzed at {new Date(imageResult.analyzed_at).toLocaleTimeString()} · Verified Cryptographic Hashes
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={linkToInvestigation}
                  disabled={linking || linkedSuccess}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold"
                >
                  {linkedSuccess ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-200" />
                      SEALED TO VAULT
                    </>
                  ) : linking ? (
                    'SEALING...'
                  ) : (
                    <>
                      <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                      SEAL TO INVESTIGATION VAULT
                    </>
                  )}
                </Button>
              </CardHeader>
              <CardContent className="p-4 space-y-4">
                {/* Cryptographic Hash Bar */}
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-slate-400 font-bold">SHA-256 CHECKSUM</span>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(imageResult.sha256, 'sha256')}
                      className="text-xs font-mono text-cyan-400 flex items-center gap-1 hover:underline cursor-pointer"
                    >
                      {copiedHash === 'sha256' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedHash === 'sha256' ? 'COPIED' : 'COPY'}</span>
                    </button>
                  </div>
                  <div className="font-mono text-xs text-emerald-300 break-all select-all bg-slate-900/80 p-2 rounded-sm border border-slate-800/60">
                    {imageResult.sha256}
                  </div>
                  <div className="grid grid-cols-2 gap-2 pt-1 text-[11px] font-mono text-slate-400">
                    <div>MD5: <span className="text-slate-200">{imageResult.md5}</span></div>
                    <div>SIZE: <span className="text-slate-200">{(imageResult.file_size_bytes / 1024).toFixed(1)} KB</span></div>
                  </div>
                </div>

                {/* Perceptual Hashes (dHash and pHash) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 font-bold">dHash (Difference)</span>
                      <button
                        type="button"
                        onClick={() => {
                          setCompareHash1(imageResult.dhash);
                          copyToClipboard(imageResult.dhash, 'dhash');
                        }}
                        className="text-[10px] text-cyan-400 hover:underline cursor-pointer"
                      >
                        {copiedHash === 'dhash' ? 'Copied' : 'Copy'}
                      </button>
                    </div>
                    <div className="text-[11px] text-slate-300 break-all bg-slate-900 p-1.5 rounded-sm">
                      {imageResult.dhash}
                    </div>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 font-bold">pHash (2D DCT)</span>
                      <button
                        type="button"
                        onClick={() => {
                          setCompareHash1(imageResult.phash);
                          copyToClipboard(imageResult.phash, 'phash');
                        }}
                        className="text-[10px] text-cyan-400 hover:underline cursor-pointer"
                      >
                        {copiedHash === 'phash' ? 'Copied' : 'Copy'}
                      </button>
                    </div>
                    <div className="text-[11px] text-slate-300 break-all bg-slate-900 p-1.5 rounded-sm">
                      {imageResult.phash}
                    </div>
                  </div>
                </div>

                {/* EXIF Camera & GPS Box */}
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
                    <span className="font-bold text-slate-300 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-indigo-400" />
                      EXIF CAMERA METADATA
                    </span>
                    <Badge variant={imageResult.exif.present ? 'success' : 'outline'} className="text-[10px]">
                      {imageResult.exif.present ? 'METADATA FOUND' : 'EXIF STRIPPED'}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div>CAMERA: <span className="text-slate-200">{imageResult.exif.make || '—'} {imageResult.exif.model || ''}</span></div>
                    <div>SOFTWARE: <span className="text-slate-200">{imageResult.exif.software || 'Original firmware'}</span></div>
                    <div>TIMESTAMP: <span className="text-slate-200">{imageResult.exif.datetime || 'Undated (stripped)'}</span></div>
                    <div>
                      GPS: {imageResult.exif.gps_lat && imageResult.exif.gps_lon ? (
                        <span className="text-emerald-400 font-bold">
                          {imageResult.exif.gps_lat}, {imageResult.exif.gps_lon}
                        </span>
                      ) : (
                        <span className="text-slate-500">None reported</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* C2PA Provenance Banner */}
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-300 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                      C2PA CONTENT CREDENTIALS
                    </span>
                    <Badge
                      variant={imageResult.c2pa.status === 'valid' ? 'success' : imageResult.c2pa.status === 'invalid' ? 'danger' : 'outline'}
                      className="text-[10px]"
                    >
                      {imageResult.c2pa.status.toUpperCase()}
                    </Badge>
                  </div>
                  {imageResult.c2pa.ai_generated ? (
                    <p className="text-[11px] text-amber-300 font-bold bg-amber-950/40 p-2 rounded-sm border border-amber-800/60 mt-1">
                      ⚠️ Signed manifest declares synthetic or generative media provenance.
                    </p>
                  ) : (
                    <p className="text-[11px] text-slate-400 mt-1">
                      No generative tags detected in signature block.
                    </p>
                  )}
                </div>

                {/* OCR Text Box */}
                {imageResult.ocr.text && (
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2 font-mono text-xs">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
                      <span className="font-bold text-slate-300 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-emerald-400" />
                        EXTRACTED OCR TEXT ({imageResult.ocr.words_count} WORDS)
                      </span>
                      {imageResult.ocr.detected_license_plate && (
                        <Badge variant="accent" className="text-[10px]">
                          PLATE: {imageResult.ocr.detected_license_plate}
                        </Badge>
                      )}
                    </div>
                    <div className="p-2 bg-slate-900 rounded-sm text-slate-200 text-xs font-mono max-h-32 overflow-y-auto whitespace-pre-wrap">
                      {imageResult.ocr.text}
                    </div>
                    {imageResult.ocr.detected_license_plate && onNavigateToSearch && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onNavigateToSearch(imageResult.ocr.detected_license_plate!, 'VEHICLE')}
                        className="text-xs font-mono text-emerald-300 border-emerald-800 hover:bg-emerald-950/50"
                      >
                        <Search className="w-3 h-3 mr-1" />
                        PIVOT TO VEHICLE INTELLIGENCE ({imageResult.ocr.detected_license_plate})
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {videoResult && (
            <Card className="border-indigo-950/80 bg-[#0f1422] shadow-md">
              <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-xs font-mono font-bold text-indigo-400 flex items-center gap-2">
                    <Video className="w-4 h-4" />
                    <span>VIDEO FORENSIC DOSSIER & KEYFRAMES</span>
                  </CardTitle>
                  <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                    {videoResult.duration_seconds}s · {videoResult.resolution} · {videoResult.fps} FPS · Codec {videoResult.codec}
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={linkToInvestigation}
                  disabled={linking || linkedSuccess}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold"
                >
                  {linkedSuccess ? 'SEALED TO VAULT' : 'SEAL TO INVESTIGATION'}
                </Button>
              </CardHeader>
              <CardContent className="p-4 space-y-4">
                {/* Keyframes Visual Gallery */}
                <div className="space-y-2">
                  <span className="text-xs font-mono font-bold text-slate-300">
                    SAMPLED KEYFRAMES ({videoResult.keyframes.length})
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {videoResult.keyframes.map((kf, i) => (
                      <div key={i} className="p-2 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                        {kf.preview_data_url && (
                          <img
                            src={kf.preview_data_url}
                            alt={`Frame ${kf.time_seconds}s`}
                            className="w-full h-20 object-cover rounded-sm border border-slate-800"
                          />
                        )}
                        <div className="flex justify-between items-center text-[10px] font-mono text-slate-400">
                          <span>{kf.time_seconds}s</span>
                          <span className="text-slate-500 truncate max-w-[80px]">{kf.phash.slice(0, 8)}...</span>
                        </div>
                        {kf.ocr_text && (
                          <p className="text-[10px] font-mono text-emerald-400 truncate">
                            {kf.ocr_text}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Scene Cuts */}
                {videoResult.scene_cuts.length > 0 && (
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1 font-mono text-xs">
                    <span className="font-bold text-slate-300">
                      DETECTED SCENE CUTS ({videoResult.scene_cuts.length})
                    </span>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {videoResult.scene_cuts.map((sc, i) => (
                        <Badge key={i} variant="outline" className="text-[10px] text-slate-300">
                          {sc.time_seconds}s (Δ {sc.distance_from_previous})
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!imageResult && !videoResult && !audioResult && (
            <Card className="border-slate-800 bg-[#0f1422] p-12 text-center">
              <Camera className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h4 className="text-sm font-mono font-bold text-slate-300">NO MEDIA ANALYSIS ACTIVE</h4>
              <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                Upload an authorized media evidence file (Image, Video, or Audio) to generate cryptographic hashes, perceptual duplicates, EXIF telemetry, and OCR text findings.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
