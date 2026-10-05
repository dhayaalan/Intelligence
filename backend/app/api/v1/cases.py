import uuid
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.infrastructure.mongodb.repositories import case_repo
from app.audit.logger import audit_logger

router = APIRouter(prefix="/cases", tags=["Case Management"])

class CaseCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[str] = "HIGH"
    tags: Optional[List[str]] = Field(default_factory=list)
    targets: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class CaseUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class PaginatedCasesResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedCasesResponse)
async def list_cases_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    cases = await case_repo.list_by_tenant(current_user.tenant_id)
    if status and status.upper() != "ALL":
        cases = [c for c in cases if str(c.get("status", "")).upper() == status.upper()]
    if priority and priority.upper() != "ALL":
        cases = [c for c in cases if str(c.get("priority", "")).upper() == priority.upper()]
    if search and search.strip():
        q = search.strip().lower()
        cases = [c for c in cases if q in str(c.get("title", "")).lower() or q in str(c.get("description", "")).lower()]

    total = len(cases)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    items = cases[start:start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("")
async def list_cases(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    current_user: UserRecord = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    cases = await case_repo.list_by_tenant(current_user.tenant_id)
    if status and status.upper() != "ALL":
        cases = [c for c in cases if str(c.get("status", "")).upper() == status.upper()]
    if priority and priority.upper() != "ALL":
        cases = [c for c in cases if str(c.get("priority", "")).upper() == priority.upper()]
    if page and page_size:
        start = (page - 1) * page_size
        return cases[start:start + page_size]
    return cases

@router.post("")
async def create_case(
    req: CaseCreateRequest,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    case_id = f"case_{uuid.uuid4().hex[:10]}"
    now = datetime.utcnow().isoformat()
    case_data = {
        "id": case_id,
        "tenant_id": current_user.tenant_id,
        "title": req.title.strip(),
        "description": req.description.strip() if req.description else "",
        "priority": req.priority.upper() if req.priority else "HIGH",
        "status": "OPEN",
        "tags": req.tags or [],
        "targets": req.targets or [],
        "created_by": current_user.id,
        "created_at": now,
        "updated_at": now
    }
    await case_repo.save(current_user.tenant_id, case_data)
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="CASE_CREATED",
        resource_type="case",
        resource_id=case_id,
        details={"title": req.title}
    )
    return case_data

@router.get("/{case_id}")
async def get_case(
    case_id: str,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    case = await case_repo.get_by_id(current_user.tenant_id, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found in current organization scope")
    return case

@router.patch("/{case_id}")
async def update_case(
    case_id: str,
    req: CaseUpdateRequest,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    case = await case_repo.get_by_id(current_user.tenant_id, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found in current organization scope")
    
    if req.title is not None:
        case["title"] = req.title.strip()
    if req.description is not None:
        case["description"] = req.description.strip()
    if req.priority is not None:
        case["priority"] = req.priority.upper()
    if req.status is not None:
        case["status"] = req.status.upper()
    if req.tags is not None:
        case["tags"] = req.tags
    case["updated_at"] = datetime.utcnow().isoformat()
    
    await case_repo.save(current_user.tenant_id, case)
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="CASE_UPDATED",
        resource_type="case",
        resource_id=case_id,
        details={"status": case.get("status")}
    )
    return case
