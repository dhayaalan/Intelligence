# Search Engine & Orchestration

## 1. Module-Agnostic Design

The `SearchOrchestrator` never assumes specific modules exist. It executes dynamically across all authorized modules returned by `AuthorizationService.get_effective_modules_for_user(user)`.

```python
for module_id in effective_module_ids:
    module = module_registry.get_module(module_id)
    execute_isolated_job(module)
```

## 2. Target Classification

Targets are automatically classified by regex and IP heuristics into entity categories:
* `domain` / `subdomain`
* `ip` / `cidr`
* `email`
* `phone`
* `username`
* `url`
* `hash` (MD5, SHA-1, SHA-256)

## 3. Partial Intelligence Tolerance

If one module fails or times out, the search response status transitions to `partial`:
```json
{
  "search_id": "srch_12345",
  "status": "partial",
  "partial_warning": "Search completed with partial intelligence. Threat Intelligence temporarily unavailable.",
  "module_jobs": [
    {"module": "osint", "status": "completed", "sources": ["spiderfoot", "theharvester"]},
    {"module": "threat_intelligence", "status": "failed", "error": "Connection timeout"}
  ]
}
```
The client receives HTTP 200 with partial findings intact.
