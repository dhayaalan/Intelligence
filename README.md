# Sential Platform
### Modular Intelligence & Investigation SaaS Platform

Sential is a production-grade, modular intelligence SaaS platform designed for cyber investigators, intelligence analysts, and security teams. Built upon an autonomous, decoupled module architecture, Sential combines deep OSINT, real-time Social Media intelligence, global News aggregation, Media & Digital Forensics, and Threat Intelligence into a unified, high-density investigative workspace.

---

## 1. Architectural Architecture & Core Invariants

Sential strictly enforces a 5-tier modular separation of concerns:

```
┌────────────────────────────────────────────────────────┐
│   Presentation Layer: React 18, Vite, Tailwind CSS    │
│   Unified Shell: Universal Search, Module Workspaces   │
└───────────────────────────▲────────────────────────────┘
                            │ REST / SSE API (v1)
┌───────────────────────────▼────────────────────────────┐
│      API & Gateway: FastAPI, JWT Auth, TenantContext    │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│   Core Platform: Search Orchestrator, Module Registry  │
│   (Strictly Module-Agnostic, Zero Hardcoded Switch)   │
└─────────────┬────────────────────────────┬─────────────┘
              │ Event Bus / Contracts     │ Contracts
┌─────────────▼──────────┐      ┌──────────▼─────────────┐
│ Intelligence Execution │      │ Evidence & Vault       │
│ - OSINT (335+ tools)   │      │ - MongoDB DataStore    │
│ - Social Intelligence  │      │ - Neo4j Graph Store    │
│ - News Intelligence    │      │ - SHA-256 Provenance   │
│ - Media Forensics      │      │ - Clue-to-Clue Chains  │
│ - Threat Intelligence  │      │ - Immutable Audit Trail│
│ - Location Intel (GIS) │      └────────────────────────┘
└────────────────────────┘
```

### Key Guarantees:
1. **Module & Provider Isolation**: Failure or timeout of a single provider (e.g., Shodan, ZAP, Pytesseract, RSS feed) never halts other providers or crashes search orchestration. Structured partial results are always returned.
2. **Core Decoupling**: Core Search and Core Services never import or contain switch statements for specific modules or tools (`no if module == 'osint'`). All executions flow through the `ModuleRegistry`.
3. **5-Stage Authorization Pipeline**:
   $$\text{Platform Module Registered} \rightarrow \text{Tenant Entitled} \rightarrow \text{Role Authorized} \rightarrow \text{User Module Assigned} \rightarrow \text{Effective Access}$$
4. **Data Integrity & Zero-Fabrication**: Missing metadata (EXIF, C2PA, OCR, GPS) yields explicit `null` / `absent`, never invented values. Geographic coordinate `(0, 0)` is strictly rejected. Every evidence item is stamped with an immutable cryptographic SHA-256 fingerprint.

---

## 2. Intelligence Disciplines & Modules

| Module ID | Primary Purpose | Integrated Capabilities |
| :--- | :--- | :--- |
| `osint` | Modular Open-Source Intelligence | Domain, IP, Email, Phone, Username, Google Dorking, Subdomain discovery (crt.sh), Whois, DNS records, SEC Edgar filings. |
| `social_intelligence` | Public Social Media Intelligence | Profile search, public post normalization, Bluesky AT Protocol, Mastodon, YouTube video metadata, GitHub, Gravatar avatar checks. |
| `news_intelligence` | Global News Aggregation & Analysis | Configurable RSS/Atom feeds, canonical URL normalization, article deduplication, entity extraction, factor-based credibility analysis. |
| `media_intelligence` | Multimodal Digital Forensics | Cryptographic checksums (SHA-256, MD5), dual perceptual hashing (dHash & 2D DCT pHash, Hamming distance), image quality (Laplacian blur), EXIF/GPS extraction, C2PA Content Credentials JUMBF verification, OCR text & license plate extraction, video keyframe downsampling, audio stream inspection. |
| `threat_intelligence` | Vulnerability & Attack Surface Recon | ZAP web crawler, OpenAPI schema parser, CVE/NVD matching, IOC indicators, port scanning, security posture ratings. |
| `geo_intelligence` | Location Intelligence (GIS) | Coordinate validation, precision levels (`exact`, `city`, `country`), Leaflet mapping, timeline-spatial correlation. |

---

## 3. Unified Navigation & User Experience

Sential provides a clean, responsive, high-density dark interface structured into 4 primary functional areas:

- **Workspace**:
  - `Search` (`/search`): Universal intelligence search across all entitled modules or targeted selections.
  - `Investigations` (`/investigations`): Case lifecycle, target binding, clue-to-clue investigation, evidence vault.
  - `Recent Activity` (`/recent`): Timeline of recent queries, case updates, and audit events.
- **Intelligence**:
  - `OSINT` (`/intelligence/osint`): Deep technical domain, network, and identity recon.
  - `Social Intelligence` (`/intelligence/social`): Social profile discovery and post stream analysis.
  - `News Intelligence` (`/intelligence/news`): Multi-source news feed monitoring and credibility analysis.
  - `Media & Forensics` (`/intelligence/media`): Image, video, and audio forensic intake, hashing, and C2PA validation.
  - `Threat Intelligence` (`/intelligence/threat`): Vulnerability scanning, attack surface analysis, and IOC lookups.
  - `Location Intelligence` (`/intelligence/location`): Spatial correlation, coordinate verification, and map intelligence.
- **Investigation Resources**:
  - `Entities & Graph` (`/resources/entities`): Property graph visualization with Cytoscape, entity resolution, and relationship exploration.
  - `Evidence Vault` (`/resources/evidence`): Centralized tamper-evident repository of sealed evidence records.
  - `Reports` (`/resources/reports`): Dossier and intelligence report generation with traceable evidence citations.
- **Administration** (Role-Gated):
  - `Users & Roles` (`/admin/users`): RBAC administration and module assignments.
  - `Module Entitlements` (`/admin/modules`): Tenant-level module enablement and licensing.
  - `Provider Configuration` (`/admin/providers`): Provider health checks, credentials, and API rate limits.
  - `Collection Jobs` (`/admin/jobs`): Long-running job queues and task status.
  - `Audit Logs` (`/admin/audit`): Immutable operational and investigative audit trails.
  - `Platform Settings` (`/admin/settings`): System parameters, storage limits, and security controls.

---

## 4. Role-Based Access Control (RBAC)

| Role | Scope | Key Entitlements |
| :--- | :--- | :--- |
| **SUPER_ADMIN** | Platform-Wide | Global tenant management, user management, module registry enablement, provider configuration, global audit logs. |
| **TENANT_ADMIN** | Organization | Organization user onboarding, entitled module management, organizational audit logs, workspace settings. |
| **ANALYST** | Investigation | Universal search, case creation, clue-to-clue chaining, media forensics, evidence sealing, report generation. |
| **USER** | Read-Only / Basic | Read-only search and case inspection within assigned modules. |

### Demo Personas:

| Persona | Role | Email | Password | Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Alex Vance** | `SUPER_ADMIN` | `superadmin@sential.io` | `SuperAdmin123!` | Global Platform |
| **Sarah Connor** | `TENANT_ADMIN` | `admin@acme.com` | `TenantAdmin123!` | Acme Defense Corp |
| **Marcus Wright** | `ANALYST` | `analyst@acme.com` | `Analyst123!` | Acme Defense Corp |
| **Elena Fisher** | `USER` | `user@acme.com` | `User123!` | Acme (Read-Only) |

---

## 5. Local Execution & Docker Services

### Docker Compose Stack:
- **Backend API**: `http://localhost:8000` (FastAPI, Python 3.10)
- **Frontend UI**: `http://localhost:3000` (Nginx, React 18, Vite)
- **MongoDB**: `localhost:27018` (Primary Document Store)
- **Neo4j**: `localhost:7474` (HTTP) / `localhost:7687` (Bolt Property Graph)
- **Redis**: `localhost:6379` (Caching & Task Broker)

### Starting the Environment:
```bash
docker compose up -d
```

### Running Backend Tests:
```bash
docker exec intelligence-backend pytest tests/ -v
```

### Running Frontend Tests & Production Build:
```bash
cd frontend
npm run typecheck
npm test
npm run build
```

---

## 6. Engineering Conventions & Safe Extensibility

- **Adding a Provider**: Subclass `ProviderAdapter` under `app/modules/<module_name>/providers/`, define preflight checks, execute logic, and register through `ProviderRegistry`.
- **Adding a Module**: Subclass `IntelligenceModule` under `app/modules/<module_name>/`, create manifest, register via `module_registry.register(module, default_enabled=True)`.
- **Tenant Scope Enforcement**: All database queries must explicitly query by `tenant_id` from `TenantContext`.
- **Evidence Integrity**: Call `media_intelligence_service` or `evidence_service` to generate SHA-256 hashes before inserting records into MongoDB collections.
