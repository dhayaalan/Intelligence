from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.identity.models import UserRecord, UserRole
from app.identity.schemas import UserCreateRequest, UserUpdateRequest, UserResponse
from app.identity.service import identity_service
from app.tenancy.context import get_current_user, require_roles
from app.audit.logger import audit_logger

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserResponse])
async def list_users(
    tenant_id: Optional[str] = None,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    # Enforce tenant isolation for Tenant Admin
    target_tid = tenant_id if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    users = identity_service.list_users(target_tid)
    return [UserResponse(**u.dict()) for u in users]

@router.post("", response_model=UserResponse)
async def create_user(
    req: UserCreateRequest,
    tenant_id: Optional[str] = None,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    target_tid = tenant_id if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    if not target_tid:
        target_tid = current_user.tenant_id

    # Tenant Admin cannot create Super Admin or another Tenant Admin
    if current_user.role == UserRole.TENANT_ADMIN and req.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant Admin can create Analyst or User roles only"
        )

    try:
        user = identity_service.create_user(
            creator=current_user,
            tenant_id=target_tid,
            request=req
        )
        audit_logger.log(
            tenant_id=target_tid,
            user_id=current_user.id,
            action="USER_CREATED",
            resource_type="user",
            resource_id=user.id,
            details={"email": user.email, "role": user.role.value, "modules": user.assigned_modules}
        )
        return UserResponse(**user.dict())
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    req: UserUpdateRequest,
    current_user: UserRecord = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN))
):
    try:
        updated = identity_service.update_user(user_id, req, current_user)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**updated.dict())
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
