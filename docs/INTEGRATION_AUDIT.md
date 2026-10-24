# Comprehensive Codebase & Integration Audit

## 1. Executive Summary

This audit assesses the state of two codebases:
1. **Primary Application:** `/home/songoku/Pictures/Intelligence` (Sential Intelligence SaaS Platform)
2. **Reference Application:** `/home/songoku/Pictures/social-media-ai-agents-v2-main` (OSINT & AI Agent Suite)

The objective is to establish an authoritative inventory of working features, models, APIs, and pipelines, identifying reusable components from the reference project to integrate into the primary application without regressions or breaking changes.

---

## 2. Primary Application Audit: Sential Intelligence Platform

### 2.1 Backend Architecture & Tech Stack
- **Framework:** FastAPI (Python 3.10) with asynchronous ASGI handling via Uvicorn.
- **Databases:**
  - **MongoDB 7.0** (`motor`/`pymongo`) on host port `27018` (internal `27017`): Stores users, tenants, investigations, evidence, findings, entities, audit logs, and provider execution records.
  - **Neo4j 5.20.0-community** (`bolt://neo4j:7687`, HTTP `7474`): Stores entity relationship graphs with APOC procedures and schema constraints.
  - **Redis 7-alpine** (port `6379`/`6380`): Session caching, job status, and broker placeholder.
- **Security & Authorization:**
  - Multi-tenancy with strict tenant isolation (`app/tenancy`).
  - Role-Based Access Control (`SUPER_ADMIN`, `TENANT_ADMIN`, `INVESTIGATOR`, `ANALYST`) in `app/authorization`.
  - Immutable audit logging (`app/audit/logger.py`) for all tool runs, data modifications, and logins.
  - VAPT Scope Enforcer (`app/modules/threat_intelligence/engines/scope_enforcer.py`) to restrict intrusive network probing.
  - Egress safety controls and SSRF mitigations in `app/core/network_safety.py` and `app/core/egress_controller.py`.

### 2.2 Active Module Ecosystem
Modules conform to `app/module_sdk/contract.py` and register in `app/module_registry/registry.py`:
- `osint`: DNS, Whois/RDAP, Certificate Transparency (crt.sh), IP Geolocation, Reverse DNS, HTTP headers, TLS inspection, Username probes (Sherlock/WhatsMyName patterns), Email verification, Social handles, Vehicle registration lookup (`vehicle_registration_provider`), Shodan Camera Radar.
- `threat_intelligence`: Vulnerability intelligence (CVE/NVD), AlienVault OTX, VirusTotal, ThreatFox, OpenSanctions, GreyNoise, SEC EDGAR, GLEIF, Censys, and OWASP ZAP active scanner / spider integration.
- `news_intelligence`: Real-time RSS aggregations, global news search, bias/credibility scoring, and timeline extraction.
- `social_media_intelligence`: YouTube oEmbed telemetry, Telegram profile/userpic resolution, and Reddit community discovery.
- `geo_intelligence`: Geolocation records, coordinate bounding, and map visualization data.
- `camera_evidence`: Public and open-data camera catalog (`catalog.py` with TfL JamCams, Highways England, NYCDOT, Singapore LTA DataMall), authorized video footage ingestion, and ANPR service (`anpr_service.py`).
- `ml_contracts`: Clean microservice client boundary (`client.py`) connecting to external ML models with strict `NOT_CONFIGURED` handling.

### 2.3 Image, Video & ANPR Pipeline
- **Existing Implementation:** `app/modules/camera_evidence/anpr_service.py`
  - OpenCV-based frame decoding (`cv2.VideoCapture`).
  - Morphological edge and contour filtering (`cv2.bilateralFilter`, `cv2.Canny`, `cv2.findContours`) targeting vehicle plate aspect ratios (1.6 to 6.2).
  - Tesseract OCR inference with double-pass (`--psm 7` and `--psm 8`) with character whitelisting `[A-Z0-9]`.
  - Normalized Levenshtein similarity metric against target plate.
  - Bounded duration sampling (default 60s, configurable intervals).
  - Review states: `NO_MATCH`, `POSSIBLE_MATCH`, `CANDIDATE_MATCH`, `HUMAN_CONFIRMED`, `HUMAN_REJECTED`, `INCONCLUSIVE`.
  - Evidence thumbnails encoded as Base64 JPEG data URLs with frame timecodes.
- **Gaps:**
  - Vehicle object detection before plate cropping relies on aspect-ratio contours rather than a trained deep-learning vehicle/plate detector (e.g. YOLO/Grounding DINO).
  - No cross-frame object tracking (IoU / centroid tracking) to merge detections of the same vehicle across frames.
  - Video uploads are stored locally in `/tmp/sential_footage` rather than unified with the main evidence store.

### 2.4 Existing Five OSINT Tools Status
- **SpiderFoot:** Listed in curated tool definitions (`app/api/v1/tools.py`), but lacks an active execution runner in `tool_executor.py` (falls back to generic probe).
- **Maltego:** Listed in tool registry, but lacks graph-to-Maltego CSV/Transform export adapter.
- **Shodan:** Integrated in `_run_shodan` using Shodan Host API (`/shodan/host/{ip}`), but lacks keyless InternetDB adapter, query builder, and search filters.
- **theHarvester:** Listed in curated tool definitions, but lacks subprocess or worker runner in `tool_executor.py`.
- **Google Dorks:** Listed in tool registry, but lacks structured dork query generator and news vs. web execution separation.

---

## 3. Reference Application Audit: Social Media AI Agents v2

### 3.1 Architecture & Tech Stack
- **Frontend:** React with TanStack Start / Vite, TailwindCSS, Radix UI.
- **Backend / Services:**
  - Node.js / TanStack server functions.
  - `ai-service`: Standalone Python FastAPI microservice (`ai-service/app/main.py`) running on port 8000.
  - `osint-workers`:
    - `theharvester`: Docker container with FastAPI wrapper (`app.py`) invoking theHarvester CLI.
    - `searxng`: Dockerized meta-search instance.

### 3.2 Key Reusable Components
1. **OSINT Adapters (`src/utils/collectors/`):**
   - `spiderfoot.ts`: Complete lifecycle client for SpiderFoot REST API (`/startscan`, `/scanstatus`, `/scaneventresults`), polling engine, module attribution, and result normalization.
   - `theharvester.ts`: Client for the theHarvester worker, parsing structured JSON results (emails, hosts, IPs, URLs), passive source constraints (`crtsh`, `certspotter`).
   - `shodan-internetdb.ts`: Keyless Shodan InternetDB adapter querying ports, CPEs, hostnames, and vulnerabilities without commercial API keys.
   - `dorks.ts` / `dorks.ts`: Google Dork generator with 20+ specialized investigation templates and distinction between executable news RSS queries and browser-executable web dorks.
   - `maltego-export.ts`: Graph-to-Maltego RFC-4180 CSV exporter mapping investigation entities to `maltego.Person`, `maltego.Domain`, `maltego.IPv4Address`, etc.
2. **Vehicle Intelligence (`src/utils/vehicle-osint.ts`):**
   - NHTSA 17-character VIN decoder via keyless API.
   - Indian RTO plate state & district office mapping (covers TG, TS, MH, DL, KA, AP, KL, TN, GJ, UP, etc.).
   - Plate syntax regex validation and normalization.
3. **AI Vision & Audio Service (`ai-service`):**
   - Object detection (`detect.py` using Grounding DINO).
   - Word-level OCR with bounding boxes (`ocr.py` using Tesseract).
   - Florence-2 VLM (`ocr_vlm.py`, `describe.py`).
   - Face detection and cosine matching (`faces.py` using InsightFace).
   - Audio event classification (`audio_events.py` using YAMNet).
   - Image forensics (`forensics.py` using pHash and EXIF metadata).

---

## 4. Key Differences and Integration Boundary

| Aspect | Primary Application (Intelligence) | Reference Application | Decision |
|---|---|---|---|
| **Backend Runtime** | Python 3.10 / FastAPI | Python 3.9 (AI) + Bun/Node (Frontend) | Retain primary FastAPI backend; implement native Python adapters and workers |
| **Database** | MongoDB 7.0 + Neo4j 5.20 | In-memory / TanStack store | Keep MongoDB + Neo4j as authoritative persistence |
| **Auth & Tenancy** | Multi-tenant RBAC, JWT, Audit logging | Single-tenant demo mode | Enforce primary app's multi-tenancy & RBAC on all integrated features |
| **OSINT Strategy** | In-app deterministic tool executor | Separate worker architecture | Unify both: provide in-app native execution with optional Docker worker endpoints |
| **Vehicle / ANPR** | Real OpenCV + Tesseract pipeline in backend | Regex + NHTSA VIN lookup in TS | Combine both: enrich ANPR with RTO/VIN lookup and add multi-frame tracking |
