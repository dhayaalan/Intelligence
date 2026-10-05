# AGENTS.md — Mandatory AI Coding Directives

This document establishes the inviolable architectural laws for all AI agents and developers modifying this codebase.

## 1. Core Platform Isolation
1. **CORE MUST REMAIN MODULE-AGNOSTIC**: Never put module-specific business logic in the Core Platform.
2. **NEVER HARDCODE MODULE CHECKS**: Under no circumstances should Core Search or Core Services contain logic such as:
   ```python
   # STRICTLY FORBIDDEN:
   if module == "osint": ...
   if module == "threat_intelligence": ...
   if provider == "shodan": ...
   if tool == "zap": ...
   ```
3. **NEVER HARDCODE PROVIDER-SPECIFIC LOGIC INTO CORE**: Never write tool-specific branches inside Core search, entities, evidence, or investigations.
4. **NEVER DIRECTLY IMPORT ONE MODULE INTO ANOTHER**: `osint/` must NEVER import from `threat_intelligence/`, and `threat_intelligence/` must NEVER import from `osint/`. Communication occurs strictly through standard Core Contracts, Domain Events, or the Module SDK.
5. **NEVER CREATE PROVIDER-SPECIFIC SIDEBAR NAVIGATION**: The investigator sidebar is strictly:
   ```text
   Search
   Investigations
   Recent
   ```
   Do NOT add sidebar navigation for SpiderFoot, Shodan, Maltego, ZAP, DNS, etc. Those are providers.
6. **DO NOT CREATE TOOL-SPECIFIC TABS OR MODULE SWITCHERS**: Do not expose OSINT or Threat Intelligence as top-level navigation tabs for investigators. The primary investigator experience is unified Search and Investigation.
7. **DO NOT CREATE MODULE-SPECIFIC CONDITIONS IN CORE**: All module executions must pass through the `ModuleRegistry` and `SearchOrchestrator` contracts.

## 2. Security, Multi-Tenancy & Authorization
8. **NEVER TRUST TENANT ID FROM FRONTEND**: The authenticated `tenant_id` must always be derived from the validated JWT token (`TenantContext`).
9. **NEVER TRUST FRONTEND ROLE OR PERMISSIONS**: Server-side RBAC checks enforce all 4 roles: `SUPER_ADMIN`, `TENANT_ADMIN`, `ANALYST`, `USER`.
10. **NEVER STORE SECRETS IN SOURCE CODE**: API keys, JWT secrets, passwords, and private hashes must never be exposed to the client or logged in plaintext. Use `.env` and runtime secure configuration.
11. **PRESERVE TENANT ISOLATION**: Every tenant-owned document in MongoDB must include `tenant_id`. Cross-tenant queries are strictly prevented.

## 3. Tool, Provider & Module Standards
12. **PROVIDERS MUST IMPLEMENT THE PROVIDER CONTRACT**: Every tool must implement `ProviderAdapter` with real preflight, health checks, execution logic, error handling, and normalized findings.
13. **NEW TOOLS MUST BE ADDED AS PROVIDERS**: When adding a new capability, wrap it in a `ProviderAdapter` and register it through `ProviderRegistry`.
14. **NEW INTELLIGENCE DOMAINS MUST BE ADDED AS MODULES**: New domains (e.g. `dark_web`, `crypto`, `geospatial`) must implement `IntelligenceModule` and register via `module_registry.register(module)` without editing Core Search or Investigation logic.
15. **DO NOT DELETE EXISTING TOOL CAPABILITIES WITHOUT DOCUMENTING WHY**: All 335 OSINT tools and 33 Threat Intelligence engines must remain available and discoverable.
16. **DO NOT SILENTLY OMIT TOOLS FROM SAAS_PLATFORM**: Every tool from the reference codebase must be accounted for in `docs/TOOL_INVENTORY.md` and `docs/tool-inventory.json`.
17. **DO NOT USE STATIC INTELLIGENCE DATA**: Never fabricate fake IP addresses, domains, threats, or profile hits. When unconfigured, providers return real status `NOT_CONFIGURED`, `NOT_INSTALLED`, or graceful skipped responses.

## 4. Database & Frontend Technology Mandates
18. **USE MONGODB**: MongoDB is the primary application database. PostgreSQL is strictly prohibited. Every tenant document contains indexed `tenant_id`.
19. **USE TANSTACK REACT QUERY**: For server state in the frontend. RTK Query is strictly prohibited.
20. **USE SHADCN/UI & TAILWIND CSS**: Minimal, premium, high-information-density dark theme without government-portal design, excessive blue gradients, or unnecessary cards.

## 5. Fault Tolerance & Resilience
21. **PRESERVE MODULE FAILURE ISOLATION**: If a single module encounters an error, timeout, or provider failure, the Search Orchestrator must catch it, record it as a module-level failure, and return partial intelligence. A single module failure must NEVER crash the Search API or frontend.
22. **PRESERVE PROVIDER FAILURE ISOLATION**: If an individual provider (e.g. Shodan, ZAP) fails or times out, the remaining providers within the module must continue executing.
