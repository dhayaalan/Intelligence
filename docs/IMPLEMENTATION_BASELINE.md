# Sential Intelligence — Implementation Baseline & Pre-Refactor Audit

**Audit Date**: 2026-10-21  
**Target Repository**: `/home/songoku/Pictures/Intelligence`  
**Current Branch**: `feat/master-universal-engine-vehicle-camera-anpr`  
**Base Commit**: `3d3ec32` (on `origin/main`)  
**Backend Status**: 195/195 tests passing (`pytest`)  
**Frontend Status**: TypeScript `tsc` & Vite production build clean (0 errors)

---

## Baseline Reproduction Checks

| # | Baseline Check | Status | Verification Observations |
|---|---|---|---|
| 1 | **Search Execution & Genuine Provider Results** | Verified | Tested `TN34MA8562`, returning genuine classification, RTO attribution, and format validation without synthetic padding. |
| 2 | **Investigation Save & Reopen** | Verified | Saved search result generates canonical `inv_*` investigation ID in MongoDB and reloads with accurate count metrics. |
| 3 | **Media View Persistence Across Refresh** | Verified | Extracted media records retain stable IDs and parent linkages across query hydration. |
| 4 | **Neo4j Graph Persistence & Scoped Expansion** | Verified | Investigation graph persists nodes with `investigation_id` scoping; 1-hop expansions honor isolation without leaking global nodes. |
| 5 | **Vehicle Plate Syntax vs Live Registry** | Partially Verified (Enhanced needed) | Syntax parser correctly flags `CONFIG_REQUIRED` for live VAHAN API; needs official registry adapter + ANPR pipeline integration. |
| 6 | **Authorized Video Ingestion & Sightings** | Missing / To Implement | Video decoding and ANPR pipeline was absent. OpenCV, NumPy, and Tesseract OCR installed; needs camera catalog, video ingestion, and review workflow. |
| 7 | **Geospatial Observation Fidelity** | Verified | Coordinates and location observations retain provider attribution and UTC timestamps without synthetic travel paths. |
| 8 | **Investigation Cross-Tenant & Cross-Investigation Isolation** | Verified | Evidence, entities, and Neo4j subgraphs do not leak between different investigations or tenants. |

---

## Implementation Plan

1. **Camera Evidence & ANPR Pipeline (`app.modules.camera_evidence`)**:
   - Camera source catalog supporting documented public transport open data.
   - Bounded video frame extraction & plate candidate region localization with OpenCV.
   - Text extraction with Tesseract OCR (`--psm 7`).
   - 6 explicit match states: `NO_MATCH`, `POSSIBLE_MATCH`, `CANDIDATE_MATCH`, `HUMAN_CONFIRMED`, `HUMAN_REJECTED`, `INCONCLUSIVE`.
   - Human review confirmation/rejection workflow.
2. **Vehicle Registration Official Adapter**:
   - Official VAHAN / mParivahan registry client with truthful configuration/credential handling.
   - Strict separation of syntax parsing vs official live lookup.
3. **Geo Intelligence Sightings**:
   - Discrete, source-backed camera sighting locations linked to timeline and graph.
4. **Universal Engine & UI Refactoring**:
   - Clue-to-clue follow-ups for vehicle targets.
   - Streamlined investigator UI with unified search, dedicated vehicle/camera review section, and images/videos first-class viewer.
