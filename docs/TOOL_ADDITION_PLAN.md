# SENTIAL INTELLIGENCE PLATFORM — TOOL ADDITION & EXPANSION PLAN

**Version:** 2.1.0  
**Status:** Implemented and Tested  
**Branch:** `feat/intelligence-audit-remediation-expansion`  

---

## 1. Candidate Evaluation & Selection Matrix

Each prospective tool candidate was evaluated against investigative value, API stability, licensing, rate limits, and implementation effort.

```
                     INVESTIGATIVE VALUE
                         ▲
                         │   [Wayback CDX]
                         │   [OpenSanctions]     [NVD CVE 2.0]
                         │   [ThreatFox]         [urlscan.io]
                         │
                         │             [MISP / TAXII]
                         │
      Low Effort ────────┼────────────────────────► High Effort
                         │
                         │
```

| Candidate | Identifier | Target Module | Documentation / Endpoint | Auth Model | Free Quota / Rate Limits | Selection Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Internet Archive Wayback CDX** | `wayback_cdx` | OSINT | `https://web.archive.org/cdx/search/cdx` | Keyless / Public | Bounded by user agent; 30-100 req/min | **IMPLEMENTED (Batch 1)** |
| **urlscan.io Public Search** | `urlscan` | OSINT | `https://urlscan.io/api/v1/search/` | Optional API Key | 100 req/day free; 5000+ with API Key | **IMPLEMENTED (Batch 1)** |
| **OpenSanctions Matching API** | `opensanctions` | OSINT | `https://api.opensanctions.org/match/default` | Optional API Key | Community endpoint free for non-commercial investigations | **IMPLEMENTED (Batch 1)** |
| **abuse.ch ThreatFox Unified API** | `threatfox` | Threat Intel | `https://threatfox-api.abuse.ch/api/v1/` | Keyless / Public | Public community API; 1 req/sec safe limit | **IMPLEMENTED (Batch 1)** |
| **NIST NVD CVE API 2.0** | `nvd_cve` | Threat Intel | `https://services.nvd.nist.gov/rest/json/cves/2.0` | Optional API Key | 5 req / 30s keyless; 50 req / 30s with NIST key | **IMPLEMENTED (Batch 1)** |
| **GreyNoise Community API** | `greynoise_community` | Threat Intel | `https://api.greynoise.io/v3/community/{ip}` | Optional API Key | Free community queries for IP noise & scanner classification | **IMPLEMENTED (Batch 2)** |
| **GLEIF Legal Entity Identifier** | `gleif_lei` | OSINT | `https://api.gleif.org/api/v1/lei-records` | Keyless / Open Public | Open public standard (G20/FSB) for verified corporate legal entity data | **IMPLEMENTED (Batch 2)** |

---

## 2. Architectural Integration Standard

Every newly added provider strictly conforms to the Sential Provider Adapter contract:

1. **Subclassing `ProviderAdapter` (`app.module_sdk.provider_adapter`)**:
   - `provider_id`: Stable unique string ID.
   - `name`: Clean, human-readable display title.
   - `version`: Semantic version string.
   - `timeout_seconds`: Guarded timeout (4.0s - 10.0s).
   - `health_check()`: Live HTTP endpoint ping returning `HealthCheckResult`.
   - `execute(request: ProviderRequest) -> ProviderResponse`: Asynchronous query execution with input sanitization.

2. **Standard Result Normalization (`NormalizedResult`)**:
   - Entity payloads created via `ModuleSDK.create_entity()` with valid `EntityType` enums (`URL`, `SANCTION_RECORD`, `IOC`, `VULNERABILITY`).
   - Evidence records created via `ModuleSDK.create_evidence()` capturing raw response payloads, reference targets, and SHA-256 hashes where applicable.
   - Confidence scoring scaled from 0.0 to 1.0 based on provider match certainty.

3. **Multi-Layer Dispatch Wiring**:
   - Registered in Module Manifest (`manifest.py`).
   - Registered in Module Engine Registry (`module.py`).
   - Registered in Public Tool Definitions (`backend/app/api/v1/tools.py`).
   - Dispatched in Central Execution Engine (`backend/app/modules/tool_executor.py`).
