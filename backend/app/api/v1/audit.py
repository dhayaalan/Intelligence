from fastapi import APIRouter, Depends, Query
from typing import List, Optional, Any
from pydantic import BaseModel
from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.audit.logger import AuditLogEntry, audit_logger

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

class PaginatedAuditResponse(BaseModel):
    items: List[AuditLogEntry]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedAuditResponse)
async def list_audit_logs_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    target_tid = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    res = audit_logger.list_logs_paginated(tenant_id=target_tid, page=page, page_size=page_size, search=search)
    return PaginatedAuditResponse(**res)

@router.get("", response_model=Any)
async def list_audit_logs(
    limit: int = 100,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    target_tid = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    if page is not None or page_size is not None:
        p = page or 1
        ps = page_size or 20
        return audit_logger.list_logs_paginated(tenant_id=target_tid, page=p, page_size=ps, search=search)
    return audit_logger.list_logs(tenant_id=target_tid, limit=limit)
