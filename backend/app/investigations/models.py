from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class InvestigationStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    ARCHIVED = "archived"

class TimelineEvent(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    title: str
    description: str
    author: str
    event_type: str = "activity"  # "discovery", "evidence_added", "status_change", "note"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InvestigationNote(BaseModel):
    id: str
    author_id: str
    author_name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvestigationRecord(BaseModel):
    id: str
    tenant_id: str
    title: str
    description: str = ""
    summary: Optional[str] = None
    priority: str = "HIGH"
    status: InvestigationStatus = InvestigationStatus.OPEN
    target: str
    target_type: str
    created_by: str
    selected_modules: List[str] = Field(default_factory=lambda: ["osint", "threat_intelligence"])
    search_id: Optional[str] = None
    entity_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    notes: List[InvestigationNote] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InvestigationCreateRequest(BaseModel):
    title: str
    description: str = ""
    summary: Optional[str] = None
    priority: Optional[str] = "HIGH"
    target: str
    target_type: str
    selected_modules: List[str] = Field(default_factory=lambda: ["osint", "threat_intelligence"])
    search_id: Optional[str] = None

class InvestigationUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[InvestigationStatus] = None

class AddNoteRequest(BaseModel):
    content: str

class PaginatedInvestigationsResponse(BaseModel):
    items: List[InvestigationRecord]
    total: int
    page: int
    page_size: int
    total_pages: int
    module_counts: Dict[str, int] = Field(default_factory=dict)
