# SENTIAL INTELLIGENCE PLATFORM — INTELLIGENCE GAP ANALYSIS

**Analysis Date:** October 2026  
**Scope:** Evaluation of local local codebase against real-world intelligence feeds, authoritative APIs, and open-source integrations.  
**Branch:** `feat/intelligence-audit-remediation-expansion`  

---

## 1. Domain-by-Domain Capability Assessment

### 1.1 OSINT & Entity Intelligence
* **Existing Baseline:**
  - Fast passive DNS resolution via Cloudflare/Google DoH (`tool_dns_recon`).
  - WHOIS via RDAP queries (`tool_whois_rdap`).
  - Certificate Transparency logs via crt.sh (`tool_crt_sh`).
  - IP Geolocation and ASN lookups via ip-api (`tool_ip_geo`).
  - Social username probing across 350+ platforms (`tool_username_prober`).
* **Identified Gaps:**
  - **Archival Context Gap:** Inability to retrieve historical versions of target endpoints, investigate domain lineage, and examine deleted content.
  - **Web Tech & Surface Observation Gap:** Lacking passive historical scan metadata, DOM titles, server headers, and web technology observations.
  - **Entity Sanctions & PEP Compliance Gap:** Inability to screen corporate officers, counterparties, or high-risk targets against international sanctions and politically exposed persons watchlists.
* **Remediation Implemented in Expansion:**
  - **Wayback Machine CDX API (`WaybackCDXProvider`):** Queries Internet Archive CDX endpoint with structured timestamp, status code, and snapshot URL extraction.
  - **urlscan.io API (`URLScanProvider`):** Public search integration querying scan IDs, screenshot previews, DOM page titles, IP/ASN, and server headers.
  - **OpenSanctions / yente API (`OpenSanctionsProvider`):** Fuzzy entity screening matching international sanction lists (OFAC, EU, UN), PEP registries, and debarment catalogs with confidence scoring.
  - **GLEIF Golden Copy API (`GLEIFProvider`):** Authoritative corporate legal entity identification, ISO 17442 LEI resolution, legal addresses, and corporate status endorsed by G20 and the Financial Stability Board.

---

### 1.2 Threat Intelligence
* **Existing Baseline:**
  - Port & service banner engine (`port_service_engine`).
  - TLS/SSL cipher suite verification (`tls_engine`).
  - CISA Known Exploited Vulnerabilities (KEV) in-memory catalog.
  - FIRST Exploit Prediction Scoring System (EPSS) API lookups.
  - OWASP ZAP DAST scan and spider integration with strict VAPT scope enforcement.
* **Identified Gaps:**
  - **Community Malware IOC Enrichment Gap:** Lack of automated IOC matching against malware families, botnet C2s, and malicious hashes without commercial Shodan/VirusTotal API keys.
  - **Authoritative NVD Vulnerability Details Gap:** While EPSS provided exploit probabilities and CISA KEV provided active exploitation flags, direct NIST NVD CVSS vectors, CWE classifications, and vendor advisory metadata were absent.
  - **Internet Noise vs. Targeted Attack Disambiguation Gap:** Investigators could not easily distinguish between mass internet scanners (benign port probes, search engine indexers) and targeted attacks directed at client infrastructure.
  - **Threat Engine In-Memory Desynchronization:** `threat_intel_engine.py` was disconnected from persistent MongoDB storage.
* **Remediation Implemented in Expansion:**
  - **abuse.ch ThreatFox Unified API (`ThreatFoxProvider`):** Direct community indicator of compromise queries returning malware printable names, threat types (botnet, payload delivery, C2), confidence levels, and tags.
  - **NIST NVD CVE API 2.0 (`NVDVulnerabilityProvider`):** Authoritative vulnerability lookup returning official CVSS v3.1 base scores, severity rankings, CWE weaknesses, and National Vulnerability Database descriptions.
  - **GreyNoise Community API (`GreyNoiseCommunityProvider`):** Authoritative IP noise classification, RIOT (Rule It Out) verification for common business services, and mass-scanner identification.
  - **Persistent Threat Store Integration:** MongoDB collection queries for `ti_threat_actors`, `ti_malware`, `ti_campaigns`, and `ti_vulnerabilities`.

---

### 1.3 News Intelligence
* **Existing Baseline:**
  - Full GDELT DOC 2.0 API global query engine with sentiment and tone extraction.
  - Official Google Fact Check Tools API querying published claims from Snopes, PolitiFact, FactCheck.org, Reuters, AP, and AFP.
  - Multi-country publisher registry covering 195+ countries with source corroboration.
* **Identified Gaps:**
  - Historical archive verification of news claims (solved by `WaybackCDXProvider` integration).
  - Cross-source claim lineage and narrative alignment are operational.

---

### 1.4 Social Media Intelligence
* **Existing Baseline:**
  - Bluesky AT Protocol collector.
  - Reddit JSON public feed parser.
  - Mastodon public instance search.
  - YouTube Data API collector.
  - Telegram public channel collector.
  - Instagram and Facebook profile metadata collectors.
* **Identified Gaps:**
  - Commercial platform rate limits and authentication hurdles (e.g. X/Twitter API v2 requires commercial keys).
  - Proper differentiation between unconfigured state (`CONFIG_REQUIRED`) and operational state (`AVAILABLE`).

---

## 2. Summary of Priority Provider Additions

| Provider Candidate | Module | Priority | Selected? | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Internet Archive Wayback CDX API** | OSINT / News | P1 | **YES** | Authoritative, free, public, no API key required; solves archival gap. |
| **urlscan.io Search API** | OSINT / Threat Intel | P2 | **YES** | Public API, rich historical technology and DOM screenshots; no mandatory key. |
| **OpenSanctions Community API** | OSINT / Identity | P2 | **YES** | High investigative value for PEP and sanctions screening; no credit card required. |
| **abuse.ch ThreatFox API** | Threat Intelligence | P2 | **YES** | Authoritative IOC feed, no commercial paywall; covers malware families and C2s. |
| **NIST NVD CVE API 2.0** | Threat Intelligence | P2 | **YES** | Authoritative gold-standard CVSS and CWE classification. |
| **yente (Self-Hosted OpenSanctions)** | OSINT | P3 | Deferred | Can be deployed as a local microservice in future on-prem enterprise deployments. |
| **MISP / OpenCTI TAXII Server** | Threat Intelligence | P3 | Deferred | Requires running dedicated MISP/OpenCTI server instances; adapter design ready. |
