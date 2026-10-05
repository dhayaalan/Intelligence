from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReportRecord(BaseModel):
    id: str
    tenant_id: str
    investigation_id: str
    title: str
    type: str = "COURT_ADMISSIBLE_DOSSIER"  # COURT_ADMISSIBLE_DOSSIER, EXECUTIVE_THREAT_SUMMARY, TECHNICAL_IOC_MANIFEST
    status: str = "READY"  # DRAFT, GENERATING, READY, EXPORTED, ARCHIVED
    author: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    executive_summary: str
    classification: str = "RESTRICTED // TLP:AMBER+STRICT"
    finding_ids: List[str] = Field(default_factory=list)
    evidence_citations: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    markdown_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GenerateReportRequest(BaseModel):
    investigation_id: str
    title: str = Field(..., min_length=3, max_length=250)
    type: str = Field("COURT_ADMISSIBLE_DOSSIER", description="COURT_ADMISSIBLE_DOSSIER, EXECUTIVE_THREAT_SUMMARY, TECHNICAL_IOC_MANIFEST")
    executive_summary: str = Field(..., min_length=10)
    classification: str = Field("RESTRICTED // TLP:AMBER+STRICT")
    finding_ids: List[str] = Field(default_factory=list)
    evidence_citations: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
