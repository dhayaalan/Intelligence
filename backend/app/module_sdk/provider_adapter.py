from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
from app.module_sdk.models import HealthCheckResult, NormalizedModuleResult, SearchContext

class ProviderExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    SUCCESS_EMPTY = "SUCCESS_EMPTY"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CONFIG_REQUIRED = "CONFIG_REQUIRED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    RESTRICTED = "RESTRICTED"
    NOT_FOUND = "NOT_FOUND"
    SKIPPED = "SKIPPED"

class ProviderRequest(BaseModel):
    query: str
    target_type: str = "general"
    config: Dict[str, Any] = {}
    options: Dict[str, Any] = {}

class ProviderResponse(BaseModel):
    provider_id: str
    status: str = "success"  # Supports ProviderExecutionStatus or legacy "success", "error", "skipped"
    raw_data: Any = None
    error: Optional[str] = None
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
