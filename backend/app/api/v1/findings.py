from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.findings.models import FindingRecord, FindingCreate, FindingUpdate
from app.findings.service import finding_service

router = APIRouter(prefix="/findings", tags=["Threat Findings"])

@router.get("", response_model=List[FindingRecord])
async def list_findings(
    investigation_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    return finding_service.list_findings(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id,
        severity=severity,
        status=status,
        search=search
    )

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
