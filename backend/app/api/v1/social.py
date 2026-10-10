from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.identity.models import UserRecord
from app.tenancy.context import get_current_user
from app.modules.social_media_intelligence.models import (
    SocialSearchRequest,
    SocialSearchResponse,
    SocialPost,
    SocialPlatformType,
    CibCluster,
    CredibilityScore,
    YouTubeInvestigationResult
)
from app.modules.social_media_intelligence.service import social_media_service

router = APIRouter(prefix="/social", tags=["Social Media Intelligence"])


class CredibilityRequest(BaseModel):
    target: str
    platform: SocialPlatformType
    posts: List[SocialPost] = []
    account_age_days: Optional[int] = None
    has_custom_avatar: bool = True


class YouTubeInvestigateRequest(BaseModel):
    video_url_or_id: str


@router.post("/search", response_model=SocialSearchResponse)
async def search_social_intelligence(
    req: SocialSearchRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Executes real-time multi-platform social media intelligence collection across
    Bluesky, Telegram, Reddit, Mastodon, and YouTube with automated CIB detection.
    """
    return await social_media_service.execute_search(req)


@router.post("/analyze/cib", response_model=List[CibCluster])
async def analyze_coordinated_inauthentic_behavior(
    posts: List[SocialPost],
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Analyzes social posts for Coordinated Inauthentic Behavior (CIB) clusters,
    synchronized publication bursts (< 60s), and identical URL propagation.
    """
    return await social_media_service.analyze_cib(posts)


@router.post("/analyze/credibility", response_model=CredibilityScore)
async def analyze_account_credibility(
    req: CredibilityRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Computes explainable bot probability and credibility score (0–100)
    for a social profile based on velocity, text diversity, and link patterns.
    """
    return social_media_service.analyze_credibility(
        target_handle=req.target,
        platform=req.platform,
        posts=req.posts
    )


@router.post("/youtube/video", response_model=YouTubeInvestigationResult)
async def investigate_youtube_video(
    req: YouTubeInvestigateRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Performs forensic video intelligence on a YouTube target:
    extracts metadata, subtitle transcripts with timestamps, and comment sentiment.
    """
    result = await social_media_service.investigate_youtube_video(req.video_url_or_id)
    if not result:
        raise HTTPException(status_code=404, detail="Could not extract metadata for the specified YouTube video.")
    return result
