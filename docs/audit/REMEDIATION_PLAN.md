# Engineering Remediation Plan

**Status**: ACTIVE  
**Goal**: Transition Intelligence Platform to Enterprise Production Standard  
**Framework**: Defense-in-Depth, OWASP ASVS v4.0, Evidence Provenance Architecture

---

## 1. Prioritized Remediation Roadmap

```
[Phase 1: Security Hardening (P0)]
  ├── Task 1.1: Implement Centralized SSRF Defense (`network_safety.py`)
  ├── Task 1.2: Sanitize Evidence File Upload Path Traversal
  └── Task 1.3: Real Bitwise Cryptographic Hash Verification in Evidence Vault
         │
         ▼
[Phase 2: Eliminate Static AI/ML & Pipeline Modernization (P0/P1)]
  ├── Task 2.1: Build Centralized Model Provider Layer (`app/ai/`)
  ├── Task 2.2: Replace Hardcoded Investigation Summaries with Dynamic Grounded AI/ML Engine
  └── Task 2.3: Remove Fabricated Fixtures in News Investigation Pipeline (`investigation_pipeline.py`)
         │
         ▼
[Phase 3: Threat Engine Integrity & Tool Inventory (P1)]
  ├── Task 3.1: Fix Scanner Engine Health Check False "READY" Statuses
  ├── Task 3.2: Eliminate Synthetic Findings in Nuclei Engine
  └── Task 3.3: Publish Tool Integration Matrix & Standardized Provenance Envelopes
         │
         ▼
[Phase 4: Test Pyramid & End-to-End Validation (P2)]
  ├── Task 4.1: Unit & Regression Tests for Security & AI Pipelines
  ├── Task 4.2: Real Tool Execution Harness
  └── Task 4.3: Frontend Build & Typecheck Verification
         │
         ▼
[Phase 5: Operational Readiness & Runbooks (P3)]
  ├── Task 5.1: Create Deployment Runbook (`DEPLOYMENT.md`)
  └── Task 5.2: Create Incident Response Runbook (`INCIDENT_RESPONSE.md`)
```

---

## 2. Detailed Task Breakdown & Acceptance Criteria

### Task 1.1: SSRF Defense Guard
- **Action**: Implement `app.core.network_safety.NetworkSafety.validate_url(url)` to inspect hostname DNS resolution and reject private IPs (RFC 1918, RFC 3927, loopback, AWS/GCP metadata `169.254.169.254`).
- **Files Modified**: `backend/app/core/network_safety.py`, `backend/app/modules/news_intelligence/investigation_pipeline.py`, `backend/app/modules/news_intelligence/search_engine.py`, `backend/app/modules/tool_executor.py`.
- **Acceptance Criteria**:
  - `http://127.0.0.1:8000`, `http://localhost:27017`, `http://169.254.169.254` immediately fail with `400 Bad Request / SSRF Blocked`.
  - Public news and OSINT URLs continue to resolve and crawl cleanly.

### Task 1.2: Fix Path Traversal in Evidence Upload
- **Action**: Ensure `file.filename` is stripped of directory components using `os.path.basename` and regex sanitization before storing on disk.
- **Files Modified**: `backend/app/api/v1/evidence.py`.
- **Acceptance Criteria**:
  - Uploading a file named `../../../../etc/passwd` writes to `<storage_dir>/<tenant_id>/<ev_id>_passwd` strictly inside the tenant directory.

### Task 1.3: Real Cryptographic Evidence Verification
- **Action**: In `POST /api/v1/evidence/{evidence_id}/verify`, re-read the file content from disk (or verify stored raw payload), recompute SHA-256, and compare with `ev.hash`.
- **Files Modified**: `backend/app/api/v1/evidence.py`.
- **Acceptance Criteria**:
  - Valid, un-modified file returns `verified: True`, `status: "VALIDATED"`.
  - Modified or tampered file returns `verified: False`, `status: "TAMPERED"`.
  - Missing file returns `verified: False`, `status: "FILE_NOT_FOUND"`.

### Task 2.1: Centralized AI/ML Model Provider Layer
- **Action**: Create `backend/app/ai/models.py`, `backend/app/ai/providers.py`, and `backend/app/ai/service.py`.
  - Support configurable model backends (OpenAI, Gemini, Anthropic, Ollama/Local, and Deterministic NLP Fallback).
  - Include prompt-injection delimiters and boundary policies.
  - Track token usage, latency, prompt version, and execution status.
- **Files Modified**: `backend/app/ai/*`.
- **Acceptance Criteria**:
  - When API key is provided, invokes real LLM inference.
  - When no API key is provided, performs deterministic evidence-grounded NLP summarization without returning static placeholder text or claiming to be an LLM.

### Task 2.2: Dynamic Grounded Investigation Summaries
- **Action**: Replace static hardcoded strings in `InvestigationService._enrich_investigation_data` with dynamic synthesis based on actual entities, findings, and evidence.
- **Files Modified**: `backend/app/investigations/service.py`.
- **Acceptance Criteria**:
  - An investigation for `example.com` outputs leads and questions specific to `example.com` and its actual findings (e.g. DNS, HTTP headers, open ports).
  - No static repetitive bullet points.

### Task 2.3: Remove Fabricated Fixtures in News Investigation Pipeline
- **Action**: Rewrite `_analyze_source_lineage`, `_construct_temporal_timeline`, `_perform_media_forensics`, and `_evaluate_assessment_verdict` in `investigation_pipeline.py`.
  - Derive publication dates from actual article metadata and HTTP response headers.
  - Compare actual query terms against article body to evaluate context.
  - Remove all hardcoded "14 March 2022" dates and fake domains (`news-aggregator-wire.net`).
- **Files Modified**: `backend/app/modules/news_intelligence/investigation_pipeline.py`.
- **Acceptance Criteria**:
  - Current breaking news articles evaluate based on their actual publication date and verified claims.

### Task 3.1 & 3.2: Accurate Threat Scanner Health & Real Finding Generation
- **Action**: Update `masscan_engine.py`, `trivy_engine.py`, `gitleaks_engine.py`, `semgrep_engine.py`, `prowler_engine.py`, `testssl_engine.py`, `scoutsuite_engine.py`, `wapiti_engine.py`, `uncover_engine.py`, `amass_engine.py` to return `NOT_INSTALLED` when CLI binaries are not on the host. Update `nuclei_engine.py` to only report findings backed by real header evaluation.
- **Files Modified**: `backend/app/modules/threat_intelligence/engines/engines/*`.
- **Acceptance Criteria**:
  - Health check returns `NOT_INSTALLED` for uninstalled binaries.
  - Zero synthetic findings fabricated.
