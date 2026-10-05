# MongoDB Architecture & Schema Design

MongoDB is the primary application database for Sential Platform.

## 1. Logical Collections

| Collection | Key Attributes | Primary & Compound Indexes |
| :--- | :--- | :--- |
| **`tenants`** | `id`, `name`, `slug`, `entitled_modules`, `status`, `created_at` | `id` (unique), `slug` (unique) |
| **`users`** | `id`, `email`, `hashed_password`, `name`, `role`, `tenant_id`, `assigned_modules`, `status` | `id` (unique), `email` (unique), `tenant_id`, `(tenant_id, role)` |
| **`modules`** | `id`, `name`, `version`, `enabled`, `lifecycle_state`, `health_status`, `capabilities`, `providers` | `id` (unique), `enabled`, `lifecycle_state` |
| **`module_configurations`** | `tenant_id`, `module_id`, `config`, `updated_at` | `(tenant_id, module_id)` (unique) |
| **`provider_executions`** | `job_id`, `tenant_id`, `search_id`, `module_id`, `provider_id`, `status`, `duration_ms` | `job_id` (unique), `(tenant_id, search_id)`, `(module_id, provider_id)` |
| **`searches`** | `id`, `tenant_id`, `user_id`, `query`, `target_type`, `status`, `entities_count`, `created_at` | `id` (unique), `tenant_id`, `(tenant_id, created_at)` (desc) |
| **`investigations`** | `id`, `tenant_id`, `title`, `description`, `status`, `target`, `target_type`, `created_by`, `timeline`, `notes` | `id` (unique), `tenant_id`, `(tenant_id, status)`, `(tenant_id, updated_at)` (desc) |
| **`entities`** | `id`, `tenant_id`, `investigation_id`, `type`, `value`, `confidence`, `sources`, `metadata`, `last_seen` | `id` (unique), `(tenant_id, investigation_id)`, `(tenant_id, type, value)` |
| **`relationships`** | `id`, `tenant_id`, `source_val`, `target_val`, `relationship_type`, `confidence`, `sources` | `id` (unique), `(tenant_id, source_val, target_val)` |
| **`evidence`** | `id`, `tenant_id`, `investigation_id`, `search_id`, `source`, `provider`, `module`, `raw_data`, `hash` | `id` (unique), `(tenant_id, investigation_id)`, `hash` |
| **`jobs`** | `job_id`, `tenant_id`, `module_id`, `search_id`, `status`, `timeout_seconds`, `started_at`, `duration_ms` | `job_id` (unique), `(tenant_id, search_id)`, `status` |
| **`audit_logs`** | `id`, `tenant_id`, `user_id`, `action`, `resource_type`, `resource_id`, `timestamp` | `id` (unique), `(tenant_id, timestamp)` (desc), `action` |
| **`system_configurations`**| `key`, `value`, `updated_at` | `key` (unique) |

## 2. Multi-Tenant Boundary Enforcement

Every query and write operation on tenant-owned collections strictly requires a validated `tenant_id`:
```python
# Repository pattern enforcement:
async def find_investigation(tenant_id: str, investigation_id: str):
    return await db.investigations.find_one({
        "id": investigation_id,
        "tenant_id": tenant_id
    })
```
Under no circumstances are queries executed without tenant filtering on tenant-scoped collections.
