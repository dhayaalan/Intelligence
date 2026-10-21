from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CameraFeedType(str, Enum):
    SNAPSHOT_SERIES = "SNAPSHOT_SERIES"
    VIDEO_CLIP = "VIDEO_CLIP"
    LIVE_STREAM = "LIVE_STREAM"


class CameraAccessMethod(str, Enum):
    REST_API = "REST_API"
    SNAPSHOT_POLL = "SNAPSHOT_POLL"
    AUTHORIZED_UPLOAD = "AUTHORIZED_UPLOAD"
    RTSP_CONNECTOR = "RTSP_CONNECTOR"


class CameraAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESTRICTED = "RESTRICTED"
    CONFIGURATION_REQUIRED = "CONFIGURATION_REQUIRED"
    OFFLINE = "OFFLINE"


class ANPRMatchStatus(str, Enum):
    NO_MATCH = "NO_MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    CANDIDATE_MATCH = "CANDIDATE_MATCH"
    HUMAN_CONFIRMED = "HUMAN_CONFIRMED"
    HUMAN_REJECTED = "HUMAN_REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class CameraSourceRecord(BaseModel):
    """
    Public or authorized camera source metadata.
    Enforces clear distinction between static snapshots and live CCTV feeds.
    Strictly forbids arbitrary IP scanning or unauthorized RTSP enumeration.
    """
    source_id: str
    operator: str
    name: str
    source_url: str
    geographic_coverage: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    feed_type: CameraFeedType = CameraFeedType.SNAPSHOT_SERIES
    access_method: CameraAccessMethod = CameraAccessMethod.REST_API
    licensing_status: str = "OPEN_DATA_COMMONS"
    availability: CameraAvailability = CameraAvailability.AVAILABLE
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    auth_requirements: str = "None (Public Open Data)"
    retention_restrictions: str = "Real-time or ephemeral public transport snapshots only; no bulk historical scraping permitted"
    is_public_catalog: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ANPRDetectionRecord(BaseModel):
    """
    Forensic ANPR sighting record.
    Preserves exact frame timecode, bounding box crop, raw OCR, alternative readings,
    calibrated confidence, and review provenance.
    """
    detection_id: str
    investigation_id: Optional[str] = None
    case_id: Optional[str] = None
    tenant_id: str = "tenant_default"
    camera_id: str
    camera_operator: str
    camera_location_name: str
    camera_coordinates: Optional[Dict[str, float]] = None
    video_reference: str
    frame_number: int
    timecode_seconds: float
    source_timestamp: Optional[datetime] = None
    raw_ocr_text: str
    normalized_candidate_plate: str
    alternative_candidates: List[str] = Field(default_factory=list)
    target_plate: str
    confidence: float  # Calibrated score between 0.0 and 1.0
    match_status: ANPRMatchStatus = ANPRMatchStatus.CANDIDATE_MATCH
    
    # Reviewer tracking
    human_reviewer_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_decision_notes: Optional[str] = None
    
    # Media provenance
    frame_preview_data: Optional[str] = None  # Base64 data URL of frame thumbnail
    plate_crop_data: Optional[str] = None     # Base64 data URL of cropped license plate
    video_url: Optional[str] = None           # API streaming URL for MP4 / WebM footage
    video_frames_data: List[str] = Field(default_factory=list)  # Motion frame series for animated CCTV player
    evidence_id: Optional[str] = None
    
    detector_version: str = "OpenCV 5.0.0 Morphological Contour Filter + Tesseract 5.5.0"
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    limitations: Optional[str] = None


class ANPRReviewRequest(BaseModel):
    decision: str = Field(..., description="Decision: 'CONFIRM', 'REJECT', or 'INCONCLUSIVE'")
    notes: Optional[str] = None


class FootageIngestionRequest(BaseModel):
    camera_id: Optional[str] = None
    investigation_id: Optional[str] = None
    case_id: Optional[str] = None
    target_plate: str
    source_label: str = "Authorized Case Footage"
    known_location: Optional[str] = "Authorized Investigation Checkpoint"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_timestamp: Optional[datetime] = None
