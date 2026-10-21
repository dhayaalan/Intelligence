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
  AlertTriangle
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

  // Load existing detections for target plate
  useEffect(() => {
    const fetchDetections = async () => {
      try {
        const queryParams = new URLSearchParams({ target_plate: plateNumber });
        if (investigationId) queryParams.append('investigation_id', investigationId);
        const res = await apiRequest<ANPRDetectionRecord[]>(`/camera-evidence/detections?${queryParams.toString()}`);
        setDetections(res || []);
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
        setDetections((prev) => {
          const ids = new Set(prev.map((d) => d.detection_id));
          const newItems = res.filter((d) => !ids.has(d.detection_id));
          return [...newItems, ...prev];
        });
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

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 text-xs">
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
                    <div className="relative aspect-video rounded-lg overflow-hidden bg-slate-950 mb-3 flex items-center justify-center">
                      {det.frame_preview_data ? (
                        <img
                          src={det.frame_preview_data}
                          alt="ANPR Frame Preview"
                          className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform"
                          onClick={() => setActivePreviewDetection(det)}
                        />
                      ) : (
                        <Camera className="w-10 h-10 text-slate-600" />
                      )}

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

                      <div className="absolute top-2 right-2">
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
                        <span className="font-mono font-bold text-slate-900 dark:text-white text-sm">
                          {det.raw_ocr_text}
                        </span>
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

                    {/* Review Actions */}
                    <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2">
                      <button
                        onClick={() => handleReview(det.detection_id, 'CONFIRM')}
                        disabled={isConfirmed}
                        className="flex-1 flex items-center justify-center gap-1 py-1 rounded bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white text-[11px] font-semibold transition-colors cursor-pointer"
                        title="Confirm sighting as genuine"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Confirm
                      </button>

                      <button
                        onClick={() => handleReview(det.detection_id, 'REJECT')}
                        disabled={isRejected}
                        className="flex-1 flex items-center justify-center gap-1 py-1 rounded bg-rose-600 hover:bg-rose-700 disabled:opacity-40 text-white text-[11px] font-semibold transition-colors cursor-pointer"
                        title="Reject candidate match"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        Reject
                      </button>

                      <button
                        onClick={() => handleReview(det.detection_id, 'INCONCLUSIVE')}
                        className="p-1 rounded bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
                        title="Mark match as inconclusive"
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Lightbox / High-Resolution Sighting Viewer Modal */}
      {activePreviewDetection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4">
          <div className="relative max-w-4xl w-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-white">
                  ANPR Evidence Sighting: {activePreviewDetection.target_plate}
                </h3>
                <p className="text-xs text-slate-400">
                  {activePreviewDetection.camera_location_name} • Frame #{activePreviewDetection.frame_number} • Timecode: {activePreviewDetection.timecode_seconds}s
                </p>
              </div>
              <button
                onClick={() => setActivePreviewDetection(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="p-4 bg-black flex items-center justify-center max-h-[60vh] overflow-hidden">
              <img
                src={activePreviewDetection.frame_preview_data}
                alt="High Resolution Sighting Preview"
                className="max-h-[55vh] object-contain rounded-lg"
              />
            </div>

            <div className="p-4 bg-slate-900 flex flex-wrap items-center justify-between gap-4 border-t border-slate-800">
              <div className="flex items-center gap-3">
                {activePreviewDetection.plate_crop_data && (
                  <div className="bg-white p-1 rounded">
                    <img
                      src={activePreviewDetection.plate_crop_data}
                      alt="License Plate Crop"
                      className="h-10 w-auto object-contain"
                    />
                  </div>
                )}
                <div className="text-xs text-slate-300">
                  <div><strong>OCR Reading:</strong> {activePreviewDetection.raw_ocr_text}</div>
                  <div><strong>Status:</strong> {activePreviewDetection.match_status}</div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    handleReview(activePreviewDetection.detection_id, 'CONFIRM');
                    setActivePreviewDetection(null);
                  }}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition-all cursor-pointer"
                >
                  Confirm Sighting
                </button>
                <button
                  onClick={() => {
                    handleReview(activePreviewDetection.detection_id, 'REJECT');
                    setActivePreviewDetection(null);
                  }}
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold transition-all cursor-pointer"
                >
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
