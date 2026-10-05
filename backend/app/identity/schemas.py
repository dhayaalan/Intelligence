from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.identity.models import UserRole, UserStatus

class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str
    password: Optional[str] = None
    role: UserRole
    assigned_modules: List[str] = []

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    assigned_modules: Optional[List[str]] = None
    status: Optional[UserStatus] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    tenant_id: str
    assigned_modules: List[str]
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
