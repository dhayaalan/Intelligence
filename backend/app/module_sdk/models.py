from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ModuleHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

class HealthCheckResult(BaseModel):
    status: ModuleHealthStatus = ModuleHealthStatus.HEALTHY
    latency_ms: float = 0.0
    message: str = "Operating normally"
    provider_statuses: Dict[str, str] = Field(default_factory=dict)
    checked_at: datetime = Field(default_factory=datetime.utcnow)

class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    EMAIL = "email"
    PHONE = "phone"
    USERNAME = "username"
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP = "ip"
    HOSTNAME = "hostname"
    URL = "url"
    VULNERABILITY = "vulnerability"
    THREAT_INDICATOR = "threat_indicator"
    CERTIFICATE = "certificate"
    TECHNOLOGY = "technology"
    CRYPTO_ADDRESS = "crypto_address"

class RelationshipType(str, Enum):
    OWNS = "OWNS"
    USES = "USES"
    HOSTED_ON = "HOSTED_ON"
    RESOLVES_TO = "RESOLVES_TO"
    RELATED_TO = "RELATED_TO"
    MENTIONS = "MENTIONS"
    REGISTERED_TO = "REGISTERED_TO"
    CONNECTED_TO = "CONNECTED_TO"
    LOCATED_AT = "LOCATED_AT"
    SEEN_ON = "SEEN_ON"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    EXPOSED_BY = "EXPOSED_BY"
    CONTAINS = "CONTAINS"
    DISCOVERED_FROM = "DISCOVERED_FROM"

class EntityPayload(BaseModel):
    id: Optional[str] = None
    type: EntityType
    value: str
    confidence: float = 1.0  # 0.0 to 1.0
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RelationshipPayload(BaseModel):
    id: Optional[str] = None
    source_entity_value: str
    target_entity_value: str
    relationship_type: RelationshipType
    confidence: float = 1.0
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EvidencePayload(BaseModel):
    id: Optional[str] = None
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: str
    module: str
    collection_method: str = "automated"
    reference: str = ""
    confidence: float = 1.0
    raw_data: Any = None
    hash: Optional[str] = None

class SearchContext(BaseModel):
    search_id: str
    tenant_id: str
    user_id: str
    query: str
    target_type: str
    options: Dict[str, Any] = Field(default_factory=dict)

class NormalizedModuleResult(BaseModel):
    module: str
    execution_id: str
    status: str = "completed"  # "completed", "failed", "partial"
    entities: List[EntityPayload] = Field(default_factory=list)
    relationships: List[RelationshipPayload] = Field(default_factory=list)
    evidence: List[EvidencePayload] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0
