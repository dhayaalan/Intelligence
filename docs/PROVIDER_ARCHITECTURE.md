# Provider Architecture & Contract

## 1. Provider Isolation Principle

Tools are **Providers**, never standalone application modules or UI routes.

```text
                  INTELLIGENCE MODULE (e.g. OSINT)
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
     ProviderAdapter       ProviderAdapter       ProviderAdapter
       (SpiderFoot)           (Shodan)              (Maltego)
           │                     │                     │
           ▼                     ▼                     ▼
      External Tool         External API         Transform Hub
```

## 2. Standard Provider Contract

Every provider must implement:

```python
class ProviderAdapter(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier (e.g. 'shodan', 'spiderfoot', 'dns_intel')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        pass

    @abstractmethod
    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        """Executes the query asynchronously against the target."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Performs non-blocking diagnostic health check."""
        pass
```

## 3. Graceful Failure & Unconfigured Status

If API credentials are not provided (e.g. `SHODAN_API_KEY` or `ZAP_API_KEY`), the provider must explicitly report:
```text
Provider Health: NOT_CONFIGURED
```
It must **never** claim to be working or produce fake intelligence. When executed without configuration, it returns a skipped response with reason `Provider not configured`, allowing other providers to complete without error.
