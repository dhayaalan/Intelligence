from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FindingRecord(BaseModel):
    id: str
    tenant_id: str
    investigation_id: Optional[str] = None
    search_id: Optional[str] = None
    title: str
    description: str
    type: str = "THREAT_OBSERVATION"
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL
    confidence: int = Field(85, ge=0, le=100)
    module_id: str = "osint"
    provider_id: Optional[str] = None
    source: str = "OSINT Engine"
    status: str = "OPEN"  # OPEN, VERIFIED, MITIGATED
    mitigation: Optional[str] = None
    entity_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    observed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FindingCreate(BaseModel):
    investigation_id: Optional[str] = None
    search_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=250)
    description: str = Field(..., min_length=2)
    type: str = "THREAT_OBSERVATION"
    severity: str = Field("HIGH", description="CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL")
    confidence: int = Field(85, ge=0, le=100)
    module_id: str = "osint"
    provider_id: Optional[str] = None
    source: Optional[str] = None
    status: str = Field("OPEN", description="OPEN, VERIFIED, MITIGATED")
    mitigation: Optional[str] = None
    entity_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FindingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    confidence: Optional[int] = None
    status: Optional[str] = None
    mitigation: Optional[str] = None
