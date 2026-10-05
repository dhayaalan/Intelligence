from typing import List, Optional
import uuid
from datetime import datetime
from app.core.database import db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.identity.models import UserRecord, UserRole, UserStatus
from app.identity.schemas import UserCreateRequest, UserUpdateRequest, UserResponse
from app.authorization.service import authorization_service
from app.authorization.entitlements import entitlement_service
from app.infrastructure.mongodb.repositories import user_repo

class IdentityService:
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[UserRecord]:
        with db._lock:
            data = db.users.get(user_id)
            if data:
                return UserRecord(**data)
        col = user_repo.sync_collection
        if col is not None:
            doc = col.find_one({"id": user_id}, {"_id": 0})
            if doc:
                with db._lock:
                    db.users[user_id] = doc
                return UserRecord(**doc)
        return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserRecord]:
        clean_email = email.strip().lower()
        with db._lock:
            for data in db.users.values():
                if data.get("email", "").lower() == clean_email:
                    return UserRecord(**data)
        col = user_repo.sync_collection
        if col is not None:
            doc = col.find_one({"email": clean_email}, {"_id": 0})
            if doc:
                with db._lock:
                    db.users[doc["id"]] = doc
                return UserRecord(**doc)
        return None

    @staticmethod
    def create_user(creator: UserRecord, tenant_id: str, request: UserCreateRequest) -> UserRecord:
        # Check permissions
        if not authorization_service.can_manage_users(creator, tenant_id, request.role):
            raise PermissionError("Insufficient permissions to create user with this role or in this tenant")
            
        existing = IdentityService.get_user_by_email(request.email)
        if existing:
            raise ValueError(f"User with email '{request.email}' already exists")
            
        # Filter assigned modules to only those entitled to this tenant
        sanitized_modules = entitlement_service.filter_allowed_modules_for_tenant(
            tenant_id, request.assigned_modules
        )
        
        user_id = f"usr_{uuid.uuid4().hex[:10]}"
        raw_pwd = request.password or "SentinelSecure123!"
        hashed_pwd = get_password_hash(raw_pwd)
        
        user = UserRecord(
            id=user_id,
            email=request.email.strip().lower(),
            hashed_password=hashed_pwd,
            name=request.name.strip(),
            role=request.role,
            tenant_id=tenant_id,
            assigned_modules=sanitized_modules,
            status=UserStatus.ACTIVE if request.password else UserStatus.INVITED,
            created_at=datetime.utcnow()
        )
        
        u_dict = user.dict()
        with db._lock:
            db.users[user_id] = u_dict
        user_repo._sync_write({"id": user_id}, u_dict)
            
        return user

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[UserRecord]:
        user = IdentityService.get_user_by_email(email)
        if not user or user.status == UserStatus.DISABLED:
            return None
        if not verify_password(password, user.hashed_password):
            return None
            
        user.last_login = datetime.utcnow()
        with db._lock:
            if user.id in db.users:
                db.users[user.id]["last_login"] = user.last_login
        user_repo._sync_write({"id": user.id}, {"last_login": user.last_login.isoformat() if user.last_login else None})
            
        return user

    @staticmethod
    def list_users(tenant_id: Optional[str] = None) -> List[UserRecord]:
        with db._lock:
            users = [UserRecord(**u) for u in db.users.values()]
            if tenant_id:
                users = [u for u in users if u.tenant_id == tenant_id]
            return users

    @staticmethod
    def list_users_paginated(
        tenant_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None
    ) -> dict:
        with db._lock:
            users = [UserRecord(**u) for u in db.users.values()]
            if tenant_id:
                users = [u for u in users if u.tenant_id == tenant_id]
            if role:
                users = [u for u in users if u.role.value == role or u.role == role]
            if search:
                s = search.lower()
                users = [
                    u for u in users
                    if s in u.name.lower() or s in u.email.lower() or s in u.tenant_id.lower()
                ]
            total = len(users)
            skip = (page - 1) * page_size
            paged = users[skip : skip + page_size]
            total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
            return {
                "items": paged,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def update_user(user_id: str, request: UserUpdateRequest, actor: UserRecord) -> Optional[UserRecord]:
        target = IdentityService.get_user_by_id(user_id)
        if not target:
            return None
            
        # Cross-tenant check: Tenant Admin can only update users within their own tenant
        if actor.role != UserRole.SUPER_ADMIN and actor.tenant_id != target.tenant_id:
            raise PermissionError("Cross-tenant user update forbidden")
            
        if request.name is not None:
            target.name = request.name
        if request.role is not None:
            if not authorization_service.can_manage_users(actor, target.tenant_id, request.role):
                raise PermissionError("Cannot promote/change user to this role")
            target.role = request.role
        if request.assigned_modules is not None:
            # Tenant Admin cannot assign modules not entitled to their tenant
            target.assigned_modules = entitlement_service.filter_allowed_modules_for_tenant(
                target.tenant_id, request.assigned_modules
            )
        if request.status is not None:
            target.status = request.status
            
        t_dict = target.dict()
        with db._lock:
            db.users[user_id] = t_dict
        user_repo._sync_write({"id": user_id}, t_dict)
            
        return target

identity_service = IdentityService()
