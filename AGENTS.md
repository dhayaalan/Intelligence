# AGENTS.md — Mandatory Sential Architectural & Engineering Directives

This document establishes the inviolable architectural laws, engineering standards, and reference capability integration rules for all developers and AI coding agents modifying the Sential platform.

---

## 1. Core Platform Isolation & Decoupling

1. **CORE MUST REMAIN MODULE-AGNOSTIC**: Never introduce module-specific business logic, data models, or switch-statements into Core Platform services (`app/core/`, `app/search/orchestrator.py`, `app/domains/`).
2. **NEVER HARDCODE MODULE CHECKS IN CORE**:
   ```python
   # STRICTLY FORBIDDEN IN CORE:
   if module == "osint": ...
   if module == "threat_intelligence": ...
   if provider == "shodan": ...
   if tool == "zap": ...
   ```
3. **NEVER DIRECTLY IMPORT ACROSS MODULE BOUNDARIES**: `modules/osint/` must never import from `modules/threat_intelligence/`, and `modules/social_intelligence/` must never import from `modules/news_intelligence/`. Cross-module communication occurs strictly through standard Core Contracts (`IntelligenceModule`, `ProviderAdapter`, `NormalizedFinding`, `DomainEvent`), shared domain entities, or the Module Registry.
4. **MODULE-ORIENTED INVESTIGATOR NAVIGATION IS MANDATED**:
   The investigator shell navigation is organized around cohesive intelligence disciplines and workspaces:
   - **Workspace**: Search (`/search`), Investigations (`/investigations`), Recent Activity (`/recent`).
   - **Intelligence**: OSINT (`/intelligence/osint`), Social Intelligence (`/intelligence/social`), News Intelligence (`/intelligence/news`), Media & Forensics (`/intelligence/media`), Threat Intelligence (`/intelligence/threat`), Location Intelligence (`/intelligence/location`).
   - **Investigation Resources**: Entities & Relationship Graph (`/resources/entities`), Evidence Vault (`/resources/evidence`), Reports (`/resources/reports`).
   - **Administration**: Users & Roles (`/admin/users`), Module Entitlements (`/admin/modules`), Provider Configuration (`/admin/providers`), Collection Jobs (`/admin/jobs`), Audit Logs (`/admin/audit`), Platform Settings (`/admin/settings`).
   *Rule: Do NOT add separate sidebar entries for individual third-party tools (e.g. SpiderFoot, Shodan, Maltego, ZAP). Those are providers configured within their respective modules.*
5. **DYNAMIC EXTENSIBILITY**: All module executions pass through `ModuleRegistry` and `SearchOrchestrator`. Adding a new intelligence capability requires implementing `IntelligenceModule` and registering via `module_registry.register(module)` with zero modifications to Core Search or Investigation dispatch routines.

---

## 2. Security, Multi-Tenancy & Authorization

6. **NEVER TRUST FRONTEND TENANT IDENTIFIERS**: The authenticated `tenant_id` must ALWAYS be extracted server-side from the validated JWT token (`TenantContext`). Client-supplied tenant IDs must be treated as untrusted input.
7. **MANDATORY SERVER-SIDE RBAC ENFORCEMENT**: Every endpoint enforces role permissions across the 4 canonical roles:
   - `SUPER_ADMIN`: Global platform governance, tenant management, dynamic module enablement, provider configuration, global audit logs.
   - `TENANT_ADMIN`: Organization workspace, user onboarding, entitled module activation, organization audit logs.
   - `ANALYST`: Full investigative capability, search execution, case creation, clue-to-clue chaining, evidence vault sealing, report export.
   - `USER`: Read-only or constrained search and case inspection.
8. **5-STAGE AUTHORIZATION PIPELINE**:
   $$\text{Platform Module Registered} \rightarrow \text{Tenant Entitled} \rightarrow \text{Role Authorized} \rightarrow \text{User Module Assigned} \rightarrow \text{Effective Access}$$
9. **ZERO CLIENT SECRETS**: Secrets, API keys, private tokens, and passwords must never reach frontend bundles, client responses, or unmasked logs.
10. **STRICT TENANT DATA ISOLATION**: Every collection document in MongoDB must include an indexed `tenant_id`. Every query must enforce `{"tenant_id": current_tenant_id}`. Cross-tenant reads or writes are strictly forbidden.

---

## 3. Data Integrity & Zero-Fabrication Mandate

11. **NEVER FABRICATE INTELLIGENCE OR PLACEHOLDERS**:
    - If EXIF metadata, GPS coordinates, C2PA manifests, or OCR text are missing, return explicit `null` / `absent`.
    - Never invent fake IP addresses, mock profiles, synthetic threat scores, or plausible coordinates.
    - Coordinate `(0, 0)` is strictly rejected as a missing-value sentinel.
    - If a provider is unconfigured, return honest status `NOT_CONFIGURED`, `UNAVAILABLE`, or `RATE_LIMITED`.
12. **TAMPER-EVIDENT EVIDENCE VAULT**:
    - Every evidence artifact collected or analyzed must be stamped with a cryptographic SHA-256 hash.
    - Source provenance, collection timestamp, capturing user, and provider attribution must be permanently retained.
13. **FACTUAL VS. INFERRED DISTINCTIONS**:
    - An observed match (e.g., cryptographic SHA-256 identical match) is a fact.
    - A perceptual similarity (e.g., dHash/pHash Hamming distance $\le 10$) is a visual correlation, never biometric or definitive identity proof.
    - Credibility scores reflect transparent factor weights, not absolute truth determinations.

---

## 4. Reference Capability Integration Standards

14. **DATA CONTRACT COMPLIANCE**:
    - Module outputs normalize into standardized contracts (`NormalizedFinding`, `Entity`, `EvidenceRecord`, `MediaRecord`).
    - Raw provider payloads must be preserved in `raw_data` for auditability while exposing clean typed fields.
15. **MODULE & PROVIDER FAILURE ISOLATION**:
    - If an external tool (e.g. Shodan, ZAP, Pytesseract, or an RSS feed) fails, times out, or throws an exception, the provider adapter must catch it, record structured error telemetry, and allow the remaining providers and modules to return partial intelligence.
    - A failure in one provider must NEVER crash the module, search orchestrator, or frontend.
16. **RESOURCE BOUNDS**:
    - Large media files, video frame extraction, and background scans must operate under strict memory caps, timeouts, and asynchronous job boundaries.

---

## 5. Technology Stack & Directory Conventions

17. **DATABASE**: MongoDB (`motor` / `pymongo`) is the primary production database. PostgreSQL is strictly prohibited. Neo4j is utilized for property graph relationship queries. Redis manages job caching and broker queues.
18. **FRONTEND**: React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui components, and TanStack React Query for server state. RTK Query is strictly prohibited.
19. **DOCUMENTATION INTEGRITY**: The top-level `docs/` folder has been consolidated into `AGENTS.md` and `README.md`. Do NOT re-create a top-level `docs/` folder; maintain architectural guidance inside `AGENTS.md` and `README.md`.
