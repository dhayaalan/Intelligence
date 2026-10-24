# Cross-Repository Architecture Audit: Intelligence & Social Media AI Agents

**Date**: 2026-10-24  
**Auditor**: Senior Software Architect & Forensic Intelligence Engineering Team  
**Scope**: Target System (`Intelligence`) and Reference System (`social-media-ai-agents-v2`)  

---

## 1. Executive Summary

This architecture audit evaluates two independent, production-grade intelligence repositories:
1. **Target Application — Intelligence** (`/home/songoku/Pictures/Intelligence`):
   A multi-tenant modular OSINT, cyber threat intelligence, vehicle/camera surveillance, and case investigation SaaS platform powered by FastAPI, MongoDB, Neo4j, Redis, and React/Tailwind/TanStack Query.
2. **Reference Application — Social Media AI Agents** (`/home/songoku/Pictures/social-media-ai-agents-v2`):
   A defense-grade OSINT and media intelligence platform built for IAF PS-18, featuring client-side and server-side image/video/audio forensics, C2PA provenance validation, EXIF parsing, local audio spectral and YAMNet sound-event analysis, and zero-fabrication guarantees.

### Key Audit Mandate
- **No Monolithic Merging**: Maintain clean repository separation without merging stacks or forcing identical frameworks.
- **Contract & Isolation Respect**: Strictly adhere to `Intelligence/AGENTS.md` (core platform remains module-agnostic, tenant isolation via JWT, no hardcoded module switches) and `social-media-ai-agents-v2/CLAUDE.md` (frozen core contracts in `src/types/core.ts`, zero-fabrication rules, open-source model constraints).
- **Independent Feature Branch Delivery**:
  - `Intelligence`: `feature/media-intelligence-integration`
  - `social-media-ai-agents-v2`: `feature/media-intelligence-hardening`

---

## 2. Git & Working-Tree State

| Attribute | Target (`Intelligence`) | Reference (`social-media-ai-agents-v2`) |
| :--- | :--- | :--- |
| **Local Path** | `/home/songoku/Pictures/Intelligence` | `/home/songoku/Pictures/social-media-ai-agents-v2` |
| **Active Feature Branch** | `feature/media-intelligence-integration` | `feature/media-intelligence-hardening` |
| **Default Tracking Branch** | `origin/main` (up to date) | `origin/main` (up to date) |
| **Working Tree Status** | Clean (prior to audit artifacts) | Clean (prior to audit artifacts) |
| **Remote Push Status** | Configured (`origin` ssh) | Configured (`origin` ssh) |

---

## 3. Technology Stack & Architectural Inventory

### 3.1 Target Application: `Intelligence`

- **Backend Architecture**:
  - **Framework**: Python 3.10+, FastAPI (asynchronous REST API).
  - **Data Persistence**: MongoDB 7.0 (primary document store with tenant-scoped collections and indexes: `entities`, `relationships`, `searches`, `evidence`, `investigations`, `cases`).
  - **Graph Engine**: Neo4j 5.20 Community (cypher property graph for clue-to-clue traversal, entity expansion, and scoped subgraphs).
  - **Cache & Message Broker**: Redis 7.
  - **Security & Multi-Tenancy**: JWT bearer authentication (`TenantContext`), server-side RBAC (`SUPER_ADMIN`, `TENANT_ADMIN`, `ANALYST`, `USER`), fail-closed SSRF egress controller.
  - **Modular Architecture**:
    - `module_sdk/contract.py`: `IntelligenceModule` base class (`manifest`, `initialize`, `health_check`, `capabilities`, `search`, `shutdown`).
    - `module_sdk/provider_adapter.py`: `ProviderAdapter` base class for atomic tool integration.
    - `module_registry/registry.py`: Dynamic module loading and lifecycle management.
    - `search/orchestrator.py`: Orchestrates multi-module parallel execution, failure isolation, and normalizes findings into entities, relationships, evidence, and media.
  - **Existing Media Features**:
    - `app/modules/camera_evidence/`: Automated Number Plate Recognition (ANPR), Shodan CCTV/RTSP discovery, video capture extraction, `forensics.py` (dHash, sha256, EXIF extraction).
    - `app/search/media_extractor.py`: Extracts and normalizes image/video payloads from evidence streams.
    - `app/api/v1/investigations/{id}/media` and `link-media`: Investigation-scoped media gallery and deduplication.

- **Frontend Architecture**:
  - React 18, Vite 5, TypeScript 5, Tailwind CSS, Lucide icons, TanStack React Query 5.
  - Features: Modular investigation dashboard, Graph view (Cytoscape + React Flow), Vehicle & Camera Surveillance panel (`VehicleCameraIntelligence.tsx`), unified Search console.

### 3.2 Reference Application: `social-media-ai-agents-v2`

- **Architecture & Core Stack**:
  - TanStack Start 1.168 (SSR), React 19, Vite 8, Bun, Tailwind CSS 4, shadcn/ui.
  - Local-first architecture: No hosted cloud dependencies (Azure was removed), runs hermetically on localhost.
  - Frozen Contracts (`src/types/core.ts`): Frozen boundary schemas for `Article`, `Post`, `Entity`, `Finding`, `MediaAsset`, `VideoAsset`, `GeoPoint`, `ExifSummary`, `C2paSummary`.
- **Media Intelligence Stack**:
  - `src/utils/imaging.ts` & `src/utils/imaging-client.ts`: Pure DCT-based pHash, EXIF extraction via `exifr`, C2PA Content Credential verification via `@contentauth/c2pa` WASM, Tesseract.js OCR with local asset loading.
  - `src/utils/file-provenance.ts` & `src/utils/file-provenance-client.ts`: Deep format container inspection (JPEG/PNG trailers, PDF object enumeration, OOXML VBA macro and remote template detection, RIFF/AVI, EBML/WebM, OLE2, CMS signature validation, OCSP/CRL revocation verification).
  - `src/utils/audio-frequency.ts`, `src/utils/audio-extract-client.ts`, `src/utils/audio-events.ts`: Web Audio API spectral FFT inspection, WAV PCM-16 encoding, audio fingerprint hash matching, client-side audio analysis.
  - `ai-service/`: FastAPI vision and audio analysis service (Grounding DINO zero-shot detection, Florence-2 VLM description/OCR, InsightFace facial embeddings, YAMNet semantic audio event detection).

---

## 4. Test Baseline & Verification

### 4.1 `Intelligence` Baseline
- **Command**: `docker exec intelligence-backend pytest tests/`
- **Result**: `221 passed, 4 failed, 8 warnings in 700.36s`
  - Passing: Full coverage of module failure isolation, media intelligence contracts (`test_media_intelligence_contracts.py` 5/5), clue-to-clue investigation workflows, graph integrity, tenant security, role RBAC, ANPR, camera streams, reverse social recon.
  - 4 failures: Specific to tool executor live configuration checks (`tool_shodan`, `tool_twitter`) when external keys are not provided.
- **Frontend**:
  - `tsc --noEmit`: Clean (0 errors).
  - `npm test`: Clean (25/25 getEntityCategory assertions pass).

### 4.2 `social-media-ai-agents-v2` Baseline
- **Command**: `bun test tests/*.test.ts`
- **Result**: `2044 passed, 2 skipped, 10 failed across 99 files`
  - Exactly corresponds to the documented baseline in `PROJECT_MEMORY.md` (SearXNG config checks, presence-image collector behavior change, and live crt.sh network tests).
- **Core Export Integrity**:
  - `bun scripts/check-exports.ts`: 210 core exported symbols verified across 29 files (PASS).
- **TypeScript Check**:
  - `bun x tsc --noEmit`: 1 pre-existing type mismatch in `src/utils/collectors/person/presence-image.ts:69` (`type: "media"` instead of `"image"`).

---

## 5. Architectural Seam & Capability Mapping

| Media Capability | Reference Implementation (`social-media-ai-agents-v2`) | Target Implementation Point (`Intelligence`) | Adaptation Strategy |
| :--- | :--- | :--- | :--- |
| **Cryptographic Hashing** | `sha256Hex` in `file-provenance.ts` / `evidence.ts` | `compute_media_sha256` in `camera_evidence/forensics.py` | Unify into core `MediaIntelligenceModule` for multi-algorithm evidence integrity (SHA-256, MD5). |
| **Perceptual Hashing** | 2D DCT pHash in `imaging.ts` and `ai-service/app/forensics.py` | dHash in `camera_evidence/forensics.py` | Implement dual DCT pHash + dHash in `media_intelligence/service.py` with Hamming distance matching. |
| **EXIF & Camera Metadata** | `exifr` client-side / `ai-service/app/forensics.py` | Basic PIL EXIF in `camera_evidence/forensics.py` | Port robust EXIF/GPS coordinate parsing, camera make/model, software editing tag, capture timestamp. |
| **C2PA Provenance** | `c2pa` WASM in `imaging-client.ts` / `forensics.py` | Not implemented | Implement best-effort C2PA manifest scanner reading JUMBF/C2PA boxes from JPEG/PNG/MP4. |
| **Format Container Forensics** | Trailer walking, hidden byte detection in `file-provenance.ts` | Not implemented | Adapt container validation (JPEG EOI trailer detection, PNG IEND chunk inspection, file size limits). |
| **OCR Text Extraction** | Tesseract.js / `ai-service/app/ocr.py` | Pytesseract installed in backend Docker | Add unified OCR provider adapter in `MediaIntelligenceModule` for image and video keyframes. |
| **Video Sampling & Keyframes** | Client canvas sampling in `videos.tsx` | OpenCV frame sampling in `anpr_service.py` | Build server-side keyframe extractor with scene cut detection via OpenCV frame difference. |
| **Audio Format & Metadata** | `audio-extract.ts` / `encodeWavPcm16` | FFprobe / OpenCV audio stream detection | Implement audio stream inspection, sample rate, duration, and channel extraction. |
| **Audio Transcription** | `transcription.ts` / Whisper stub in `ai-service` | Not implemented | Provide Whisper-compatible STT adapter returning timestamped segments with fallback handling. |
| **Investigation Linkage** | Client-side `EvidenceVault` (`evidence-store.ts`) | MongoDB `investigations` collection & `evidence_repo` | Expose unified REST endpoints linking media evidence, findings, and provenance to cases. |

---

## 6. Integration Architecture for `Intelligence`

### 6.1 Compliance with `AGENTS.md`
1. **Module Independence**: Media intelligence is isolated inside `app/modules/media_intelligence/` implementing `IntelligenceModule` and registering via `module_registry.register(media_intelligence_module)`.
2. **Provider Failure Isolation**: Providers (EXIF, pHash, OCR, Keyframe, Audio, C2PA) implement `ProviderAdapter` and execute with individual error catching. A failed OCR binary never crashes search or investigation.
3. **Multi-Tenancy & Authorization**: All media evidence, jobs, and findings derive `tenant_id` from JWT context; endpoints enforce `Permission.VIEW_INVESTIGATION` and `Permission.EDIT_INVESTIGATION`.
4. **Primary Database**: Metadata, hashes, analysis findings, and investigation links persist in MongoDB (`media_jobs`, `media_evidence`).
5. **No Fake Data**: Absence of EXIF, C2PA, or OCR text is explicitly reported as `null` or `absent`, preserving forensic defensibility.
