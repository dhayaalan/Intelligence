# Clue-to-Clue Investigation Platform Audit & Integrity Report

## Executive Summary

This comprehensive audit inspects the Sential / Intelligence investigation platform across all 11 evaluation criteria defined in the Master Implementation Specification. The audit evaluated source-code implementations, schema definitions, module execution pipelines, data provenance, provider telemetry, and real operational constraints.

The objective is to establish an investigator-first, evidence-driven multi-stage reconnaissance platform where any initial clue (phone, email, name, handle, vehicle registration, domain/IP, media asset, or location) can safely initiate an auditable, multi-hop investigation without synthetic hallucination, false certainty, or unverified claims.

---

## 1. Capability Classification Matrix

| Component / Subsystem | Status Category | Real Findings & Deficiencies | Required Remediation |
| :--- | :--- | :--- | :--- |
| **Search Intent & Identifiers** | **1. Implemented & Verified** | Email and phone exact search enforce RFC 5322 & E.164 normalization. Server-side verification strictly prevents fuzzy or semantic pollution. | Maintain zero-match integrity; enrich with actionable pivots and telecommunications metadata. |
| **Search Leads & Snapshot Statistics** | **7. Incorrect & Fabricated** | Snapshot metrics manufactured `potential_contradictions_count` (`2 if len(articles) > 3 else ...`) and forced `unverified_claims_count >= 1`. `investigative_leads` was statically hardcoded with dummy `EV-001`/`EV-002` references. | Remove hardcoded leads; calculate leads dynamically from evidentiary gaps, contradictory statements, and uncorroborated single-source claims. Report 0 contradictions when none exist. |
| **YouTube Video Intelligence** | **7. Incorrect & Fabricated** | `get_subtitles()` returned a hardcoded synthetic segment `"Official broadcast recording for video item..."`. Channel IDs were derived via regex over author names. Video `upload_date` defaulted to collection timestamp `datetime.now()`. | Remove synthetic subtitles. Return `TRANSCRIPT_UNAVAILABLE` when transcripts are not genuinely accessible. Separate publication timestamp from collection timestamp. Preserve authentic channel ID. |
| **Social Media Collectors** | **3 & 5. Connected but Deprecated / Unconfigured** | Facebook and Instagram collectors hardcode deprecated Meta Graph API `v18.0`. Lack of credentials logged as general success empty in some codepaths. | Migrate Meta Graph API version to configurable `META_GRAPH_API_VERSION` (default `v21.0`). Truthful provider execution states (`AUTH_REQUIRED`, `CONFIG_REQUIRED`, `SUCCESS_EMPTY`). |
| **News Article & Image Integrity** | **2. Partially Functional** | Dossier compiler supports OpenGraph image extraction, but missing or generic articles previously risked array-index thumbnail reuse. | Strictly decouple article IDs from images. Guarantee unique canonical URLs and render neutral SVG placeholder states when no authentic publisher hero image is verified. |
| **Geo Intelligence & Location History** | **4. Missing as Dedicated Engine** | `GEO INTELLIGENCE` scope only mapped to `news_intelligence` and `osint`. No dedicated geographic observation model, temporal range filters (7d, 30d, 3m, 6m, 12m, 3y, 5y, custom), or authorized location import pipeline. | Build a dedicated `GeoIntelligenceService` and observation schema. Support authorized location imports (JSON/CSV/GPX/KML), coordinate bounds, and honest non-interpolated travel observations. |
| **Vehicle Registration Strategy** | **4. Missing** | No dedicated vehicle plate resolution adapter or jurisdiction parser existed in the codebase. | Implement a dedicated `VehicleIntelligenceAdapter` with plate syntax validation, jurisdiction parsing, and clear reporting when government/telecom authority databases are restricted/unconfigured. |
| **Multi-Stage Clue-to-Clue Engine** | **3. Present as Metadata but Not Executed** | `PivotDiscoveryEngine` only returned proposed candidate pivots as static search response metadata. No automated, bounded multi-hop execution occurred. | Build an asynchronous, bounded multi-stage investigation engine that accepts any starting clue, normalizes it, runs stage 1, extracts candidate clues, safely schedules stage 2 follow-ups (depth limit, concurrency, idempotency, parent-child provenance), and correlates all findings. |
| **Relationship Graph (Neo4j)** | **1. Implemented & Verified** | Neo4j cluster is operational on bolt://localhost:7687. Bounded 1-hop expansion and Cypher injection protections verified. Frontend canvas previously suffered visual clutter. | Integrate compact dot-matrix canvas, branch-aware expand/collapse, shared-node deduplication, and rich relationship inspector displaying supporting evidence provenance. |
| **Provider Execution States** | **2. Partially Functional** | `ProviderResponse.status` only supported `"success"`, `"error"`, `"skipped"`. Failed configurations appeared as empty queries. | Implement truthful provider execution states: `SUCCESS`, `SUCCESS_EMPTY`, `PARTIAL`, `FAILED`, `CONFIG_REQUIRED`, `AUTH_REQUIRED`, `RATE_LIMITED`, `RESTRICTED`, `NOT_FOUND`, `SKIPPED`. |

---

## 2. Priority Remediation Roadmap

1. **Priority 1 — Data Integrity & Honesty (Phase 1 & 4)**:
   - Eliminate hardcoded subtitle generation in `youtube.py`; implement `TRANSCRIPT_UNAVAILABLE` status.
   - Decouple YouTube publication timestamp from collection timestamp; preserve genuine channel IDs.
   - Remove manufactured snapshot counts (`potential_contradictions_count`, `unverified_claims_count`) and hardcoded investigative leads in `orchestrator.py`.
   - Update Meta Graph API to configurable `v21.0`.

2. **Priority 2 — Universal Multi-Stage Clue-to-Clue Investigation Engine (Phase 2 & 3)**:
   - Implement `MultiStageInvestigationEngine` supporting automated, bounded follow-up job execution.
   - Enforce safe depth limits (hop depth 1 to 3), parent-child provenance tracking, and deduplication keys.
   - Implement dedicated strategies for: Email, Phone, Name/Alias, Username, Vehicle Registration, Domain/IP, and Media.

3. **Priority 3 — Dedicated Geo Intelligence & Location History (Phase 5)**:
   - Create `GeographicObservation` model with temporal uncertainty, coordinate provenance, and source attribution.
   - Support server-side temporal filters: `7d`, `30d`, `3m`, `6m`, `12m`, `3y`, `5y`, `custom`.
   - Implement authorized location import endpoint (`JSON`, `CSV`, `GPX`, `KML`).
   - Strictly prohibit synthetic travel route interpolation between non-continuous observations.

4. **Priority 4 — News Intelligence & Incident Correlation (Phase 6)**:
   - Ensure all query parameters (exact quotes, booleans, date ranges, countries, publishers) pass to retrieval services.
   - Correlate articles to incidents with evidentiary rigor: `DIRECTLY_SUPPORTED`, `SOURCE_REPORTED`, `POSSIBLE_ASSOCIATION`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE`.
   - Enforce stable canonical image references with neutral fallback placeholders.

5. **Priority 5 — Relationship Graph & Unified Investigator UX (Phases 7, 8, 9)**:
   - Maintain Neo4j relationship intelligence with epistemic provenance.
   - Polish modern, readable graph canvas with intelligent branch expansion and collapse.
   - Ensure the unified investigator workspace exposes all functional areas with complete evidentiary lineage.
