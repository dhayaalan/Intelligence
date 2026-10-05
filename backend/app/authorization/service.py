from typing import List, Optional
from app.identity.models import UserRecord, UserRole
from app.authorization.roles import ROLE_PERMISSIONS, PERM_SEARCH_EXECUTE, PERM_TENANT_USERS_MANAGE
from app.authorization.entitlements import entitlement_service
from app.module_registry.registry import module_registry

class AuthorizationService:
    """Central authorization service enforcing RBAC and multi-layer module entitlement policies."""
    
    @staticmethod
    def has_permission(user: UserRecord, permission: str) -> bool:
        allowed_perms = ROLE_PERMISSIONS.get(user.role, set())
        return permission in allowed_perms

    @staticmethod
    def can_access_module(user: UserRecord, module_id: str) -> bool:
        """Evaluates the multi-layer module authorization pipeline:
        Platform Level -> Tenant Entitlement -> Role Permission -> User Assignment
        """
        # 1. Platform Module Check: Is module globally registered and enabled?
        if not module_registry.is_module_enabled(module_id):
            return False

        # Super admin has platform-wide access to all enabled modules
        if user.role == UserRole.SUPER_ADMIN:
            return True

        # 2. Tenant Entitlement Check: Is the tenant licensed/entitled to this module?
        if not entitlement_service.is_tenant_entitled_to_module(user.tenant_id, module_id):
            return False

        # 3. Role Permission Check: Can this role execute intelligence searches?
        if not AuthorizationService.has_permission(user, PERM_SEARCH_EXECUTE):
            return False

        # Tenant admin has access to all tenant-entitled modules
        if user.role == UserRole.TENANT_ADMIN:
            return True

        # 4. User Module Assignment Check: Has this user been assigned this module?
        return module_id in user.assigned_modules

    @staticmethod
    def get_effective_modules_for_user(user: UserRecord) -> List[str]:
        """Returns the list of module IDs that pass all authorization layers for this user."""
        all_registered = [m.id for m in module_registry.list_all_modules()]
        effective = []
        for mod_id in all_registered:
            if AuthorizationService.can_access_module(user, mod_id):
                effective.append(mod_id)
        return effective

    @staticmethod
    def can_manage_users(creator: UserRecord, target_tenant_id: str, requested_role: UserRole) -> bool:
        """Validates whether a user is authorized to create/manage users with the specified role."""
        if creator.role == UserRole.SUPER_ADMIN:
            return True
            
        if creator.role == UserRole.TENANT_ADMIN:
            # Tenant Admin cannot manage other tenants
            if creator.tenant_id != target_tenant_id:
                return False
            # Tenant Admin cannot create SUPER_ADMIN or another TENANT_ADMIN
            if requested_role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
                return False
            return True
            
        return False

authorization_service = AuthorizationService()
