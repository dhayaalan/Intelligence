from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Optional
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.reports.models import ReportRecord, GenerateReportRequest
from app.reports.service import report_service

router = APIRouter(prefix="/reports", tags=["Intelligence Reports & Dossiers"])

@router.get("", response_model=List[ReportRecord])
async def list_reports(
    investigation_id: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    return report_service.list_reports(
        tenant_id=current_user.tenant_id,
        investigation_id=investigation_id
    )

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
