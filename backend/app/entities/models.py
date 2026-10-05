from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.module_sdk.models import EntityType

class EntityRecord(BaseModel):
    id: str
    tenant_id: str
    investigation_id: Optional[str] = None
    type: EntityType
    value: str
    confidence: float = 1.0
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
