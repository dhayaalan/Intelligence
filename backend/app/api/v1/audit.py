from fastapi import APIRouter, Depends
from typing import List
from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.audit.logger import AuditLogEntry, audit_logger

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogEntry])
async def list_audit_logs(
    limit: int = 100,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    target_tid = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    return audit_logger.list_logs(tenant_id=target_tid, limit=limit)
