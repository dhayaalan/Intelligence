# Platform Architecture & Technical Baseline Audit

**Repository**: `/home/songoku/Pictures/Intelligence`  
**Classification**: Sensitive Investigative / Defence-Sector Standard  
**Date**: October 2026  
**Status**: Comprehensive Baseline Assessment  

---

## 1. Executive Summary

This audit assesses the readiness of the Intelligence Platform to handle high-assurance regional narrative monitoring, multimodal intelligence collection, operational security (OPSEC), and isolated vulnerability assessment and penetration testing (VA/PT).

The platform contains foundational modularity across **OSINT**, **Threat Intelligence**, **News Intelligence**, and **Social Media Intelligence**. Following recent refactorings, synthetic data fallbacks have been removed, tool executors enforce genuine API credential gates, and crawler engines support HTTP 429 backoff and checkpointing. 

However, critical architectural enhancements are required to address broader regional, operational security, and reconnaissance isolation mandates.

---

## 2. Component-by-Component Assessment

### 2.1 OSINT Tool Registry & Adapters
- **Current State**: Contains 345+ registered tool definitions and active tool runners in `backend/app/modules/tool_executor.py`. Probers verify genuine HTTP responses (e.g. GitHub, GitLab, Reddit, Keybase APIs). Missing credentials return honest `CONFIG_REQUIRED` states.
- **Gaps**: Lacks regional execution routing (executing OSINT queries through geographically designated egress profiles) and lacks automated transliteration/alias expansion for non-Latin script entities.

### 2.2 News Intelligence
- **Current State**: Fully deterministic engine querying Google News RSS, Bing News RSS, and GDELT DOC 2.0 API concurrently. Excised all synthetic article generation. Provides story clustering and ClaimReview schema modeling.
- **Gaps**: Geotargeting relies on coarse domain extensions (.in, .pk, .fr) without multi-region comparative orchestration. Does not provide side-by-side regional framing breakdowns (e.g., contrasting coverage across South India, North India, Pakistan, and Bangladesh).

### 2.3 Social Media Intelligence Crawlers
- **Current State**: `ResilientCrawlerEngine` implements token-bucket rate limiting, `Retry-After` parsing, full-jitter exponential backoff, cursor checkpointing, circuit breaking, and deduplication across Bluesky, Telegram, Reddit, Mastodon, and YouTube.
- **Gaps**:
  - Collectors lack region-specific search parameters and regional terminology mappings.
  - No fail-closed egress gateway mechanism for operations requiring specific geographic source perspectives.

### 2.4 Search, URL Ingestion & Multimodal Processing
- **Current State**: URL validation utilizes `NetworkSafety.validate_url()` with loopback and private IP blocking. YouTube embed extraction is operational.
- **Gaps**:
  - Image investigation lacks perceptual hashing (`pHash`/dHash) for near-duplicate media tracking.
  - No unified seed ingestion workflow accepting arbitrary multimodal seeds (article URL + image + social post + keywords) for joint pivot research.

### 2.5 Investigation, Case Management & Evidence Graph
- **Current State**: Multi-tenant database schema (`DataStore`) storing investigations, entities, relationships, evidence, and search histories. Graph relationships include `basis`, `methodology`, and `uncertainty_notes`.
- **Gaps**: Timelines do not distinguish between first publication time vs first collection time by the platform, risking erroneous original-source attribution.

### 2.6 Threat Intelligence & VA/PT Infrastructure
- **Current State**: `ThreatIntelligenceModule` orchestrates 34 security scanning engines. `validator.py` features `SSRFGuard` with comprehensive CIDR filtering (`BLOCKED_IP_NETWORKS`, `RFC1918_PRIVATE_NETWORKS`).
- **Gaps**:
  - Scanning engines execute in-process within backend worker threads rather than within isolated, non-root sandbox execution containers.
  - Active scanning lacks a mandatory cryptographically signed authorization scope gate and approval workflow for intrusive operations.
  - Attack telemetry and raw scanner output are stored adjacent to normal investigative evidence rather than in a segregated, read-only quarantine store.

### 2.7 OPSEC & Network Security
- **Current State**: Role-based access control (SUPER_ADMIN, TENANT_ADMIN, ANALYST, USER), JWT authentication, and basic secret masking.
- **Gaps**:
  - No formal egress gateway controller. Egress routing lacks fail-closed enforcement (allowing accidental direct network leakage if an authorized proxy/VPN disconnects).
  - Risk of untrusted content execution from scraped third-party HTML, SVGs, or media files.

---

## 3. Findings & Remediation Matrix

| Area | Severity | Finding | Operational Risk | Target Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **Regional Intel** | HIGH | Search queries lack regional lexicon and geographic facet comparison. | Inability to track cross-border propaganda, narrative divergence, or local sentiment nuances. | Build Region-Aware Search Orchestrator & Multi-Region Narrative Comparison Engine. |
| **Multimodal** | MEDIUM | Lack of perceptual image hashing and multi-seed ingestion. | Recycled visual disinfo paired with new text goes undetected. | Integrate perceptual image hashing (dHash/pHash) and multimodal seed pipeline. |
| **OPSEC** | HIGH | No fail-closed network egress routing for investigative requests. | Real investigator IP address and geolocation leaked to target servers if proxy fails. | Implement `EgressRouteController` with strict fail-closed enforcement and credential isolation. |
| **VA/PT Security**| HIGH | Security scanning runs in-process without strict target scope allowlists. | Risk of scanner pivoting into internal application subnets or scanning unauthorized third parties. | Build `VAPTScopeEnforcer` with strict allowlists, impact levels, and emergency kill-switch. |
| **Evidence** | MEDIUM | Platform collection time could be conflated with original publication time. | Analyst mistakenly assumes our collection time is the origin of a narrative. | Strict schema separation: `original_publication_timestamp` vs `collected_at_timestamp`. |

---

## 4. Architectural Verification Baseline

The backend test suite demonstrates complete stability:
```bash
pytest backend/tests/ -v
# Output: 48 passed, 0 failures (100% pass rate)
```
Frontend typecheck and build pass cleanly:
```bash
cd frontend && npm run typecheck && npm run build
# Output: tsc passed (0 errors), vite build completed
```

This clean operational foundation allows us to proceed directly into engineering the Regional Intelligence, Multimodal Discovery, OPSEC, and VA/PT Isolation layers.
