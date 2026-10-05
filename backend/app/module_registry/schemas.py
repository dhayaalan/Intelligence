from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.module_sdk.manifest import ModuleConfigField
from app.module_sdk.models import ModuleHealthStatus

class ModuleLifecycleState(str, Enum):
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    CONFIGURED = "configured"
    ENABLED = "enabled"
    HEALTHY = "healthy"
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

class ModuleRegistryItem(BaseModel):
    id: str
    name: str
    version: str
    description: str
    enabled: bool = True
    lifecycle_state: ModuleLifecycleState = ModuleLifecycleState.AVAILABLE
    health_status: ModuleHealthStatus = ModuleHealthStatus.HEALTHY
    health_message: str = "Operating normally"
    latency_ms: float = 0.0
    capabilities: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    providers: List[str] = Field(default_factory=list)
    provider_statuses: Dict[str, str] = Field(default_factory=dict)
    configuration_schema: List[ModuleConfigField] = Field(default_factory=list)
    ui_metadata: Dict[str, Any] = Field(default_factory=dict)
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    last_executed_at: Optional[datetime] = None

class ModuleToggleRequest(BaseModel):
    enabled: bool

class ModuleConfigureRequest(BaseModel):
    config: Dict[str, Any]
