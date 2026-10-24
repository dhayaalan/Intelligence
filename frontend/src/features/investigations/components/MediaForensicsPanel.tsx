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
  ArrowRight,
  RotateCcw,
  Compass,
  Link as LinkIcon,
  Crosshair,
  Eye,
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

  // Intake mode and URL acquisition
  const [intakeMode, setIntakeMode] = useState<'upload' | 'url'>('upload');
  const [remoteUrl, setRemoteUrl] = useState('');
  const [analyzingUrl, setAnalyzingUrl] = useState(false);
  const [activeCaseTitle, setActiveCaseTitle] = useState<string | null>(null);

  const resetInspector = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setImageResult(null);
    setVideoResult(null);
    setAudioResult(null);
    setError(null);
    setActiveCaseTitle(null);
    setLinkedSuccess(false);
  };

  const loadShowcaseCase = (caseId: 'traffic' | 'deepfake' | 'drone' | 'audio') => {
    setError(null);
    setLinkedSuccess(false);
    setSelectedFile(null);
    setPreviewUrl(null);

    if (caseId === 'traffic') {
      setMediaType('image');
      setVideoResult(null);
      setAudioResult(null);
      setActiveCaseTitle('Surveillance Camera: TN34MA8256 (Salem Northern Junction)');
      setImageResult({
        sha256: 'c7e2b10499b780447385418b76c8bb8d08569527ecbcf0879133857e4e899b19',
        md5: 'e3d790472e3d74c868c2f2d90efcb944',
        file_size_bytes: 482104,
        mime_type: 'image/jpeg',
        dhash: '1101010010101000111001101011001011000001111110010011000000010001',
        phash: '1000110001001111100110100011111000101011000111010111111001011100',
        exif: {
          present: true,
          make: 'Hikvision',
          model: 'DS-2CD2T87G2-L Security Camera',
          software: 'V5.7.1 build 220110',
          datetime: '2026-10-24 14:32:08 UTC',
          gps_lat: 11.66432,
          gps_lon: 78.14601,
          gps_precision: 'HIGH_CONFIDENCE_EXIF',
          raw_tags_count: 38,
        },
        c2pa: {
          status: 'valid',
          signed_by: 'Hikvision Hardware Root of Trust',
          generator: 'Embedded DSP v4.2',
          ai_generated: false,
        },
        ocr: {
          text: 'TN34MA8256 SPEED_LIMIT_40 SALEM_INTERSECTION_NORTH',
          words_count: 5,
          confidence: 97.4,
          detected_license_plate: 'TN34MA8256',
          detected_urls: [],
          detected_emails: [],
        },
        quality: {
          width: 3840,
          height: 2160,
          megapixels: 8.3,
          sharpness_score: 91.2,
          is_blurry: false,
        },
        analyzed_at: new Date().toISOString(),
      });
    } else if (caseId === 'deepfake') {
      setMediaType('image');
      setVideoResult(null);
      setAudioResult(null);
      setActiveCaseTitle('C2PA Synthetic Deepfake: Embassy Evacuation Hoax');
      setImageResult({
        sha256: 'a93b4d812e9177a419c8f0e5138fbdc8012674e1d7bbef88e7b7f165a210d481',
        md5: '71a8e12df8820c7d413b56788e01bf28',
        file_size_bytes: 1248920,
        mime_type: 'image/png',
        dhash: '0011010010101001110001101011001011000001111110010011000000010001',
        phash: '1100110001001111100110100011111000101011000111010111111001011100',
        exif: {
          present: false,
          raw_tags_count: 0,
        },
        c2pa: {
          status: 'invalid',
          signed_by: 'UNVERIFIED_SELF_SIGNED',
          generator: 'Midjourney v6.0 / Stability AI SDXL',
          ai_generated: true,
          ai_evidence: 'Synthetic diffusion noise signature detected in frequency spectrum; EXIF camera metadata deliberately stripped; non-natural skin texture variance.',
        },
        ocr: {
          text: 'BREAKING NEWS: EMBASSY ZONE EVACUATED\nOfficial emergency protocol declared.',
          words_count: 8,
          confidence: 94.0,
          detected_urls: ['t.me/intelwire_mirror'],
          detected_emails: [],
        },
        quality: {
          width: 2048,
          height: 2048,
          megapixels: 4.2,
          sharpness_score: 87.5,
          is_blurry: false,
          quality_warning: 'Synthetic texture smoothing detected in facial boundary regions.',
        },
        analyzed_at: new Date().toISOString(),
      });
    } else if (caseId === 'drone') {
      setMediaType('video');
      setImageResult(null);
      setAudioResult(null);
      setActiveCaseTitle('Aerial Reconnaissance Drone: Sector 4 Flight Pass');
      setVideoResult({
        sha256: 'f81b29a7d3c019485b01837ecbcf0879133857e4e899b19e2b10499b78044738',
        file_size_bytes: 8421000,
        format: 'mp4',
        codec: 'h264 / aac',
        duration_seconds: 24.5,
        fps: 30.0,
        resolution: '1920x1080',
        frame_count: 735,
        keyframes: [
          {
            time_seconds: 1.2,
            frame_index: 36,
            phash: '8c4f9a3e2b1d7e5c',
            dhash: 'd4a8e6b2c1f93011',
            ocr_text: 'ALT: 850m | SPEED: 120km/h',
          },
          {
            time_seconds: 6.8,
            frame_index: 204,
            phash: '7b3e8a2d1c0f6d4b',
            dhash: 'c3b7f5a1b0e82900',
            ocr_text: 'GRID: 34.0522° N, 118.2437° W',
          },
          {
            time_seconds: 14.1,
            frame_index: 423,
            phash: '9d5e0b4f3c2e8f6d',
            dhash: 'e5c9f7b3d1f04122',
            ocr_text: 'TARGET_CLASS: HEAVY_VEHICLE_CONVOY',
          },
          {
            time_seconds: 21.0,
            frame_index: 630,
            phash: '6a2c7f1d0b9e5c3a',
            dhash: 'b2a6e4d0a9d71899',
            ocr_text: 'STATION_LOCK: ACTIVE',
          },
        ],
        scene_cuts: [
          { index: 1, time_seconds: 6.8, distance_from_previous: 42.1 },
          { index: 2, time_seconds: 14.1, distance_from_previous: 58.7 },
        ],
        ocr_findings: [
          'ALT: 850m',
          'GRID: 34.0522° N, 118.2437° W',
          'TARGET_CLASS: HEAVY_VEHICLE_CONVOY',
          'STATION_LOCK: ACTIVE',
        ],
        transcript: [
          { start_seconds: 1.0, end_seconds: 5.2, text: 'Sensors online, entering designated surveillance sector.', confidence: 0.94 },
          { start_seconds: 7.0, end_seconds: 13.5, text: 'Target vehicle cluster in sight, initiating high-resolution optical tracking.', confidence: 0.91 },
          { start_seconds: 15.0, end_seconds: 22.0, text: 'Perceptual hash keyframe recorded, cryptographic hash verified.', confidence: 0.96 },
        ],
        audio_present: true,
        analyzed_at: new Date().toISOString(),
      });
    } else if (caseId === 'audio') {
      setMediaType('audio');
      setImageResult(null);
      setVideoResult(null);
      setActiveCaseTitle('Tactical Radio Audio Intercept: Channel 7 Wire');
      setAudioResult({
        sha256: '38bc74a9f12019485b01837ecbcf0879133857e4e899b19e2b10499b78044738',
        file_size_bytes: 1450200,
        format: 'wav (PCM 16-bit)',
        sample_rate: 16000,
        channels: 1,
        duration_seconds: 18.2,
        transcript: [
          { start_seconds: 0.5, end_seconds: 5.8, text: 'Checkpoint alpha to base, vehicle TN34MA8256 cleared through barrier.', confidence: 0.93 },
          { start_seconds: 7.2, end_seconds: 12.0, text: 'Speed exceeding posted limits heading toward western bypass.', confidence: 0.89 },
          { start_seconds: 13.5, end_seconds: 17.8, text: 'Forwarding telemetry to regional operations center.', confidence: 0.95 },
        ],
        detected_language: 'en (98% confidence)',
        analyzed_at: new Date().toISOString(),
      });
    }
  };

  const runUrlAnalysis = async () => {
    if (!remoteUrl.trim()) {
      setError('Please provide a valid media URL to inspect.');
      return;
    }
    setAnalyzingUrl(true);
    setError(null);
    setLinkedSuccess(false);

    try {
      const res = await apiRequest<any>('/media-intelligence/analyze/url', {
        method: 'POST',
        body: JSON.stringify({ url: remoteUrl.trim(), media_type: mediaType }),
      });
      setActiveCaseTitle(`Remote URL: ${remoteUrl.split('?')[0].split('/').pop() || 'Evidence'}`);
      if (res.media_type === 'video') {
        setVideoResult(res.result);
        setImageResult(null);
        setAudioResult(null);
        setMediaType('video');
      } else if (res.media_type === 'audio') {
        setAudioResult(res.result);
        setImageResult(null);
        setVideoResult(null);
        setMediaType('audio');
      } else {
        setImageResult(res.result);
        setVideoResult(null);
        setAudioResult(null);
        setMediaType('image');
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to acquire and inspect remote media URL');
    } finally {
      setAnalyzingUrl(false);
    }
  };

  const runAnalysis = async () => {
    if (!selectedFile) {
      setError('Please select a media file to inspect.');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setActiveCaseTitle(selectedFile.name);

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

              {/* Intake Mode Switcher: Local File vs Remote URL */}
              <div className="flex items-center justify-between text-xs font-mono pt-1">
                <span className="text-[10px] text-slate-500 uppercase font-bold">SOURCE:</span>
                <div className="flex gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
                  <button
                    type="button"
                    onClick={() => setIntakeMode('upload')}
                    className={cn(
                      'px-2.5 py-1 rounded text-[11px] font-bold cursor-pointer transition-colors',
                      intakeMode === 'upload' ? 'bg-slate-800 text-white shadow-xs' : 'text-slate-400 hover:text-white'
                    )}
                  >
                    File Upload
                  </button>
                  <button
                    type="button"
                    onClick={() => setIntakeMode('url')}
                    className={cn(
                      'px-2.5 py-1 rounded text-[11px] font-bold cursor-pointer transition-colors flex items-center gap-1',
                      intakeMode === 'url' ? 'bg-cyan-900/60 text-cyan-200 border border-cyan-700/60' : 'text-slate-400 hover:text-white'
                    )}
                  >
                    <LinkIcon className="w-3 h-3" />
                    <span>Remote URL</span>
                  </button>
                </div>
              </div>

              {intakeMode === 'upload' ? (
                <>
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
                </>
              ) : (
                <div className="space-y-3 p-4 rounded-xl border border-slate-800 bg-slate-950/60">
                  <span className="text-xs font-mono font-bold text-slate-300 block">
                    Remote Media Acquisition:
                  </span>
                  <input
                    type="url"
                    value={remoteUrl}
                    onChange={(e) => setRemoteUrl(e.target.value)}
                    placeholder={`https://example.com/evidence.${mediaType === 'image' ? 'jpg' : mediaType === 'video' ? 'mp4' : 'wav'}`}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-hidden focus:border-cyan-500"
                  />
                  <Button
                    onClick={runUrlAnalysis}
                    disabled={!remoteUrl.trim() || analyzingUrl}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold"
                  >
                    {analyzingUrl ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin mr-2" />
                        ACQUIRING & INSPECTING URL...
                      </>
                    ) : (
                      <>
                        <LinkIcon className="w-3.5 h-3.5 mr-2" />
                        FETCH & RUN FORENSIC ANALYSIS
                      </>
                    )}
                  </Button>
                </div>
              )}

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
              <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-2">
                    <Camera className="w-4 h-4" />
                    <span>IMAGE FORENSIC DOSSIER</span>
                  </CardTitle>
                  <p className="text-[11px] text-slate-400 font-mono mt-0.5 truncate max-w-sm">
                    {activeCaseTitle ? `${activeCaseTitle} · ` : ''}Verified Cryptographic Hashes
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={resetInspector}
                    className="border-slate-700 text-slate-300 hover:text-white text-xs font-mono h-8 cursor-pointer"
                  >
                    <RotateCcw className="w-3 h-3 mr-1" />
                    <span>Reset</span>
                  </Button>
                  <Button
                    size="sm"
                    onClick={linkToInvestigation}
                    disabled={linking || linkedSuccess}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold h-8 cursor-pointer"
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
                </div>
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
                      GPS:{' '}
                      {imageResult.exif.gps_lat && imageResult.exif.gps_lon ? (
                        <span className="inline-flex items-center gap-1.5">
                          <span className="text-emerald-400 font-bold">
                            {imageResult.exif.gps_lat}, {imageResult.exif.gps_lon}
                          </span>
                          <a
                            href={`https://www.google.com/maps?q=${imageResult.exif.gps_lat},${imageResult.exif.gps_lon}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300 underline font-sans"
                            title="Open in Maps"
                          >
                            <ExternalLink className="w-3 h-3" />
                            <span>Map</span>
                          </a>
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
              <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-xs font-mono font-bold text-indigo-400 flex items-center gap-2">
                    <Video className="w-4 h-4" />
                    <span>VIDEO FORENSIC DOSSIER & KEYFRAMES</span>
                  </CardTitle>
                  <p className="text-[11px] text-slate-400 font-mono mt-0.5 truncate max-w-sm">
                    {activeCaseTitle ? `${activeCaseTitle} · ` : ''}{videoResult.duration_seconds}s · {videoResult.resolution} · Codec {videoResult.codec}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={resetInspector}
                    className="border-slate-700 text-slate-300 hover:text-white text-xs font-mono h-8 cursor-pointer"
                  >
                    <RotateCcw className="w-3 h-3 mr-1" />
                    <span>Reset</span>
                  </Button>
                  <Button
                    size="sm"
                    onClick={linkToInvestigation}
                    disabled={linking || linkedSuccess}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold h-8 cursor-pointer"
                  >
                    {linkedSuccess ? 'SEALED TO VAULT' : 'SEAL TO INVESTIGATION'}
                  </Button>
                </div>
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

          {audioResult && (
            <Card className="border-purple-950/80 bg-[#0f1422] shadow-md">
              <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-xs font-mono font-bold text-purple-400 flex items-center gap-2">
                    <FileAudio className="w-4 h-4" />
                    <span>AUDIO FORENSIC DOSSIER & TRANSCRIPT</span>
                  </CardTitle>
                  <p className="text-[11px] text-slate-400 font-mono mt-0.5 truncate max-w-sm">
                    {activeCaseTitle ? `${activeCaseTitle} · ` : ''}{audioResult.duration_seconds}s · {audioResult.sample_rate} Hz · {audioResult.channels === 1 ? 'Mono' : 'Stereo'} · {audioResult.format}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={resetInspector}
                    className="border-slate-700 text-slate-300 hover:text-white text-xs font-mono h-8 cursor-pointer"
                  >
                    <RotateCcw className="w-3 h-3 mr-1" />
                    <span>Reset</span>
                  </Button>
                  <Button
                    size="sm"
                    onClick={linkToInvestigation}
                    disabled={linking || linkedSuccess}
                    className="bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs font-bold h-8 cursor-pointer"
                  >
                    {linkedSuccess ? 'SEALED TO VAULT' : 'SEAL TO INVESTIGATION'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-4 space-y-4">
                {/* Cryptographic Hash Bar */}
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-slate-400 font-bold">SHA-256 CHECKSUM</span>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(audioResult.sha256, 'sha256')}
                      className="text-xs font-mono text-cyan-400 flex items-center gap-1 hover:underline cursor-pointer"
                    >
                      {copiedHash === 'sha256' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedHash === 'sha256' ? 'COPIED' : 'COPY'}</span>
                    </button>
                  </div>
                  <div className="font-mono text-xs text-purple-300 break-all select-all bg-slate-900/80 p-2 rounded-sm border border-slate-800/60">
                    {audioResult.sha256}
                  </div>
                  <div className="grid grid-cols-3 gap-2 pt-1 text-[11px] font-mono text-slate-400">
                    <div>FORMAT: <span className="text-slate-200">{audioResult.format}</span></div>
                    <div>DURATION: <span className="text-slate-200">{audioResult.duration_seconds}s</span></div>
                    <div>LANGUAGE: <span className="text-purple-300 font-bold">{audioResult.detected_language || 'en (NLP)'}</span></div>
                  </div>
                </div>

                {/* NLP Audio Transcript */}
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2 font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
                    <span className="font-bold text-slate-300 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-purple-400" />
                      SPEECH-TO-TEXT NLP TRANSCRIPT
                    </span>
                    <Badge variant="outline" className="text-[10px] text-purple-300 border-purple-800">
                      WHISPER PROVENANCE
                    </Badge>
                  </div>
                  <div className="space-y-1.5 pt-1">
                    {audioResult.transcript.map((seg, i) => (
                      <div key={i} className="p-2 rounded bg-slate-900 border border-slate-800/80 flex items-start justify-between gap-3 text-xs">
                        <div>
                          <span className="text-[10px] text-slate-500 font-mono">[{seg.start_seconds}s - {seg.end_seconds}s]:</span>
                          <p className="text-slate-200 font-mono mt-0.5">{seg.text}</p>
                        </div>
                        <span className="text-[10px] font-mono text-emerald-400 shrink-0">
                          {Math.round(seg.confidence * 100)}% conf
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {!imageResult && !videoResult && !audioResult && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="p-4 rounded-xl border border-slate-800 bg-[#0f1422]">
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Real-World Forensic Evidence Showcase:</span>
                </h4>
                <p className="text-[11px] text-slate-500 font-mono mt-1">
                  Click any pre-verified intelligence case below to instantly inspect cryptographic hashes, C2PA manifests, video keyframes, or vehicle plate OCR:
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {/* Showcase Case 1: Traffic Surveillance CCTV */}
                <div
                  onClick={() => loadShowcaseCase('traffic')}
                  className="p-4 rounded-xl border border-slate-800 bg-[#0f1422] hover:border-emerald-500/60 hover:bg-emerald-950/10 transition-all cursor-pointer space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                      TRAFFIC CCTV • IMAGE
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">8.3 MP · 4K</span>
                  </div>
                  <h5 className="text-xs font-bold font-mono text-slate-200 group-hover:text-emerald-300 transition-colors">
                    Salem North CCTV: Plate TN34MA8256
                  </h5>
                  <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
                    Extracted license plate <strong className="text-emerald-400 font-mono">TN34MA8256</strong>, sanitized EXIF GPS coordinates, camera hardware signature, and perceptual dHash verification.
                  </p>
                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-emerald-400">
                    <span>Inspect Forensic Dossier</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

                {/* Showcase Case 2: C2PA Synthetic Deepfake */}
                <div
                  onClick={() => loadShowcaseCase('deepfake')}
                  className="p-4 rounded-xl border border-slate-800 bg-[#0f1422] hover:border-amber-500/60 hover:bg-amber-950/10 transition-all cursor-pointer space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20">
                      C2PA SYNTHETIC • DEEPFAKE
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">TAMPERED</span>
                  </div>
                  <h5 className="text-xs font-bold font-mono text-slate-200 group-hover:text-amber-300 transition-colors">
                    Disinformation Evacuation Deepfake
                  </h5>
                  <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
                    C2PA signature declares synthetic Midjourney v6.0 provenance, stripped EXIF camera tags, and OCR headline parsing.
                  </p>
                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-amber-400">
                    <span>Inspect Provenance Manifest</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

                {/* Showcase Case 3: Recon Drone Video */}
                <div
                  onClick={() => loadShowcaseCase('drone')}
                  className="p-4 rounded-xl border border-slate-800 bg-[#0f1422] hover:border-indigo-500/60 hover:bg-indigo-950/10 transition-all cursor-pointer space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20">
                      AERIAL SURVEILLANCE • VIDEO
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">24.5s · 1080p</span>
                  </div>
                  <h5 className="text-xs font-bold font-mono text-slate-200 group-hover:text-indigo-300 transition-colors">
                    Recon Drone Keyframe Decomposition
                  </h5>
                  <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
                    Sampled keyframes with individual pHash fingerprints, 2 detected scene cuts, vehicle convoy OCR telemetry, and audio transcription.
                  </p>
                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-indigo-400">
                    <span>Inspect Video Keyframes</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>

                {/* Showcase Case 4: Tactical Audio Intercept */}
                <div
                  onClick={() => loadShowcaseCase('audio')}
                  className="p-4 rounded-xl border border-slate-800 bg-[#0f1422] hover:border-purple-500/60 hover:bg-purple-950/10 transition-all cursor-pointer space-y-2 group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-bold border border-purple-500/20">
                      COMMUNICATIONS • AUDIO
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">16 kHz PCM</span>
                  </div>
                  <h5 className="text-xs font-bold font-mono text-slate-200 group-hover:text-purple-300 transition-colors">
                    Channel 7 Tactical Radio Wire Intercept
                  </h5>
                  <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
                    Speech-to-text NLP transcript identifying target convoy checkpoint clearance and vehicle speed telemetry.
                  </p>
                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-purple-400">
                    <span>Inspect Audio Telemetry</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
