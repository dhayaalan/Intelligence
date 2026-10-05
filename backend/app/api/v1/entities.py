from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.entities.models import EntityRecord
from app.entities.service import entity_service
from app.module_sdk.models import EntityPayload

router = APIRouter(prefix="/entities", tags=["Entities"])

@router.get("", response_model=List[EntityRecord])
async def list_entities(
    investigation_id: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    return entity_service.list_entities(current_user.tenant_id, investigation_id)

@router.post("", response_model=EntityRecord)
async def create_entity(
    payload: EntityPayload,
    investigation_id: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    return entity_service.upsert_entity(current_user.tenant_id, payload, investigation_id)

@router.get("/{entity_id}", response_model=EntityRecord)
async def get_entity(
    entity_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    ent = entity_service.get_entity(current_user.tenant_id, entity_id)
    if not ent:
        raise HTTPException(status_code=404, detail="Entity not found in this tenant")
    return ent
