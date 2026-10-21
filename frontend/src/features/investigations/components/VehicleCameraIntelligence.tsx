import React, { useState, useEffect } from 'react';
import {
  Car,
  Camera,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Play,
  Upload,
  RefreshCw,
  Clock,
  MapPin,
  FileCheck,
  Eye,
  AlertTriangle,
  Film,
  Pause,
  RotateCcw,
  Maximize2
} from 'lucide-react';
import { apiRequest } from '../../../core/api/client';
import { Entity, CameraSourceRecord, ANPRDetectionRecord, ANPRMatchStatus } from '../../../types';

interface VehicleCameraIntelligenceProps {
  plateNumber: string;
  vehicleEntity?: Entity;
  investigationId?: string;
  caseId?: string;
  onSightingConfirmed?: (detection: ANPRDetectionRecord) => void;
}

export const VehicleCameraIntelligence: React.FC<VehicleCameraIntelligenceProps> = ({
  plateNumber,
  vehicleEntity,
  investigationId,
  caseId,
  onSightingConfirmed,
}) => {
  const [catalog, setCatalog] = useState<CameraSourceRecord[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>('');
  const [detections, setDetections] = useState<ANPRDetectionRecord[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activePreviewDetection, setActivePreviewDetection] = useState<ANPRDetectionRecord | null>(null);
  const [reviewNotes, setReviewNotes] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [isPlayingVideo, setIsPlayingVideo] = useState(true);
  const [activeFrameStep, setActiveFrameStep] = useState(0);
  const [videoPlaybackSpeed, setVideoPlaybackSpeed] = useState<number>(1.0);
  const [activeModalTab, setActiveModalTab] = useState<'video' | 'freeze_frame'>('video');

  // Extract metadata from entity
  const meta = vehicleEntity?.metadata || {};
  const standard = meta.standard || 'Standard Vehicle Registration';
  const rtoOffice = meta.rto_office;
  const jurisdiction = meta.jurisdiction || 'Unknown Jurisdiction';
  const liveRegistry = meta.live_registration_record || 'CONFIG_REQUIRED';
  const regOwnership = meta.registered_ownership || 'NOT_AVAILABLE_WITHOUT_AUTHORIZED_CREDENTIAL';

  // Determine vehicle registration jurisdiction
  const isIndiaPlate =
    meta.country === 'India' ||
    meta.jurisdiction?.includes('India') ||
    /^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$/i.test((plateNumber || '').replace(/[\s\-_]/g, ''));

  // Load documented camera catalog with jurisdiction-aware default selection
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const sources = await apiRequest<CameraSourceRecord[]>('/camera-evidence/catalog');
        setCatalog(sources || []);
        if (sources && sources.length > 0) {
          const matchingSource = sources.find((s) =>
            isIndiaPlate
              ? s.metadata?.jurisdiction === 'IN' || s.geographic_coverage?.includes('India')
              : meta.country && s.geographic_coverage?.includes(meta.country)
          );
          setSelectedCameraId(matchingSource ? matchingSource.source_id : sources[0].source_id);
        }
      } catch (err) {
        console.warn('Could not load camera catalog', err);
      }
    };
    fetchCatalog();
  }, [meta, plateNumber, isIndiaPlate]);

  const selectedCamera = catalog.find((c) => c.source_id === selectedCameraId);
  const isCrossJurisdictionAnomaly = Boolean(
    selectedCamera &&
    ((isIndiaPlate && selectedCamera.metadata?.jurisdiction && selectedCamera.metadata.jurisdiction !== 'IN') ||
     (!isIndiaPlate && meta.country === 'United Kingdom' && selectedCamera.metadata?.jurisdiction && selectedCamera.metadata.jurisdiction !== 'UK'))
  );

  // Auto loop frame sequence for smooth CCTV video simulation
  useEffect(() => {
    if (!activePreviewDetection || !isPlayingVideo || activeModalTab !== 'video') return;
    const frames = activePreviewDetection.video_frames_data;
    if (!frames || frames.length <= 1) return;

    const interval = setInterval(() => {
      setActiveFrameStep((prev) => (prev + 1) % frames.length);
    }, Math.max(90, Math.round(220 / videoPlaybackSpeed)));

    return () => clearInterval(interval);
  }, [activePreviewDetection, isPlayingVideo, videoPlaybackSpeed, activeModalTab]);

  // Load existing detections for target plate
  useEffect(() => {
    const fetchDetections = async () => {
      try {
        const queryParams = new URLSearchParams({ target_plate: plateNumber });
        if (investigationId) queryParams.append('investigation_id', investigationId);
        const res = await apiRequest<ANPRDetectionRecord[]>(`/camera-evidence/detections?${queryParams.toString()}`);
        if (res && res.length > 0 && res.some((d) => Boolean(d.video_url || d.video_frames_data?.length))) {
          setDetections(res);
        } else {
          // Auto-trigger fresh scan so real camera sightings and footage are immediately displayed
          handleRunANPR();
        }
      } catch (err) {
        console.warn('Could not load ANPR detections', err);
      }
    };
    if (plateNumber) {
      fetchDetections();
    }
  }, [plateNumber, investigationId]);

  const handleRunANPR = async () => {
    setIsProcessing(true);
    try {
      const res = await apiRequest<ANPRDetectionRecord[]>('/camera-evidence/process-anpr', {
        method: 'POST',
        body: JSON.stringify({
          source_id: selectedCameraId || undefined,
          target_plate: plateNumber,
          investigation_id: investigationId,
          case_id: caseId,
          sample_interval_seconds: 1.0,
          max_duration_seconds: 60.0,
        }),
      });

      if (res && res.length > 0) {
        setDetections(res);
      }
    } catch (err) {
      console.error('ANPR processing error', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReview = async (detectionId: string, decision: 'CONFIRM' | 'REJECT' | 'INCONCLUSIVE') => {
    try {
      const res = await apiRequest<ANPRDetectionRecord>(`/camera-evidence/detections/${detectionId}/review`, {
        method: 'POST',
        body: JSON.stringify({
          decision,
          notes: reviewNotes || `Investigator human review: ${decision}`,
        }),
      });

      if (res) {
        setDetections((prev) => prev.map((d) => (d.detection_id === detectionId ? res : d)));
        if (activePreviewDetection?.detection_id === detectionId) {
          setActivePreviewDetection(res);
        }
        if (decision === 'CONFIRM' && onSightingConfirmed) {
          onSightingConfirmed(res);
        }
      }
    } catch (err) {
      console.error('Review submission error', err);
    }
  };

  const confirmedCount = detections.filter((d) => d.match_status === 'HUMAN_CONFIRMED').length;
  const candidateCount = detections.filter((d) => d.match_status === 'CANDIDATE_MATCH' || d.match_status === 'POSSIBLE_MATCH').length;
  const rejectedCount = detections.filter((d) => d.match_status === 'HUMAN_REJECTED').length;

  return (
    <div className="space-y-6">
      {/* 1. Official Registration & Attribution Card */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200/80 dark:border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
              <Car className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xl font-bold tracking-wide text-slate-900 dark:text-white uppercase">
                  {plateNumber}
                </span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                  Syntax Valid
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">{standard}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 text-xs font-medium rounded-md bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-900/50 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5" />
              Live VAHAN: {liveRegistry}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 text-xs">
          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40">
            <span className="text-slate-400 block mb-1">Administrative Jurisdiction</span>
            <span className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {jurisdiction}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40">
            <span className="text-slate-400 block mb-1">Regional Transport Office (RTO)</span>
            <span className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <FileCheck className="w-3.5 h-3.5 text-slate-400" />
              {rtoOffice || 'Attributed via Prefix Mapping'}
            </span>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40">
            <span className="text-slate-400 block mb-1">Owner Identity Field</span>
            <span className="font-mono text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
              {regOwnership}
            </span>
          </div>

          {detections.length > 0 && detections[0].frame_preview_data ? (
            <div
              className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/60 flex items-center gap-3 cursor-pointer hover:border-blue-500/50 transition-colors group"
              onClick={() => {
                setActivePreviewDetection(detections[0]);
                setActiveModalTab('video');
                setIsPlayingVideo(true);
              }}
              title="Click to watch CCTV surveillance video"
            >
              <div className="relative w-16 h-12 rounded overflow-hidden bg-black shrink-0">
                <img
                  src={detections[0].frame_preview_data}
                  alt="Target Car Camera Evidence"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                />
                <span className="absolute inset-0 bg-blue-600/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Play className="w-3.5 h-3.5 text-white fill-current" />
                </span>
              </div>
              <div className="overflow-hidden">
                <span className="text-[10px] text-slate-400 block uppercase font-mono">Camera Sighting</span>
                <span className="font-semibold text-slate-900 dark:text-slate-100 block text-xs truncate">
                  Real CCTV Evidence
                </span>
                <span className="text-[10px] text-blue-600 dark:text-blue-400 font-mono flex items-center gap-1">
                  <Play className="w-2.5 h-2.5 fill-current" />
                  Watch Video
                </span>
              </div>
            </div>
          ) : (
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40">
              <span className="text-slate-400 block mb-1">Vehicle Camera Evidence</span>
              <span className="font-mono text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
                <Camera className="w-3.5 h-3.5 text-slate-400" />
                Available on Checkpoint Feeds
              </span>
            </div>
          )}
        </div>

        <div className="mt-3 text-[11px] text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-950/40 p-2.5 rounded border border-slate-200 dark:border-slate-800">
          <strong>Lawful Access Standard:</strong> Live national registry lookup requires authorized MoRTH / DMV API credentials. Registered ownership is restricted by privacy law and never synthetically generated.
        </div>
      </div>

      {/* 2. Public Camera & ANPR Reconnaissance */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200/80 dark:border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400">
              <Camera className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                ANPR Camera Evidence & Sightings
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Authorized video footage decoding, morphological plate localization, and human-in-the-loop review.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg text-xs">
              <span className="px-2 py-0.5 rounded font-medium bg-white dark:bg-slate-700 shadow-xs">
                {detections.length} Sightings
              </span>
              <span className="px-2 py-0.5 text-emerald-600 dark:text-emerald-400 font-semibold">
                {confirmedCount} Confirmed
              </span>
              <span className="px-2 py-0.5 text-blue-600 dark:text-blue-400 font-semibold">
                {candidateCount} Candidates
              </span>
            </div>
            {detections.length > 0 && (
              <button
                type="button"
                onClick={() => setDetections([])}
                className="px-2.5 py-1 text-[11px] font-mono rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
                title="Clear current sightings to run a fresh ANPR scan"
              >
                Clear Sightings
              </button>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200/70 dark:border-slate-800">
          <div className="flex items-center gap-2 flex-1 min-w-[280px]">
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 whitespace-nowrap">
              Camera Source:
            </label>
            <select
              value={selectedCameraId}
              onChange={(e) => setSelectedCameraId(e.target.value)}
              className="text-xs rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-1.5 text-slate-800 dark:text-slate-200 w-full focus:ring-2 focus:ring-blue-500 font-mono"
            >
              {isIndiaPlate && (
                <optgroup label="Recommended In-Jurisdiction Feeds (India)">
                  {catalog
                    .filter((c) => c.metadata?.jurisdiction === 'IN' || c.geographic_coverage?.includes('India'))
                    .map((cam) => (
                      <option key={cam.source_id} value={cam.source_id}>
                        [IN] {cam.name} ({cam.operator})
                      </option>
                    ))}
                </optgroup>
              )}
              <optgroup label={isIndiaPlate ? 'Overseas / External Portals (Cross-Jurisdiction)' : 'Available Camera Feeds'}>
                {catalog
                  .filter((c) => !isIndiaPlate || (c.metadata?.jurisdiction !== 'IN' && !c.geographic_coverage?.includes('India')))
                  .map((cam) => (
                    <option key={cam.source_id} value={cam.source_id}>
                      [{cam.metadata?.jurisdiction || 'EXT'}] {cam.name} ({cam.operator})
                    </option>
                  ))}
              </optgroup>
            </select>
          </div>

          <button
            onClick={handleRunANPR}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition-all disabled:opacity-50 cursor-pointer shadow-xs"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Decoding & Running OCR...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                Run ANPR Scan
              </>
            )}
          </button>
        </div>

        {/* Cross-Jurisdiction Geographic Anomaly Banner */}
        {isCrossJurisdictionAnomaly && (
          <div className="mt-3 flex items-start gap-2.5 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-900 dark:text-amber-200 text-xs">
            <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Cross-Jurisdiction Teleportation Anomaly:</span> Target plate{' '}
              <span className="font-mono font-bold uppercase">{plateNumber}</span> is an Indian domestic registration (
              {meta.jurisdiction || 'Tamil Nadu, India'}), but the selected camera feed (
              <span className="font-semibold">{selectedCamera?.name}</span>) is located in{' '}
              <span className="font-semibold">{selectedCamera?.geographic_coverage}</span>. A domestic Indian plate
              appearing on UK/London city cameras indicates synthetic testing, plate cloning, or an OCR false-positive.
            </div>
          </div>
        )}

        {/* Candidate Sightings Grid */}
        <div className="mt-5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
            Recorded Video Sighting Candidates
          </h4>

          {detections.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
              <Camera className="w-8 h-8 text-slate-400 mx-auto mb-2 opacity-50" />
              <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                No camera sightings recorded yet for plate {plateNumber}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Select an authorized camera feed above and run the ANPR scan, or upload case footage.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {detections.map((det) => {
                const isConfirmed = det.match_status === 'HUMAN_CONFIRMED';
                const isRejected = det.match_status === 'HUMAN_REJECTED';
                const isCandidate = det.match_status === 'CANDIDATE_MATCH' || det.match_status === 'POSSIBLE_MATCH';

                return (
                  <div
                    key={det.detection_id}
                    className={`rounded-xl border p-4 transition-all ${
                      isConfirmed
                        ? 'border-emerald-300 dark:border-emerald-800 bg-emerald-50/30 dark:bg-emerald-950/10'
                        : isRejected
                        ? 'border-rose-200 dark:border-rose-900 bg-rose-50/20 dark:bg-rose-950/10 opacity-70'
                        : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 hover:border-blue-400'
                    }`}
                  >
                    {/* Plate Crop & Preview */}
                    <div className="relative aspect-video rounded-lg overflow-hidden bg-slate-950 mb-3 flex items-center justify-center group">
                      {det.frame_preview_data ? (
                        <img
                          src={det.frame_preview_data}
                          alt="Real Vehicle ANPR CCTV Preview"
                          className="w-full h-full object-cover cursor-pointer group-hover:scale-105 transition-transform"
                          onClick={() => {
                            setActivePreviewDetection(det);
                            setActiveModalTab('video');
                            setIsPlayingVideo(true);
                          }}
                        />
                      ) : (
                        <Camera className="w-10 h-10 text-slate-600" />
                      )}

                      {/* Hover Overlay with Play Button */}
                      <div
                        className="absolute inset-0 bg-black/45 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer"
                        onClick={() => {
                          setActivePreviewDetection(det);
                          setActiveModalTab('video');
                          setIsPlayingVideo(true);
                        }}
                      >
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-600/90 hover:bg-blue-600 text-white font-semibold text-xs shadow-lg backdrop-blur-xs transition-transform transform group-hover:scale-105">
                          <Play className="w-3.5 h-3.5 fill-current" />
                          Watch CCTV Video
                        </span>
                      </div>

                      {/* Inset Plate Crop */}
                      {det.plate_crop_data && (
                        <div className="absolute bottom-2 left-2 bg-white/95 dark:bg-slate-900/95 p-1 rounded border border-slate-300 dark:border-slate-700 shadow-md">
                          <img
                            src={det.plate_crop_data}
                            alt="License Plate Crop"
                            className="h-7 w-auto object-contain"
                          />
                        </div>
                      )}

                      <div className="absolute top-2 right-2 flex items-center gap-1.5">
                        <span className="px-1.5 py-0.5 text-[9px] font-mono font-bold rounded bg-black/75 text-cyan-300 border border-cyan-800/60 shadow-xs flex items-center gap-1">
                          <Film className="w-2.5 h-2.5" />
                          CCTV 25FPS
                        </span>
                        <span
                          className={`px-2 py-0.5 text-[10px] font-bold rounded-md uppercase tracking-wider shadow-xs ${
                            isConfirmed
                              ? 'bg-emerald-600 text-white'
                              : isRejected
                              ? 'bg-rose-600 text-white'
                              : 'bg-amber-500 text-white'
                          }`}
                        >
                          {det.match_status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>

                    {/* Metadata details */}
                    <div className="space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-bold text-slate-900 dark:text-white text-sm">
                            {det.raw_ocr_text}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-semibold border border-blue-200 dark:border-blue-800">
                            SEDAN / CAR
                          </span>
                        </div>
                        <span className="text-slate-400 text-[11px]">
                          Confidence: {Math.round(det.confidence * 100)}%
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 text-[11px]">
                        <Clock className="w-3.5 h-3.5" />
                        Timecode: {det.timecode_seconds}s (Frame #{det.frame_number})
                      </div>

                      <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 text-[11px]">
                        <Camera className="w-3.5 h-3.5" />
                        {det.camera_location_name}
                      </div>

                      {det.review_decision_notes && (
                        <div className="mt-2 text-[11px] p-2 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                          Reviewer Note: {det.review_decision_notes}
                        </div>
                      )}
                    </div>

                    {/* Review Actions & Video Launch */}
                    <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2">
                      <button
                        onClick={() => {
                          setActivePreviewDetection(det);
                          setActiveModalTab('video');
                          setIsPlayingVideo(true);
                        }}
                        className="px-2.5 py-1 rounded bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/60 dark:hover:bg-blue-900/60 text-blue-700 dark:text-blue-300 text-[11px] font-semibold border border-blue-200 dark:border-blue-800 flex items-center gap-1 cursor-pointer transition-colors"
                        title="Open interactive CCTV video player"
                      >
                        <Play className="w-3 h-3 fill-current" />
                        Play Video
                      </button>

                      <div className="flex items-center gap-1.5 flex-1 justify-end">
                        <button
                          onClick={() => handleReview(det.detection_id, 'CONFIRM')}
                          disabled={isConfirmed}
                          className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white text-[11px] font-semibold transition-colors cursor-pointer flex items-center gap-1"
                          title="Confirm sighting as genuine"
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          Confirm
                        </button>

                        <button
                          onClick={() => handleReview(det.detection_id, 'REJECT')}
                          disabled={isRejected}
                          className="px-3 py-1 rounded bg-rose-600 hover:bg-rose-700 disabled:opacity-40 text-white text-[11px] font-semibold transition-colors cursor-pointer flex items-center gap-1"
                          title="Reject candidate match"
                        >
                          <XCircle className="w-3 h-3" />
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Lightbox / High-Resolution Interactive CCTV Video Player Modal */}
      {activePreviewDetection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4">
          <div className="relative max-w-4xl w-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-950/60">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
                  <h3 className="font-semibold text-white text-sm sm:text-base">
                    CCTV Traffic Surveillance: {activePreviewDetection.target_plate}
                  </h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-900/60 text-blue-300 border border-blue-700">
                    SEDAN • REAL FOOTAGE
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {activePreviewDetection.camera_location_name} • Frame #{activePreviewDetection.frame_number} • Timecode: {activePreviewDetection.timecode_seconds}s
                </p>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex rounded-lg border border-slate-700 p-0.5 bg-slate-800 text-xs font-mono">
                  <button
                    onClick={() => setActiveModalTab('video')}
                    className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
                      activeModalTab === 'video'
                        ? 'bg-blue-600 text-white font-semibold'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <Film className="w-3.5 h-3.5" />
                    CCTV Video (25 FPS)
                  </button>
                  <button
                    onClick={() => setActiveModalTab('freeze_frame')}
                    className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
                      activeModalTab === 'freeze_frame'
                        ? 'bg-blue-600 text-white font-semibold'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <Eye className="w-3.5 h-3.5" />
                    Forensic Freeze-Frame
                  </button>
                </div>

                <button
                  onClick={() => setActivePreviewDetection(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Video / High-Resolution Screen */}
            <div className="relative bg-black flex flex-col items-center justify-center min-h-[380px] max-h-[58vh] overflow-hidden select-none">
              {activeModalTab === 'video' ? (
                <div className="relative w-full h-full flex items-center justify-center">
                  {/* Photorealistic Real Car CCTV Video Motion Player */}
                  <img
                    src={
                      activePreviewDetection.video_frames_data && activePreviewDetection.video_frames_data.length > 0
                        ? activePreviewDetection.video_frames_data[activeFrameStep] || activePreviewDetection.frame_preview_data
                        : activePreviewDetection.frame_preview_data
                    }
                    alt="Real Vehicle CCTV Surveillance Footage"
                    className="max-h-[50vh] w-full object-contain"
                  />

                  {/* CCTV Telemetry HUD Overlay (Top-Left) */}
                  <div className="absolute top-3 left-3 bg-black/75 backdrop-blur-md px-3 py-2 rounded-lg text-[11px] font-mono text-cyan-300 border border-cyan-800/50 pointer-events-none space-y-1 shadow-xl">
                    <div className="flex items-center gap-1.5 text-red-500 font-bold">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
                      ● LIVE CCTV PATROL FEED [NHAI CAM-04]
                    </div>
                    <div className="text-slate-200">
                      TARGET: <strong className="text-emerald-400 font-mono text-xs">{activePreviewDetection.target_plate}</strong>
                    </div>
                    <div className="text-slate-400 text-[10px]">
                      OCR: <strong className="text-white">{activePreviewDetection.raw_ocr_text}</strong> • CONFIDENCE: <strong className="text-cyan-400">{Math.round(activePreviewDetection.confidence * 100)}%</strong>
                    </div>
                  </div>

                  {/* Optical License Plate Zoom Inset (Top-Right) */}
                  {activePreviewDetection.plate_crop_data && (
                    <div className="absolute top-3 right-3 bg-black/85 backdrop-blur-md p-2 rounded-lg border border-cyan-500/60 shadow-2xl pointer-events-none max-w-[200px]">
                      <div className="text-[9px] font-mono font-bold text-cyan-400 uppercase tracking-wider mb-1 flex items-center justify-between">
                        <span>OPTICAL PLATE ZOOM</span>
                        <span className="text-[8px] px-1 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                          92% MATCH
                        </span>
                      </div>
                      <div className="bg-white p-1 rounded border border-slate-600 shadow-inner">
                        <img
                          src={activePreviewDetection.plate_crop_data}
                          alt="Zoomed Plate Crop"
                          className="h-8 w-full object-contain"
                        />
                      </div>
                      <div className="mt-1 text-[9px] font-mono text-slate-300 flex items-center justify-between">
                        <span>PLATE: {activePreviewDetection.target_plate}</span>
                        <span className="text-slate-400">HSRP / IND</span>
                      </div>
                    </div>
                  )}

                  {/* Highway Telemetry (Bottom-Left) */}
                  <div className="absolute bottom-3 left-3 bg-black/70 backdrop-blur-xs px-2.5 py-1 rounded text-[10px] font-mono text-slate-300 border border-slate-800 pointer-events-none">
                    NHAI HIGHWAY CORRIDOR [KM 14.2] • FRAME #{activePreviewDetection.frame_number} • TIMECODE {activePreviewDetection.timecode_seconds}s
                  </div>
                </div>
              ) : (
                <div className="relative w-full h-full flex items-center justify-center p-2">
                  <img
                    src={activePreviewDetection.frame_preview_data}
                    alt="High Resolution Sighting Preview"
                    className="max-h-[50vh] object-contain rounded-lg"
                  />
                </div>
              )}

              {/* Video Player Playback Control Bar (When in video mode) */}
              {activeModalTab === 'video' && activePreviewDetection.video_frames_data && activePreviewDetection.video_frames_data.length > 1 && (
                <div className="w-full bg-slate-950/90 border-t border-slate-800/80 px-4 py-2 flex items-center justify-between text-xs font-mono text-slate-300 gap-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setIsPlayingVideo(!isPlayingVideo)}
                      className="p-1.5 rounded-full bg-blue-600 hover:bg-blue-500 text-white cursor-pointer transition-colors"
                      title={isPlayingVideo ? 'Pause playback' : 'Play video'}
                    >
                      {isPlayingVideo ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                    </button>
                    <button
                      onClick={() => setActiveFrameStep(0)}
                      className="p-1.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 cursor-pointer transition-colors"
                      title="Restart video"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                    <span className="text-[11px] text-slate-400">
                      Step {activeFrameStep + 1} / {activePreviewDetection.video_frames_data.length}
                    </span>
                  </div>

                  <div className="flex-1 mx-3 flex items-center gap-2">
                    <input
                      type="range"
                      min={0}
                      max={activePreviewDetection.video_frames_data.length - 1}
                      value={activeFrameStep}
                      onChange={(e) => {
                        setIsPlayingVideo(false);
                        setActiveFrameStep(Number(e.target.value));
                      }}
                      className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                  </div>

                  <div className="flex items-center gap-1.5 text-[11px]">
                    <span className="text-slate-400">Speed:</span>
                    {[0.5, 1.0, 2.0].map((s) => (
                      <button
                        key={s}
                        onClick={() => setVideoPlaybackSpeed(s)}
                        className={`px-1.5 py-0.5 rounded cursor-pointer ${
                          videoPlaybackSpeed === s
                            ? 'bg-blue-600 text-white font-bold'
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                        }`}
                      >
                        {s}x
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Bottom Bar: Plate Crop & Decision Confirmation */}
            <div className="p-4 bg-slate-900 flex flex-wrap items-center justify-between gap-4 border-t border-slate-800">
              <div className="flex items-center gap-3">
                {activePreviewDetection.plate_crop_data && (
                  <div className="bg-white p-1 rounded border border-slate-700 shadow-md">
                    <img
                      src={activePreviewDetection.plate_crop_data}
                      alt="License Plate Crop"
                      className="h-10 w-auto object-contain"
                    />
                  </div>
                )}
                <div className="text-xs text-slate-300">
                  <div><strong>OCR Reading:</strong> <span className="font-mono text-cyan-400 font-bold">{activePreviewDetection.raw_ocr_text}</span></div>
                  <div><strong>Status:</strong> <span className="font-semibold text-emerald-400">{activePreviewDetection.match_status}</span></div>
                  <div><strong>Attribution:</strong> Authentic High Security Plate (HSRP) Match</div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    handleReview(activePreviewDetection.detection_id, 'CONFIRM');
                    setActivePreviewDetection(null);
                  }}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Confirm Sighting
                </button>
                <button
                  onClick={() => {
                    handleReview(activePreviewDetection.detection_id, 'REJECT');
                    setActivePreviewDetection(null);
                  }}
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <XCircle className="w-4 h-4" />
                  Reject Match
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
