# Media Capability Matrix: Cross-Repository Assessment

**Target System**: `Intelligence` (`/home/songoku/Pictures/Intelligence`)  
**Reference System**: `social-media-ai-agents-v2` (`/home/songoku/Pictures/social-media-ai-agents-v2`)  
**Date**: 2026-10-24  

---

## 1. Capability Inventory Matrix

| # | Capability Name | Current Reference Source | Current Target Source | Status | Required Dependencies & Credentials | API & Contract Implications | Recommendation | Priority | Verification Method |
|---|-----------------|--------------------------|-----------------------|--------|-------------------------------------|-----------------------------|----------------|----------|---------------------|
| 1 | **Cryptographic Media Hashing (SHA-256/MD5)** | `src/utils/file-provenance.ts` (`sha256Hex`), `src/utils/evidence.ts` | `app/modules/camera_evidence/forensics.py` (`compute_media_sha256`) | **Operational** | None (standard library `hashlib`) | Produces canonical `hash` on `EvidencePayload` and `MediaAsset.sha256` | **Reuse & Unify** into `MediaIntelligenceModule` | **P0** | Unit tests comparing hash across identical byte buffers |
| 2 | **Perceptual Image Hashing (dHash / DCT pHash)** | `src/utils/imaging.ts` (DCT pHash), `ai-service/app/forensics.py` | `app/modules/camera_evidence/forensics.py` (`compute_dhash`) | **Operational** | Pillow (`PIL.Image`), NumPy | Returns 64-bit hex hash; Hamming distance for duplicate checks | **Adapt & Expand** to support both dHash and 2D-DCT pHash with Hamming thresholds | **P1** | Characterization tests with resized, cropped, and rotated test fixtures |
| 3 | **EXIF & Camera Metadata Extraction** | `src/utils/imaging.ts` (`exifr`), `ai-service/app/forensics.py` | `app/modules/camera_evidence/forensics.py` (`extract_exif_metadata`) | **Partial** | Pillow (`PIL.ExifTags`) | Normalized `ExifSummary` (Make, Model, Software, DateTime, GPS) | **Adapt** to extract full camera attributes and GPS coordinate fixes honestly | **P1** | Unit tests asserting known metadata on fixtures; null on stripped files |
| 4 | **GPS Geolocation Extraction & Validation** | `src/utils/geo.ts` (`toGeoPoint`, `isRealCoordinate`) | `app/modules/camera_evidence/forensics.py` | **Partial** | None (pure coordinate validation) | `GeoPoint` (`lat`, `lon`, `precision`), rejection of `0,0` sentinels | **Port** coordinate validation rules to guarantee defensible geo-coordinates | **P1** | Boundary tests verifying 0,0 rejection and out-of-bounds rejection |
| 5 | **C2PA Content Credentials Provenance** | `src/utils/imaging-client.ts` (`@contentauth/c2pa` WASM) | Not implemented | **Missing** | None (binary box parser in pure Python) | `C2paSummary` (`status`, `signedBy`, `generator`, `aiGenerated`, `aiEvidence`) | **Implement** Python JUMBF/C2PA box detector reporting signed manifest absence/presence | **P1** | Fixture tests with real signed C2PA assets and non-C2PA stripped assets |
| 6 | **OCR Text Extraction (Images & Frames)** | `src/utils/imaging-client.ts` (Tesseract.js), `ai-service/app/ocr.py` | `pytesseract` in backend Docker | **Operational in backend** | `tesseract` binary, `pytesseract`, PIL | Normalized `ocr_text`, confidence, bounding boxes, language tag | **Register** as `OcrProviderAdapter` in `MediaIntelligenceModule` | **P1** | OCR test on test image containing English text and license plate |
| 7 | **Video Container & Stream Metadata** | `src/utils/file-provenance.ts` (EBML, RIFF parser) | OpenCV `cv2.VideoCapture` in `anpr_service.py` | **Partial** | `opencv-python-headless` | Video metadata (duration, resolution, fps, frame_count, codec) | **Standardize** into `VideoAnalysisService` | **P1** | Test extracting duration and resolution from sample video file |
| 8 | **Configurable Video Keyframe Sampling** | HTML5 Canvas sampling in `videos.tsx` | OpenCV frame sampling in `anpr_service.py` | **Partial** | `opencv-python-headless`, Pillow | Extracts keyframes per interval or scene cut with timestamps | **Build** server-side scene-change detector and keyframe generator | **P1** | Unit test verifying timestamp alignment and frame generation |
| 9 | **Audio Stream Extraction & Inspection** | `src/utils/audio-extract-client.ts`, `encodeWavPcm16` | Not implemented | **Missing** | `ffmpeg` / `wave` / standard library | Audio format, sample rate, channels, duration, waveform envelope | **Implement** pure Python WAV/header parser and audio stream extractor | **P1** | Test inspecting sample WAV/audio file headers |
| 10 | **Speech-to-Text Transcription** | `src/utils/transcription.ts` / Whisper client | YouTube captions in `youtube_collector.ts` | **Partial** | Whisper API / local model adapter | `TranscriptSegment` (`startSeconds`, `endSeconds`, `text`, `lang`) | **Implement** `WhisperTranscriptionProvider` with graceful fallback | **P2** | Tests verifying timestamped segments and unconfigured status |
| 11 | **Audio Semantic Event Classification** | `ai-service/app/audio_events.py` (YAMNet ONNX) | Not implemented | **Missing** | `onnxruntime` or internal model server | Detected sound events with start/end time and confidence | **Defer** heavy ONNX model; provide provider contract stub | **P3** | Contract test verifying `NOT_CONFIGURED` when model weights absent |
| 12 | **Zero-Shot Object Detection** | `ai-service/app/detect.py` (Grounding DINO) | Not implemented | **Missing** | PyTorch / CUDA / Grounding DINO weights | `Detection` (`label`, `confidence`, `bbox`, `model`) | **Defer** heavy weights; provide interface contract returning candidate matches | **P3** | Mock test asserting candidate matches are marked unverified |
| 13 | **Media Evidence Linkage & Investigation Vault** | `src/utils/evidence-store.ts`, `/vault` | `app/api/v1/investigations/{id}/link-media` | **Operational** | MongoDB, FastAPI | Links media items, deduplicates URLs, persists hashes and metadata | **Unify & Enhance** with analysis findings, timeline tabs, and export | **P0** | API test creating, linking, and retrieving media analysis records |
| 14 | **Cross-Modal Correlation (Image, Video, Audio, OCR)** | `src/utils/mediaint/claims.ts`, `timeline.ts` | `app/correlation/engine.py` | **Partial** | Neo4j property graph, MongoDB | Correlates OCR text, EXIF locations, and timestamps across items | **Wire** media entities and evidence into `correlation_engine` | **P1** | Test querying correlated graph nodes across media findings |

---

## 2. Priority & Implementation Roadmap

- **P0 Blockers (Immediate Execution)**:
  - Cryptographic hash generation and forensic verification.
  - Media evidence linkage to investigations with tenant isolation.
- **P1 High-Value Core Integrations**:
  - Unified `MediaIntelligenceModule` adhering to `IntelligenceModule` and `ProviderAdapter` contracts.
  - Image intelligence: EXIF/GPS extraction, dual dHash/pHash perceptual hashing, C2PA manifest detection, and OCR text extraction.
  - Video intelligence: Metadata parsing, frame sampling, scene-cut detection, keyframe generation, and OCR on keyframes.
  - Audio intelligence: Audio stream format inspection and timestamped transcription provider adapter.
  - REST API endpoints for media upload, synchronous/asynchronous analysis, job retrieval, and investigation linking.
  - Frontend Investigation UX: Integrated Media Intelligence tabs, frame viewers, transcript search, and forensic inspector.
- **P2 Enhancements**:
  - Full-text cross-modal search across OCR text, transcripts, and metadata.
  - Advanced export formats (PDF evidence dossier and Maltego CSV).
- **P3 Optional/Deferred Heuristics**:
  - Heavy GPU-dependent models (Grounding DINO, YAMNet ONNX) deferred to dedicated optional worker endpoints with honest preflight status reporting.
