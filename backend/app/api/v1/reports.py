from fastapi import APIRouter, Depends, HTTPException, Response, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.reports.models import ReportRecord, GenerateReportRequest
from app.reports.service import report_service

router = APIRouter(prefix="/reports", tags=["Intelligence Reports & Dossiers"])

class PaginatedReportsResponse(BaseModel):
    items: List[ReportRecord]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedReportsResponse)
async def list_reports_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    investigation_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    reps = report_service.list_reports(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id
    )
    if search and search.strip():
        q = search.strip().lower()
        reps = [r for r in reps if q in str(r.title or "").lower() or q in str(r.executive_summary or "").lower()]

    total = len(reps)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    items = reps[start:start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("", response_model=List[ReportRecord])
async def list_reports(
    investigation_id: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    current_user: UserRecord = Depends(get_current_user)
):
    reps = report_service.list_reports(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id
    )
    if page and page_size:
        start = (page - 1) * page_size
        return reps[start:start + page_size]
    return reps

@router.post("", response_model=ReportRecord)
async def generate_report(
    req: GenerateReportRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    return report_service.generate_report(
        tenant_id=current_user.tenant_id,
        author_name=current_user.name,
        req=req
    )

@router.get("/{report_id}", response_model=ReportRecord)
async def get_report(
    report_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    rep = report_service.get_report(current_user.tenant_id, report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Dossier report not found in tenant scope")
    return rep

@router.get("/{report_id}/export")
async def export_report_markdown(
    report_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    rep = report_service.get_report(current_user.tenant_id, report_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Dossier report not found in tenant scope")
    
    headers = {
        "Content-Disposition": f"attachment; filename=dossier_{rep.id}.md"
    }
    return Response(content=rep.markdown_content or "", media_type="text/markdown", headers=headers)
