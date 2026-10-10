"""
ML Team Integration Contract: Data Models & Schemas

Defines the explicit boundary for future external AI/ML microservices developed
independently by the ML team. Contains zero internal model inference or weights.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MLExecutionStatus(str, Enum):
    NOT_CONFIGURED = "not_configured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class MLContext(BaseModel):
    """Execution context and security envelope passed to external ML services."""
    tenant_id: str
    user_id: str
    investigation_id: Optional[str] = None
    classification_level: str = "TLP:AMBER"
    trace_id: str


class EvidenceReference(BaseModel):
    """Cryptographic evidence reference passed for grounded citation."""
    evidence_id: str
    citation_label: str
    sha256_hash: str
    source_uri: Optional[str] = None
    snippet: Optional[str] = None


class MLAnalysisRequest(BaseModel):
    """Validated input passed to external ML analysis service."""
    target: str
    target_type: str
    query: str
    context: MLContext
    evidence: List[EvidenceReference] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class MLAnalysisResponse(BaseModel):
    """Structured result expected from external ML analysis service."""
    status: MLExecutionStatus
    model_id: Optional[str] = None
    synthesis: Optional[str] = None
    citations: List[EvidenceReference] = Field(default_factory=list)
    key_assertions: List[str] = Field(default_factory=list)
    intelligence_gaps: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None


class MLPersonaCorrelationRequest(BaseModel):
    """Input payload for multi-platform persona correlation."""
    target_handle: str
    context: MLContext
    platforms: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class MLPersonaCorrelationResponse(BaseModel):
    """Structured persona correlation returned from external ML service."""
    status: MLExecutionStatus
    model_id: Optional[str] = None
    discovered_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    credibility_score: Optional[float] = None
    risk_indicators: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None


class MLCapability(BaseModel):
    """Registered external ML capability."""
    name: str
    version: str
    description: str
    endpoint_path: str
    status: MLExecutionStatus
