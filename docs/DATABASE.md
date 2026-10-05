# Database Schema & Storage Boundaries

## Core Tables (PostgreSQL / Relational Store)

* `tenants`: Primary multi-tenant organization boundaries.
* `users`: Identity accounts with bcrypt passwords, assigned roles, and module entitlements.
* `investigations`: Case files, targets, status, and linked evidence pointers.
* `entities`: Correlated cross-module entities with confidence scores and extensible typed module metadata.
* `relationships`: Directional relationships (`OWNS`, `USES`, `RESOLVES_TO`, etc.) between entities.
* `evidence`: Immutable raw evidence records with SHA-256 cryptographic provenance hashes.
* `searches`: Historical search execution audit records.
* `audit_logs`: Security trace logs keyed by tenant and user.

## Module Schema Isolation

Modules do not alter Core tables directly. Module-specific telemetry and raw outputs are stored in `metadata` JSON attributes or isolated module tables (`osint_records`, `threat_intelligence_records`).
