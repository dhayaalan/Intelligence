# Module Architecture & Lifecycle

## 1. Module Independence

Each module operates inside its own domain boundary. A module may fail, crash, or time out without causing platform downtime or aborting search execution:

```text
OSINT failure
     ↓
OSINT reports failed job
     ↓
Search remains active
     ↓
Threat Intelligence completes
     ↓
Investigation continues with partial findings
```

## 2. Standard IntelligenceModule Contract

All modules implement the abstract contract defined in `app.module_sdk.contract.IntelligenceModule`:

```python
class IntelligenceModule(ABC):
    @property
    @abstractmethod
    def manifest(self) -> ModuleManifest:
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        pass

    @abstractmethod
    async def capabilities(self) -> List[str]:
        pass

    @abstractmethod
    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass
```

## 3. Module Lifecycle States

```text
DISCOVERED → REGISTERED → CONFIGURED → ENABLED → HEALTHY → AVAILABLE
                                                              │
                                                        Degradation
                                                              ↓
                                                     DEGRADED / UNAVAILABLE
```
