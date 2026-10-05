from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.findings.models import FindingRecord, FindingCreate, FindingUpdate
from app.findings.service import finding_service

router = APIRouter(prefix="/findings", tags=["Threat Findings"])

from pydantic import BaseModel

class PaginatedFindingsResponse(BaseModel):
    items: List[FindingRecord]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedFindingsResponse)
async def list_findings_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    investigation_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    findings = finding_service.list_findings(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
        severity=severity,
        status=status,
        search=search
    )
    total = len(findings)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    items = findings[start:start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("", response_model=List[FindingRecord])
async def list_findings(
    investigation_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    current_user: UserRecord = Depends(get_current_user)
):
    findings = finding_service.list_findings(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
        severity=severity,
        status=status,
        search=search
    )
    if page and page_size:
        start = (page - 1) * page_size
        return findings[start:start + page_size]
    return findings

@router.post("", response_model=FindingRecord)
async def create_finding(
    data: FindingCreate,
    current_user: UserRecord = Depends(get_current_user)
):
    return finding_service.create_finding(
        tenant_id=current_user.tenant_id,
        data=data
    )

@router.get("/{finding_id}", response_model=FindingRecord)
async def get_finding(
    finding_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    fnd = finding_service.get_finding(current_user.tenant_id, finding_id)
    if not fnd:
        raise HTTPException(status_code=404, detail="Finding not found in current tenant scope")
    return fnd

@router.patch("/{finding_id}", response_model=FindingRecord)
async def update_finding(
    finding_id: str,
    update: FindingUpdate,
    current_user: UserRecord = Depends(get_current_user)
):
    fnd = finding_service.update_finding(current_user.tenant_id, finding_id, update)
    if not fnd:
        raise HTTPException(status_code=404, detail="Finding not found in current tenant scope")
    return fnd
