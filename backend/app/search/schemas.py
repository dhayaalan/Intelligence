from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.module_sdk.models import EntityPayload, RelationshipPayload, EvidencePayload

class SearchRequest(BaseModel):
    query: str
    target_type: Optional[str] = None
    search_mode: Optional[str] = "ACTIVE"
    selected_modules: Optional[List[str]] = None
    selected_scopes: Optional[List[str]] = None
    options: Dict[str, Any] = Field(default_factory=dict)

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
    investigation_snapshot: Optional[Dict[str, Any]] = None
    key_findings: List[Dict[str, Any]] = Field(default_factory=list)
    investigative_leads: List[Dict[str, Any]] = Field(default_factory=list)
    pipeline_trace: List[Dict[str, Any]] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime = Field(default_factory=datetime.utcnow)
