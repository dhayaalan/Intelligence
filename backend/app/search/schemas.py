from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.module_sdk.models import EntityPayload, RelationshipPayload, EvidencePayload

class ProviderExecutionStatus(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    RUNNING = "running"
    SUCCESSFUL_WITH_RESULTS = "successful_with_results"
    SUCCESSFUL_WITH_NO_RESULTS = "successful_with_no_results"
    PARTIAL = "partial"
    CONFIGURATION_REQUIRED = "configuration_required"
    AUTHENTICATION_REQUIRED = "authentication_required"
    RESTRICTED = "restricted"
    FAILED = "failed"
    SKIPPED_WITH_REASON = "skipped_with_reason"

class ProviderExecutionRecord(BaseModel):
    provider_id: str
    provider_name: str
    module_id: str
    status: str  # from ProviderExecutionStatus
    reason: Optional[str] = None
    target_type_matched: Optional[str] = None
    items_count: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    target_type: Optional[str] = None
    search_mode: Optional[str] = "ACTIVE"
    selected_modules: Optional[List[str]] = None
    selected_scopes: Optional[List[str]] = None
    options: Dict[str, Any] = Field(default_factory=dict)

class MediaRecord(BaseModel):
    id: str
    media_type: str  # "image" or "video"
    url: str
    thumbnail_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    source_provider: str
    source_platform: Optional[str] = None
    parent_id: Optional[str] = None
    parent_type: Optional[str] = None  # "post", "article", "video", "entity", "profile"
    parent_title: Optional[str] = None
    publication_date: Optional[str] = None
    collection_date: Optional[str] = None
    verification_status: str = "VERIFIED"  # "VERIFIED", "UNVERIFIED", "RESTRICTED", "DEGRADED"
    canonical_source_url: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ModuleJobStatusRecord(BaseModel):
    module: str
    module_name: str
    job_id: str
    status: str  # "completed", "failed", "timed_out", "partial"
    duration_ms: float = 0.0
    sources: List[str] = Field(default_factory=list)
    error: Optional[str] = None

class SearchResponse(BaseModel):
    search_id: str
    query: str
    target_type: str
    intent: Optional[str] = "GENERAL_RESEARCH"
    intent_explanation: Optional[str] = None
    selected_scopes: List[str] = Field(default_factory=lambda: ["ALL INTELLIGENCE"])
    status: str  # "completed", "partial", "failed"
    investigation_id: Optional[str] = None
    partial_warning: Optional[str] = None
    module_jobs: List[ModuleJobStatusRecord] = Field(default_factory=list)
    entities: List[EntityPayload] = Field(default_factory=list)
    relationships: List[RelationshipPayload] = Field(default_factory=list)
    evidence: List[EvidencePayload] = Field(default_factory=list)
    media: List[MediaRecord] = Field(default_factory=list)
    investigation_snapshot: Optional[Dict[str, Any]] = None
    key_findings: List[Dict[str, Any]] = Field(default_factory=list)
    investigative_leads: List[Dict[str, Any]] = Field(default_factory=list)
    pipeline_trace: List[Dict[str, Any]] = Field(default_factory=list)
    collection_completeness_index: Optional[float] = None  # 0.0 to 100.0 (CCI)
    coverage_telemetry: Optional[Dict[str, Any]] = None
    suggested_pivots: List[Dict[str, Any]] = Field(default_factory=list)
    executed_pivots: List[Dict[str, Any]] = Field(default_factory=list)
    multi_stage_metadata: Optional[Dict[str, Any]] = None
    provider_executions: List[ProviderExecutionRecord] = Field(default_factory=list)
    clarification_guidance: Optional[str] = None
    input_classification: Optional[Dict[str, Any]] = None
    search_mode: str = "TEXT_SEARCH"
    active_search_mode_label: str = "Text search"
    is_exact_identifier: bool = False
    normalized_identifier: Optional[str] = None
    validation_error: Optional[str] = None
    stats: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=datetime.utcnow)

