from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ProviderStatus(str, Enum):
    REGISTERED = "REGISTERED"
    CONFIGURED = "CONFIGURED"
    HEALTH_CHECK_PENDING = "HEALTH_CHECK_PENDING"
    OPERATIONAL = "OPERATIONAL"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    NOT_INSTALLED = "NOT_INSTALLED"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"

class ProviderMetadata(BaseModel):
    provider_id: str
    name: str
    module_id: str
    category: str
    provider_type: str = "API_ADAPTER"  # CLI_ADAPTER, REST_API, PLATFORM_PROBER, AGGREGATOR, DEEP_ENGINE, SCANNER_ENGINE
    capabilities: List[str] = Field(default_factory=list)
    supported_targets: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    is_enabled: bool = True
    status: str = ProviderStatus.REGISTERED.value
    auth_required: bool = False
    env_vars: List[str] = Field(default_factory=list)
    timeout_seconds: float = 10.0
    rate_limit: Optional[str] = None
    last_health_check: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 1.0

class ProviderToggleRequest(BaseModel):
    enabled: bool

class ProviderFilterQuery(BaseModel):
    module_id: Optional[str] = None
    category: Optional[str] = None
    capability: Optional[str] = None
    search: Optional[str] = None
    status: Optional[str] = None
    enabled_only: bool = False
    page: int = 1
    page_size: int = 50

class ProviderStats(BaseModel):
    total_providers: int
    total_osint_providers: int
    total_threat_intel_providers: int
    enabled_providers: int
    healthy_providers: int
    operational_providers: int = 0
    registered_providers: int = 0
    pending_check_providers: int = 0
    not_configured_providers: int = 0
    not_installed_providers: int = 0
    degraded_providers: int = 0
    status_breakdown: Dict[str, int] = Field(default_factory=dict)
    categories: Dict[str, int] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

