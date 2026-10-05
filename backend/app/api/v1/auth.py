from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import create_access_token
from app.identity.models import UserRecord
from app.identity.schemas import LoginRequest, TokenResponse, UserResponse
from app.identity.service import identity_service
from app.tenancy.context import get_current_user
from app.audit.logger import audit_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = identity_service.authenticate(req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role.value,
        "tenant_id": user.tenant_id
    }
    access_token = create_access_token(token_payload)
    
    audit_logger.log(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="auth",
        resource_id=user.id
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user.dict())
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserRecord = Depends(get_current_user)):
    return UserResponse(**current_user.dict())
