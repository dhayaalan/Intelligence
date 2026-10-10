# Initial Architecture & Security Audit Report

**Date**: 2026-10-09  
**Repository**: `/home/songoku/Pictures/Intelligence`  
**Auditor**: Principal Architect & Security Engineering Team  
**Assessment Standard**: OWASP ASVS v4.0, OWASP Top 10, NIST SP 800-218 (SSDF)

---

## 1. Executive Summary

This audit encompasses the full full-stack repository including:
- **Backend**: FastAPI modular monolith, Pydantic schemas, MongoDB asynchronous/synchronous repositories with transactional in-memory fallback, multi-tenant RBAC engine, event-driven module orchestrator, 34 threat intelligence scanner adapters, 350+ OSINT platform probe catalog, news retrieval engine, and investigation evidence vaults.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, Lucide icons, Canvas-based Graph Studio, and modular investigation workspaces.
- **Integrations & Intelligence Engines**: OSINT providers, Threat Intelligence DAST/ZAP scanners, Google News RSS, YouTube public search, and media extraction pipelines.

While the foundational multi-tenant authorization and modular provider architectures are sound, the audit identified critical vulnerabilities and architectural defects across:
1. **SSRF Risks in External Content Fetching**
2. **Path Traversal in Evidence Uploads**
3. **Mocked / Fabricated Evidence Hash Verification**
4. **Repetitive, Static, and Hardcoded AI/ML Responses**
5. **Simulated Vulnerability Findings and False Tool Health Statuses**

---

## 2. Architecture Discovery

```
                         ┌────────────────────────────────────────┐
                         │   Frontend (React 19 + TypeScript)     │
                         │   Graph Studio, Search, Investigations │
                         └───────────────────┬────────────────────┘
                                             │ HTTP / JWT Bearer
                                             ▼
                         ┌────────────────────────────────────────┐
                         │      FastAPI Gateway & Auth (v1)       │
                         │   Role Check (SuperAdmin/TenantAdmin)  │
                         └───────┬────────────────────────┬───────┘
                                 │                        │
                 ┌───────────────┴────────┐      ┌────────┴──────────────┐
                 │  Search Orchestrator   │      │    Tools Dispatcher   │
                 └───────┬────────────────┘      └────────┬──────────────┘
                         │                                │
        ┌────────────────┼────────────────┐               │
        ▼                ▼                ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     OSINT    │ │ Threat Intel │ │     News     │ │  Tool Exec   │
│ (352 Platforms)│ (34 Engines) │ │ Intelligence │ │ (34 Curated) │
└───────┬──────┘ └───────┬──────┘ └───────┬──────┘ └───────┬──────┘
        │                │                │                │
        └────────────────┼────────────────┼────────────────┘
                         ▼
        ┌────────────────────────────────────────┐
        │  Evidence Vault & MongoDB Persistence  │
        └────────────────────────────────────────┘
```

- **Backend Stack**: Python 3.10, FastAPI 0.110+, Pydantic v1/v2 compat, Motor/PyMongo, HTTPX async networking, BeautifulSoup4.
- **Database Layer**: Dual-mode storage (`Database` in-memory locking dict + `MongoDB` collections for cases, investigations, entities, evidence, reports, and search history).
- **Security Posture**: Tenant isolation derived strictly from JWT `tenant_id` claim; roles enforced via `require_roles`.

---

## 3. Prioritized Audit Findings

### Priority 0: Critical Security & Integrity Defects

#### SEC-01: Server-Side Request Forgery (SSRF) in URL Ingestion
- **Affected Files**:
  - `backend/app/modules/news_intelligence/investigation_pipeline.py` (Line 56)
  - `backend/app/modules/news_intelligence/search_engine.py` (Lines 87, 240)
  - `backend/app/modules/tool_executor.py` (Lines 310, 390)
- **Vulnerability**: Unrestricted URL extraction using `httpx.get(url)` without validating whether the resolved IP address falls within private, loopback, link-local, or cloud metadata ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`).
- **Impact**: Attackers can trigger requests to internal microservices, AWS/GCP instance metadata endpoints, or local ports (e.g. `http://127.0.0.1:8080` ZAP daemon, `http://127.0.0.1:27017` MongoDB).
- **Remediation**: Implement a centralized `NetworkSafety` utility that parses the destination URL, resolves DNS, validates against RFC 1918 / RFC 3927 / loopback CIDR blocks, and prevents redirects to private IPs.

#### SEC-02: Path Traversal in Evidence File Upload
- **Affected File**: `backend/app/api/v1/evidence.py` (Line 95)
- **Vulnerability**: 
  ```python
  file_path = os.path.join(tenant_dir, f"{ev_id}_{file.filename}")
  ```
  `file.filename` is concatenated directly into `os.path.join`. If a filename contains traversal sequences (e.g. `../../secret.txt`), it can write files outside the intended directory.
- **Impact**: Arbitrary file overwrite or directory escape.
- **Remediation**: Sanitize `file.filename` with `os.path.basename` and regex stripping of non-alphanumeric/extension characters.

#### SEC-03: Fabricated Evidence Hash Verification
- **Affected File**: `backend/app/api/v1/evidence.py` (Lines 145–163)
- **Vulnerability**: 
  The endpoint `POST /api/v1/evidence/{evidence_id}/verify` unconditionally returns `"verified": True` without re-reading the stored artifact from disk or checking whether the SHA-256 hash has been altered.
- **Impact**: Falsely certifies chain-of-custody integrity for tampered evidence.
- **Remediation**: Re-read the file from disk (or verify the raw payload), recompute `hashlib.sha256()`, compare with `evidence.hash`, and return authentic verification states (`VALIDATED`, `TAMPERED`, `FILE_NOT_FOUND`).

#### SEC-04: Static and Fabricated News Investigation Intelligence
- **Affected File**: `backend/app/modules/news_intelligence/investigation_pipeline.py` (Lines 283–628)
- **Vulnerability**:
  - `_analyze_source_lineage` injects hardcoded dummy mirror domains (`news-aggregator-wire.net`, `daily-repost-feed.org`).
  - `_construct_temporal_timeline` and `_perform_media_forensics` inject static dates (`2022-03-14T08:12:00Z`).
  - `_assemble_evidence_vault` injects fake local archive URLs (`https://archive.local/reference/historical_2022`).
  - `_evaluate_assessment_verdict` hardcodes `VerificationVerdict.OUT_OF_CONTEXT` regardless of the actual news story.
- **Impact**: All news investigations yield identical fabricated results claiming 2022 archival dates.
- **Remediation**: Remove fabricated fixtures. Ground analysis dynamically in real article text, authentic metadata, and live multi-source search comparisons.

---

### Priority 1: High Priority AI/ML & Tool Engine Defects

#### ENG-01: Threat Intelligence Engines Falsely Reporting "READY"
- **Affected Files**:
  - `backend/app/modules/threat_intelligence/engines/engines/masscan_engine.py` (Line 63)
  - `backend/app/modules/threat_intelligence/engines/engines/trivy_engine.py` (Line 62)
  - `backend/app/modules/threat_intelligence/engines/engines/gitleaks_engine.py` (Line 62)
  - `backend/app/modules/threat_intelligence/engines/engines/semgrep_engine.py` (Line 62)
  - `backend/app/modules/threat_intelligence/engines/engines/prowler_engine.py` (Line 63)
  - `backend/app/modules/threat_intelligence/engines/engines/testssl_engine.py` (Line 62)
  - `backend/app/modules/threat_intelligence/engines/engines/scoutsuite_engine.py` (Line 62)
  - `backend/app/modules/threat_intelligence/engines/engines/wapiti_engine.py` (Line 62)
  - `backend/app/modules/threat_intelligence/engines/engines/uncover_engine.py` (Line 63)
  - `backend/app/modules/threat_intelligence/engines/engines/amass_engine.py` (Line 63)
- **Defect**: When binaries are missing from the system, engines return `"status": "READY"` in health checks.
- **Impact**: Operators and analysts are misled into believing scanning tools are active when they are absent.
- **Remediation**: Ensure health check accurately reports `"status": "NOT_INSTALLED"` or `"CONFIG_REQUIRED"` when CLI tools are not installed.

#### ENG-02: Nuclei Engine Injecting Synthetic Findings
- **Affected File**: `backend/app/modules/threat_intelligence/engines/engines/nuclei_engine.py` (Lines 75–86)
- **Defect**: Always injects a hardcoded finding `"http-missing-security-headers"` regardless of actual target headers.
- **Remediation**: Execute real HTTP header analysis before reporting missing headers, or return clean results if headers are present.

#### AIML-01: Repetitive Static Investigation Summaries
- **Affected File**: `backend/app/investigations/service.py` (Lines 66–151)
- **Defect**: `_enrich_investigation_data` injects the exact same static bullet points ("Primary upstream attribution source remains unconfirmed.", "Historical infrastructure ownership prior to current monitoring window.") into every investigation.
- **Remediation**: Implement a centralized AI/ML Service (`app/ai/service.py`) that generates dynamic, evidence-grounded investigation summaries, open questions, and recommended actions based on the actual correlated findings, entities, and targets.

---

### Priority 2: Medium Priority Architectural & Operational Gaps

#### ARCH-01: Absence of Centralized AI Model Provider Layer
- **Defect**: No configurable abstraction for LLMs (OpenAI, Gemini, Anthropic, Ollama/vLLM) with prompt injection defenses, input sanitization, token tracking, and structured schema outputs.
- **Remediation**: Build `backend/app/ai/providers.py` and `models.py` with multi-provider fallbacks and strict security boundaries.

#### ARCH-02: Result Authenticity & Lifecycle States
- **Defect**: Tools do not systematically communicate evidence provenance levels (Level 0 through Level 4) or verification states (`VERIFIED_WITHIN_SCOPE`, `UNVERIFIED`, `DISPUTED`).
- **Remediation**: Standardize tool output envelopes with authenticity classifications and verification metadata.

---

### Priority 3: Low Priority Documentation & Runbooks

#### OPS-01: Deployment & Incident Response Runbooks Missing
- **Defect**: Lack of actionable production operations guides for multi-tenant deployment, secret rotation, and incident handling.
- **Remediation**: Author `docs/runbooks/DEPLOYMENT.md` and `docs/runbooks/INCIDENT_RESPONSE.md`.
