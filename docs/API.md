# REST & Real-Time API Reference

All requests must provide an `Authorization: Bearer <JWT>` header unless accessing `/auth/login`.

## Authentication
* `POST /api/v1/auth/login`: Authenticate email/password and obtain JWT access token.
* `GET /api/v1/auth/me`: Retrieve current user profile and role permissions.

## Search
* `POST /api/v1/search`: Execute multi-module intelligence search across authorized modules.
* `GET /api/v1/search/recent`: List recent searches in the caller's tenant.
* `GET /api/v1/search/stream?query=...`: Server-Sent Events (SSE) stream for live job progress.

## Investigations
* `GET /api/v1/investigations`: List cases in caller's tenant.
* `POST /api/v1/investigations`: Create a new investigation.
* `GET /api/v1/investigations/{id}`: Retrieve case details, timeline, and linked resources.
* `PATCH /api/v1/investigations/{id}`: Update case title, description, or status.
* `POST /api/v1/investigations/{id}/notes`: Record an analyst note.
* `POST /api/v1/investigations/{id}/link-evidence`: Link an evidence record to the case.

## Module Registry
* `GET /api/v1/modules`: List registered modules and lifecycle status.
* `POST /api/v1/modules/{id}/toggle`: (Super Admin) Enable or disable a module platform-wide.
* `POST /api/v1/modules/{id}/config`: Configure dynamic module settings.
* `GET /api/v1/modules/{id}/health`: Run on-demand diagnostic health check.

## Administration
* `GET /api/v1/tenants`: (Super Admin) List all tenant organizations.
* `POST /api/v1/tenants`: (Super Admin) Provision new tenant organization.
* `GET /api/v1/users`: List users (tenant-scoped for Tenant Admin).
* `POST /api/v1/users`: Create/invite user (restricted to Analyst/User for Tenant Admin).
* `GET /api/v1/audit`: List audit logs.
