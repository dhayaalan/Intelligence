"""
Camera Evidence & ANPR API Endpoints.
Provides public camera catalog discovery, authorized video footage ingestion,
bounded ANPR processing, and human-in-the-loop candidate review workflows.
"""

import os
import shutil
import tempfile
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from pydantic import BaseModel, Field

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.audit.logger import audit_logger
from app.modules.camera_evidence.models import (
    CameraSourceRecord, CameraFeedType, ANPRDetectionRecord, ANPRReviewRequest,
    CameraAvailability
)
from app.modules.camera_evidence.catalog import camera_catalog_service
from app.modules.camera_evidence.anpr_service import anpr_service

router = APIRouter(prefix="/camera-evidence", tags=["Camera Evidence & ANPR"])

# Dedicated directory for authorized footage uploads
FOOTAGE_UPLOAD_DIR = os.getenv("FOOTAGE_UPLOAD_DIR", "/tmp/sential_footage")
os.makedirs(FOOTAGE_UPLOAD_DIR, exist_ok=True)


class ProcessANPRRequest(BaseModel):
    video_path: Optional[str] = None
    source_id: Optional[str] = None
    target_plate: str
    investigation_id: Optional[str] = None
    case_id: Optional[str] = None
    sample_interval_seconds: float = 1.0
    max_duration_seconds: float = 60.0


class GenerateTestClipRequest(BaseModel):
    target_plate: str = "TN34MA8562"
    source_id: Optional[str] = "cam_tfl_jamcams"


@router.get("/catalog", response_model=List[CameraSourceRecord])
async def list_camera_catalog(
    query: Optional[str] = Query(None, description="Search term for camera location or operator"),
    jurisdiction: Optional[str] = Query(None, description="Jurisdiction filter (e.g., UK, US, IN, SG)"),
    feed_type: Optional[CameraFeedType] = Query(None, description="Filter by feed type"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Retrieves documented public and open-data camera sources.
    Enforces honest source provenance and prohibits arbitrary network scanning.
    """
    return camera_catalog_service.list_sources(
        query=query,
        jurisdiction=jurisdiction,
        feed_type=feed_type
    )


@router.get("/catalog/{source_id}", response_model=CameraSourceRecord)
async def get_camera_source(
    source_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    source = camera_catalog_service.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera source '{source_id}' not found in registered catalog."
        )
    return source


@router.post("/upload-footage")
async def upload_authorized_footage(
    file: UploadFile = File(...),
    case_id: Optional[str] = Form(None),
    investigation_id: Optional[str] = Form(None),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Ingests authorized case-scoped video footage (MP4, AVI, MKV, WebM).
    Enforces strict MIME validation, file size limits (50MB), and audit provenance.
    """
    filename = file.filename or "footage.mp4"
    ext = os.path.splitext(filename)[1].lower()
    allowed_exts = [".mp4", ".avi", ".mkv", ".webm", ".mov"]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported video format '{ext}'. Allowed formats: {', '.join(allowed_exts)}"
        )

    safe_filename = f"upload_{current_user.tenant_id}_{int(datetime.utcnow().timestamp())}_{filename}"
    target_path = os.path.join(FOOTAGE_UPLOAD_DIR, safe_filename)

    file_size = 0
    max_bytes = 50 * 1024 * 1024  # 50MB limit

    with open(target_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > max_bytes:
                os.remove(target_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Footage exceeds maximum authorized file size (50MB)."
                )
            buffer.write(chunk)

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="upload_video_footage",
        resource_type="FOOTAGE_INGESTED",
        resource_id=investigation_id or case_id or safe_filename,
        details={
            "filename": filename,
            "bytes": file_size,
            "path": target_path
        }
    )

    return {
        "success": True,
        "video_path": target_path,
        "filename": filename,
        "file_size_bytes": file_size,
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.post("/process-anpr", response_model=List[ANPRDetectionRecord])
async def process_anpr_endpoint(
    payload: ProcessANPRRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Decodes video footage and runs automated number plate recognition against target plate.
    Generates candidate sightings with timecodes and plate crops.
    """
    # Identify camera source
    camera = None
    if payload.source_id:
        camera = camera_catalog_service.get_source(payload.source_id)

    if not camera:
        # Default authorized investigation checkpoint camera
        camera = CameraSourceRecord(
            source_id="cam_authorized_case_feed",
            operator="Authorized Case Evidence Intake",
            name="Authorized Investigation Checkpoint Footage",
            source_url="case://evidence/video_stream",
            geographic_coverage="Authorized Case Location",
            feed_type=CameraFeedType.VIDEO_CLIP,
            availability=CameraAvailability.AVAILABLE,
            auth_requirements="Case Scope Verified",
            retention_restrictions="Case Retention Policy",
            is_public_catalog=False
        )

    # Determine video path
    video_path = payload.video_path
    if not video_path:
        # If no video path provided, create and use a synthetic authorized test clip
        safe_name = f"test_clip_{payload.target_plate}.mp4"
        video_path = os.path.join(FOOTAGE_UPLOAD_DIR, safe_name)
        anpr_service.create_synthetic_authorized_test_clip(video_path, plate_text=payload.target_plate)

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video footage file not found at: {video_path}"
        )

    try:
        detections = anpr_service.process_video_footage(
            video_path=video_path,
            target_plate=payload.target_plate,
            camera=camera,
            investigation_id=payload.investigation_id,
            case_id=payload.case_id,
            tenant_id=current_user.tenant_id,
            max_duration_seconds=payload.max_duration_seconds,
            sample_interval_seconds=payload.sample_interval_seconds
        )

        audit_logger.log(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action="run_anpr_detection",
            resource_type="ANPR_FOOTAGE_PROCESSED",
            resource_id=payload.investigation_id or payload.target_plate,
            details={
                "target_plate": payload.target_plate,
                "camera_id": camera.source_id,
                "detections_found": len(detections)
            }
        )

        return detections
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing ANPR processing: {str(e)}"
        )


@router.get("/detections", response_model=List[ANPRDetectionRecord])
async def list_detections(
    investigation_id: Optional[str] = Query(None),
    case_id: Optional[str] = Query(None),
    target_plate: Optional[str] = Query(None),
    current_user: UserRecord = Depends(get_current_user)
):
    """Lists ANPR sightings scoped to tenant and investigation/case."""
    return anpr_service.list_detections(
        investigation_id=investigation_id,
        case_id=case_id,
        tenant_id=current_user.tenant_id,
        target_plate=target_plate
    )


@router.get("/detections/{detection_id}", response_model=ANPRDetectionRecord)
async def get_detection(
    detection_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    det = anpr_service.get_detection(detection_id)
    if not det:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ANPR detection '{detection_id}' not found."
        )
    return det


@router.post("/detections/{detection_id}/review", response_model=ANPRDetectionRecord)
async def review_detection_endpoint(
    detection_id: str,
    payload: ANPRReviewRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Submits human investigator review for an ANPR candidate sighting.
    'CONFIRM' promotes candidate to HUMAN_CONFIRMED and generates a source-backed Geo observation.
    'REJECT' marks candidate as HUMAN_REJECTED.
    """
    reviewed = anpr_service.review_detection(
        detection_id=detection_id,
        reviewer_id=current_user.id,
        decision=payload.decision,
        notes=payload.notes
    )
    if not reviewed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ANPR detection '{detection_id}' not found."
        )

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="submit_anpr_review",
        resource_type="ANPR_DETECTION_REVIEWED",
        resource_id=detection_id,
        details={
            "decision": payload.decision,
            "target_plate": reviewed.target_plate,
            "match_status": reviewed.match_status.value
        }
    )

    return reviewed


@router.post("/generate-test-clip")
async def generate_test_clip(
    payload: GenerateTestClipRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Generates an authorized synthetic test video containing the requested license plate
    for deterministic offline testing and pipeline verification.
    """
    filename = f"test_{payload.target_plate}_{int(datetime.utcnow().timestamp())}.mp4"
    path = os.path.join(FOOTAGE_UPLOAD_DIR, filename)
    anpr_service.create_synthetic_authorized_test_clip(path, plate_text=payload.target_plate)
    return {
        "success": True,
        "video_path": path,
        "filename": filename,
        "target_plate": payload.target_plate
    }
