from typing import List, Optional
import uuid
from app.core.database import db
from app.tenancy.models import TenantRecord, TenantCreateRequest, TenantUpdateRequest, TenantStatus
from app.infrastructure.mongodb.repositories import tenant_repo

class TenancyService:
    @staticmethod
    def create_tenant(request: TenantCreateRequest) -> TenantRecord:
        tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
        tenant = TenantRecord(
            id=tenant_id,
            name=request.name,
            slug=request.slug,
            entitled_modules=request.entitled_modules,
            status=TenantStatus.ACTIVE
        )
        t_dict = tenant.dict()
        with db._lock:
            db.tenants[tenant_id] = t_dict
        tenant_repo._sync_write({"id": tenant_id}, t_dict)
        return tenant

    @staticmethod
    def get_tenant(tenant_id: str) -> Optional[TenantRecord]:
        with db._lock:
            data = db.tenants.get(tenant_id)
            if data:
                return TenantRecord(**data)
        # Check MongoDB directly if not found in memory
        col = tenant_repo.sync_collection
        if col is not None:
            doc = col.find_one({"id": tenant_id}, {"_id": 0})
            if doc:
                with db._lock:
                    db.tenants[tenant_id] = doc
                return TenantRecord(**doc)
        return None

    @staticmethod
    def list_tenants() -> List[TenantRecord]:
        with db._lock:
            return [TenantRecord(**d) for d in db.tenants.values()]

    @staticmethod
    def update_tenant(tenant_id: str, request: TenantUpdateRequest) -> Optional[TenantRecord]:
        with db._lock:
            data = db.tenants.get(tenant_id)
            if not data:
                return None
            tenant = TenantRecord(**data)
            if request.name is not None:
                tenant.name = request.name
            if request.entitled_modules is not None:
                tenant.entitled_modules = request.entitled_modules
            if request.status is not None:
                tenant.status = request.status
            t_dict = tenant.dict()
            db.tenants[tenant_id] = t_dict
        tenant_repo._sync_write({"id": tenant_id}, t_dict)
        return tenant

tenancy_service = TenancyService()
