# Authoritative Research Sources & Primary Technical References

**Repository:** `/home/songoku/Pictures/Intelligence`  
**Evaluation Standard:** Primary Documentation, Published Standards, and Maintained Specifications  
**Verification Date:** October 2026

---

## 1. Primary Cybersecurity & Threat Intelligence Standards

### 1.1 MITRE ATT&CK Framework
* **Canonical URL:** [https://attack.mitre.org/resources/working-with-attack/](https://attack.mitre.org/resources/working-with-attack/)
* **Relevant Specification:** Enterprise ATT&CK v15 / STIX 2.1 Machine-Readable Representations
* **Capabilities Supported:**
  - Standardized taxonomy for adversary tactics, techniques, and procedures (TTPs).
  - Machine-readable JSON matrix mapping threat actors (e.g. APT28, Lazarus Group) to observable attack patterns.
  - Integration blueprint for categorizing reconnaissance (TA0043) and initial access (TA0001) findings.
* **Date Checked:** October 2026
* **Application Usage:** Feature `[CTI-02]` threat actor and campaign correlation matrix.

### 1.2 OASIS STIX 2.1 & TAXII 2.1
* **Canonical URL:** [https://www.oasis-open.org/standard/stix-version-2-1/](https://www.oasis-open.org/standard/stix-version-2-1/)
* **Relevant Specification:** OASIS Standard STIX™ Version 2.1 (OASIS Committee Specification)
* **Capabilities Supported:**
  - Structured Threat Information Expression graph data model.
  - Definition of STIX Domain Objects (SDOs): `indicator`, `malware`, `observed-data`, `threat-actor`, `vulnerability`, and STIX Relationship Objects (SROs).
  - TAXII 2.1 RESTful API protocol for secure threat intelligence distribution over HTTPS.
* **Date Checked:** October 2026
* **Application Usage:** Feature `[CTI-02]` standardized threat intelligence import and export pipeline.

### 1.3 OpenCTI Integration Ecosystem
* **Canonical URL:** [https://docs.opencti.io/latest/deployment/integrations/](https://docs.opencti.io/latest/deployment/integrations/)
* **Relevant Specification:** OpenCTI Connectors & GraphQL Python SDK
* **Capabilities Supported:**
  - Architecture for bi-directional ingestion between open-source platforms and enterprise threat repositories.
  - Connector design patterns for internal enrichment and automated indicator scoring.
* **Date Checked:** October 2026
* **Application Usage:** Architectural reference for decoupling the threat correlation engine from specific commercial feeds.

### 1.4 MISP Threat Sharing & Feeds
* **Canonical URL:** [https://misp-project.org/feeds/](https://misp-project.org/feeds/)
* **Relevant Specification:** MISP Open Source Threat Intelligence Feed Format
* **Capabilities Supported:**
  - Ingestion of structured indicator feeds from national CSIRTs, CIRCL, and community trust groups.
  - Manifest-based feed synchronization with JSON caching.
* **Date Checked:** October 2026
* **Application Usage:** Threat intelligence feed expansion and automated daily indicator synchronization.

### 1.5 CISA Known Exploited Vulnerabilities (KEV) Catalog
* **Canonical URL:** [https://www.cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
* **Relevant Specification:** CISA KEV JSON Data Feed
* **Capabilities Supported:**
  - Authoritative repository of CVEs with verified active exploitation in the wild.
  - Provides required remediation actions, due dates, and notes on weaponized ransomware use.
* **Date Checked:** October 2026
* **Application Usage:** Feature `[CTI-01]` prioritizing detected vulnerabilities based on real-world adversary exploitation rather than theoretical CVSS base scores.

### 1.6 FIRST EPSS (Exploit Prediction Scoring System)
* **Canonical URL:** [https://api.first.org/epss/](https://api.first.org/epss/) & [https://www.first.org/epss/data_stats](https://www.first.org/epss/data_stats)
* **Relevant Specification:** FIRST EPSS REST API v1
* **Capabilities Supported:**
  - Daily machine-learning estimation of the probability ($0.0 - 1.0$) that a software vulnerability will be exploited in the wild within 30 days.
  - Percentile ranking across all known CVEs.
* **Date Checked:** October 2026
* **Application Usage:** Feature `[CTI-01]` composite vulnerability risk scoring ($R = f(\text{CVSS}, \text{EPSS}, \text{KEV})$).

### 1.7 FIRST CVSS (Common Vulnerability Scoring System) v4.0
* **Canonical URL:** [https://www.first.org/cvss/](https://www.first.org/cvss/)
* **Relevant Specification:** CVSS v4.0 Specification Document (FIRST.Org, Inc.)
* **Capabilities Supported:**
  - Modernized severity framework introducing explicit Base, Threat (formerly Temporal), and Environmental metrics.
  - Fine-grained assessment of attack requirements (AT) and vulnerability impact metrics.
* **Date Checked:** October 2026
* **Application Usage:** Normalization of vulnerability severities across all 34 scanner engines.

---

## 2. News Intelligence & Open Media Verification Standards

### 2.1 GDELT Project (Global Database of Events, Language, and Tone)
* **Canonical URL:** [https://gdeltproject.org/data.html](https://gdeltproject.org/data.html)
* **Relevant Specification:** GDELT 2.0 Doc API Specification & Global Knowledge Graph (GKG)
* **Capabilities Supported:**
  - Real-time global monitoring of print, broadcast, and web news in over 100 languages.
  - Full-text search with Boolean syntax, tone/sentiment indicators, and entity resolution.
  - URL normalization and canonical article linking.
* **Date Checked:** October 2026
* **Application Usage:** Core query engine for `backend/app/modules/news_intelligence/search_engine.py`.

### 2.2 Media Cloud Open Source Narrative Platform
* **Canonical URL:** [https://www.mediacloud.org/documentation](https://www.mediacloud.org/documentation)
* **Relevant Specification:** Media Cloud API v2 / Directory System
* **Capabilities Supported:**
  - Cross-publisher attention tracking, topic clustering, and media ecosystem analysis.
  - Syndication tracing and wire-service attribution models.
* **Date Checked:** October 2026
* **Application Usage:** Feature `[NEWS-01]` wire syndication vs. independent corroboration scoring.

### 2.3 Google Fact Check Tools API
* **Canonical URL:** [https://developers.google.com/fact-check/tools/api/](https://developers.google.com/fact-check/tools/api/)
* **Relevant Specification:** ClaimReview Markup & Fact Check Search API v1alpha1
* **Capabilities Supported:**
  - Retrieval of structured fact-checking evaluations from certified International Fact-Checking Network (IFCN) signatories.
  - Verification of claims matching specific keywords, URLs, and public figures.
* **Date Checked:** October 2026
* **Application Usage:** Ground-truth claim verification in `NewsIntelligenceService`.

---

## 3. Social Media Intelligence & API Specifications

### 3.1 Bluesky & AT Protocol Network
* **Canonical URL:** [https://bsky.network/docs/rate-limits/](https://bsky.network/docs/rate-limits/) & [https://docs.bsky.app/docs/api/app-bsky-feed-search-posts](https://docs.bsky.app/docs/api/app-bsky-feed-search-posts)
* **Relevant Specification:** AT Protocol XRPC API
* **Capabilities Supported:**
  - Authenticated and public endpoints for searching posts, actor profiles, and repost graphs.
  - Explicit rate-limit boundaries: 3,000 requests per 5 minutes on public relay endpoints.
* **Date Checked:** October 2026
* **Application Usage:** Collector implementation `backend/app/modules/social_media_intelligence/collectors/bluesky.py`.

### 3.2 Mastodon & ActivityPub Search API
* **Canonical URL:** [https://docs.joinmastodon.org/methods/search/](https://docs.joinmastodon.org/methods/search/)
* **Relevant Specification:** Mastodon REST API Methods (`GET /api/v2/search`)
* **Capabilities Supported:**
  - Multi-instance search across federated microblogging nodes.
  - Rate limits: 300 requests per 5-minute window per application token.
* **Date Checked:** October 2026
* **Application Usage:** Collector implementation `backend/app/modules/social_media_intelligence/collectors/mastodon.py`.

---

## 4. Operational Security (OPSEC) & Zero-Trust Governance

### 4.1 NIST Special Publication 800-207: Zero Trust Architecture
* **Canonical URL:** [https://csrc.nist.gov/pubs/sp/800/207/final](https://csrc.nist.gov/pubs/sp/800/207/final)
* **Relevant Specification:** National Institute of Standards and Technology (NIST) Special Publication 800-207
* **Capabilities Supported:**
  - Decoupling of investigator credentials from external collection probes.
  - Fail-closed network egress policies preventing deanonymization through direct network fallback.
  - Least privilege and immutable logging across security boundaries.
* **Date Checked:** October 2026
* **Application Usage:** Egress control kernel `backend/app/core/egress_controller.py` and VA/PT scope isolation.

### 4.2 NIST Special Publication 800-190: Application Container Security Guide
* **Canonical URL:** [https://csrc.nist.gov/pubs/sp/800/190/final](https://csrc.nist.gov/pubs/sp/800/190/final)
* **Capabilities Supported:**
  - Guidelines for isolating untrusted security scanning workloads into ephemeral, non-root runner containers with dropped Linux capabilities (`CAP_DROP_ALL`).
* **Date Checked:** October 2026
* **Application Usage:** Feature `[CTI-03]` isolated worker container execution model.
