from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.identity.models import UserRecord, UserRole
from app.tenancy.context import get_current_user, require_roles
from app.module_registry.registry import module_registry
from app.module_registry.schemas import ModuleRegistryItem, ModuleToggleRequest, ModuleConfigureRequest
from app.authorization.entitlements import entitlement_service
from app.audit.logger import audit_logger

router = APIRouter(prefix="/modules", tags=["Module Registry"])

@router.get("", response_model=List[ModuleRegistryItem])
async def list_modules(current_user: UserRecord = Depends(get_current_user)):
    """Lists modules. Super Admin sees all modules; Tenant users see their entitled modules."""
    all_mods = module_registry.list_all_modules()
    if current_user.role == UserRole.SUPER_ADMIN:
        return all_mods
        
    # Filter by tenant entitlement
    entitled_ids = set(entitlement_service.get_tenant_entitled_modules(current_user.tenant_id))
    return [m for m in all_mods if m.id in entitled_ids]

@router.post("/{module_id}/toggle", response_model=ModuleRegistryItem)
async def toggle_module(
    module_id: str,
    req: ModuleToggleRequest,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN))
):
    """Enables or disables a module platform-wide (Super Admin only)."""
    if req.enabled:
        success = module_registry.enable_module(module_id)
    else:
        success = module_registry.disable_module(module_id)
        
    if not success:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found in registry")
        
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="MODULE_TOGGLED",
        resource_type="module",
        resource_id=module_id,
        details={"enabled": req.enabled}
    )
    
    return module_registry.get_module_info(module_id)

@router.post("/{module_id}/config")
async def configure_module(
    module_id: str,
    req: ModuleConfigureRequest,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    """Configures module parameters dynamically using the module's schema."""
    module_registry.configure_module(current_user.tenant_id, module_id, req.config)
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="MODULE_CONFIGURED",
        resource_type="module",
        resource_id=module_id
    )
    return {"status": "configured", "module_id": module_id}

@router.get("/{module_id}/health", response_model=ModuleRegistryItem)
async def check_module_health(
    module_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    item = await module_registry.check_module_health(module_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
    return item
