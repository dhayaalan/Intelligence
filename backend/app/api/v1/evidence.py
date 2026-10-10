import hashlib
import os
import re
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional, Dict, Any
from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.evidence.models import EvidenceRecord
from app.evidence.service import evidence_service
from app.module_sdk.models import EvidencePayload
from app.audit.logger import audit_logger

router = APIRouter(prefix="/evidence", tags=["Evidence Vault"])

EVIDENCE_STORAGE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../storage/evidence")
)

from pydantic import BaseModel

class PaginatedEvidenceResponse(BaseModel):
    items: List[EvidenceRecord]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("/paginated", response_model=PaginatedEvidenceResponse)
async def list_evidence_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    investigation_id: Optional[str] = None,
    search_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
) -> Dict[str, Any]:
    records = evidence_service.list_evidence(current_user.tenant_id, investigation_id, search_id)
    if search and search.strip():
        q = search.strip().lower()
        records = [
            r for r in records
            if q in str(r.title or "").lower() or q in str(r.description or "").lower() or q in str(r.source or "").lower()
        ]
    total = len(records)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    items = records[start:start + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("", response_model=List[EvidenceRecord])
async def list_evidence(
    investigation_id: Optional[str] = None,
    search_id: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    current_user: UserRecord = Depends(get_current_user)
):
    records = evidence_service.list_evidence(current_user.tenant_id, investigation_id, search_id)
    if page and page_size:
        start = (page - 1) * page_size
        return records[start:start + page_size]
    return records

@router.post("", response_model=EvidenceRecord)
async def store_evidence(
    payload: EvidencePayload,
    investigation_id: Optional[str] = None,
    search_id: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    return evidence_service.store_evidence(current_user.tenant_id, payload, investigation_id, search_id)

@router.post("/upload", response_model=EvidenceRecord)
async def upload_evidence_file(
    file: UploadFile = File(...),
    investigation_id: Optional[str] = Form(None),
    source: Optional[str] = Form("Direct Upload"),
    current_user: UserRecord = Depends(get_current_user)
):
    """Uploads a binary or document evidence file, computes SHA-256 seal, and stores safely."""
    content = await file.read()
    sha256_hash = hashlib.sha256(content).hexdigest()
    ev_id = f"ev_{uuid.uuid4().hex[:12]}"
    
    # Path traversal defense: extract base filename and sanitize
    raw_name = file.filename or "uploaded_file"
    base_name = os.path.basename(raw_name)
    sanitized_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', base_name)
    if not sanitized_name:
        sanitized_name = "uploaded_file"

    tenant_dir = os.path.join(EVIDENCE_STORAGE_DIR, current_user.tenant_id)
    os.makedirs(tenant_dir, exist_ok=True)
    file_path = os.path.join(tenant_dir, f"{ev_id}_{sanitized_name}")
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    payload = EvidencePayload(
        id=ev_id,
        source=source or "Direct Upload",
        provider="manual_upload",
        module="evidence_vault",
        collection_method="secure_browser_upload",
        reference=sanitized_name,
        confidence=1.0,
        raw_data={
            "filename": sanitized_name,
            "content_type": file.content_type,
            "file_size": len(content),
            "storage_path": file_path,
        },
        hash=sha256_hash,
        timestamp=datetime.utcnow().isoformat()
    )
    
    record = evidence_service.store_evidence(
        tenant_id=current_user.tenant_id,
        payload=payload,
        investigation_id=investigation_id
    )
    
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="EVIDENCE_UPLOADED",
        resource_type="evidence",
        resource_id=ev_id,
        details={"filename": sanitized_name, "hash": sha256_hash, "size": len(content)}
    )
    
    return record

@router.get("/{evidence_id}", response_model=EvidenceRecord)
async def get_evidence(
    evidence_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    ev = evidence_service.get_evidence(current_user.tenant_id, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found in this tenant")
    return ev

@router.post("/{evidence_id}/verify")
async def verify_evidence_hash(
    evidence_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """Executes authentic bitwise hash verification against the stored artifact or payload."""
    ev = evidence_service.get_evidence(current_user.tenant_id, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found in this tenant")
    
    storage_path = ev.raw_data.get("storage_path") if ev.raw_data else None
    computed_hash = None
    verification_status = "VALIDATED"
    is_verified = False
    message = ""

    if storage_path and os.path.exists(storage_path):
        try:
            with open(storage_path, "rb") as f:
                disk_content = f.read()
            computed_hash = hashlib.sha256(disk_content).hexdigest()
            if computed_hash == ev.hash:
                is_verified = True
                verification_status = "VALIDATED"
                message = "Bitwise SHA-256 hash verified directly against stored physical evidence file on disk."
            else:
                is_verified = False
                verification_status = "TAMPERED"
                message = f"INTEGRITY VIOLATION: Computed hash '{computed_hash}' does not match genesis anchor '{ev.hash}'."
        except Exception as e:
            verification_status = "READ_ERROR"
            message = f"Error reading stored artifact from disk: {str(e)}"
    elif ev.raw_data and ("raw_content" in ev.raw_data or "extracted_text" in ev.raw_data):
        raw_text = str(ev.raw_data.get("raw_content") or ev.raw_data.get("extracted_text"))
        computed_hash = hashlib.sha256(raw_text.encode()).hexdigest()
        is_verified = (computed_hash == ev.hash)
        verification_status = "VALIDATED" if is_verified else "TAMPERED"
        message = (
            "Verified against raw evidence payload." if is_verified
            else f"INTEGRITY VIOLATION: Computed payload hash does not match genesis anchor."
        )
    else:
        # File is not on disk and no raw content payload
        verification_status = "FILE_NOT_FOUND"
        is_verified = False
        message = "Underlying physical evidence file not found in storage. Cannot certify cryptographic integrity."

    return {
        "id": ev.id,
        "recorded_hash": ev.hash,
        "computed_hash": computed_hash,
        "verified": is_verified,
        "status": verification_status,
        "genesis_match": is_verified,
        "message": message,
        "verified_at": datetime.utcnow().isoformat(),
        "tenant_id": current_user.tenant_id
    }
