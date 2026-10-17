from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ModuleHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

class HealthCheckResult(BaseModel):
    module_id: Optional[str] = None
    status: ModuleHealthStatus = ModuleHealthStatus.HEALTHY
    latency_ms: float = 0.0
    message: str = "Operating normally"
    provider_statuses: Dict[str, str] = Field(default_factory=dict)
    details: Dict[str, Any] = Field(default_factory=dict)
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
    PUBLISHER = "publisher"
    ARTICLE = "article"
    CLAIM = "claim"
    NARRATIVE = "narrative"
    EVENT = "event"
    KEYWORD = "keyword"
    TOPIC = "topic"
    LOCATION = "location"
    VEHICLE = "vehicle"
    MEDIA = "media"
    POST = "post"
    VIDEO = "video"
    IMAGE = "image"
    UNKNOWN = "unknown"

class RelationshipType(str, Enum):
    OWNS = "OWNS"
    USES = "USES"
    HOSTED_ON = "HOSTED_ON"
    RESOLVES_TO = "RESOLVES_TO"
    RELATED_TO = "RELATED_TO"
    MENTIONS = "MENTIONS"
    PUBLISHED = "PUBLISHED"
    CORROBORATES = "CORROBORATES"
    CONTRADICTS = "CONTRADICTS"
    QUOTES = "QUOTES"
    AMPLIFIES = "AMPLIFIES"
    REPORTS_ON = "REPORTS_ON"
    REGISTERED_TO = "REGISTERED_TO"
    CONNECTED_TO = "CONNECTED_TO"
    LOCATED_AT = "LOCATED_AT"
    SEEN_ON = "SEEN_ON"
    AUTHORED = "AUTHORED"
    HAS_IDENTIFIER = "HAS_IDENTIFIER"
    ACCOUNT_REFERENCES_ENTITY = "ACCOUNT_REFERENCES_ENTITY"
    ARTICLE_MENTIONS_ENTITY = "ARTICLE_MENTIONS_ENTITY"
    VIDEO_PUBLISHED_BY_CHANNEL = "VIDEO_PUBLISHED_BY_CHANNEL"
    POST_REFERENCES_LOCATION = "POST_REFERENCES_LOCATION"
    ARTICLE_REPORTS_ON_EVENT = "ARTICLE_REPORTS_ON_EVENT"
    EVENT_OCCURS_AT_LOCATION = "EVENT_OCCURS_AT_LOCATION"
    DOMAIN_RESOLVES_TO_IP = "DOMAIN_RESOLVES_TO_IP"
    EVIDENCE_SUPPORTS_RELATIONSHIP = "EVIDENCE_SUPPORTS_RELATIONSHIP"
    POSSIBLE_ASSOCIATION = "POSSIBLE_ASSOCIATION"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    EXPOSED_BY = "EXPOSED_BY"
    CONTAINS = "CONTAINS"
    PRESIDENT = "PRESIDENT"
    FOUNDER = "FOUNDER"
    CO_FOUNDER = "CO_FOUNDER"
    ADVOCACY_DIRECTOR = "ADVOCACY_DIRECTOR"
    ADVISORY_BOARD = "ADVISORY_BOARD"
    POWERED_BY = "POWERED_BY"
    PROJECT_OF = "PROJECT_OF"
    WORKS_WITH = "WORKS_WITH"
    SISTER_NGO = "SISTER_NGO"
    FUNDING = "FUNDING"
    NEXUS = "NEXUS"
    SEMINAR_CIRCUIT = "SEMINAR_CIRCUIT"

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
    basis: str = "DIRECT_OBSERVATION"  # DIRECT_OBSERVATION, INFERRED_COORDINATION, MATCHING_IDENTIFIER, EXPLICIT_SOURCE_STATEMENT, ANALYST_ASSERTION
    methodology: Optional[str] = None
    uncertainty_notes: Optional[str] = None
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
    module: str = ""
    execution_id: str = "default-exec"
    status: str = "completed"  # "completed", "failed", "partial"
    entities: List[EntityPayload] = Field(default_factory=list)
    relationships: List[RelationshipPayload] = Field(default_factory=list)
    evidence: List[EvidencePayload] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0

    def __init__(self, **data: Any) -> None:
        if "module_id" in data and ("module" not in data or not data["module"]):
            data["module"] = data["module_id"]
        super().__init__(**data)

    @property
    def module_id(self) -> str:
        return self.module
