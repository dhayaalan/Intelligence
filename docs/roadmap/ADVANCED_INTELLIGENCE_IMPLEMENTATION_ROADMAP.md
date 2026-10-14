# Strategic Advanced Intelligence Implementation Roadmap

**Repository:** `/home/songoku/Pictures/Intelligence`  
**Classification:** Phased Execution & Engineering Architecture Plan  
**Target Architecture:** Modular, NIST SP 800-207 Zero-Trust, Defense-Grade OSINT/CTI  
**Effort Standard:** Relative Engineering Complexity (Person-Weeks & Story Points, No Invented Calendar Dates)

---

## 1. Phased Implementation Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 0: Operational Correctness & Integrity Baseline                   │
│ • Remove misleading simulated fallback data in legacy providers         │
│ • Expose collector health and rate-limit diagnostics in UI             │
│ • Lock down VA/PT Scope Permit gates and fail-closed egress             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Core Investigation Quality & Threat Prioritization             │
│ • CISA KEV & FIRST EPSS real-time vulnerability enrichment             │
│ • News wire syndication vs. independent corroboration scoring           │
│ • Multi-stage explainable query pivoting architecture                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Containerized VA/PT Workers & Threat Intelligence Interop      │
│ • Ephemeral, non-root runner containers for Nuclei, Nikto, Subfinder    │
│ • Historical passive DNS and infrastructure timeline integration        │
│ • STIX 2.1 / TAXII 2.1 intelligence bundle import and export            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Advanced Social & Multimodal Narrative Intelligence            │
│ • Multi-platform CIB lexical and temporal cluster analysis              │
│ • Server-side video keyframe sampling and perceptual dHash matching     │
│ • Authenticated collector token rotation and quota management           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Unified Knowledge Graph, Alerting & Case Operations            │
│ • Cross-module entity disambiguation and graph persistence              │
│ • Material change detection and investigative watchlists                │
│ • Reproducible case export dossiers and chain-of-custody tracking       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase 0 — Operational Correctness & Integrity Baseline

### Objective
Ensure that every status presented in the application reflects authentic execution, eliminating synthetic fixtures from live discovery paths and surfacing real provider health.

### Key Deliverables:
1. **Purge Synthetic Data Fallbacks in Legacy OSINT:**
   - Deprecate hardcoded CVE and port arrays in `backend/app/modules/osint/providers/shodan.py` and align with `tool_executor.py` (`CONFIG_REQUIRED` status when `SHODAN_API_KEY` is missing).
2. **Collector Diagnostics & Quota Transparency:**
   - Update Social and News search APIs to return structured provider statuses (`HEALTHY`, `RATE_LIMITED`, `ACCESS_DENIED`, `TIMEOUT`) and display real-time degradation banners in the UI.
3. **Audit Verification Pipeline:**
   - Maintain the automated `verify_tools.py` script as a mandatory CI barrier preventing unverified catalog entries.

### Dependencies & Prerequisites: None.
### Estimated Effort: 2 Person-Weeks (1 Sprint)
### Acceptance Criteria:
- When a search is conducted without an external API key, the system explicitly returns `CONFIG_REQUIRED` or lists missing credentials without returning simulated or hardcoded IP/CVE records.
- Automated tests pass with 100% genuine assertion checks.

---

## 3. Phase 1 — Core Investigation Quality & Threat Prioritization

### Objective
Provide high-value intelligence enhancements that reuse existing modular infrastructure with zero disruption to core architecture.

### Key Deliverables:
1. **[CTI-01] CISA KEV & FIRST EPSS Vulnerability Enrichment:**
   - Integrate daily background caching of CISA KEV JSON.
   - Implement real-time client for FIRST EPSS API to display 30-day exploit probabilities on all detected CVEs.
2. **[NEWS-01] Wire Syndication & Independent Corroboration Engine:**
   - Implement text-minhash clustering to group identical wire releases.
   - Display explicit corroboration statuses: `CORROBORATED`, `SINGLE_SOURCE_REPEATED`, `CONTRADICTED`, `UNVERIFIED`.
3. **[OSINT-03] Collection Completeness Index (CCI):**
   - Provide an audit score on every search indicating what percentage of target categories were successfully probed.

### Dependencies & Prerequisites: Phase 0 completed.
### Estimated Effort: 3 Person-Weeks (1.5 Sprints)
### Acceptance Criteria:
- Vulnerability lookup on weaponized CVEs (e.g. `CVE-2023-48795`) shows `in_cisa_kev: True` and real EPSS score.
- News search on syndicated wire events groups affiliate republications into a single story cluster with an honesty disclaimer.

---

## 4. Phase 2 — Containerized VA/PT Workers & Threat Intelligence Interop

### Objective
Harden active reconnaissance execution by isolating scanner engines from the core application host and enabling enterprise threat data sharing.

### Key Deliverables:
1. **[CTI-03] Ephemeral Runner Container Worker Architecture:**
   - Build a non-root, capability-dropped scanner runner container (`sentinel-scanner-runner`) containing installed binaries for `nuclei`, `subfinder`, `nikto`, `testssl.sh`, `naabu`, and `amass`.
   - Implement a Celery / Redis task dispatcher that passes signed `ScopePermit` tokens and collects structured JSON outputs.
2. **[OSINT-02] Historical Passive DNS & Certificate Timelines:**
   - Integrate CIRCL Passive DNS / AlienVault OTX historical DNS API into the unified domain investigation workflow.
3. **[CTI-02] STIX 2.1 & TAXII 2.1 Intelligence Exchange:**
   - Implement Python `stix2` serializer for findings, observables, and investigations.

### Dependencies & Prerequisites: Redis instance, Docker socket or Kubernetes cluster credentials.
### Estimated Effort: 6 Person-Weeks (3 Sprints)
### Acceptance Criteria:
- Running an active Nuclei scan executes inside a separate container, completes without error, and streams normalized findings back to the main database without installing binaries on the FastAPI host.
- Case exports can be downloaded as valid STIX 2.1 bundles verified against OASIS JSON schemas.

---

## 5. Phase 3 — Advanced Social & Multimodal Narrative Intelligence

### Objective
Expand social intelligence collection resilience, cross-platform narrative tracking, and forensic media verification.

### Key Deliverables:
1. **[SOC-01] Cross-Platform Coordinated Inauthentic Behavior (CIB) Clustering:**
   - Extend CIB engine to evaluate lexical n-gram similarity, unshortened URL propagation, and temporal distribution patterns across Bluesky, Telegram, Reddit, and Mastodon.
2. **[NEWS-02] Server-Side Video Keyframe Extraction & Media Forensics:**
   - Integrate lightweight server-side video sampling (`ffmpeg`) to extract keyframes from MP4/video URLs and compute 64-bit dHash perceptual sequences.
3. **[SOC-02] Managed Credential Vault for Social Collectors:**
   - Provide secure tenant-isolated storage for Reddit OAuth2 client keys, Telegram API IDs, and Bluesky session tokens with automatic token refresh.

### Dependencies & Prerequisites: Phase 1 & Phase 2 completed.
### Estimated Effort: 5 Person-Weeks (2.5 Sprints)
### Acceptance Criteria:
- A coordinated link campaign across Bluesky and Telegram is detected and displayed in a synchronized timeline.
- A recycled video URL is identified by matching its sampled keyframe dHash against previously indexed dispatches.

---

## 6. Phase 4 — Unified Knowledge Graph, Alerting & Case Operations

### Objective
Unify cross-module investigations into an auditable, multi-hop knowledge graph with scheduled monitoring and automated alerting.

### Key Deliverables:
1. **[CORR-01] Unified Entity Disambiguation & Cross-Module Graph:**
   - Correlate entities across OSINT, Threat Intel, Social Intel, and News Intel into a persistent, multi-hop graph while respecting tenant privacy boundaries.
2. **Scheduled Topic Watchlists & Material Change Alerts:**
   - Implement recurring cron/background polling for tracked keywords, domains, and vulnerabilities with email/webhook notification.
3. **Forensic Evidence Dossiers & Reproducible PDF/JSON Export:**
   - Generate cryptographically hashed evidence packets with complete chain-of-custody metadata, tool versions, and collection timestamps.

### Dependencies & Prerequisites: Phases 0–3 completed.
### Estimated Effort: 4 Person-Weeks (2 Sprints)
### Acceptance Criteria:
- Opening an entity node in Graph Studio visualizes connections across News, Social, and Threat scans.
- Watchlist background job alerts an investigator when a tracked domain changes its DNS A record or is mentioned in a new regional news report.

---

## 7. Resource & Dependency Summary

| Phase | Duration (Effort) | Primary Skills Required | Key External Dependencies |
| :--- | :---: | :--- | :--- |
| **Phase 0** | 2 Weeks | Backend Python, React UI | Local codebase only |
| **Phase 1** | 3 Weeks | Security Data Engineering, CTI | CISA KEV JSON, FIRST EPSS API |
| **Phase 2** | 6 Weeks | DevOps, Docker/K8s, Network Security | Redis, Docker Engine, STIX2 |
| **Phase 3** | 5 Weeks | Video Forensics, Media Forensics | ffmpeg, Pillow, OAuth2 Providers |
| **Phase 4** | 4 Weeks | Graph Databases, Full-Stack SaaS | MongoDB / Neo4j, Celery Beat |
| **Total** | **20 Weeks** | **Cross-Functional Team (3–4 Engineers)** | **Robust, Defense-Grade Production System** |
