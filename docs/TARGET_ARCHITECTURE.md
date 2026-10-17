# Target Architecture & Migration Plan

**Date:** October 17, 2026  
**Repository:** `/home/songoku/Pictures/Intelligence`  
**Branch:** `feat/safe-codebase-refactor-investigator-ui`  

---

## 1. Architectural Principles

1. **Clear Separation of Concerns:** Core platform services handle auth, tenancy, and audit, without embedding provider-specific business logic.
2. **Provider Modularity:** Intelligence providers conform to a declarative interface (`search(context) -> NormalizedModuleResult`), reporting transparent 10-state lifecycles.
3. **First-Class Media Intelligence:** Images and Videos are extracted, normalized, linked to source provenance, and surfaced directly in the primary search workspace.
4. **Dual Persistence with Singular Ownership:**
   - **MongoDB:** Authoritative system of record for entities, investigations, source evidence, and media items.
   - **Neo4j:** Authoritative graph engine for multi-hop traversals, relationship queries, and visual graph expansion.
5. **Investigator-First Ergonomics:** High readability (14-16px font), straightforward low-click navigation, clear visual hierarchy, accessible color contrasts, and zero fabricated claims.

---

## 2. Conceptual Layers

```
+-----------------------------------------------------------------------------------+
|                           API & Presentation Layer                                |
|  - Fast, Typed FastAPI Endpoints (/search, /investigations, /entities, /media)   |
|  - React/TypeScript Frontend with TanStack React Query                            |
|  - Investigator-First UI: Overview, All, Profiles, Images, Videos, News, Graph    |
+-----------------------------------------------------------------------------------+
                                         │
+-----------------------------------------------------------------------------------+
|                        Intelligence Execution Layer                               |
|  - Universal TargetClassifier (15 canonical targets + explicit prefixes)         |
|  - Query Normalization & Ambiguity Guard                                          |
|  - Complete Relevant-Source Discovery & 10-State Provider Tracking                |
|  - Multi-Module Concurrent Dispatch (OSINT, Threat, News, Social, Geo)            |
|  - Bounded Recursive Pivoting (loop prevention, depth/count limits)               |
+-----------------------------------------------------------------------------------+
                                         │
+-----------------------------------------------------------------------------------+
|                       Evidence & Correlation Layer                                |
|  - Correlation Engine (deduplication, source ranking, clustering)                 |
|  - Media Normalization Pipeline (Images & Videos extraction, provenance binding)  |
|  - Entity Resolution & Disambiguation                                            |
|  - Truthful Assurance Scoring (Collection Completeness Index)                     |
+-----------------------------------------------------------------------------------+
                                         │
+-----------------------------------------------------------------------------------+
|                             Persistence Layer                                     |
|  - MongoDB Repositories: EntityRepo, InvestigationRepo, EvidenceRepo, MediaRepo   |
|  - Neo4j Graph Service: Constraints, Node/Edge Upserts, 1-Hop Expansion           |
|  - In-Memory & Redis Hot Caching                                                  |
+-----------------------------------------------------------------------------------+
                                         │
+-----------------------------------------------------------------------------------+
|                              Platform Core                                        |
|  - Authentication & JWT Token Management                                          |
|  - Multi-Tenant Isolation & SaaS Licensing Entitlements                           |
|  - Role-Based Access Control (RBAC)                                               |
|  - Asynchronous Job Execution & Event Bus                                         |
|  - Structured Audit Logging                                                       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Incremental Migration Plan

| Stage | Focus Area | Actions | Safety Gate |
|---|---|---|---|
| **Stage 1** | Baseline & Contracts | Audit completed, 188 backend tests verified passing, frontend typechecked. | Baseline snapshot verified. |
| **Stage 2** | Media Data Models | Add `MediaRecord` to `schemas.py`, implement media extraction in `orchestrator.py` & providers. | Backend tests pass, zero regressions. |
| **Stage 3** | Frontend Media Components | Implement `ImagesTab`, `VideosTab`, `MediaViewerModal` with thumbnail fallbacks, source links, and metadata. | Frontend compiles cleanly with `tsc --noEmit`. |
| **Stage 4** | Investigator-First UI | Refactor `SearchPage.tsx` tab header into required compact standard, upgrade typography to 14-16px, improve evidence cards. | Manual & automated UI verification. |
| **Stage 5** | Search Code Cleanup | Decompose oversized render methods, remove duplicate helpers, update documentation. | Full regression suite passes 100%. |
