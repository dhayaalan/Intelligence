"""
Standardized Profile Extraction, Provenance, and Snapshot Models for OSINT.
Adheres to Phase 2 and Phase 3 specifications of the Regional OSINT Architecture.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ExtractionStatus(str, Enum):
    """
    Standardized extraction and resolution status.
    Ensures URL discovery is never conflated with metadata extraction.
    """
    DISCOVERED = "DISCOVERED"
    PROFILE_VALIDATED = "PROFILE_VALIDATED"
    METADATA_EXTRACTED = "METADATA_EXTRACTED"
    CONTENT_COLLECTED = "CONTENT_COLLECTED"
    PARTIAL_EXTRACTION = "PARTIAL_EXTRACTION"
    CONFIG_REQUIRED = "CONFIG_REQUIRED"
    ACCESS_RESTRICTED = "ACCESS_RESTRICTED"
    RATE_LIMITED = "RATE_LIMITED"
    UNAVAILABLE = "UNAVAILABLE"
    PARSE_ERROR = "PARSE_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNVERIFIED = "UNVERIFIED"


class ExtractedFieldProvenance(BaseModel):
    """
    Field-level provenance explaining the origin and confidence of each extracted value.
    """
    field_name: str
    value: Any
    source_provider: str
    source_path: str = "root"
    is_inferred: bool = False
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 0.90
    extraction_note: Optional[str] = None


class PublicAccountStatistics(BaseModel):
    """
    Public account statistics.
    Crucial: None represents uncollected or unsupported values.
    Zero is only recorded when explicitly returned by the source.
    """
    followers: Optional[int] = None
    following: Optional[int] = None
    post_count: Optional[int] = None
    subscribers: Optional[int] = None
    likes: Optional[int] = None
    repositories_count: Optional[int] = None
    stars: Optional[int] = None
    contributions: Optional[int] = None
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)


class ProfileArtifactItem(BaseModel):
    """
    Public artifact collected from a platform (post, repo, tweet, video, gist, etc.)
    """
    artifact_id: str
    artifact_type: str = "post"
    canonical_url: str
    text_content: Optional[str] = None
    published_at: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    attachment_types: List[str] = Field(default_factory=list)
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProfileExtractionResult(BaseModel):
    """
    Standardized, high-fidelity OSINT Profile Extraction Contract.
    Normalizes profile attributes across social, code, gaming, publishing, and developer platforms.
    """
    # Identity & Platform
    platform_id: str
    platform_name: str
    native_id: Optional[str] = None
    username: str
    display_name: Optional[str] = None
    canonical_url: str
    submitted_url: Optional[str] = None
    account_type: Optional[str] = None
    is_verified: Optional[bool] = None

    # Profile Metadata
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    website_urls: List[str] = Field(default_factory=list)
    locale: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    account_created_at: Optional[str] = None
    account_updated_at: Optional[str] = None

    # Public Account Statistics
    statistics: PublicAccountStatistics = Field(default_factory=PublicAccountStatistics)

    # Public Content Artifacts
    artifacts: List[ProfileArtifactItem] = Field(default_factory=list)

    # Collection & Provenance Metadata
    status: ExtractionStatus = ExtractionStatus.DISCOVERED
    first_seen_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fetched_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_cached: bool = False
    source_endpoint: str = ""
    extraction_method: str = "HTTP_PROBE"
    requested_region: Optional[str] = None
    observed_egress_route: Optional[str] = None
    fields_extracted: List[str] = Field(default_factory=list)
    fields_unsupported: List[str] = Field(default_factory=list)
    field_provenance: Dict[str, ExtractedFieldProvenance] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    evidence_hash: Optional[str] = None
    raw_preview: Dict[str, Any] = Field(default_factory=dict)


class ProfileChangeRecord(BaseModel):
    """
    Represents an observed difference between two consecutive profile snapshots.
    """
    field_name: str
    previous_value: Any
    new_value: Any
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_provider: str


class ProfileSnapshot(BaseModel):
    """
    Versioned historical observation of a profile for tracking change over time.
    """
    snapshot_id: str
    profile_key: str  # e.g., platform_id:username
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    result: ProfileExtractionResult
    changes_from_previous: List[ProfileChangeRecord] = Field(default_factory=list)
