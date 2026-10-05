# Sential Platform
### Modular Investigator-First OSINT & Threat Intelligence SaaS Platform

Sential is a production-grade intelligence SaaS platform built on a decoupled, modular architecture. It provides threat intelligence analysts and cyber investigators with a unified, high-density investigative workspace powered by autonomous, independently extensible intelligence modules.

---

## Key Architectural Principles

1. **Module Isolation**: Every intelligence module (`OSINT`, `Threat Intelligence`, and future modules) is isolated. Failure of one module or third-party provider never crashes the search engine or other modules.
2. **Core Stability**: The Core Platform owns tenancy, authentication, authorization, search orchestration, entity registries, evidence vaults, and audit logs. The Core contains zero module-specific conditionals (`no if module == 'osint'`).
3. **Pluggable Architecture**: New intelligence capabilities can be added by implementing the `IntelligenceModule` contract and registering them with the `ModuleRegistry` without modifying Core Search or Investigation logic.
4. **Multi-Layer Authorization Pipeline**:
   $$\text{Platform Module} \rightarrow \text{Tenant Entitlement} \rightarrow \text{Role Permission} \rightarrow \text{User Module Assignment} \rightarrow \text{Effective Access}$$
5. **Cryptographic Provenance**: Every evidence item collected is stamped with provider attribution and a tamper-resistant SHA-256 integrity hash.

---

## 4 Strict RBAC Roles

* **SUPER_ADMIN**: Platform Governance Workspace (Tenants, Global Users, Dynamic Module Registry, Providers, Health, Jobs, Audit).
* **TENANT_ADMIN**: Organization Workspace (Organization Users, Analyst/User onboarding, Entitled Modules, Organization Audit).
* **ANALYST**: Investigator Workspace (Default Search, Cases/Investigations, Timeline, Evidence Vault, Notes).
* **USER**: Minimal Investigator Workspace (Search and Read Cases).

---

## Quickstart & Local Execution

### 1. Backend

```bash
cd backend
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5174](http://localhost:5174) in your browser.

### 3. Demo Persona Logins

| Persona | Role | Email | Password | Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Alex Vance** | `SUPER_ADMIN` | `superadmin@sential.io` | `SuperAdmin123!` | Platform-wide |
| **Sarah Connor** | `TENANT_ADMIN` | `admin@acme.com` | `TenantAdmin123!` | Acme Defense Corp |
| **Marcus Wright** | `ANALYST` | `analyst@acme.com` | `Analyst123!` | Acme Defense Corp |
| **Elena Fisher** | `USER` | `user@acme.com` | `User123!` | Acme (OSINT Only) |

---

## Running the Acceptance Test Suite

To run all 15 acceptance tests covering module independence, provider failure isolation, dynamic pluggability, multi-tenant isolation, and RBAC security:

```bash
cd backend
python3 -m pytest tests/ -v
```

---

## Documentation Index

Comprehensive engineering documents are located in `/docs`:

* [ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture and structural overview
* [MODULE_ARCHITECTURE.md](docs/MODULE_ARCHITECTURE.md) — Module isolation and lifecycle specifications
* [MODULE_DEVELOPMENT.md](docs/MODULE_DEVELOPMENT.md) — Guide for building and registering new intelligence modules
* [RBAC.md](docs/RBAC.md) — 4-role model and permission matrix
* [MULTI_TENANCY.md](docs/MULTI_TENANCY.md) — Multi-tenancy boundaries and isolation proofs
* [AUTHORIZATION.md](docs/AUTHORIZATION.md) — Multi-layer entitlement evaluation pipeline
* [ENVIRONMENT.md](docs/ENVIRONMENT.md) — Environment variables and secret configurations
* [SEARCH_ENGINE.md](docs/SEARCH_ENGINE.md) — Module-agnostic Search Orchestrator specifications
* [INVESTIGATION_WORKFLOW.md](docs/INVESTIGATION_WORKFLOW.md) — Single-workspace investigation flow
* [INTEGRATIONS.md](docs/INTEGRATIONS.md) — Provider adapters (SpiderFoot, Shodan, Maltego, DNS, ZAP, IOCs)
* [DATABASE.md](docs/DATABASE.md) — Relational schema and tenant-scoped tables
* [API.md](docs/API.md) — Complete REST and SSE API endpoint reference
* [SECURITY.md](docs/SECURITY.md) — Security guardrails, password hashing, and SSRF prevention
* [OBSERVABILITY.md](docs/OBSERVABILITY.md) — Structured logging, correlation IDs, and metrics
* [DEPLOYMENT.md](docs/DEPLOYMENT.md) — Docker Compose and production deployment instructions
* [AGENTS.md](AGENTS.md) — AI coding agent directives
