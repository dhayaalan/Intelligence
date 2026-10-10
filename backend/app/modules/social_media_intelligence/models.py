from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SocialPlatformType(str, Enum):
    BLUESKY = "bluesky"
    TELEGRAM = "telegram"
    REDDIT = "reddit"
    MASTODON = "mastodon"
    YOUTUBE = "youtube"


class CredibilityBand(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    INAUTHENTIC = "INAUTHENTIC"


class SocialPost(BaseModel):
    id: str
    platform: SocialPlatformType
    author: str
    author_id: str
    text: str
    created_at: str
    url: str
    langs: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    likes_count: int = 0
    reposts_count: int = 0
    views_count: Optional[int] = None
    channel_name: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    is_forwarded: bool = False
    forwarded_from: Optional[str] = None
    sentiment: Optional[str] = None
    entities: List[str] = Field(default_factory=list)
    credibility_score: Optional[float] = None


class CibCluster(BaseModel):
    cluster_id: str
    primary_topic: str
    post_count: int
    account_count: int
    accounts: List[str]
    start_time: str
    end_time: str
    duration_seconds: float
    synchronization_velocity: float  # posts per minute during burst
    shared_urls: List[str] = Field(default_factory=list)
    identical_phrases: List[str] = Field(default_factory=list)
    coordination_confidence: float
    caveat_warning: str


class CredibilityScore(BaseModel):
    target: str
    platform: SocialPlatformType
    overall_score: float  # 0 to 100
    band: CredibilityBand
    account_age_days: Optional[int] = None
    post_velocity_per_day: float = 0.0
    has_custom_avatar: bool = True
    text_repetition_rate: float = 0.0  # 0.0 to 1.0
    domain_diversity_score: float = 1.0  # 0.0 to 1.0
    bot_probability: float = 0.0  # 0.0 to 1.0
    factors: Dict[str, float] = Field(default_factory=dict)
    rationale: str


class YouTubeSubtitleSegment(BaseModel):
    start_seconds: float
    duration_seconds: float
    text: str


class YouTubeSubtitleTrack(BaseModel):
    language: str
    is_auto_generated: bool
    segments: List[YouTubeSubtitleSegment] = Field(default_factory=list)
    full_text: str = ""


class YouTubeComment(BaseModel):
    id: str
    author: str
    author_channel_url: Optional[str] = None
    text: str
    likes: int = 0
    published_at: str
    sentiment: Optional[str] = "NEUTRAL"


class YouTubeMetadata(BaseModel):
    video_id: str
    url: str
    title: str
    channel_title: str
    channel_id: str
    channel_url: str
    duration_seconds: int
    view_count: int
    like_count: int
    comment_count: int
    upload_date: str
    description: str
    thumbnail_url: str
    tags: List[str] = Field(default_factory=list)


class YouTubeInvestigationResult(BaseModel):
    metadata: YouTubeMetadata
    subtitles: Optional[YouTubeSubtitleTrack] = None
    top_comments: List[YouTubeComment] = Field(default_factory=list)
    detected_entities: List[str] = Field(default_factory=list)
    detected_claims: List[str] = Field(default_factory=list)
    sentiment_summary: Dict[str, Any] = Field(default_factory=dict)


class SocialSearchRequest(BaseModel):
    query: str
    platforms: Optional[List[SocialPlatformType]] = None
    limit: int = 25
    min_credibility: float = 0.0
    detect_cib: bool = True


class SocialSearchResponse(BaseModel):
    search_id: str
    query: str
    total_results: int
    results: List[SocialPost]
    cib_clusters: List[CibCluster] = Field(default_factory=list)
    execution_time_ms: float
