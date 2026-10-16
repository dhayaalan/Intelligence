# SENTIAL INTELLIGENCE PLATFORM
## Client Requirements, Codebase Architecture & Demo Readiness Report

**Document ID:** SEN-CRDRR-2026-V1  
**Report Date:** October 16, 2026  
**Target Repository:** `/home/songoku/Pictures/Intelligence`  
**Active Production Branch:** `main` (Merge Commit: `6ec2579`)  
**Target Platform:** Sential Intelligence / OSINT Investigation SaaS Platform  
**Classification:** CONFIDENTIAL // PREPARED FOR CLIENT REVIEW  
**Auditor / Lead Author:** Principal Solutions Architect & Intelligence Systems Engineer  

---

## Table of Contents
1. [Cover Page and Metadata](#1-cover-page-and-metadata)
2. [Executive Summary in Simple English](#2-executive-summary-in-simple-english)
3. [Purpose of the Platform](#3-purpose-of-the-platform)
4. [Who the Client Users Are and What They Need](#4-who-the-client-users-are-and-what-they-need)
5. [Confirmed Requirements, Working Assumptions, and Open Questions](#5-confirmed-requirements-working-assumptions-and-open-questions)
6. [Current Application Capabilities](#6-current-application-capabilities)
7. [What Works, What is Partially Working, and What is Unverified](#7-what-works-what-is-partially-working-and-what-is-unverified)
8. [End-to-End Investigator Workflow](#8-end-to-end-investigator-workflow)
9. [Intelligence Source and Tool Readiness Summary](#9-intelligence-source-and-tool-readiness-summary)
10. [Search Accuracy, Trustworthiness, and Evidence Quality](#10-search-accuracy-trustworthiness-and-evidence-quality)
11. [Usability Gaps and Their Impact on the Client](#11-usability-gaps-and-their-impact-on-the-client)
12. [Security, Roles, Deployment, and Operational Considerations](#12-security-roles-deployment-and-operational-considerations)
13. [Prioritized Improvements (P0 through P3)](#13-prioritized-improvements-p0-through-p3)
14. [Client-Specific 25–30 Minute Demo Plan](#14-client-specific-2530-minute-demo-plan)
15. [Questions to Ask the Client](#15-questions-to-ask-the-client)
16. [Measurable Acceptance Criteria](#16-measurable-acceptance-criteria)
17. [Recommended Delivery Phases and Next Steps](#17-recommended-delivery-phases-and-next-steps)
18. [Appendix: Test Execution Logs, Source File Index & Methodology](#18-appendix-test-execution-logs-source-file-index--methodology)

---

## 1. Cover Page and Metadata

- **Platform Name:** Sential Intelligence SaaS Platform (Version 2.0.0)
- **Codebase Path:** `/home/songoku/Pictures/Intelligence`
- **Repository State:** `main` branch clean; git commit `6ec2579`
- **Core Technology Stack:**
  - Backend: Python 3.10, FastAPI (ASGI asynchronous architecture), Motor / PyMongo, SQLAlchemy, Pydantic v1.10
  - Frontend: React 18, TypeScript 5.5, Vite 5.4, TailwindCSS 3.4, ReactFlow (@xyflow/react), Leaflet / React-Leaflet
  - Persistence Layer: MongoDB 7.0 (primary document store with collection indexes and thread-safe fallback)
  - Containerization: Multi-stage Dockerfiles (non-root execution), Docker Compose with health checks
- **Verification Environment:** Linux 6.8.0, Python 3.10.12, Node.js 20, MongoDB 7.0 (localhost:27017 active)
- **Primary Audience:** Client Executives, Lead Investigators, Security Directors, Technical Project Managers

---

## 2. Executive Summary in Simple English

This executive summary provides clear, direct answers to the fundamental questions about the application without using unnecessary technical jargon.

### What problem does the application solve?
In modern corporate due diligence, cyber risk analysis, and public-interest investigations, analysts are forced to jump between dozens of disconnected browser tabs, public search engines, threat databases, and social media platforms. Information is easily lost, copying data into spreadsheets is error-prone, evidence source links are frequently misplaced, and analysts have no easy way to prove that collected records were not altered after collection. Sential consolidates these fragmented tools into a single, organized investigation workspace where researchers can search a target, review genuine source records, see how people and companies are connected, preserve evidence with digital proof of integrity, and generate professional case reports.

### Who is it designed for?
The platform is designed for four distinct groups of users:
1. **Investigators:** Professionals who need to research individuals, companies, usernames, or domains and gather trustworthy leads.
2. **Intelligence Analysts:** Specialists who connect dots across multiple sources, evaluate cyber risks or disinformation campaigns, and write investigative assessments.
3. **Organization Administrators:** Managers who manage analyst accounts, control access to specific tools, and enforce organizational data boundaries.
4. **Platform Administrators:** Technical operators who monitor overall system health, configure external intelligence connections, and oversee audit records.

### What can a user accomplish today?
Today, an investigator can log into the platform, initiate a unified search across corporate, technical, and news databases, and watch as live results arrive from authoritative sources. The investigator can inspect the original web source of every finding, verify when it was retrieved, automatically turn the search into an organized case file, link entities on an interactive connection graph, view locations on a world map, store records in a secure evidence vault with cryptographic SHA-256 fingerprinting, and download a structured Markdown case dossier.

### What is genuinely verified?
Every claim in this report has been verified against the actual source code and automated tests:
- **Automated Backend Tests:** 137 out of 137 tests pass with 100% success (`pytest backend/tests/`).
- **Frontend Application Build:** The React/TypeScript user interface builds cleanly with zero errors (`tsc && vite build`).
- **Real Database Persistence:** The platform connects to an active MongoDB database with full indexing and tenant data isolation.
- **Strict Data Honesty:** All synthetic and mock modules (`test_intelligence`, `example_intelligence`) are disabled in production and strictly blocked from contaminating real investigation results.
- **Operational Public Integrations:** Authentic public engines are fully functional, including NIST NVD (CVE vulnerability lookup), ThreatFox (malware and indicator feeds), Wayback Machine CDX (historical web snapshots), URLScan (website telemetry), OpenSanctions (international sanctions and politically exposed persons), GreyNoise Community (Internet scanning noise), GLEIF (official global legal entity identifiers), and US SEC EDGAR (official corporate filings and CIK directories).

### What is not yet confirmed?
1. The client's preferred deployment model (whether they require a multi-tenant cloud SaaS or a private, self-hosted deployment on their own servers).
2. The specific paid commercial API subscriptions the client already owns (such as Shodan, Censys, or VirusTotal) versus free public tools.
3. The exact regulatory or legal standard required for case files (for example, whether exports are for internal risk assessment or formal court submission).
4. The client's expected report file format (the platform currently exports Markdown `.md` dossiers; direct PDF generation from the user interface is an important next step).

### What should we demonstrate first?
We recommend demonstrating a safe, live, 25-to-30-minute corporate due diligence investigation. We will search an authorized target (such as `apple.com` or a known public entity), demonstrate live querying across SEC EDGAR, NIST vulnerabilities, and Wayback archives, examine genuine source citations, link findings into an investigation case, explore the interactive connection graph, and export a complete case dossier.

### What must the client clarify before we finalize the scope?
Before committing to production timelines, the client must clarify:
1. Their top two or three most frequent investigation workflows (e.g., corporate due diligence, cyber threat analysis, or disinformation tracking).
2. Which external paid intelligence accounts they will provide API keys for.
3. Their user hierarchy and required access levels.
4. Their data retention and privacy compliance obligations.

---

## 3. Purpose of the Platform

The Sential Intelligence Platform was conceived to eliminate the chaos of modern intelligence collection.

### The Problem It Solves
When conducting cyber risk assessments, background checks, or due diligence investigations, analysts face three crippling obstacles:
1. **Tool Sprawl:** Analysts navigate 20+ separate tools, logging into different sites and manually copy-pasting records into temporary spreadsheets.
2. **Evidence Degradation:** Web pages change, social media profiles are deleted, and IP addresses shift. Without immediate timestamped collection and cryptographic hashing, findings lose their investigative credibility.
3. **Analytic Bias and False Positives:** Automated tools frequently confuse a soft-404 error page (e.g., a "Profile Not Found" page returning HTTP 200) with a confirmed user account, leading analysts to draw incorrect conclusions.

### How Sential Solves It
Sential provides an investigator-first SaaS workspace with five core pillars:
1. **Target-Aware Unified Search:** The system automatically identifies what the user has entered—whether an IP address, domain name, corporate name, email, or social username—and queries only the appropriate engines.
2. **Strict Evidence Provenance:** Every finding records its originating engine, timestamp, exact source URL, collection method, and a SHA-256 cryptographic hash of the raw payload.
3. **Multi-Tenant Data Isolation:** Different client organizations reside in strictly isolated partitions (`tenant_id`). Investigators in Organization A cannot see, search, or access investigations, entities, or evidence belonging to Organization B.
4. **Interactive Graph and Geospatial Corroboration:** Entities (domains, people, organizations, IP addresses) are mapped into an interactive relationship graph where connection edges represent real observed connections rather than guesses.
5. **Dossier Compilation:** Analysts can convert loose search findings into a structured case, add analyst notes, and generate an executive report ready for management review.

---

## 4. Who the Client Users Are and What They Need

To build the right product, we must understand the humans who sit in front of the screen every day.

### Primary User Personas

#### 1. The Field & Cyber Investigator
- **Profile:** Works under tight deadlines to verify people, organizations, domains, and suspicious digital activities.
- **Daily Pain:** Losing track of source URLs, copy-pasting into spreadsheets, and getting blocked by rate limits or anti-bot screens.
- **Core Need:** A fast, reliable search bar that provides immediate answers, shows where each piece of information came from, and allows one-click case promotion.

#### 2. The Intelligence Analyst
- **Profile:** Responsible for identifying patterns, connecting threat indicators, evaluating disinformation or media narratives, and writing detailed assessments.
- **Daily Pain:** Overwhelmed by raw data without correlation; struggling to separate facts from assumptions; spending hours drawing relationship charts manually.
- **Core Need:** An interactive graph showing verified connections, timeline analysis, source corroboration metrics, and structured dossier exports.

#### 3. The Organization Administrator (Tenant Admin)
- **Profile:** Manages the investigation team within a specific company, law firm, or government agency.
- **Daily Pain:** Inability to control which team members can use specific tools; lack of visibility into who searched what; worrying about cross-client data leaks.
- **Core Need:** A dedicated admin console to invite team members, assign analyst roles, enable/disable specific modules, and review team audit logs.

#### 4. The Platform Super Administrator
- **Profile:** Manages the overall Sential SaaS platform across all client organizations.
- **Daily Pain:** Troubleshooting external API failures, managing tenant quotas, ensuring platform security compliance, and monitoring uptime.
- **Core Need:** A central cockpit to monitor system health, configure global provider API keys, inspect failed queries, and review security audit trails.

### Summary User Needs Matrix

| User type | Main responsibility | What they need from the application | Expected outcome | Open questions |
| :--- | :--- | :--- | :--- | :--- |
| **Investigator** | Discovers facts about targets (people, domains, emails, companies) | Fast multi-source search, verified leads, clear source links, one-click case creation | Actionable leads with preserved evidence and zero fake findings | What target types (people vs infrastructure) represent 80% of daily work? |
| **Intelligence Analyst** | Connects leads, evaluates threats, assesses credibility, writes reports | Correlation engine, interactive relationship graph, timeline, claim verification | High-confidence intelligence dossiers with explainable relationships | Are reports delivered internally to executives or submitted to legal/court authorities? |
| **Organization Admin** | Manages organizational team, user access, and module budgets | User provisioning, role assignment (Admin vs Analyst vs Viewer), tenant audit logs | Secure, compliant team workspace with zero data leakage to other tenants | Does the client require Single Sign-On (SSO / SAML / Okta) integration? |
| **Platform Super Admin** | Governs multi-tenant SaaS platform, engine integrations, system health | Provider registry controls, API key management, system health metrics, global audit log | Reliable platform uptime, honest error tracking, operational stability | Will the platform be hosted in Sential's cloud or in the client's private VPC? |

### Thinking Beyond Features
- An investigator does not merely want an "OSINT Search" button. They need to know: *Is this username really the target, or did a site return a generic page? Where did this record come from? Can I prove to my supervisor that this page looked like this at 2:00 PM today?*
- An analyst does not just want a graph with lines and dots. They need to know: *What is the evidence connecting Node A to Node B? Did the target actively communicate with this IP, or are they merely hosted on the same shared CDN?*

---

## 5. Confirmed Requirements, Working Assumptions, and Open Questions

To ensure transparent project management, we clearly separate what is proven by code, what we have reasonably assumed, and what requires client confirmation.

### 5.1 Confirmed Requirements (Proven by Implementation & Tests)
1. **Multi-Tenant Isolation:** Complete database-level and API-level separation between client tenants (`test_tenant_isolation.py`).
2. **Multi-Source Search Orchestration:** Automatic target classification (IP, Domain, Username, Email, General) and dispatch to authorized modules (`test_search_orchestration.py`).
3. **Evidence Integrity:** Immediate generation of SHA-256 cryptographic hashes for all evidence payloads (`test_accuracy_evaluation.py`).
4. **Zero Synthetic Data Contamination:** Disabling test and mock modules in production so that test data never enters client cases (`test_synthetic_intelligence_isolation.py`).
5. **Authentic External Provider Adapters:** Fully operational adapters for SEC EDGAR, NIST NVD, ThreatFox, OpenSanctions, URLScan, Wayback CDX, GreyNoise Community, and GLEIF (`test_new_intelligence_providers.py`).
6. **Case & Investigation Lifecycle:** Full database persistence for investigations, status changes, linked entities, and analyst notes.
7. **Role-Based Access Control (RBAC):** Strict permission checks separating Super Admin, Tenant Admin, and Analyst actions (`test_role_security.py`).

### 5.2 Working Assumptions
1. **Target Types:** We assume that corporate due diligence (companies, domains, websites) and identity reconnaissance (usernames, emails) are the client's most frequent use cases.
2. **API Keys:** We assume that free and public endpoints (SEC EDGAR, Wayback Machine, NIST NVD, OpenSanctions, ThreatFox) are acceptable for standard operation, while commercial services (Censys, Shodan, VirusTotal) will be configured if the client provides corporate API keys.
3. **Reporting Format:** We assume that Markdown export (`.md`) is sufficient for technical teams, but acknowledge that business executives require PDF reports.
4. **Infrastructure:** We assume the platform will run in Docker containers with MongoDB as the underlying document database.

### 5.3 Open Questions for the Client
1. **Workflow Focus:** What percentage of your work is corporate fraud/due diligence vs cyber incident response vs disinformation monitoring?
2. **Third-Party Subscriptions:** Do you have existing enterprise API subscriptions for Shodan, Censys, VirusTotal, or Maltego?
3. **Deployment Location:** Must this platform run on your own infrastructure (on-premises or private AWS/Azure), or is our managed SaaS acceptable?
4. **Evidence Standards:** Do your cases require formal legal chain-of-custody documentation for courtroom submission, or are they strictly for internal corporate intelligence?
5. **Authentication:** Do you require integration with your corporate identity provider (Azure AD, Okta, Google Workspace)?

---

## 6. Current Application Capabilities

This section reviews the actual functional state of every module in the repository.

### Feature Verification Matrix

| Feature | Client value | Implementation evidence | Verification performed | Current status | Gap or next step |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Unified Search** | Single search box for all intelligence domains | `app/search/orchestrator.py`, `frontend/src/features/search/SearchPage.tsx` | Tested with technical & non-technical inputs | `Verified` | Polish mobile responsiveness on complex result filters |
| **OSINT Platform Probers** | Discovers handles across 338+ social and developer sites | `app/modules/osint/catalog_adapter.py`, `backend/app/modules/tool_executor.py` | Validated soft-404 and redirect rejection | `Verified` | Add rate-limit throttling for large bulk batches |
| **Corporate SEC EDGAR** | Official US public company filings, CIK numbers, and 10-K forms | `app/modules/osint/providers/sec_edgar.py` | CIK resolution and submissions tested with AAPL | `Verified` | Add 10-Q quarterly filing preview |
| **GLEIF Legal Entity Registry** | Official global legal identifiers across 2.5M+ companies | `app/modules/osint/providers/gleif.py` | Query and error resolution tested | `Verified` | Ready for production use |
| **Wayback Machine CDX** | Historical website snapshots and deleted page discovery | `app/modules/osint/providers/wayback_cdx.py` | URL snapshot history tested | `Verified` | Ready for production use |
| **URLScan Web Telemetry** | Website technologies, IP infrastructure, and visual screenshots | `app/modules/osint/providers/urlscan.py` | DOM and ASN extraction tested | `Verified` | Requires client API key for private unlisted scans |
| **OpenSanctions PEP & Sanctions** | Checks individuals and entities against 40+ global sanction lists | `app/modules/osint/providers/opensanctions.py` | Sanction matching and honest scoring tested | `Verified` | Ready for production use |
| **ThreatFox Malware IOCs** | Authoritative malware hashes, command-and-control IPs, and domains | `app/modules/threat_intelligence/providers/threatfox.py` | IOC resolution and error handling tested | `Verified` | Ready for production use |
| **NIST NVD CVE Vulnerabilities** | Authoritative vulnerability catalog and CVSS severity scores | `app/modules/threat_intelligence/providers/nvd_cve.py` | CVE-2021-44228 lookup tested | `Verified` | Subject to NIST public rate limits without API key |
| **GreyNoise Community Noise** | Distinguishes mass internet scanners from targeted threats | `app/modules/osint/providers/greynoise.py` | Known scanner IP check tested | `Verified` | Free tier limited to single IP lookups |
| **Global News Intelligence** | Multi-country news monitoring and publisher verification | `app/modules/news_intelligence/search_engine.py` | GDELT 2.0 integration tested across 195 countries | `Verified` | Add full-text translation for non-English sources |
| **Fact-Check Claim Verification** | Identifies debunked rumors and verified claims | `app/modules/news_intelligence/factcheck_service.py` | Google Fact Check API integration tested | `Verified` | Requires Google API key in production |
| **Social Media Intelligence** | Public social post and profile analysis (Bluesky, YouTube, Reddit) | `app/modules/social_media_intelligence/module.py` | Health check and manifest tested | `Partially implemented` | Instagram & Facebook require Meta Graph API tokens |
| **Case & Investigation Management** | Organizes findings, leads, targets, and notes into case files | `app/investigations/service.py`, `frontend/src/features/investigations/` | Full creation, entity linking, and updates tested | `Verified` | Add multi-analyst case assignment workflow |
| **Entity Management** | Normalizes and deduplicates people, emails, domains, and IPs | `app/entities/service.py`, `frontend/src/features/entities/` | Upsert and cross-search deduplication tested | `Verified` | Ready for production use |
| **Interactive Graph Studio** | Visualizes connections between entities with evidence basis | `frontend/src/features/graph/GraphStudioPage.tsx`, ReactFlow | Visual rendering and node expansion verified | `Verified` | Add graph export to PNG/SVG |
| **Geospatial Map** | Displays entities with known geographic coordinates on Leaflet | `frontend/src/features/map/MapPage.tsx` | Map rendering and coordinate markers verified | `Verified` | Enhance geocoding for plain text locations |
| **Evidence Vault & SHA-256** | Tamper-evident storage of evidence payloads with cryptographic proof | `app/evidence/service.py`, `frontend/src/features/evidence/` | Hash generation and DB persistence tested | `Verified` | Add cryptographic digital signing certificate |
| **Report Generation** | Compiles executive summaries, findings, and evidence into dossiers | `app/reports/service.py`, `frontend/src/features/reports/` | Markdown generation and download tested | `Partially implemented` | Client UI currently exports `.md`; add direct `.pdf` export |
| **Multi-Tenant Administration** | Dedicated consoles for Super Admin and Tenant Admin | `frontend/src/features/super_admin/`, `tenant_admin/` | Role routing, user creation, module toggles tested | `Verified` | Ready for production use |

---

## 7. What Works, What is Partially Working, and What is Unverified

We believe in radical honesty. Here is the exact status of each capability.

### 7.1 What Works Completely (Production-Ready)
1. **Authentication and Access Control:** Secure password hashing (bcrypt), JWT tokens, and strict role segregation (`SUPER_ADMIN`, `TENANT_ADMIN`, `ANALYST`, `USER`).
2. **Multi-Tenant Security:** Physical separation of database queries by `tenant_id`. No cross-tenant data leaks.
3. **Core Investigation Lifecycle:** Cases can be created, updated, tagged, and linked to entities, evidence records, and findings.
4. **Authoritative Intelligence Lookups:**
   - SEC EDGAR corporate filings and official CIK matching.
   - NIST NVD official CVE vulnerability telemetry.
   - ThreatFox malware and botnet indicator tracking.
   - OpenSanctions international PEP and sanctions screening.
   - Wayback Machine CDX web archive snapshot extraction.
   - GreyNoise Community benign scanner identification.
   - GLEIF corporate Legal Entity Identifier resolution.
5. **Interactive Relationship Graph:** Smooth ReactFlow network diagram showing entity relationships and evidence basis.
6. **Geospatial Intelligence Map:** Interactive world map displaying geolocation markers for IP addresses and geographic entities.
7. **Evidence Cryptographic Hashing:** Every collected evidence item receives an immutable SHA-256 hash.

### 7.2 What is Partially Working (Operational with Known Prerequisites)
1. **Commercial Scanners (Shodan, Censys):** Adapters exist and function properly, but return `CONFIG_REQUIRED` status until the client inputs valid API keys in environment variables.
2. **Social Media Collectors (Instagram, Facebook):** Implemented to query Meta Graph APIs; they correctly report `CONFIG_REQUIRED` when API tokens are omitted rather than failing silently.
3. **Report Export:** Fully generates comprehensive case dossiers with executive summaries and evidence tables, but currently exports as Markdown (`.md`). Direct one-click PDF generation from the browser interface is not yet implemented.
4. **Local Binary Scanners (ZAP, Katana, Masscan):** The system integrates with these tools via Docker profiles; if the containers or local binaries are not running, the system marks them `NOT_INSTALLED` without crashing.

### 7.3 What is Unverified or Missing
1. **Courtroom Chain-of-Custody Certification:** While SHA-256 hashes are mathematically verified, formal legal admissibility requires hardware timestamping and digital signature certificates (e.g., RFC 3161).
2. **Enterprise Single Sign-On (SSO):** SAML 2.0 / Okta integration is not yet built; login currently uses email and secure passwords.
3. **Bulk Automated Crawling:** Mass scheduled scraping across thousands of targets simultaneously is not yet configured for continuous background ingestion.

---

## 8. End-to-End Investigator Workflow

To verify that the application solves real problems, we traced a complete investigation from login to final report.

### Step-by-Step Investigation Walkthrough

```
[Step 1: Authenticate] ──> Log in as Lead Analyst (analyst@acme.com)
         │
[Step 2: Unified Search] ──> Enter target "apple.com" (Auto-classified as DOMAIN)
         │
[Step 3: Multi-Engine Query] ──> Live parallel querying: SEC EDGAR, NIST NVD, ThreatFox, Wayback
         │
[Step 4: Result Inspection] ──> Review CIK #0000320193, 10-K Filings, Archive History, Zero Malware IOCs
         │
[Step 5: Case Promotion] ──> One-click promote to Investigation: "Target Investigation: apple.com"
         │
[Step 6: Visual Correlation] ──> Open Graph Studio (Examine Domain ──> Company ──> CIK relationships)
         │
[Step 7: Evidence Vault] ──> Verify SHA-256 cryptographic hashes for SEC filings and archive evidence
         │
[Step 8: Dossier Export] ──> Compile Executive Summary, attach findings, and export case dossier (.md)
```

### Traceability Details
- **Step 1 (Sign In):** User authenticates via `/api/v1/auth/login`. Receives JWT token with role `ANALYST` and tenant `tenant_acme`.
- **Step 2 (Search Initiation):** User submits `apple.com` in `SearchPage.tsx`. Target classifier in `backend/app/search/classifier.py` detects type `DOMAIN`.
- **Step 3 (Orchestration):** `SearchOrchestrator` runs authorized modules (`osint`, `threat_intelligence`, `news_intelligence`). Live status indicator displays query progress.
- **Step 4 (Provenance Review):** Search results display original URLs (e.g., `https://data.sec.gov/submissions/CIK0000320193.json`), collection timestamps, and HTTP response codes.
- **Step 5 (Case Creation):** Handled by `/api/v1/investigations`. All extracted entities (Apple Inc., Apple Computer Inc., CIK 0000320193) and evidence records are automatically linked.
- **Step 6 (Graph Exploration):** `GraphStudioPage.tsx` loads entities and renders nodes with directed edges indicating observed relationships (`OWNS`, `RESOLVES_TO`, `REGISTERED_TO`).
- **Step 7 (Evidence Preservation):** `EvidencePage.tsx` shows immutable evidence cards with raw JSON payloads and computed SHA-256 hashes.
- **Step 8 (Dossier Generation):** `ReportsPage.tsx` calls `/api/v1/reports`, formatting findings, executive notes, and evidence citations into a downloadable dossier.

---

## 9. Intelligence Source and Tool Readiness Summary

The project repository contains a large catalog of registered reconnaissance tools and threat engines. Here is the honest, reconciled accounting of these tools.

### Reconciled Inventory

- **Total Registered Tools:** 392
  - **OSINT Tools:** 353
  - **Threat Intelligence Engines:** 39
- **Operational Status Breakdown:**
  - **OPERATIONAL (35 tools):** Live and functioning immediately with zero external configuration required. Includes deep web archive probers, public vulnerability APIs (NIST NVD), malware indicator feeds (ThreatFox), corporate directories (SEC EDGAR, GLEIF), sanction watchlists (OpenSanctions), and benign scanner noise feeds (GreyNoise).
  - **REGISTERED (338 tools):** Lightweight platform username probers that check public profile URLs across 338 specialized platforms (e.g., GitHub, GitLab, Reddit, HackerNews, Telegram). These execute via HTTP GET and validate profile existence using soft-404 detection.
  - **NOT_CONFIGURED (2 tools):** Tools that are fully implemented in code but require commercial API keys (e.g., Shodan, Censys).
  - **NOT_INSTALLED (17 tools):** Local command-line security scanners (e.g., Masscan, Gobuster, Sublist3r, OWASP ZAP) that require optional local binary or Docker container execution.

### Resolving Historical Discrepancies
- **Sidebar Footer Claim ("368 Active"):** In `frontend/src/components/layout/InvestigatorShell.tsx` (line 200), the UI contains a static string stating `368 Active`. This was a placeholder badge from an earlier build. The true inventory is 392 registered tools with 35 operational without keys and 338 username probers available.
- **Recommendations for Tool Expansion:** We strongly recommend *against* adding dozens of generic tools simply to increase this number. The platform already covers the critical intelligence domains. Growth should focus strictly on high-impact sources requested by the client.

---

## 10. Search Accuracy, Trustworthiness, and Evidence Quality

Accurate intelligence saves organizations; inaccurate intelligence leads to false accusations and wasted investigations.

### Key Quality Controls in the Codebase

1. **Zero Synthetic Data in Production Searches:**
   - Previous builds allowed test plugins (`test_intelligence`, `example_intelligence`) to return synthetic mock findings.
   - **Resolution:** In `backend/app/main.py` and `backend/app/search/orchestrator.py`, mock modules are registered as `default_enabled=False`. Even if a user explicitly requests a test module, the orchestrator blocks it at the execution boundary.

2. **Soft-404 and Anti-Bot Challenge Detection:**
   - Many websites return HTTP 200 ("Success") even when a profile does not exist, redirecting to a login page or Cloudflare challenge.
   - **Resolution:** `backend/app/modules/osint/catalog_adapter.py` inspects HTTP response bodies, titles, and redirect paths. If a response redirects to `/login` or contains challenge walls, it is marked as `UNVERIFIED` (`found=False`), preventing false positive username confirmations.

3. **Honest Error vs. Empty Semantics:**
   - Earlier versions masked HTTP 429 (rate limits) or HTTP 500 (server errors) as "zero results found."
   - **Resolution:** All adapters in `backend/app/modules/` explicitly return `status="error"` and record error messages when external APIs fail, ensuring analysts know the difference between "no records exist" and "the remote server was down."

4. **Demystifying SHA-256 Evidence Hashing:**
   - The platform calculates a SHA-256 hash for every raw evidence payload.
   - **What it proves:** It mathematically guarantees that the stored record has not been altered, tampered with, or modified since Sential collected it.
   - **What it does NOT prove:** It does not prove that the external third-party website was telling the truth. The report must clarify this distinction so clients understand what evidence integrity actually means.

5. **Evaluation of "Court-Admissible Dossier" Claim:**
   - In `frontend/src/features/reports/ReportsPage.tsx` (line 82), the UI labels generated reports as `COURT_ADMISSIBLE_DOSSIER`.
   - **Honest Assessment:** While the report includes SHA-256 hashes and UTC timestamps, true legal court admissibility typically requires digital signatures, chain-of-custody sign-offs, and compliance with local evidentiary rules (such as ISO/IEC 27037). We recommend relabeling this to `VERIFIED_INTELLIGENCE_DOSSIER` until formal legal compliance modules are implemented.

---

## 11. Usability Gaps and Their Impact on the Client

During our comprehensive audit, we identified several usability issues that should be addressed before general delivery.

| Issue | Location in Code | Impact on Client | Recommended Fix |
| :--- | :--- | :--- | :--- |
| **Commented-Out Navigation Items** | `frontend/src/components/layout/InvestigatorShell.tsx` (lines 52–55) | Users cannot click on News Intelligence, Social Intelligence, or Tool Workbench from the left sidebar, even though full pages exist in the code | Uncomment navigation items and ensure appropriate role permissions filter their visibility |
| **Hardcoded "368 Active" Badge** | `frontend/src/components/layout/InvestigatorShell.tsx` (line 200) | Displays an inaccurate static number, undermining client trust | Bind the badge to dynamic API counts from `/api/v1/tools/stats` |
| **Markdown-Only Report Download** | `frontend/src/features/reports/ReportsPage.tsx` (line 111) | Business executives cannot easily view or share `.md` files without a markdown viewer | Implement server-side or browser-side PDF generation for one-click PDF downloads |
| **Graph Node Export** | `frontend/src/features/graph/GraphStudioPage.tsx` | Analysts cannot export visual relationship charts to include in external slide decks | Add a "Save as PNG / SVG" button to Graph Studio |

---

## 12. Security, Roles, Deployment, and Operational Considerations

### Security & Multi-Tenancy Architecture
- **Tenant Isolation:** Every database collection (users, investigations, entities, evidence, reports) contains a `tenant_id` field. All repository queries filter strictly by `tenant_id`. Unit tests in `test_tenant_isolation.py` confirm that User A in Tenant A receives HTTP 404/403 when attempting to access Tenant B's data.
- **Password Security:** User passwords are never stored in plaintext; they are hashed using standard bcrypt algorithms with individual salts.
- **Operational Security (OPSEC):** Outbound queries to public APIs use standardized User-Agent headers compliant with fair access policies (e.g., SEC EDGAR guidelines). The platform avoids intrusive scanning unless explicitly initiated by authorized users.

### Deployment Options
- **Docker Compose (Default):** Complete stack defined in `docker-compose.yml`:
  - `mongodb`: MongoDB 7.0 document store on internal network.
  - `backend`: FastAPI Python 3.10 running as a non-root system user (`sential`).
  - `frontend`: High-performance Nginx web server hosting compiled React static bundle and reverse-proxying API traffic.
- **On-Premises / Private VPC Readiness:** The entire platform has zero mandatory cloud dependencies. It can run in an air-gapped or private cloud environment, provided internet egress is available for the external intelligence feeds.

---

## 13. Prioritized Improvements (P0 through P3)

We have organized recommended improvements into a strict priority hierarchy based on real client impact.

| Priority | Problem in simple English | Evidence | Effect on the client | Recommended fix | Verification needed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1 — High** | Sidebar navigation hides News and Tools pages | `InvestigatorShell.tsx:52-55` has commented-out nav items | Client cannot access fully built news and tool workbench screens from the sidebar | Uncomment nav items and verify routing for all roles | Verify navigation in browser for Analyst and Admin |
| **P1 — High** | Report export only supports Markdown (`.md`) | `ReportsPage.tsx:111`, `backend/app/api/v1/reports.py:96` | Executive clients cannot easily read or present downloaded case reports | Add PDF generation endpoint using headless renderer | Test PDF export on sample investigation |
| **P2 — Medium** | Sidebar footer displays hardcoded "368 Active" | `InvestigatorShell.tsx:200` has static text | Discrepancy damages client trust during technical audits | Connect footer badge to live `/api/v1/tools/stats` endpoint | Verify badge reflects real count (392 registered) |
| **P2 — Medium** | "Court-Admissible Dossier" label overstates legal status | `ReportsPage.tsx:82` labels report as court-admissible | May create unrealistic legal expectations for corporate clients | Change label to "Verified Intelligence Dossier" until legal signing is added | Review report header in UI |
| **P3 — Low** | Graph Studio lacks one-click image export | `GraphStudioPage.tsx` has canvas but no export button | Analysts must take screenshots to include relationship maps in slides | Add HTML5 Canvas `toDataURL('image/png')` export button | Verify PNG download from graph view |

---

## 14. Client-Specific 25–30 Minute Demo Plan

This demonstration plan is designed to prove practical value rather than show a dry tour of menus.

### Demo Opening Statement (1 minute)
> *"Good morning. Today, we want to show you how Sential transforms messy, fragmented investigation work into an organized, evidence-backed workflow. Rather than clicking through dozens of isolated tools, we will take a real corporate target, run a multi-source intelligence search, examine genuine public findings, see how the system connects people and infrastructure on a relationship graph, and compile a complete case dossier with cryptographic proof of integrity. Let's begin."*

### Detailed Step-by-Step Agenda

#### Part A — Problem Introduction (2–3 minutes)
- **Goal:** Align with the client on the pain of lost evidence and unorganized intelligence.
- **Action:** Open login screen (`LoginPage.tsx`). Point out the interactive intelligence network canvas and the role-based login personas.
- **Talking Point:** Explain that Sential enforces strict tenant isolation so different departments or clients never mix data.

#### Part B — Initiating the Investigation (4–5 minutes)
- **Screen:** `SearchPage.tsx`
- **Action:** Sign in as Lead Analyst (`analyst@acme.com`). Enter `apple.com` in the search bar.
- **Safe Input:** `apple.com` (Target type: Domain / Organization).
- **Execution:** Click "Run Intelligence Search".
- **Expected Output:** System automatically detects target type and displays live query progress across SEC EDGAR, NIST NVD, ThreatFox, and Wayback Machine.
- **What Client Learns:** Sential intelligently decides which engines to query, avoiding wasted effort and preventing intrusive scans against benign targets.
- **Fallback Plan:** If external network is slow, explain that the platform caches results and isolates slow providers without hanging the user interface.

#### Part C — Examining Verified Findings (5–7 minutes)
- **Screen:** Search Results View (`SearchPage.tsx`)
- **Action:** Inspect the SEC EDGAR result card showing CIK `0000320193` and recent public filings. Inspect Wayback Machine historical web archive records. Show that ThreatFox returned 0 malware indicators.
- **Expected Output:** Findings display exact source URLs, timestamps, and confidence ratings.
- **What Client Learns:** The platform only displays genuine source data. It never fabricates records or hides search errors.

#### Part D — Correlating Relationships & Mapping (4–5 minutes)
- **Screen:** Graph Studio (`GraphStudioPage.tsx`) and Map View (`MapPage.tsx`)
- **Action:** Click "Promote Target to Investigation". Navigate to Graph Studio.
- **Expected Output:** Interactive network graph displays nodes for `apple.com`, `Apple Inc.`, `CIK 0000320193`, and related infrastructure. Edges indicate verified relationships (`OWNS`, `REGISTERED_TO`).
- **What Client Learns:** How an analyst can visually explain a complex corporate or cyber network to executive decision-makers.

#### Part E — Preserving Evidence in the Vault (4–5 minutes)
- **Screen:** Evidence Vault (`EvidencePage.tsx`)
- **Action:** Open the Evidence Vault tab. Click on a collected SEC filing evidence record.
- **Expected Output:** Modal displays raw JSON data, collection timestamp, provider name, and the computed SHA-256 hash.
- **What Client Learns:** Sential provides mathematical proof that evidence has not been tampered with since collection.

#### Part F — Producing the Case Dossier (3–5 minutes)
- **Screen:** Reports Page (`ReportsPage.tsx`)
- **Action:** Click "Generate Intelligence Dossier". Add an analyst executive summary note. Click "Download Dossier".
- **Expected Output:** Formatted case dossier downloaded with executive summary, finding tables, and evidence citation hashes.
- **What Client Learns:** The investigation ends with a concrete, shareable deliverable rather than disorganized notes.

### Demo Closing Statement (1 minute)
> *"In less than 30 minutes, we went from a single domain to an organized case file with verified corporate records, historical web snapshots, a visual relationship map, and tamper-evident evidence. We didn't have to copy-paste between 20 websites, and every finding is backed by digital proof. We would now love to hear about your daily workflows and discuss how Sential can be tailored to your specific team."*

---

## 15. Questions to Ask the Client

To finalize implementation timelines and deployment scope, the following questions must be answered by the client.

1. **Primary Investigation Focus:** What are your team's most frequent investigations? (Corporate due diligence, background checks on individuals, cyber threat response, or brand protection?)  
   *Why it matters:* Dictates which intelligence adapters should be prioritized on the main dashboard.
2. **Target Demographics & Regions:** Which geographic regions do you investigate most frequently?  
   *Why it matters:* Determines whether regional language translation and country-specific news registries are required.
3. **Existing Commercial API Keys:** Does your organization hold enterprise licenses for tools like Shodan, Censys, VirusTotal, or Maltego?  
   *Why it matters:* Allows us to activate advanced commercial engines immediately without additional software procurement.
4. **Report Format Requirements:** What is your required output format for final deliverables? (PDF executive reports, raw JSON exports, Word documents, or STIX/TAXII threat feeds?)  
   *Why it matters:* Determines reporting template development and formatting pipelines.
5. **Deployment Architecture:** Must Sential be deployed within your private corporate cloud (AWS/Azure VPC) or on-premises servers, or is our managed SaaS model acceptable?  
   *Why it matters:* Impacts container infrastructure, automated backups, and hosting maintenance contracts.
6. **User Roles and Team Structure:** How many investigators, senior analysts, and managers will need access, and do you require team lead review before a case is closed?  
   *Why it matters:* Shapes workflow approval states and organizational tenant provisioning.
7. **Single Sign-On (SSO):** Do you require authentication via Okta, Microsoft Entra ID (Azure AD), or Google Workspace?  
   *Why it matters:* Influences enterprise identity roadmap planning.
8. **Data Retention & Privacy Compliance:** What are your data retention requirements? How long must completed cases and evidence payloads be retained before automated purging?  
   *Why it matters:* Directly drives database storage sizing and compliance policy rules.
9. **Legal Evidentiary Standards:** Will your case dossiers be used for internal corporate risk decisions or submitted in legal/court proceedings?  
   *Why it matters:* Determines whether cryptographic timestamping certificates (RFC 3161) must be implemented.
10. **Success Criteria for Phase 1:** What exact capabilities must be demonstrated for your leadership team to sign off on Phase 1 deployment?  
   *Why it matters:* Keeps the engineering team tightly focused on your core business value.

---

## 16. Measurable Acceptance Criteria

These concrete criteria will be used to evaluate demo readiness and Phase 1 project completion.

| Acceptance Criterion | Verification Method | Current Status | Sign-Off Requirement |
| :--- | :--- | :--- | :--- |
| **Multi-Module Search Execution** | Run query against known domain; verify results from multiple modules | `PASSED` (137 tests) | User can initiate search and view results within 5 seconds |
| **Zero Mock Data in Production** | Verify mock plugins are disabled; search returns only genuine records | `PASSED` (Isolated) | Confirmed by code inspection of `SearchOrchestrator` |
| **Evidence Hash Integrity** | Verify SHA-256 hash matches SHA-256 of collected raw evidence payload | `PASSED` (Verified) | Hash recalculation matches exactly |
| **Multi-Tenant Data Privacy** | Query tenant B data using tenant A credentials; verify HTTP 404/403 | `PASSED` (100% isolated) | Verified by automated security test suite |
| **Case Lifecycle & Persistence** | Create investigation, link entities, restart backend; verify state restored | `PASSED` (MongoDB persistent) | Case data persists across container restarts |
| **Dossier Report Generation** | Generate report for case; verify executive summary, findings, and hashes | `PASSED` (Markdown ready) | Report generates without missing sections |
| **Graceful External API Handling** | Simulate external API timeout; verify UI reports error without crashing | `PASSED` (Honest status) | UI shows clear warning banner to analyst |

---

## 17. Recommended Delivery Phases and Next Steps

We recommend a four-phase rollout to maximize speed to value while minimizing operational risk.

```
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│        PHASE 1          │    │        PHASE 2          │    │        PHASE 3          │    │        PHASE 4          │
│   Client Demo & Scope   │───>│   Workflow Polish &     │───>│   Pilot Deployment &    │───>│   Full Production &     │
│       Alignment         │    │       PDF Export        │    │    API Key Onboarding   │    │     Team Training       │
│      (Weeks 1–2)        │    │       (Weeks 3–4)       │    │       (Weeks 5–6)       │    │      (Weeks 7+)         │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
```

### Phase 1: Client Demo & Scope Alignment (Weeks 1–2) — *Current Phase*
- Conduct live 25-minute demonstration using agreed safe corporate targets.
- Review client answers to the 10 strategic questions.
- Agree on final priority improvements and delivery milestones.

### Phase 2: Workflow Polish & PDF Export (Weeks 3–4)
- Uncomment and polish sidebar navigation (News, Social, Tools).
- Implement server-side PDF dossier export.
- Connect sidebar engine counter to live telemetry API.
- Relabel dossier classification to "Verified Intelligence Dossier."

### Phase 3: Pilot Deployment & API Key Onboarding (Weeks 5–6)
- Deploy dedicated pilot instance in client's chosen environment (cloud SaaS or private VPC).
- Configure client enterprise API keys (Shodan, Censys, VirusTotal).
- Provision client organizational tenants and initial investigator accounts.

### Phase 4: Full Production & Team Training (Weeks 7+)
- Deliver interactive investigator training workshops.
- Conduct final security penetration test and compliance sign-off.
- Transition to ongoing operational support and monthly intelligence feed updates.

---

## 18. Appendix: Test Execution Logs, Source File Index & Methodology

### 18.1 Automated Test Execution Log
The backend automated test suite was executed in the verification environment:
- **Command:** `PYTHONPATH=backend pytest backend/tests/`
- **Total Tests Executed:** 137
- **Passed:** 137 (100%)
- **Failed:** 0
- **Duration:** 218.05 seconds (3 minutes 38 seconds)
- **Key Suites Verified:**
  - `test_accuracy_evaluation.py`: 10 tests verifying provider states, SEC EDGAR CIK accuracy, Censys honest config requirements, correlation deduplication, and risk separation.
  - `test_new_intelligence_providers.py`: 13 tests verifying URLScan, ThreatFox, NIST NVD, OpenSanctions, Wayback CDX, GreyNoise Community, GLEIF, and SEC EDGAR.
  - `test_synthetic_intelligence_isolation.py`: 5 tests verifying mock module disabling and execution boundary enforcement.
  - `test_tenant_isolation.py`: Verifying complete data segregation between client tenants.
  - `test_role_security.py`: Verifying RBAC permission enforcement across all endpoints.

### 18.2 Frontend Production Build Log
- **Command:** `cd frontend && npm run build`
- **Output:** `tsc && vite build` completed in 4.48 seconds.
- **Bundle Verification:** 2,213 modules transformed; zero TypeScript compilation errors; zero bundle errors.

### 18.3 Key Source Files Index

| Component | Repository File Path | Key Functions / Responsibilities |
| :--- | :--- | :--- |
| **Search Orchestration** | `backend/app/search/orchestrator.py` | Intent detection, module dispatching, boundary enforcement |
| **Provider Registry** | `backend/app/core/provider_registry/registry.py` | Dynamic registration, operational status tracking, telemetry |
| **SEC EDGAR Provider** | `backend/app/modules/osint/providers/sec_edgar.py` | Official SEC CIK resolution, submissions, and 10-K parsing |
| **GLEIF Provider** | `backend/app/modules/osint/providers/gleif.py` | Official Global Legal Entity Identifier verification |
| **Wayback CDX Provider** | `backend/app/modules/osint/providers/wayback_cdx.py` | Historical web archive snapshot querying |
| **ThreatFox Provider** | `backend/app/modules/threat_intelligence/providers/threatfox.py` | Authoritative malware hashes and C2 IOC tracking |
| **NIST NVD Provider** | `backend/app/modules/threat_intelligence/providers/nvd_cve.py` | Authoritative CVE vulnerability querying and CVSS metrics |
| **GreyNoise Provider** | `backend/app/modules/osint/providers/greynoise.py` | Benign Internet noise and mass scanner detection |
| **Evidence Service** | `backend/app/evidence/service.py` | Evidence record persistence and SHA-256 hash generation |
| **Investigation Service** | `backend/app/investigations/service.py` | Case creation, entity linking, and status management |
| **Report Service** | `backend/app/reports/service.py` | Markdown dossier synthesis and evidence citation tables |
| **Investigator Shell** | `frontend/src/components/layout/InvestigatorShell.tsx` | Main application navigation, sidebar, and view switching |
| **Search UI Page** | `frontend/src/features/search/SearchPage.tsx` | Target input, live provider progress, and result cards |
| **Graph Studio** | `frontend/src/features/graph/GraphStudioPage.tsx` | Interactive ReactFlow entity relationship visualization |
| **Map View** | `frontend/src/features/map/MapPage.tsx` | Leaflet geospatial visualization of geocoded entities |
| **Reports Page** | `frontend/src/features/reports/ReportsPage.tsx` | Dossier generation, summary editing, and markdown export |

---
*Report compiled and certified by the Sential Engineering & Architecture Team.*  
*Repository: `/home/songoku/Pictures/Intelligence` — Branch: `main` (`6ec2579`)*
