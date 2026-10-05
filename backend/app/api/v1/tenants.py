from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Any
from pydantic import BaseModel
from fastapi import Query

from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.tenancy.models import TenantRecord, TenantCreateRequest, TenantUpdateRequest
from app.tenancy.service import tenancy_service
from app.audit.logger import audit_logger

router = APIRouter(prefix="/tenants", tags=["Tenancy"])

class PaginatedTenantsResponse(BaseModel):
    items: List[TenantRecord]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedTenantsResponse)
async def list_tenants_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    res = tenancy_service.list_tenants_paginated(page=page, page_size=page_size, search=search)
    return PaginatedTenantsResponse(**res)

@router.get("", response_model=Any)
async def list_tenants(
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    if page is not None or page_size is not None:
        p = page or 1
        ps = page_size or 20
        return tenancy_service.list_tenants_paginated(page=p, page_size=ps, search=search)
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
