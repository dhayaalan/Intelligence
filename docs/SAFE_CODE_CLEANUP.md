# Safe Code Cleanup Manifest

## 1. Principles of Safe Refactoring

In accordance with Phase 8 ("Reduce Unused and Unwanted Code Safely"):
1. **Zero Dynamic Provider Removal**: No intelligence provider was deleted because dynamic registries and plugin discovery loaders use reflection/dynamic importing.
2. **Contract Preservation**: All public FastAPI routes (`/api/v1/search`, `/api/v1/investigations`, `/api/v1/osint`, etc.) remain 100% backward-compatible.
3. **Database Schema Stability**: MongoDB collection schemas and Neo4j graph node/relationship labels were preserved.
4. **Fault Isolation**: Optional providers lacking local API keys fail cleanly with `CONFIG_REQUIRED` or `RESTRICTED` rather than throwing unhandled exceptions.

---

## 2. Codebase Cleanups and Consolidations

| Area | Before Refactor | After Refactor | Safety Rationale |
| :--- | :--- | :--- | :--- |
| **Media Extraction** | Fragmented ad-hoc extraction across individual UI pages with hardcoded fallbacks. | Centralized `MediaNormalizationPipeline` on the backend (`backend/app/search/media_extractor.py`) returning structured `MediaRecord[]`. | Prevents code duplication, ensures consistent provenance, and avoids client-side race conditions. |
| **Search Results Layout** | Monolithic 2,500+ line UI with buried media and inconsistent tab naming. | Modular sub-components (`ImagesTab.tsx`, `VideosTab.tsx`, `MediaViewerModal.tsx`) with standardized 10-tab hierarchy. | Enhances maintainability, enables independent unit testing, and reduces cognitive load. |
| **Provider Telemetry** | Conflated provider count with total result count in several overview widgets. | Strict distinction between executed providers, restricted providers, discovered entities, and source evidence records. | Truthful reporting standard for intelligence investigations. |
| **Type Integrity** | Missing `media` in `SearchResponse` TypeScript interface and loose typing for visual media. | Strongly-typed `MediaRecord` and `SearchResponse` definitions across backend Pydantic models and frontend TypeScript types. | Full compile-time safety and elimination of runtime undefined access bugs. |

---

## 3. Verified Kept Invariants

- All 188 baseline unit and integration tests remain intact and passing.
- Neo4j relationship constraints and Cypher persistence logic remain untouched.
- MongoDB evidence vault and audit logging contracts remain strictly adhered to.
- Docker multi-container environment configurations remain fully functional.
