from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.module_sdk.manifest import ModuleManifest
from app.module_sdk.models import HealthCheckResult, NormalizedModuleResult, SearchContext

class IntelligenceModule(ABC):
    """Standard contract that every modular intelligence domain must implement."""
    
    @property
    @abstractmethod
    def manifest(self) -> ModuleManifest:
        """Returns the module declarative manifest."""
        pass

    @property
    def module_id(self) -> str:
        return self.manifest.id

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def version(self) -> str:
        return self.manifest.version

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initializes module dependencies, provider adapters, and caches."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Performs non-blocking diagnostic health check across providers."""
        pass

    @abstractmethod
    async def capabilities(self) -> List[str]:
        """Returns supported capabilities (e.g. search, enrichment, entity_discovery)."""
        pass

    @abstractmethod
    async def search(self, context: SearchContext) -> NormalizedModuleResult:
        """Executes module intelligence gathering against target in an isolated fashion."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully closes sessions, clients, and connections."""
        pass
