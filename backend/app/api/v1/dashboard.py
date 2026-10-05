from fastapi import APIRouter, Depends
from typing import Any, Dict
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.infrastructure.mongodb.repositories import dashboard_repo

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary"])

@router.get("/summary")
async def get_dashboard_summary(
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    """Calculates live aggregated SaaS metrics directly from MongoDB."""
    return await dashboard_repo.get_summary(current_user.tenant_id)
