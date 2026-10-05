# Observability, Structured Logging & Tracing

## Trace Identification

Every operation carries structured context across layers:
* `request_id`: Client HTTP request identifier
* `tenant_id`: Derived multi-tenant organization context
* `user_id`: Authenticated user UUID
* `search_id`: Root search orchestrator identifier
* `job_id`: Independent module asynchronous job UUID
* `module_id`: Intelligence module identifier (e.g. `osint`, `threat_intelligence`)
* `provider_id`: External service integration identifier

## Structured JSON Output Example

```json
{
  "timestamp": "2026-10-02T12:45:00.123Z",
  "level": "INFO",
  "message": "DomainEvent: ModuleExecutionCompleted",
  "logger": "sential",
  "tenant_id": "tenant_acme",
  "search_id": "srch_123456",
  "module_id": "osint",
  "job_id": "job_987654"
}
```
Sensitive credentials are automatically masked into `******` by `StructuredJsonFormatter`.
