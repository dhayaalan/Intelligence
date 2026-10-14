# Advanced Intelligence Feature Catalog & Capability Specification

**Repository:** `/home/songoku/Pictures/Intelligence`  
**Classification:** Strategic Engineering Backlog  
**Architecture:** Modular, Investigator-First, Zero-Trust (NIST SP 800-207)

---

## 1. Catalog Overview & Taxonomy

This catalog details the prioritized feature portfolio required to elevate the Sential Intelligence Platform into a defense-grade investigation environment.

### Priority Structure:
- **P0 (Critical Baseline):** Zero-defect foundation, authentic data provenance, security containment, and eliminating synthetic/broken behaviors.
- **P1 (High-Value Capability):** Essential analytical differentiators directly serving investigative workflows.
- **P2 (Operational Expansion):** Scalability, deep feeds, specialized adapters, and automated correlation.
- **P3 (Long-Term Strategic):** Advanced automated graph reasoning, external intelligence sharing (STIX/TAXII), and enterprise integrations.

---

## 2. Open Source Intelligence (OSINT) & Attack Surface Discovery

### [OSINT-01] Multi-Stage Query Pivoting & Discovery Traceability
- **Status:** `PARTIAL` (Search orchestration detects targets, but multi-hop pivoting is manual).
- **Existing Implementation:** `backend/app/search/orchestrator.py`, `backend/app/modules/tool_executor.py`.
- **Investigator Problem Solved:** Investigators often find an initial artifact (e.g., an email or IP) and must manually execute 5–10 subsequent queries to discover linked domains, certificates, handles, and organization aliases.
- **Verified Gap:** The current search orchestrator runs parallel initial queries but does not automatically extract high-confidence entity pivots (e.g., registrant email -> other registered domains) into an explainable exploration graph.
- **Proposed Behavior:** When an investigator inspects a result, the system extracts high-confidence pivots with traceable provenance, allowing one-click execution of secondary expansion queries with automated deduplication and parent-child link tracking.
- **External Research Sources:** MITRE ATT&CK Reconnaissance (T1596, T1590), Maltego Transform Architecture, SpiderFoot event-driven architecture.
- **Dependencies:** Entity extraction normalization, unified evidence graph.
- **Complexity:** `M` | **Investigator Value:** `HIGH` | **Priority:** `P1`
- **Phase:** Phase 1 | **Prerequisites:** None.

---

### [OSINT-02] Historical DNS, Passive SSL/TLS & Infrastructure Timeline
- **Status:** `PARTIAL` (Current CT logs (`crtsh_engine.py`) and DNS probers (`dns_engine.py`) return current/recent records).
- **Existing Implementation:** `backend/app/modules/threat_intelligence/engines/engines/crtsh_engine.py`, `backend/app/modules/tool_executor.py`.
- **Investigator Problem Solved:** Adversaries frequently rotate DNS A records, use fast-flux IP pools, and cycle TLS certificates. Point-in-time checks miss decommissioned or transient infrastructure.
- **Verified Gap:** Lack of historical IP-to-domain and domain-to-nameserver timelines across a unified time axis.
- **Proposed Behavior:** Integrate passive DNS repositories (e.g., SecurityTrails API, CIRCL Passive DNS, or AlienVault OTX historical DNS) to display chronological IP-resolution timelines with first-seen and last-seen timestamps.
- **External Research Sources:** CIRCL Passive DNS API standard, RFC 8499 (DNS Terminology), ICANN Security and Stability Advisory Committee (SSAC).
- **Dependencies:** Egress controller, external API credential vault.
- **Complexity:** `M` | **Investigator Value:** `HIGH` | **Priority:** `P1`
- **Phase:** Phase 2 | **Prerequisites:** OSINT-01.

---

### [OSINT-03] Source Coverage & Collection Completeness Telemetry
- **Status:** `PARTIAL` (Provider status reporting implemented in `backend/app/api/v1/search.py`, but lacks statistical coverage scoring).
- **Existing Implementation:** `backend/app/api/v1/search.py`, `backend/app/modules/social_media_intelligence/service.py`.
- **Investigator Problem Solved:** Analysts risk concluding an entity does not exist simply because a rate-limited or unauthenticated provider silently returned 0 results.
- **Verified Gap:** Search responses list results but do not display an aggregate collection confidence score indicating what percentage of intended target categories were successfully probed.
- **Proposed Behavior:** Calculate an explicit Collection Completeness Index ($CCI = \frac{\text{Successful Queries}}{\text{Attempted Queries}} \times \text{Category Weighting}$) and render warnings when key platforms were unprobed or throttled.
- **Complexity:** `S` | **Investigator Value:** `HIGH` | **Priority:** `P0`
- **Phase:** Phase 0 | **Prerequisites:** None.

---

## 3. Cyber Threat Intelligence (CTI) & Defensive Vulnerability Assessment

### [CTI-01] CISA KEV & FIRST EPSS Multi-Dimensional Vulnerability Prioritization
- **Status:** `MISSING` (Current CVE lookup in `tool_executor.py` queries NVD for CVSS scores, but lacks exploitation telemetry).
- **Existing Implementation:** `backend/app/modules/tool_executor.py` (`_run_cve_intelligence`).
- **Investigator Problem Solved:** Prioritizing vulnerabilities based purely on CVSS severity (e.g. CVSS 9.8) leads to alert fatigue on unexploitable edge services while missing actively weaponized lower-CVSS flaws.
- **Verified Gap:** No integration with CISA Known Exploited Vulnerabilities (KEV) catalog or FIRST Exploit Prediction Scoring System (EPSS).
- **Proposed Behavior:** Enrich every detected CVE with:
  1. `in_cisa_kev`: Boolean flag indicating verified in-the-wild exploitation.
  2. `epss_score`: Real-time probability ($0.0 - 1.0$) of exploitation in the next 30 days from FIRST EPSS API.
  3. `composite_risk_score`: Mathematical combination of CVSS v3.1/v4, EPSS, and asset exposure.
- **External Research Sources:**
  - CISA KEV Catalog API: `https://www.cisa.gov/known-exploited-vulnerabilities-catalog`
  - FIRST EPSS Data & API: `https://api.first.org/epss/`
  - FIRST CVSS v4.0 Specification: `https://www.first.org/cvss/v4.0/specification-document`
- **Dependencies:** Outbound caching for daily KEV JSON ingestion.
- **Complexity:** `S` | **Investigator Value:** `CRITICAL` | **Priority:** `P0`
- **Phase:** Phase 1 | **Prerequisites:** None.

---

### [CTI-02] STIX 2.1 & TAXII 2.1 Threat Indicator Ingestion & Export
- **Status:** `MISSING` (Internal IOCs are stored in custom JSON schemas without standardized STIX 2.1 serialization).
- **Existing Implementation:** `backend/app/modules/threat_intelligence/manifest.py`, `backend/app/evidence/models.py`.
- **Investigator Problem Solved:** Threat investigators cannot seamlessly ingest indicator feeds from external ISACs, national CERTs, or OpenCTI / MISP instances without manual translation.
- **Verified Gap:** Inability to import or export STIX 2.1 Bundles containing `indicator`, `attack-pattern`, `malware`, `threat-actor`, and `relationship` SDOs (STIX Domain Objects).
- **Proposed Behavior:** Implement STIX 2.1 serializer/deserializer conforming to OASIS STIX 2.1 specification, enabling drag-and-drop bundle ingestion and structured case exports.
- **External Research Sources:** OASIS STIX v2.1 Specification, OASIS TAXII v2.1 Specification, OpenCTI STIX2 Python Client.
- **Dependencies:** Python `stix2` library, evidence correlation engine.
- **Complexity:** `L` | **Investigator Value:** `HIGH` | **Priority:** `P2`
- **Phase:** Phase 2 | **Prerequisites:** CTI-01.

---

### [CTI-03] Containerized Worker Isolation for Active Reconnaissance
- **Status:** `PLANNED` (Architecturally designed in `docs/roadmap/VA_PT_ISOLATION_DESIGN.md`; host currently lacks CLI scanner binaries).
- **Existing Implementation:** `backend/app/modules/threat_intelligence/engines/scope_enforcer.py`.
- **Investigator Problem Solved:** Executing security tools (`nuclei`, `nikto`, `testssl.sh`, `subfinder`) directly on the backend host introduces command injection risks, resource exhaustion, and privilege escalation vulnerabilities.
- **Verified Gap:** The current host operating system has zero scanner binaries installed; scanners currently run in in-process fallbacks.
- **Proposed Behavior:** Deploy isolated, unprivileged, non-root runner containers orchestrated via Celery / Redis. The main API dispatches signed Scope Permits; the worker executes the job in an ephemeral container with strict CPU/memory limits and dedicated outbound network routes.
- **External Research Sources:** NIST SP 800-190 (Application Container Security Guide), CIS Docker Benchmark.
- **Dependencies:** Redis message broker, Docker daemon socket / Kubernetes Job controller.
- **Complexity:** `XL` | **Investigator Value:** `CRITICAL` | **Priority:** `P1`
- **Phase:** Phase 2 | **Prerequisites:** VA/PT Scope Enforcer (complete).

---

## 4. Social Media Intelligence (SOCMINT)

### [SOC-01] Multi-Platform Coordinated Amplification & Botnet Correlation
- **Status:** `PARTIAL` (CIB detection exists for single search results within 60s; lacks historical account graph correlation).
- **Existing Implementation:** `backend/app/modules/social_media_intelligence/engines/cib_engine.py`, `backend/app/modules/social_media_intelligence/engines/credibility_engine.py`.
- **Investigator Problem Solved:** Coordinated disinformation networks amplify narratives across multiple accounts with subtle delays (2–5 minutes) and minor lexical permutations to evade simplistic threshold detectors.
- **Verified Gap:** Current CIB engine uses strict exact-URL and sub-60-second burst matching. It does not measure semantic similarity, shared URL shortener redirects, or account registration clustering.
- **Proposed Behavior:** Introduce Jaccard n-gram lexical similarity, unshortened URL canonicalization, and inter-post temporal distribution analysis. Render an explainable coordination score with explicit false-positive caveats.
- **External Research Sources:** Stanford Internet Observatory CIB Methodology, EU DisinfoLab Forensic Playbooks.
- **Dependencies:** Multimodal engine, canonical URL resolver.
- **Complexity:** `M` | **Investigator Value:** `HIGH` | **Priority:** `P1`
- **Phase:** Phase 3 | **Prerequisites:** None.

---

### [SOC-02] Authenticated Collector Resilience & Rate-Limit Telemetry
- **Status:** `PARTIAL` (Circuit breakers and backoff implemented in `crawler_engine.py`, but collectors lack managed OAuth2 token rotation).
- **Existing Implementation:** `backend/app/modules/social_media_intelligence/crawler_engine.py`, `backend/app/modules/social_media_intelligence/collectors/`.
- **Investigator Problem Solved:** When collecting social media evidence during an active investigation, unauthenticated endpoints hit platform rate limits (e.g. Reddit HTTP 429), dropping evidence midway through a case.
- **Verified Gap:** Collectors lack tenant-isolated token vaults for rotating API credentials and surfacing remaining request quotas to the user interface.
- **Proposed Behavior:** Integrate an API quota telemetry monitor that records `x-ratelimit-remaining`, `x-ratelimit-reset`, and provides explicit degradation banners in the UI instead of failing silently.
- **External Research Sources:** Bluesky AT Protocol Rate Limits (`bsky.network/docs/rate-limits/`), Mastodon API Rate Limiting Docs.
- **Dependencies:** Redis cache for token buckets, Egress controller.
- **Complexity:** `M` | **Investigator Value:** `HIGH` | **Priority:** `P0`
- **Phase:** Phase 1 | **Prerequisites:** None.

---

## 5. News Intelligence & Multimodal Forensics

### [NEWS-01] Claim-Level Verification Matrix & Corroboration Engine
- **Status:** `PARTIAL` (Deterministic claim extraction exists in `service.py`, but cross-publisher corroboration scoring is basic).
- **Existing Implementation:** `backend/app/modules/news_intelligence/service.py`, `backend/app/modules/news_intelligence/search_engine.py`.
- **Investigator Problem Solved:** Investigators are overwhelmed by hundreds of syndicated duplicate articles repeating the same unverified press release, misinterpreting volume as independent corroboration.
- **Verified Gap:** No automated syndication and wire-copy deduplication to distinguish 20 independent investigations from 20 newspapers republishing the same Reuters/AP wire copy.
- **Proposed Behavior:** Implement text-minhash and wire attribution extraction. Provide a Claim Verification Matrix classifying claims as:
  - `CORROBORATED`: Two or more independent (non-syndicated) publishers with primary attribution.
  - `SINGLE_SOURCE_REPEATED`: High volume of dispatches, but all tracing back to a single originating statement.
  - `CONTRADICTED`: Conflicting statements identified in peer-tier publishers.
  - `UNVERIFIED`: Secondary reporting with no identifiable primary source.
- **External Research Sources:** GDELT 2.0 Global Entity Graph Documentation, Media Cloud Open Source Narrative Framework.
- **Dependencies:** Multilingual transliteration engine, article extractor.
- **Complexity:** `L` | **Investigator Value:** `CRITICAL` | **Priority:** `P0`
- **Phase:** Phase 1 | **Prerequisites:** None.

---

### [NEWS-02] Cross-Platform Video Keyframe Extraction & Media Forensics
- **Status:** `PARTIAL` (YouTube subtitle and oEmbed metadata extraction functional; video frame perceptual hashing missing).
- **Existing Implementation:** `backend/app/modules/social_media_intelligence/collectors/youtube.py`, `backend/app/modules/news_intelligence/multimodal_engine.py`.
- **Investigator Problem Solved:** Disinformation campaigns frequently reuse old combat, disaster, or protest footage with misleading modern captions.
- **Verified Gap:** The current multimodal engine extracts 64-bit dHash for still images, but cannot sample keyframes from video links or MP4 streams.
- **Proposed Behavior:** Implement lightweight server-side video keyframe sampling (sampling 1 frame per 10 seconds or scene change) and compute 64-bit dHash sequences to detect recycled historical footage.
- **External Research Sources:** Google Fact Check Tools API, InVID-WeVerify Media Forensics Guidelines.
- **Dependencies:** `ffmpeg` / `imageio` in isolated worker environment.
- **Complexity:** `L` | **Investigator Value:** `HIGH` | **Priority:** `P2`
- **Phase:** Phase 3 | **Prerequisites:** CTI-03 (Worker Isolation).

---

## 6. Cross-Module Evidence Correlation & Investigation Graphs

### [CORR-01] Unified Entity Resolution & Multi-Hop Relationship Graph
- **Status:** `PARTIAL` (Graph Studio renders nodes in-memory; lacks cross-investigation entity disambiguation).
- **Existing Implementation:** `frontend/src/features/graph/GraphStudioComponent.tsx`, `backend/app/entities/`.
- **Investigator Problem Solved:** An entity (e.g. an organization or malware author) discovered in News Intelligence is not automatically correlated with the same domain or email discovered in an OSINT search or Social Intelligence investigation.
- **Verified Gap:** Entities are siloed per investigation record; no global graph resolution linking identical hashes, canonical domains, or cryptographic signatures across tenant cases.
- **Proposed Behavior:** Implement a deterministic Entity Disambiguation Service that links identical observables across cases while preserving tenant isolation boundaries.
- **Dependencies:** MongoDB entity indexes, evidence models.
- **Complexity:** `L` | **Investigator Value:** `HIGH` | **Priority:** `P1`
- **Phase:** Phase 2 | **Prerequisites:** OSINT-01.

---

## 7. Comparative Feature Prioritization Matrix

| Feature ID | Domain | Complexity | Value | Security Impact | Priority | Recommended Phase |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **CTI-01** | Threat Intel | `S` | Critical | Low | **P0** | Phase 1 (Core Integrity) |
| **OSINT-03**| OSINT | `S` | High | Low | **P0** | Phase 1 (Core Integrity) |
| **NEWS-01** | News Intel | `L` | Critical | Low | **P0** | Phase 1 (Core Integrity) |
| **SOC-02** | Social Intel | `M` | High | Medium | **P0** | Phase 1 (Core Integrity) |
| **CTI-03** | Threat Intel | `XL` | Critical | Critical | **P1** | Phase 2 (Hardening) |
| **OSINT-01**| OSINT | `M` | High | Low | **P1** | Phase 2 (Pivoting) |
| **OSINT-02**| OSINT | `M` | High | Low | **P1** | Phase 2 (Passive DNS) |
| **SOC-01** | Social Intel | `M` | High | Low | **P1** | Phase 3 (Social Expansion) |
| **CORR-01** | Evidence Graph| `L` | High | Medium | **P1** | Phase 3 (Correlation) |
| **CTI-02** | Threat Intel | `L` | High | Low | **P2** | Phase 4 (STIX/TAXII) |
| **NEWS-02** | News Intel | `L` | High | Low | **P2** | Phase 4 (Video Forensics)|
