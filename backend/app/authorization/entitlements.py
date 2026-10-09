from typing import List, Set
from app.tenancy.service import tenancy_service

class EntitlementService:
    """Evaluates tenant-level module entitlements according to SaaS licensing."""

    @staticmethod
    def get_tenant_entitled_modules(tenant_id: str) -> List[str]:
        if tenant_id == "platform_admin" or tenant_id == "system":
            # Platform admins have access to all system capabilities
            return ["osint", "threat_intelligence", "test_intelligence", "news_intelligence"]
            
        tenant = tenancy_service.get_tenant(tenant_id)
        if not tenant:
            return []
        return tenant.entitled_modules

    @staticmethod
    def is_tenant_entitled_to_module(tenant_id: str, module_id: str) -> bool:
        entitled = EntitlementService.get_tenant_entitled_modules(tenant_id)
        return module_id in entitled

    @staticmethod
    def filter_allowed_modules_for_tenant(tenant_id: str, requested_modules: List[str]) -> List[str]:
        entitled = set(EntitlementService.get_tenant_entitled_modules(tenant_id))
        return [m for m in requested_modules if m in entitled]

entitlement_service = EntitlementService()
