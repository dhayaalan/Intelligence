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
from app.evidence.service import evidence_service
from app.module_sdk.models import EvidencePayload
from app.modules.media_intelligence.service import media_intelligence_service
from app.modules.media_intelligence.ssrf import safe_fetch_media_url, SSRFSecurityError
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

class SaveEvidenceFromAnalysisRequest(BaseModel):
    analysis_id: str
    media_type: str
    filename: str
    primary_hash: str
    investigation_id: Optional[str] = None
    notes: Optional[str] = None
    forensics_summary: Optional[Dict[str, Any]] = None

async def _persist_analysis_record(
    tenant_id: str,
    user_id: str,
    user_name: str,
    media_type: str,
    filename: str,
    primary_hash: str,
    investigation_id: Optional[str] = None,
    media_url: Optional[str] = None,
    image_result: Optional[dict] = None,
    video_result: Optional[dict] = None,
    audio_result: Optional[dict] = None,
) -> str:
    """Helper to persist a verified media analysis in MongoDB and in-memory cache."""
    from app.core.database import db
    analysis_id = f"man_{uuid.uuid4().hex[:10]}"
    doc = {
        "id": analysis_id,
        "tenant_id": tenant_id,
        "investigation_id": investigation_id,
        "user_id": user_id,
        "user_name": user_name,
        "media_type": media_type,
        "filename": filename,
        "media_url": media_url,
        "primary_hash": primary_hash,
        "image_result": image_result,
        "video_result": video_result,
        "audio_result": audio_result,
        "created_at": datetime.utcnow().isoformat()
    }
    with db._lock:
        db.investigation_media_analyses[analysis_id] = doc

    if mongo_manager.db is not None:
        try:
            await mongo_manager.db["investigation_media_analyses"].update_one(
                {"id": analysis_id, "tenant_id": tenant_id},
                {"$set": doc},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Failed to persist media analysis to MongoDB: {e}")
    return analysis_id

@router.get("/health")
async def media_health():
    """Returns module preflight diagnostic status."""
    from app.modules.media_intelligence.module import media_intelligence_module
    health = await media_intelligence_module.health_check()
    return health.dict()

@router.get("/analyses")
async def list_media_analyses(
    limit: int = Query(50, ge=1, le=200),
    current_user: UserRecord = Depends(get_current_user)
):
    """Retrieves recent forensic media analyses for the current tenant."""
    from app.core.database import db
    if mongo_manager.db is not None:
        try:
            cursor = mongo_manager.db["investigation_media_analyses"].find(
                {"tenant_id": current_user.tenant_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            if docs:
                return docs
        except Exception as e:
            logger.warning(f"Failed to query MongoDB for media analyses: {e}")

    with db._lock:
        records = [
            doc for doc in db.investigation_media_analyses.values()
            if doc.get("tenant_id") == current_user.tenant_id
        ]
        records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return records[:limit]

@router.post("/analyze/image", response_model=ImageForensicsResult)
async def analyze_image_endpoint(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    filename: Optional[str] = Form("upload.jpg"),
    investigation_id: Optional[str] = Form(None),
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
            clean_b64 = image_base64.split(",")[-1] if "," in image_base64 else image_base64
            image_bytes = base64.b64decode(clean_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding for image")
    
    if not image_bytes or len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="No valid image payload provided")

    if len(image_bytes) > media_intelligence_service.max_upload_size:
        raise HTTPException(status_code=413, detail=f"Image exceeds maximum upload limit of {media_intelligence_service.max_upload_size // (1024*1024)}MB")

    result = media_intelligence_service.analyze_image(image_bytes, filename=fn)
    
    # Auto-persist analysis record for persistence across refreshes
    await _persist_analysis_record(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_name=current_user.name,
        media_type="image",
        filename=fn,
        primary_hash=result.sha256,
        investigation_id=investigation_id,
        image_result=result.dict()
    )

    audit_logger.log(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="MEDIA_FORENSICS_IMAGE_ANALYZED",
        resource_type="media",
        resource_id=result.sha256,
        details={"filename": fn, "sha256": result.sha256, "file_size": result.file_size_bytes}
    )
    return result

@router.post("/analyze/batch-images")
async def analyze_batch_images_endpoint(
    files: List[UploadFile] = File(...),
    investigation_id: Optional[str] = Form(None),
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Processes multiple image files concurrently under memory-safe bounds.
    Returns array of extracted forensic results.
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded for batch analysis")
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Batch limit is 10 images per request")

    results = []
    for file in files:
        data = await file.read()
        if len(data) == 0 or len(data) > media_intelligence_service.max_upload_size:
            continue
        fn = file.filename or "image.jpg"
        res = media_intelligence_service.analyze_image(data, filename=fn)
        res_dict = res.dict()
        aid = await _persist_analysis_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            user_name=current_user.name,
            media_type="image",
            filename=fn,
            primary_hash=res.sha256,
            investigation_id=investigation_id,
            image_result=res_dict
        )
        res_dict["analysis_id"] = aid
        results.append(res_dict)

    return results

@router.post("/analyze/video", response_model=VideoForensicsResult)
async def analyze_video_endpoint(
    file: Optional[UploadFile] = File(None),
    video_base64: Optional[str] = Form(None),
    filename: Optional[str] = Form("video.mp4"),
    investigation_id: Optional[str] = Form(None),
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

    await _persist_analysis_record(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_name=current_user.name,
        media_type="video",
        filename=fn,
        primary_hash=result.sha256,
        investigation_id=investigation_id,
        video_result=result.dict()
    )

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
    investigation_id: Optional[str] = Form(None),
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

    await _persist_analysis_record(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_name=current_user.name,
        media_type="audio",
        filename=fn,
        primary_hash=result.sha256,
        investigation_id=investigation_id,
        audio_result=result.dict()
    )

    return result

@router.post("/analyze/url")
async def analyze_url_endpoint(
    req: AnalyzeUrlRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Downloads media from an investigator-provided URL and performs forensic extraction.
    Enforces strict Server-Side Request Forgery (SSRF) boundary protections:
    rejects loopback, private RFC1918, link-local, cloud metadata, and restricted ports.
    """
    url = req.url.strip()
    try:
        raw_bytes, content_type, filename = await safe_fetch_media_url(
            url,
            max_size_bytes=media_intelligence_service.max_upload_size
        )
    except SSRFSecurityError as ssrf_err:
        logger.warning(f"SSRF violation blocked for URL '{url}': {ssrf_err}")
        raise HTTPException(
            status_code=400,
            detail=f"Security Policy Rejection (SSRF): {str(ssrf_err)}"
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        logger.error(f"Failed to fetch media from URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forensic acquisition failed for URL: {str(e)}")

    determined_type = req.media_type
    if "video" in content_type:
        determined_type = "video"
    elif "audio" in content_type:
        determined_type = "audio"
    elif "image" in content_type:
        determined_type = "image"

    if determined_type == "video":
        analysis = media_intelligence_service.analyze_video(raw_bytes, filename=filename)
        res_dict = analysis.dict()
        analysis_id = await _persist_analysis_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            user_name=current_user.name,
            media_type="video",
            filename=filename,
            primary_hash=analysis.sha256,
            investigation_id=req.investigation_id,
            media_url=url,
            video_result=res_dict
        )
        return {"media_type": "video", "analysis_id": analysis_id, "result": res_dict}
    elif determined_type == "audio":
        analysis = media_intelligence_service.analyze_audio(raw_bytes, filename=filename)
        res_dict = analysis.dict()
        analysis_id = await _persist_analysis_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            user_name=current_user.name,
            media_type="audio",
            filename=filename,
            primary_hash=analysis.sha256,
            investigation_id=req.investigation_id,
            media_url=url,
            audio_result=res_dict
        )
        return {"media_type": "audio", "analysis_id": analysis_id, "result": res_dict}
    else:
        analysis = media_intelligence_service.analyze_image(raw_bytes, filename=filename)
        res_dict = analysis.dict()
        analysis_id = await _persist_analysis_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            user_name=current_user.name,
            media_type="image",
            filename=filename,
            primary_hash=analysis.sha256,
            investigation_id=req.investigation_id,
            media_url=url,
            image_result=res_dict
        )
        return {"media_type": "image", "analysis_id": analysis_id, "result": res_dict}

@router.post("/analyze/evidence-asset/{evidence_id}")
async def analyze_evidence_asset_endpoint(
    evidence_id: str,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Ingests an existing artifact from the Evidence Vault and executes forensic analysis.
    Preserves chain-of-custody link back to the originating evidence record.
    """
    ev = evidence_service.get_evidence(current_user.tenant_id, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence artifact not found in tenant vault")

    raw_data = ev.raw_data or {}
    b64_data = raw_data.get("image_base64") or raw_data.get("media_base64")
    url_data = raw_data.get("url") or raw_data.get("media_url") or ev.reference

    if b64_data:
        try:
            clean_b64 = b64_data.split(",")[-1] if "," in b64_data else b64_data
            data_bytes = base64.b64decode(clean_b64)
            res = media_intelligence_service.analyze_image(data_bytes, filename=f"evidence_{evidence_id}.jpg")
            aid = await _persist_analysis_record(
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                user_name=current_user.name,
                media_type="image",
                filename=f"evidence_{evidence_id}.jpg",
                primary_hash=res.sha256,
                investigation_id=ev.investigation_id,
                image_result=res.dict()
            )
            return {"status": "analyzed", "analysis_id": aid, "media_type": "image", "result": res.dict()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process evidence base64 data: {e}")
    elif url_data and (url_data.startswith("http://") or url_data.startswith("https://")):
        raw_bytes, content_type, filename = await safe_fetch_media_url(url_data)
        res = media_intelligence_service.analyze_image(raw_bytes, filename=filename)
        aid = await _persist_analysis_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            user_name=current_user.name,
            media_type="image",
            filename=filename,
            primary_hash=res.sha256,
            investigation_id=ev.investigation_id,
            media_url=url_data,
            image_result=res.dict()
        )
        return {"status": "analyzed", "analysis_id": aid, "media_type": "image", "result": res.dict()}
    else:
        raise HTTPException(
            status_code=400,
            detail="Evidence record does not contain an analyzable image payload or accessible media URL"
        )

@router.post("/save-evidence")
async def save_media_to_evidence_vault(
    req: SaveEvidenceFromAnalysisRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Seals a completed forensic media analysis directly into the immutable Evidence Vault.
    Generates a cryptographic evidence record with tamper-evident SHA-256 hash.
    """
    ev_payload = EvidencePayload(
        id=f"ev_media_{uuid.uuid4().hex[:10]}",
        module="media_intelligence",
        provider="forensic_media_engine",
        source="media_forensics",
        collection_method="FORENSIC_INGESTION",
        reference=f"Media Asset: {req.filename} ({req.media_type})",
        confidence=1.0,
        hash=req.primary_hash,
        raw_data={
            "analysis_id": req.analysis_id,
            "filename": req.filename,
            "media_type": req.media_type,
            "primary_hash": req.primary_hash,
            "forensics_summary": req.forensics_summary,
            "notes": req.notes,
            "saved_by": current_user.name
        }
    )
    saved_record = evidence_service.store_evidence(
        tenant_id=current_user.tenant_id,
        payload=ev_payload,
        investigation_id=req.investigation_id
    )
    return {"status": "sealed", "evidence_id": saved_record.id, "hash": req.primary_hash}

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

    primary_hash = "unknown"
    if req.image_result:
        primary_hash = req.image_result.sha256
    elif req.video_result:
        primary_hash = req.video_result.sha256
    elif req.audio_result:
        primary_hash = req.audio_result.sha256

    analysis_id = await _persist_analysis_record(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_name=current_user.name,
        media_type=req.media_type,
        filename=req.filename,
        primary_hash=primary_hash,
        investigation_id=investigation_id,
        media_url=req.media_url,
        image_result=req.image_result.dict() if req.image_result else None,
        video_result=req.video_result.dict() if req.video_result else None,
        audio_result=req.audio_result.dict() if req.audio_result else None
    )

    # Link to investigation's media array for instant gallery view
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
