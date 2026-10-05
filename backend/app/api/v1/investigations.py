from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.investigations.models import (
    InvestigationRecord, InvestigationCreateRequest,
    InvestigationUpdateRequest, AddNoteRequest, PaginatedInvestigationsResponse
)
from app.investigations.service import investigation_service
from app.audit.logger import audit_logger
from fastapi import Query

router = APIRouter(prefix="/investigations", tags=["Investigations"])

class LinkResourceRequest(BaseModel):
    resource_id: str

@router.get("/paginated", response_model=PaginatedInvestigationsResponse)
async def list_investigations_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    module: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    """Paginated investigations listing with accurate real-time module counters."""
    return investigation_service.list_investigations_paginated(
        tenant_id=current_user.tenant_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        module=module,
        search=search
    )

@router.get("", response_model=List[InvestigationRecord])
async def list_investigations(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    return investigation_service.list_investigations(
        tenant_id=current_user.tenant_id,
        status=status,
        priority=priority,
        module=module,
        search=search
    )

@router.post("", response_model=InvestigationRecord)
async def create_investigation(
    req: InvestigationCreateRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    inv = investigation_service.create_investigation(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_name=current_user.name,
        request=req
    )
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="INVESTIGATION_CREATED",
        resource_type="investigation",
        resource_id=inv.id,
        details={"title": inv.title, "target": inv.target}
    )
    return inv

@router.get("/{investigation_id}", response_model=InvestigationRecord)
async def get_investigation(
    investigation_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    inv = investigation_service.get_investigation(current_user.tenant_id, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")
    return inv

@router.patch("/{investigation_id}", response_model=InvestigationRecord)
async def update_investigation(
    investigation_id: str,
    req: InvestigationUpdateRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    inv = investigation_service.update_investigation(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
        request=req,
        user_name=current_user.name
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")
    return inv

@router.post("/{investigation_id}/notes", response_model=InvestigationRecord)
async def add_investigation_note(
    investigation_id: str,
    req: AddNoteRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    inv = investigation_service.add_note(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
        user_id=current_user.id,
        user_name=current_user.name,
        content=req.content
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")
    return inv

@router.post("/{investigation_id}/link-entity")
async def link_entity_to_investigation(
    investigation_id: str,
    req: LinkResourceRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    success = investigation_service.link_entity(current_user.tenant_id, investigation_id, req.resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")
    return {"status": "linked", "entity_id": req.resource_id}

@router.post("/{investigation_id}/link-evidence")
async def link_evidence_to_investigation(
    investigation_id: str,
    req: LinkResourceRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    success = investigation_service.link_evidence(current_user.tenant_id, investigation_id, req.resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")
    return {"status": "linked", "evidence_id": req.resource_id}
