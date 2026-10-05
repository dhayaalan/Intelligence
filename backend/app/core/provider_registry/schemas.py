from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ProviderMetadata(BaseModel):
    provider_id: str
    name: str
    module_id: str
    category: str
    provider_type: str = "API_ADAPTER"  # CLI_ADAPTER, REST_API, PLATFORM_PROBER, AGGREGATOR
    capabilities: List[str] = Field(default_factory=list)
    supported_targets: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    is_enabled: bool = True
    status: str = "HEALTHY"  # HEALTHY, DEGRADED, NOT_CONFIGURED, RATE_LIMITED, DISABLED
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
    categories: Dict[str, int] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
