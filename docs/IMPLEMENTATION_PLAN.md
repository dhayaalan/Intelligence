# Implementation Plan

## 1. Plan Overview

This plan details the phased migration of capabilities from the reference application (`social-media-ai-agents-v2-main`) to the primary application (`Intelligence`), integrating five key OSINT tools, video/image media processing with ANPR, local Docker deployment configurations, and investigation workflow unification.

---

## 2. Phase Breakdown

### Phase 1: Codebase Audit & Baseline Verification (Completed)
- Audit both codebases, runtime requirements, models, dependencies, and test baselines.
- Produce `docs/INTEGRATION_AUDIT.md`, `docs/FEATURE_MAPPING.md`, `docs/INTEGRATION_ARCHITECTURE.md`, `docs/IMPLEMENTATION_PLAN.md`.

### Phase 2: Core OSINT Provider Architecture & Adapter Implementation
- Implement `BaseOSINTProvider` interface in `app/modules/osint/providers/base.py`.
- **SpiderFoot:** Implement `SpiderFootProvider` (`app/modules/osint/providers/spiderfoot.py`) supporting local/remote REST API, active/passive scans, status polling, and module attribution.
- **theHarvester:** Implement `TheHarvesterProvider` (`app/modules/osint/providers/theharvester.py`) supporting worker HTTP endpoint and safe local CLI execution, passive CT sources, email/host/IP parsing.
- **Shodan:** Implement enhanced `ShodanProvider` (`app/modules/osint/providers/shodan.py`) with keyless InternetDB + full Host API + query generator + DNS enrichment.
- **Google Dorks:** Implement `GoogleDorksProvider` (`app/modules/osint/providers/google_dorks.py`) with curated template library, news RSS query executor, and browser search generator.
- **Maltego:** Implement `MaltegoProvider` (`app/modules/osint/providers/maltego.py`) with RFC-4180 CSV export for Maltego table import and local Transform endpoint.
- Connect all 5 providers into `app/modules/tool_executor.py` so they can be invoked via `/tools/{tool_id}/run` and batch runs.

### Phase 3: Vehicle Intelligence & VIN Enrichment Migration
- Port NHTSA keyless 17-character VIN decoder and Indian RTO state/office mapping into Python in `app/modules/osint/providers/vehicle_intelligence.py`.
- Connect vehicle intelligence with ANPR detection records for automatic jurisdiction and make/model correlation.

### Phase 4: Video / Image Intelligence, ANPR & Temporal Tracking Enhancements
- Enhance `app/modules/camera_evidence/anpr_service.py`:
  - Add temporal cross-frame tracking to cluster sightings of the same vehicle across frames (preventing duplicate evidence clutter).
  - Add perceptual hash (pHash) and EXIF extraction for image evidence (`app/modules/camera_evidence/forensics.py`).
  - Retain separate detection confidence vs. OCR confidence.
  - Store evidence records directly in MongoDB with frame timecode, crop base64, reviewer confirmation state.

### Phase 5: Local Execution & Docker Deployment Configuration
- Update `docker-compose.yml` to include optional profiles:
  - `theharvester-worker`: Container for running theHarvester in an isolated worker.
  - `spiderfoot`: Optional local container running `spiderfoot/spiderfoot:latest`.
  - Update `.env.example` with documented configuration parameters for all 5 tools and media directories.
- Author `docs/DEPLOYMENT.md`, `docs/INTEGRATION_STATUS.md`, `docs/KNOWN_LIMITATIONS.md`.

### Phase 6: Frontend Investigation Workspace Unification
- Update `InvestigatorShell.tsx` navigation to expose all tool workbench and intelligence modules.
- Ensure the Tools Workbench, Vehicle ANPR modal, and Investigation Detail pages display provider states (`AVAILABLE`, `CONFIG_REQUIRED`), real-time job progress, evidence provenance, and verified/unverified badges.

### Phase 7: Automated Testing & Verification
- Add comprehensive pytest suites for all 5 providers, ANPR temporal tracking, and vehicle intelligence.
- Run complete test suite and verify 100% pass rate.
