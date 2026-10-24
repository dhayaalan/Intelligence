from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ExifData(BaseModel):
    present: bool = False
    make: Optional[str] = None
    model: Optional[str] = None
    software: Optional[str] = None
    datetime: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    gps_precision: Optional[str] = None  # "exact", "city", "country"
    raw_tags_count: int = 0

class C2paData(BaseModel):
    status: str = "absent"  # "valid", "invalid", "absent", "error"
    signed_by: Optional[str] = None
    generator: Optional[str] = None
    ai_generated: bool = False
    ai_evidence: Optional[str] = None

class QualityMetrics(BaseModel):
    width: int = 0
    height: int = 0
    megapixels: float = 0.0
    sharpness_score: float = 0.0
    is_blurry: bool = False
    quality_warning: Optional[str] = None

class OcrFinding(BaseModel):
    text: str = ""
    words_count: int = 0
    confidence: float = 0.0
    detected_license_plate: Optional[str] = None
    detected_urls: List[str] = Field(default_factory=list)
    detected_emails: List[str] = Field(default_factory=list)

class ImageForensicsResult(BaseModel):
    sha256: str
    md5: str
    file_size_bytes: int
    mime_type: str
    dhash: str
    phash: str
    exif: ExifData
    c2pa: C2paData
    ocr: OcrFinding
    quality: QualityMetrics
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

class Keyframe(BaseModel):
    time_seconds: float
    frame_index: int
    phash: str
    dhash: str
    preview_data_url: Optional[str] = None
    ocr_text: Optional[str] = None

class SceneCut(BaseModel):
    index: int
    time_seconds: float
    distance_from_previous: float

class TranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str
    confidence: float = 1.0
    lang: Optional[str] = None

class VideoForensicsResult(BaseModel):
    sha256: str
    file_size_bytes: int
    format: str
    codec: str
    duration_seconds: float
    fps: float
    resolution: str
    frame_count: int
    keyframes: List[Keyframe] = Field(default_factory=list)
    scene_cuts: List[SceneCut] = Field(default_factory=list)
    ocr_findings: List[str] = Field(default_factory=list)
    transcript: List[TranscriptSegment] = Field(default_factory=list)
    audio_present: bool = False
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

class AudioForensicsResult(BaseModel):
    sha256: str
    file_size_bytes: int
    format: str
    sample_rate: int
    channels: int
    duration_seconds: float
    transcript: List[TranscriptSegment] = Field(default_factory=list)
    detected_language: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

class MediaComparisonRequest(BaseModel):
    hash1: str
    hash2: str
    algorithm: str = "phash"  # "dhash" or "phash"

class MediaComparisonResponse(BaseModel):
    algorithm: str
    hamming_distance: int
    max_distance: int = 64
    similarity_percentage: float
    match_type: str  # "EXACT_MATCH", "NEAR_DUPLICATE", "DISSIMILAR"
    is_candidate_match: bool

class MediaAnalysisJobRecord(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    investigation_id: Optional[str] = None
    media_type: str  # "image", "video", "audio"
    filename: Optional[str] = None
    status: str = "completed"  # "pending", "processing", "completed", "failed"
    image_result: Optional[ImageForensicsResult] = None
    video_result: Optional[VideoForensicsResult] = None
    audio_result: Optional[AudioForensicsResult] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
