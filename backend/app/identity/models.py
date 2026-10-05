from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    TENANT_ADMIN = "TENANT_ADMIN"
    ANALYST = "ANALYST"
    INVESTIGATOR = "INVESTIGATOR"
    USER = "USER"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INVITED = "invited"
    DISABLED = "disabled"

class UserRecord(BaseModel):
    id: str
    email: str
    hashed_password: str
    name: str
    role: UserRole
    tenant_id: str
    assigned_modules: List[str] = Field(default_factory=list)
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
