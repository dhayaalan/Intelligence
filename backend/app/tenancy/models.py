from enum import Enum
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field

class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class TenantRecord(BaseModel):
    id: str
    name: str
    slug: str
    entitled_modules: List[str] = Field(default_factory=list)
    status: TenantStatus = TenantStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TenantCreateRequest(BaseModel):
    name: str
    slug: str
    entitled_modules: List[str] = ["osint", "threat_intelligence", "news_intelligence"]

class TenantUpdateRequest(BaseModel):
    name: str = None
    entitled_modules: List[str] = None
    status: TenantStatus = None
