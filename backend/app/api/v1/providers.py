from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.core.provider_registry.registry import provider_registry
from app.core.provider_registry.schemas import (
    ProviderMetadata, ProviderToggleRequest, ProviderStats
)
from app.audit.logger import audit_logger

router = APIRouter(prefix="/providers", tags=["Provider Registry"])

from typing import List, Optional, Any
from pydantic import BaseModel

class PaginatedProvidersResponse(BaseModel):
    items: List[ProviderMetadata]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedProvidersResponse)
async def list_providers_paginated(
    module_id: Optional[str] = Query(None, description="Filter by module: 'osint' or 'threat_intelligence'"),
    category: Optional[str] = Query(None, description="Filter by tool category"),
    capability: Optional[str] = Query(None, description="Filter by capability (e.g. domain, ip, username)"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    search: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    enabled_only: bool = Query(False, description="Filter only enabled providers"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=500),
    current_user: UserRecord = Depends(get_current_user)
):
    all_providers = provider_registry.list_providers(
        module_id=module_id,
        category=category,
        capability=capability,
        target_type=target_type,
        search=search,
        status=status,
        enabled_only=enabled_only
    )
    total = len(all_providers)
    skip = (page - 1) * page_size
    paged = all_providers[skip : skip + page_size]
    total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
    return PaginatedProvidersResponse(
        items=paged,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("", response_model=Any)
async def list_providers(
    module_id: Optional[str] = Query(None, description="Filter by module: 'osint' or 'threat_intelligence'"),
    category: Optional[str] = Query(None, description="Filter by tool category"),
    capability: Optional[str] = Query(None, description="Filter by capability (e.g. domain, ip, username)"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    search: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    enabled_only: bool = Query(False, description="Filter only enabled providers"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=500),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Search and filter registered providers.
    Supports granular discovery across 300+ OSINT platforms and 33 Threat Intel engines.
    """
    all_providers = provider_registry.list_providers(
        module_id=module_id,
        category=category,
        capability=capability,
        target_type=target_type,
        search=search,
        status=status,
        enabled_only=enabled_only
    )
    if page is not None or page_size is not None:
        p = page or 1
        ps = page_size or 24
        total = len(all_providers)
        skip = (p - 1) * ps
        paged = all_providers[skip : skip + ps]
        total_pages = max(1, (total + ps - 1) // ps) if total > 0 else 1
        return {
            "items": paged,
            "total": total,
            "page": p,
            "page_size": ps,
            "total_pages": total_pages
        }
    return all_providers[offset : offset + limit]

@router.get("/stats", response_model=ProviderStats)
async def get_provider_stats(current_user: UserRecord = Depends(get_current_user)):
    """Returns dynamic provider count metrics (300+ OSINT, 33 Threat Intel) and category breakdowns."""
    return provider_registry.get_stats()

@router.get("/{provider_id}", response_model=ProviderMetadata)
async def get_provider(provider_id: str, current_user: UserRecord = Depends(get_current_user)):
    """Retrieves operational metadata and health for an individual provider."""
    meta = provider_registry.get_metadata(provider_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found in registry")
    return meta

@router.post("/{provider_id}/toggle", response_model=ProviderMetadata)
async def toggle_provider(
    provider_id: str,
    req: ProviderToggleRequest,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    """Enables or disables an individual provider (Super Admin only). Failure isolation preserved."""
    meta = provider_registry.get_metadata(provider_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")
        
    if req.enabled:
        provider_registry.enable(provider_id)
    else:
        provider_registry.disable(provider_id)
        
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="PROVIDER_TOGGLED",
        resource_type="provider",
        resource_id=provider_id,
        details={"enabled": req.enabled, "module_id": meta.module_id}
    )
    return provider_registry.get_metadata(provider_id)

@router.get("/{provider_id}/health")
async def check_provider_health(
    provider_id: str,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    """Triggers an on-demand real-time health check for a provider."""
    adapter = provider_registry.get_adapter(provider_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Provider adapter '{provider_id}' not found")
        
    result = await adapter.health_check()
    return {
        "provider_id": provider_id,
        "status": result.status.value,
        "latency_ms": result.latency_ms,
        "message": result.message,
        "checked_at": result.checked_at.isoformat()
    }
