# Sential Intelligence — Post-Merge Remediation Report

**Repository**: `dhayaalan/Intelligence`  
**Base Commit**: `60883d10b7eefa615ea35f98687d85637c39aa71`  
**Execution Date**: 2026-10-15  
**Auditor & Remediation Lead**: Antigravity AI  

---

## Executive Summary

Following code merges and architectural review of the Sential Threat Intelligence and OSINT platform, this remediation was executed directly in `/home/songoku/Pictures/Intelligence`. All changes prioritize **reliability, source provenance, evidence integrity, authorization, and honest collection-status reporting** over vanity metrics or simulated coverage.

Every P0 vulnerability and P1 functional requirement has been addressed with code implementations, automated regression tests, and verification runs.

---

## Remediation Item Matrix

| Issue ID | Severity | Category | Affected Components | Root Cause | Code Change | Test Added & Status |
|:---|:---:|:---|:---|:---|:---|:---:|
| **SEC-01** | **P0** | Secrets & Auth | `backend/app/core/config.py`, `backend/app/identity/bootstrap.py`, `backend/app/main.py` | Default JWT signing secret and super-admin fallback password ("SuperAdmin123!") permitted in production startup. | Added `validate_production_configuration()` enforcing 32+ char high-entropy `SECRET_KEY`, prohibiting placeholder strings, and requiring explicit non-default `INITIAL_SUPER_ADMIN_PASSWORD` in production. | `test_production_config_validation_rejects_weak_or_default_secrets` (PASSED) |
| **SEC-02** | **P0** | Database & Persistence | `backend/app/infrastructure/mongodb/client.py`, `docker-compose.yml`, `.env.example` | Cleartext credentials logged in MongoDB URI strings; failed DB connections allowed silent in-memory fallback in production. | Added `sanitize_mongo_uri()` credential masking; enforced fail-fast `RuntimeError` on DB connection failure in production; sanitized `.env.example` and `docker-compose.yml` secrets. | `test_sanitize_mongo_uri`, `test_production_mongo_unavailability_raises_runtime_error` (PASSED) |
| **SEC-03** | **P0** | Tenant Isolation | `backend/app/modules/osint/snapshot_service.py`, `backend/app/api/v1/tools.py` | Profile snapshot history was keyed only by `target_username` without tenant scoping, permitting cross-tenant observation leakage. | Scoped snapshot lookup, recording, and in-memory fallback cache by `tenant_id`. Added `tenant_id` context to tool endpoints. | `test_tenant_isolation_profile_snapshots` (PASSED) |
| **SEC-04** | **P0** | Authorization & SSRF | `backend/app/api/v1/news.py` | Source registration allowed unprivileged `USER` role to register sources without validation, risking SSRF and spam. | Restricted `POST /api/v1/news/sources` to `SUPER_ADMIN`, `TENANT_ADMIN`, and `ANALYST` (403 for `USER`). Enforced SSRF validation on domain and feed URLs. Defaulted new sources to unverified. | `test_news_source_registration_role_enforcement`, `test_news_source_registration_ssrf_rejection` (PASSED) |
| **OPSEC-01** | **P0** | Regional Egress | `backend/app/core/egress_controller.py`, `backend/tests/test_regional_osint_improvements.py` | Regional egress allowed mock IP generation and simulated routing. HTTPX 0.28+ proxy argument incompatibility (`proxies=` vs `proxy=`). | Disabled mock routing by default (`OPSEC_ALLOW_GATEWAY_MOCKS=false`) and prohibited simulated routes in production. Implemented HTTPX 0.28.1+ `proxy=` parameter. Enforced fail-closed zero-trust validation with real geolocation verification. | `test_egress_controller_fail_closed_on_unverified_gateway` (PASSED) |
| **INTEL-01** | **P0** | Fabricated Intel | `backend/app/modules/news_intelligence/search_engine.py`, `backend/app/api/v1/news.py` | Unknown article IDs generated synthetic fallback articles with generic author "Special Investigation Desk"; claims generated fake quotes from "Dr. Aris Vance". | Non-existent article IDs return `None` (HTTP 404). Grounded claim verification in `fact_check_service` returning `INSUFFICIENT_EVIDENCE` or `UNVERIFIED` without fake quotes or synthetic contradictions. | `test_unknown_article_returns_404`, `test_claim_investigation_returns_unverified_without_synthetic_contradictions` (PASSED) |
| **INTEL-02** | **P0** | Metric Inflation | `backend/app/modules/news_intelligence/search_engine.py`, `CountryComparisonTable.tsx` | Metrics inflated via `len(items) * 2` for evidence and `max(1, count)` for sources. "Sufficient multi-source coverage" displayed even when 0 articles existed. | Eliminated synthetic multiplication factors; derived counts strictly from retrieved records; updated table to accurately display "Unassessed / single or zero source" and honest status badges. | Matrix & engine assertions verified (PASSED) |
| **NEWS-01** | **P1** | Geographic Scope | `backend/app/modules/news_intelligence/search_engine.py`, `NewsIntelligencePage.tsx` | Search engine was hardcoded to 6 countries and silently sliced results to 10 countries; "Any Language" did not unconstrain language filters. | Dynamically queries verified editions across continents; removed silent 10-country truncation; passed `undefined` for `language_filter="all"` to genuinely disable language constraints. | Multi-country & worldwide tests verified (PASSED) |
| **NEWS-02** | **P1** | Multi-Country UI | `frontend/src/features/news_intelligence/NewsIntelligencePage.tsx` | Frontend supported only single country selection. | Converted country selection to multi-select with individual dismissible badges, "Clear All" action, and automatic multi-country comparison matrix triggering. | Frontend build `tsc && vite build` (PASSED in 4.36s) |
| **SOC-01** | **P1** | Social Collectors | `backend/app/modules/social_media_intelligence/collectors/instagram.py` | Magic fallback account ID `"17841400000000000"` used when `INSTAGRAM_BUSINESS_ACCOUNT_ID` was missing. | Removed magic account ID. Returns empty result with transparent `CONFIG_REQUIRED` checkpoint if token or account ID is not configured. | `test_instagram_collector_no_magic_account_id` (PASSED) |

---

## Detailed Root Cause Analysis & Fix Specifications

### 1. P0: Elimination of Fabricated Intelligence
- **Previous Flaw**: When an investigator clicked or requested an article ID that was absent or expired, `news_retrieval_engine.get_article()` generated a synthetic record with title `"Disinformation Campaign Analysis: ..."` and author `"Special Investigation Desk"`. Similarly, claim investigations containing keywords like `"hacked"` fabricated quotes attributed to fictional personas such as `"Dr. Aris Vance"` and `"Official Technical Audit Commission"`.
- **Remediation**:
  1. `get_article(article_id)` now checks memory and MongoDB, and if absent, returns `None`. `GET /api/v1/news/articles/{article_id}` raises `HTTPException(status_code=404, detail="Article not found")`.
  2. `investigate_claim()` passes candidate evidence to `fact_check_service.evaluate_claim_evidence()`. When evidence is absent or inconclusive, it returns verdict `INSUFFICIENT_EVIDENCE` or `UNVERIFIED` with confidence `0.0-30.0` and empty contradiction lists. No synthetic personas or quotes are ever generated.
  3. Metric calculations: `evidence` count is exactly `len(scored_items)` (not `* 2`); verified sources count in comparison rows is `actual_count` (not `max(1, count)`).

### 2. P0: Secure Secrets, Bootstrap, and Production Startup
- **Previous Flaw**: Production environment permitted startup with default placeholder secrets (`"sential-super-secure..."`), default administrator password (`"SuperAdmin123!"`), and silently continued with in-memory persistence if MongoDB was down.
- **Remediation**:
  1. `Settings.validate_production_configuration()` validates `SECRET_KEY` entropy (minimum 32 characters, no placeholder strings, no "changeme" / "changethis" substrings).
  2. `bootstrap.py` raises `RuntimeError` if `APP_ENV=production` and `INITIAL_SUPER_ADMIN_PASSWORD` is absent or equals `"SuperAdmin123!"`. Uses `$setOnInsert` to prevent overwriting existing administrative credentials.
  3. `connect_to_mongo()` masks credentials in logs via `sanitize_mongo_uri()` and raises `RuntimeError` during production startup if the database connection fails.
  4. Docker Compose and `.env.example` replaced secret-bearing defaults with required configuration placeholders.

### 3. P0: Strict Tenant Isolation
- **Previous Flaw**: `snapshot_service.py` cached and queried profile snapshots solely by platform and target username, allowing Tenant B to view observations recorded by Tenant A.
- **Remediation**:
  1. Profile snapshot records, queries, and in-memory caches now incorporate `tenant_id` at every layer (`f"{tenant_id}:{platform_id}:{username}"`).
  2. `GET /api/v1/tools/profile-snapshots` extracts `current_user.tenant_id` and passes it directly to the service.

### 4. P0: Real Regional Egress & Fail-Closed Isolation
- **Previous Flaw**: `egress_controller.py` had `OPSEC_ALLOW_GATEWAY_MOCKS=true` enabled, generating synthetic IPs (`103.21.xxx.xxx`) and passing health checks without network traffic. HTTPX 0.28+ raised `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`.
- **Remediation**:
  1. `OPSEC_ALLOW_GATEWAY_MOCKS` defaults to `False` and is prohibited in production.
  2. Implemented HTTPX 0.28.1+ `proxy=` parameter with backward-compatible fallback.
  3. Enforced actual exit IP and geolocation probe (`https://api.ipify.org` and `https://ipapi.co/{ip}/json/`). If the detected country does not match the configured gateway country, the controller marks `REGION_MISMATCH` and fails closed. Direct network fallback is strictly prohibited.

### 5. P1: Worldwide News Intelligence & Multi-Country Analysis
- **Previous Flaw**: The search engine queried a static 6-country edition list, sliced results to the first 10 countries, and single-select UI prevented multi-country comparisons.
- **Remediation**:
  1. Dynamically constructs regional queries across all configured editions in the ISO 3166-1 country registry.
  2. Allows unconstrained language queries when `languageFilter="all"`.
  3. Updated `NewsIntelligencePage.tsx` with a multi-select country control and removable chips, enabling comparative search across arbitrary country pairs or worldwide mode.
  4. Updated `CountryComparisonTable.tsx` to truthfully distinguish `NO_MATCHING_RESULTS` from `NO_SOURCES_CONFIGURED`, `UNVERIFIED`, and `WORKING_TESTED_REAL`.

### 6. P1: Social Media Intelligence & Provider Transparency
- **Previous Flaw**: `instagram.py` contained hardcoded fallback business account ID `"17841400000000000"`.
- **Remediation**:
  1. Removed magic account ID.
  2. If `INSTAGRAM_BUSINESS_ACCOUNT_ID` or token is missing, logs explicit configuration requirement, records checkpoint status `CONFIG_REQUIRED`, and returns empty posts honestly.
