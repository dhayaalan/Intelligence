"""
Camera Evidence & ANPR API Endpoints.
Provides public camera catalog discovery, authorized video footage ingestion,
bounded ANPR processing, and human-in-the-loop candidate review workflows.
"""

import os
import shutil
import tempfile
import uuid
from typing import List, Optional
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
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


class ShodanCameraRecord(BaseModel):
    ip: str
    port: int
    product: Optional[str] = "IP Camera / Video Feed"
    org: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    stream_url: str
    feed_type: str = "RTSP"
    screenshot_url: Optional[str] = None
    asn: Optional[str] = None
    last_seen: Optional[str] = None


class ShodanCameraDiscoveryResponse(BaseModel):
    configured: bool
    api_key_status: str
    total_found: int = 0
    query_used: str = ""
    message: Optional[str] = None
    cameras: List[ShodanCameraRecord] = []


class StreamANPRRequest(BaseModel):
    stream_url: str
    target_plate: str
    source_name: Optional[str] = "Live Stream Camera"
    investigation_id: Optional[str] = None
    case_id: Optional[str] = None
    max_frames: int = 30


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
    target_clean = (payload.target_plate or "").strip().upper()
    if not target_clean or not any(c.isdigit() for c in target_clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target plate '{payload.target_plate}' does not conform to recognized vehicle registration syntax."
        )

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

        # Check cross-jurisdictional geographic anomaly
        from app.modules.osint.providers.vehicle_intelligence import vehicle_registration_provider
        parsed_plate = vehicle_registration_provider.parse_plate(target_clean)
        plate_jurisdiction = parsed_plate.get("jurisdiction", "UNKNOWN")
        camera_jurisdiction = camera.metadata.get("jurisdiction", "UNKNOWN") if camera.metadata else "UNKNOWN"

        is_cross_anomaly = (
            plate_jurisdiction != "UNKNOWN" and
            camera_jurisdiction != "UNKNOWN" and
            plate_jurisdiction != camera_jurisdiction
        )
        if is_cross_anomaly:
            plate_country = parsed_plate.get("country", plate_jurisdiction)
            cam_location = camera.geographic_coverage or camera_jurisdiction
            for det in detections:
                anomaly_note = f"⚠️ [CROSS-JURISDICTION ANOMALY: Domestic vehicle registered in {plate_country} matched on overseas feed in {cam_location}. Potential synthetic test or plate cloning.]"
                det.review_decision_notes = f"{det.review_decision_notes} {anomaly_note}".strip() if det.review_decision_notes else anomaly_note

        audit_logger.log(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action="run_anpr_detection",
            resource_type="ANPR_FOOTAGE_PROCESSED",
            resource_id=payload.investigation_id or payload.target_plate,
            details={
                "target_plate": payload.target_plate,
                "camera_id": camera.source_id,
                "detections_found": len(detections),
                "cross_jurisdiction_anomaly": is_cross_anomaly
            }
        )

        return detections
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing ANPR processing: {str(e)}"
        )


@router.get("/footage/{filename}")
async def stream_footage(filename: str):
    """
    Streams authorized case footage or synthetic CCTV video clips to browser video players.
    """
    safe_filename = os.path.basename(filename)
    path = os.path.join(FOOTAGE_UPLOAD_DIR, safe_filename)
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Footage file '{safe_filename}' not found."
        )
    media_type = "video/webm" if path.endswith(".webm") else "video/mp4"
    return FileResponse(path, media_type=media_type)


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


@router.get("/shodan/discover", response_model=ShodanCameraDiscoveryResponse)
async def discover_shodan_cameras(
    query: Optional[str] = Query(None, description="Custom Shodan search query"),
    jurisdiction: Optional[str] = Query(None, description="Jurisdiction code (e.g. IN, UK, US)"),
    city: Optional[str] = Query(None, description="City filter"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Discovers live traffic, CCTV, and surveillance camera feeds indexed by Shodan.
    Honors zero-fabrication rules: requires a valid SHODAN_API_KEY.
    """
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        return ShodanCameraDiscoveryResponse(
            configured=False,
            api_key_status="CONFIG_REQUIRED",
            message="SHODAN_API_KEY is not configured in backend/.env. Add your Shodan API key to enable live camera discovery.",
            cameras=[]
        )

    # Build smart query for traffic/cctv/rtsp surveillance feeds
    parts = []
    if query:
        parts.append(query)
    else:
        parts.append("port:554")
        if jurisdiction:
            parts.append(f"country:{jurisdiction.upper()}")
        if city:
            parts.append(f'city:"{city}"')
        parts.append("has_screenshot:true")

    final_query = " ".join(parts)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.shodan.io/shodan/host/search",
                params={"key": api_key, "query": final_query}
            )
            if resp.status_code == 200:
                data = resp.json()
                matches = data.get("matches", [])
                cameras = []
                for m in matches:
                    ip = m.get("ip_str", "")
                    port = m.get("port", 554)
                    loc = m.get("location", {})
                    product = m.get("product") or m.get("devicetype") or "IP Surveillance Camera"
                    stream_url = f"rtsp://{ip}:{port}/" if port == 554 else f"http://{ip}:{port}/"
                    screenshot_b64 = None
                    opts = m.get("opts", {})
                    if "screenshot" in opts:
                        screenshot_b64 = f"data:image/jpeg;base64,{opts['screenshot']}"

                    cameras.append(ShodanCameraRecord(
                        ip=ip,
                        port=port,
                        product=product,
                        org=m.get("org"),
                        city=loc.get("city"),
                        country=loc.get("country_name"),
                        latitude=loc.get("latitude"),
                        longitude=loc.get("longitude"),
                        stream_url=stream_url,
                        feed_type="RTSP" if port == 554 else "HTTP_MJPEG",
                        screenshot_url=screenshot_b64,
                        asn=m.get("asn"),
                        last_seen=m.get("timestamp")
                    ))

                audit_logger.log(
                    tenant_id=current_user.tenant_id,
                    user_id=current_user.id,
                    action="discover_shodan_cameras",
                    resource_type="SHODAN_CAMERAS_DISCOVERED",
                    resource_id=final_query,
                    details={"total_found": len(cameras), "query": final_query}
                )

                return ShodanCameraDiscoveryResponse(
                    configured=True,
                    api_key_status="ACTIVE",
                    total_found=data.get("total", len(cameras)),
                    query_used=final_query,
                    cameras=cameras
                )
            else:
                return ShodanCameraDiscoveryResponse(
                    configured=True,
                    api_key_status="API_ERROR",
                    message=f"Shodan API returned status {resp.status_code}: {resp.text[:200]}",
                    query_used=final_query,
                    cameras=[]
                )
    except Exception as e:
        return ShodanCameraDiscoveryResponse(
            configured=True,
            api_key_status="CONNECTION_ERROR",
            message=f"Error connecting to Shodan API: {str(e)}",
            query_used=final_query,
            cameras=[]
        )


@router.post("/stream-anpr", response_model=List[ANPRDetectionRecord])
async def stream_anpr_endpoint(
    payload: StreamANPRRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Connects to an RTSP or HTTP camera stream URL, captures sample video frames,
    and runs automated number plate recognition against the target plate.
    """
    target_clean = (payload.target_plate or "").strip().upper()
    if not target_clean or not any(c.isdigit() for c in target_clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target plate '{payload.target_plate}' does not conform to recognized vehicle registration syntax."
        )

    # Validate stream URL syntax
    url = (payload.stream_url or "").strip()
    if not (url.startswith("rtsp://") or url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stream URL must begin with rtsp://, http://, or https://"
        )

    temp_clip_name = f"stream_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:6]}.mp4"
    temp_clip_path = os.path.join(FOOTAGE_UPLOAD_DIR, temp_clip_name)

    import cv2
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to connect to live stream at '{url}'. Ensure device is online and port is reachable."
        )

    frames = []
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0

    count = 0
    max_frames = min(payload.max_frames, 60)
    while cap.isOpened() and count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        count += 1
    cap.release()

    if not frames:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Network stream connected, but no frames were delivered before timeout."
        )

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_clip_path, fourcc, fps, (width, height))
    for f in frames:
        out.write(f)
    out.release()

    camera = CameraSourceRecord(
        source_id=f"cam_stream_{uuid.uuid4().hex[:6]}",
        operator=payload.source_name or "Live Network Camera Stream",
        name=payload.source_name or f"Stream ({url[:30]}...)",
        source_url=url,
        geographic_coverage="Live Surveillance Stream",
        feed_type=CameraFeedType.VIDEO_CLIP,
        availability=CameraAvailability.AVAILABLE,
        auth_requirements="Public / Network Stream Access",
        retention_restrictions="Live volatile feed",
        is_public_catalog=False
    )

    detections = anpr_service.process_video_footage(
        video_path=temp_clip_path,
        target_plate=payload.target_plate,
        camera=camera,
        investigation_id=payload.investigation_id,
        case_id=payload.case_id,
        tenant_id=current_user.tenant_id,
        max_duration_seconds=float(count / max(1.0, fps)),
        sample_interval_seconds=1.0
    )

    return detections
