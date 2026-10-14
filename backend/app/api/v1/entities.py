from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Any
from pydantic import BaseModel
from fastapi import Query

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.entities.models import EntityRecord
from app.entities.service import entity_service
from app.module_sdk.models import EntityPayload

router = APIRouter(prefix="/entities", tags=["Entities"])

class PaginatedEntitiesResponse(BaseModel):
    items: List[EntityRecord]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedEntitiesResponse)
async def list_entities_paginated(
    investigation_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    res = entity_service.list_entities_paginated(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
        page=page,
        page_size=page_size,
        search=search,
        type=type
    )
    return PaginatedEntitiesResponse(**res)

@router.get("", response_model=Any)
async def list_entities(
    investigation_id: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    if page is not None or page_size is not None:
        p = page or 1
        ps = page_size or 20
        return entity_service.list_entities_paginated(
            tenant_id=current_user.tenant_id,
            investigation_id=investigation_id,
            page=p,
            page_size=ps,
            search=search,
            type=type
        )
    return entity_service.list_entities(current_user.tenant_id, investigation_id)

@router.post("", response_model=EntityRecord)
async def create_entity(
    payload: EntityPayload,
    investigation_id: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    return entity_service.upsert_entity(current_user.tenant_id, payload, investigation_id)

class CorrelateRequest(BaseModel):
    investigation_ids: Optional[List[str]] = None

@router.get("/correlate", response_model=Any)
async def correlate_entities_get(
    investigation_ids: Optional[List[str]] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    from app.entities.resolver import entity_disambiguation_service
    return entity_disambiguation_service.correlate_entities(
        tenant_id=current_user.tenant_id,
        investigation_ids=investigation_ids
    )

@router.post("/correlate", response_model=Any)
async def correlate_entities_post(
    req: Optional[CorrelateRequest] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    from app.entities.resolver import entity_disambiguation_service
    inv_ids = req.investigation_ids if req else None
    return entity_disambiguation_service.correlate_entities(
        tenant_id=current_user.tenant_id,
        investigation_ids=inv_ids
    )

@router.get("/resolve", response_model=Any)
async def resolve_entity(
    value: str = Query(..., description="Observable value to resolve"),
    type: Optional[str] = Query(None, description="Optional entity type filter"),
    current_user: UserRecord = Depends(get_current_user)
):
    from app.entities.resolver import entity_disambiguation_service
    from app.module_sdk.models import EntityType
    type_enum = None
    if type:
        try:
            type_enum = EntityType(type.lower())
        except Exception:
            pass
    resolved = entity_disambiguation_service.resolve_observable(
        tenant_id=current_user.tenant_id,
        value=value,
        entity_type=type_enum
    )
    if not resolved:
        raise HTTPException(status_code=404, detail="Observable could not be resolved in tenant")
    return resolved

@router.get("/{entity_id}", response_model=EntityRecord)
async def get_entity(
    entity_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    ent = entity_service.get_entity(current_user.tenant_id, entity_id)
    if not ent:
        raise HTTPException(status_code=404, detail="Entity not found in this tenant")
    return ent
