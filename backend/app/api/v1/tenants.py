from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.tenancy.models import TenantRecord, TenantCreateRequest, TenantUpdateRequest
from app.tenancy.service import tenancy_service
from app.audit.logger import audit_logger

router = APIRouter(prefix="/tenants", tags=["Tenancy"])

@router.get("", response_model=List[TenantRecord])
async def list_tenants(current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))):
    return tenancy_service.list_tenants()

@router.post("", response_model=TenantRecord)
async def create_tenant(
    req: TenantCreateRequest,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    tenant = tenancy_service.create_tenant(req)
    audit_logger.log(
        tenant_id=tenant.id,
        user_id=current_user.id,
        action="TENANT_CREATED",
        resource_type="tenant",
        resource_id=tenant.id,
        details={"name": tenant.name, "modules": tenant.entitled_modules}
    )
    return tenant

@router.get("/{tenant_id}", response_model=TenantRecord)
async def get_tenant(tenant_id: str, current_user: UserRecord = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden cross-tenant access")
        
    tenant = tenancy_service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.patch("/{tenant_id}", response_model=TenantRecord)
async def update_tenant(
    tenant_id: str,
    req: TenantUpdateRequest,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    tenant = tenancy_service.update_tenant(tenant_id, req)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
