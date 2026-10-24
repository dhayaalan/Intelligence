import uuid
import base64
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from pydantic import BaseModel

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.audit.logger import audit_logger
from app.infrastructure.mongodb.client import mongo_manager
from app.investigations.service import investigation_service
from app.modules.media_intelligence.service import media_intelligence_service
from app.modules.media_intelligence.models import (
    ImageForensicsResult, VideoForensicsResult, AudioForensicsResult,
    MediaComparisonRequest, MediaComparisonResponse, MediaAnalysisJobRecord
)

logger = logging.getLogger("sential.media_intelligence.router")

router = APIRouter(prefix="/media-intelligence", tags=["Media Forensics & Intelligence"])

class AnalyzeUrlRequest(BaseModel):
    url: str
    media_type: str = "image"  # "image", "video", "audio"
    investigation_id: Optional[str] = None

class LinkAnalysisRequest(BaseModel):
    investigation_id: str
    media_type: str
    filename: str
    media_url: Optional[str] = None
    image_result: Optional[ImageForensicsResult] = None
    video_result: Optional[VideoForensicsResult] = None
    audio_result: Optional[AudioForensicsResult] = None

@router.get("/health")
async def media_health():
    """Returns module preflight diagnostic status."""
    from app.modules.media_intelligence.module import media_intelligence_module
    health = await media_intelligence_module.health_check()
    return health.dict()

@router.post("/analyze/image", response_model=ImageForensicsResult)
async def analyze_image_endpoint(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    filename: Optional[str] = Form("upload.jpg"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Performs forensic inspection on an image.
    Extracts SHA-256, MD5, dHash, DCT pHash, EXIF camera metadata, GPS fixes, C2PA, and OCR text.
    """
    image_bytes = None
    fn = filename or "upload.jpg"

    if file:
        fn = file.filename or fn
        image_bytes = await file.read()
    elif image_base64:
        try:
            # Strip data URL prefix if present
            clean_b64 = image_base64.split(",")[-1] if "," in image_base64 else image_base64
            image_bytes = base64.b64decode(clean_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding for image")
    
    if not image_bytes or len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="No valid image payload provided")

    if len(image_bytes) > media_intelligence_service.max_upload_size:
        raise HTTPException(status_code=413, detail=f"Image exceeds maximum upload limit of {media_intelligence_service.max_upload_size // (1024*1024)}MB")

    result = media_intelligence_service.analyze_image(image_bytes, filename=fn)
    
    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="MEDIA_FORENSICS_IMAGE_ANALYZED",
        resource_type="media",
        resource_id=result.sha256,
        details={"filename": fn, "sha256": result.sha256, "file_size": result.file_size_bytes}
    )
    return result

@router.post("/analyze/video", response_model=VideoForensicsResult)
async def analyze_video_endpoint(
    file: Optional[UploadFile] = File(None),
    video_base64: Optional[str] = Form(None),
    filename: Optional[str] = Form("video.mp4"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Performs video sampling, scene cut detection, keyframe extraction, and OCR analysis.
    """
    video_bytes = None
    fn = filename or "video.mp4"

    if file:
        fn = file.filename or fn
        video_bytes = await file.read()
    elif video_base64:
        try:
            clean_b64 = video_base64.split(",")[-1] if "," in video_base64 else video_base64
            video_bytes = base64.b64decode(clean_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding for video")

    if not video_bytes or len(video_bytes) == 0:
        raise HTTPException(status_code=400, detail="No valid video payload provided")

    if len(video_bytes) > media_intelligence_service.max_upload_size:
        raise HTTPException(status_code=413, detail="Video exceeds maximum upload limit")

    result = media_intelligence_service.analyze_video(video_bytes, filename=fn)

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="MEDIA_FORENSICS_VIDEO_ANALYZED",
        resource_type="media",
        resource_id=result.sha256,
        details={"filename": fn, "duration": result.duration_seconds, "keyframes_count": len(result.keyframes)}
    )
    return result

@router.post("/analyze/audio", response_model=AudioForensicsResult)
async def analyze_audio_endpoint(
    file: Optional[UploadFile] = File(None),
    audio_base64: Optional[str] = Form(None),
    filename: Optional[str] = Form("audio.wav"),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Inspects audio stream, header metadata, and generates timestamped transcription.
    """
    audio_bytes = None
    fn = filename or "audio.wav"

    if file:
        fn = file.filename or fn
        audio_bytes = await file.read()
    elif audio_base64:
        try:
            clean_b64 = audio_base64.split(",")[-1] if "," in audio_base64 else audio_base64
            audio_bytes = base64.b64decode(clean_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding for audio")

    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="No valid audio payload provided")

    result = media_intelligence_service.analyze_audio(audio_bytes, filename=fn)
    return result

@router.post("/analyze/url")
async def analyze_url_endpoint(
    req: AnalyzeUrlRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Downloads media from an investigator-provided URL and performs forensic extraction.
    """
    url = req.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Invalid media URL: must begin with http:// or https://")

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "Sential-Intelligence-Forensics/2.0 (+https://sential.io/security)"}
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch media from URL (HTTP {resp.status_code})")
            
            content_type = resp.headers.get("content-type", "").lower()
            raw_bytes = resp.content

            if len(raw_bytes) == 0:
                raise HTTPException(status_code=400, detail="Retrieved empty file from media URL")

            if len(raw_bytes) > media_intelligence_service.max_upload_size:
                raise HTTPException(status_code=413, detail="Remote media exceeds maximum upload limit")

            # Determine type
            determined_type = req.media_type
            filename = url.split("?")[0].split("/")[-1] or "media_evidence"
            
            if "video" in content_type:
                determined_type = "video"
            elif "audio" in content_type:
                determined_type = "audio"
            elif "image" in content_type:
                determined_type = "image"

            if determined_type == "video":
                analysis = media_intelligence_service.analyze_video(raw_bytes, filename=filename)
                return {"media_type": "video", "result": analysis.dict()}
            elif determined_type == "audio":
                analysis = media_intelligence_service.analyze_audio(raw_bytes, filename=filename)
                return {"media_type": "audio", "result": analysis.dict()}
            else:
                analysis = media_intelligence_service.analyze_image(raw_bytes, filename=filename)
                return {"media_type": "image", "result": analysis.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch and analyze media URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forensic acquisition failed for URL: {str(e)}")

@router.post("/compare-hash", response_model=MediaComparisonResponse)
async def compare_hashes_endpoint(
    req: MediaComparisonRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Computes Hamming distance and candidate similarity between two perceptual hashes.
    """
    if not req.hash1 or not req.hash2:
        raise HTTPException(status_code=400, detail="Both hash1 and hash2 are required")
    return media_intelligence_service.compare_hashes(req.hash1, req.hash2, req.algorithm)

# -----------------------------------------------------------------------------
# Investigation-Scoped Media Linking & Vault Persistence
# -----------------------------------------------------------------------------
@router.post("/investigations/{investigation_id}/media-analysis")
async def link_media_analysis_to_investigation(
    investigation_id: str,
    req: LinkAnalysisRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Links a verified forensic media analysis report directly to an investigation.
    Creates an investigation media record and persists findings in MongoDB.
    """
    inv = investigation_service.get_investigation(current_user.tenant_id, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")

    analysis_id = f"man_{uuid.uuid4().hex[:10]}"
    primary_hash = "unknown"
    if req.image_result:
        primary_hash = req.image_result.sha256
    elif req.video_result:
        primary_hash = req.video_result.sha256
    elif req.audio_result:
        primary_hash = req.audio_result.sha256

    analysis_doc = {
        "id": analysis_id,
        "tenant_id": current_user.tenant_id,
        "investigation_id": investigation_id,
        "user_id": current_user.id,
        "user_name": current_user.name,
        "media_type": req.media_type,
        "filename": req.filename,
        "media_url": req.media_url,
        "primary_hash": primary_hash,
        "image_result": req.image_result.dict() if req.image_result else None,
        "video_result": req.video_result.dict() if req.video_result else None,
        "audio_result": req.audio_result.dict() if req.audio_result else None,
        "created_at": datetime.utcnow().isoformat()
    }

    from app.core.database import db

    # Store in-memory
    with db._lock:
        db.investigation_media_analyses[analysis_id] = analysis_doc

    # Store in MongoDB if available
    if mongo_manager.db is not None:
        try:
            await mongo_manager.db["investigation_media_analyses"].update_one(
                {"id": analysis_id, "tenant_id": current_user.tenant_id},
                {"$set": analysis_doc},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to persist media analysis to MongoDB: {e}")

    # Also link to investigation's media array for instant gallery view
    media_item = {
        "id": analysis_id,
        "media_type": req.media_type,
        "url": req.media_url or f"/api/v1/media-intelligence/investigations/{investigation_id}/media-analysis/{analysis_id}",
        "title": f"Forensic Media: {req.filename}",
        "source_provider": "MEDIA_INTELLIGENCE",
        "sha256": primary_hash,
        "verification_status": "VERIFIED"
    }
    investigation_service.link_media(current_user.tenant_id, investigation_id, media_item)

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="INVESTIGATION_MEDIA_ANALYSIS_LINKED",
        resource_type="investigation",
        resource_id=investigation_id,
        details={"analysis_id": analysis_id, "media_type": req.media_type, "primary_hash": primary_hash}
    )

    return {"status": "linked", "analysis_id": analysis_id, "primary_hash": primary_hash}

@router.get("/investigations/{investigation_id}/media-analyses")
async def list_investigation_media_analyses(
    investigation_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """Retrieves all forensic media analyses attached to this investigation."""
    from app.core.database import db
    inv = investigation_service.get_investigation(current_user.tenant_id, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found in this tenant")

    if mongo_manager.db is not None:
        try:
            cursor = mongo_manager.db["investigation_media_analyses"].find(
                {"investigation_id": investigation_id, "tenant_id": current_user.tenant_id},
                {"_id": 0}
            ).sort("created_at", -1)
            docs = await cursor.to_list(length=100)
            if docs:
                return docs
        except Exception:
            pass

    with db._lock:
        return [
            doc for doc in db.investigation_media_analyses.values()
            if doc.get("investigation_id") == investigation_id and doc.get("tenant_id") == current_user.tenant_id
        ]

@router.get("/investigations/{investigation_id}/media-analysis/{analysis_id}")
async def get_investigation_media_analysis(
    investigation_id: str,
    analysis_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """Retrieves a single forensic media analysis record."""
    from app.core.database import db
    if mongo_manager.db is not None:
        try:
            doc = await mongo_manager.db["investigation_media_analyses"].find_one(
                {"id": analysis_id, "investigation_id": investigation_id, "tenant_id": current_user.tenant_id},
                {"_id": 0}
            )
            if doc:
                return doc
        except Exception:
            pass

    with db._lock:
        doc = db.investigation_media_analyses.get(analysis_id)
        if doc and doc.get("tenant_id") == current_user.tenant_id and doc.get("investigation_id") == investigation_id:
            return doc

    raise HTTPException(status_code=404, detail="Media analysis record not found")
    return doc
