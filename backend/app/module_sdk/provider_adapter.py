from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel
from app.module_sdk.models import HealthCheckResult, NormalizedModuleResult, SearchContext

class ProviderRequest(BaseModel):
    query: str
    target_type: str
    config: Dict[str, Any] = {}
    options: Dict[str, Any] = {}

class ProviderResponse(BaseModel):
    provider_id: str
    status: str = "success"  # "success", "error", "skipped"
    raw_data: Any = None
    error: str = None
    duration_ms: float = 0.0

class ProviderAdapter(ABC):
    """Abstract adapter interface that all provider integrations must implement."""
    
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
        """Executes the provider search/query against the target."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """Evaluates health of the provider."""
        pass
