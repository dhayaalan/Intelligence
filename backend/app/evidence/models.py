from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EvidenceRecord(BaseModel):
    id: str
    tenant_id: str
    investigation_id: Optional[str] = None
    search_id: Optional[str] = None
    source: str
    provider: str
    module: str
    collection_method: str = "automated"
    reference: str = ""
    confidence: float = 1.0
    raw_data: Any = None
    hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
