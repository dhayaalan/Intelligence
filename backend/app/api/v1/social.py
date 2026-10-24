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
    YouTubeInvestigationResult,
    SocialCrawlRequest,
    SocialCrawlResult,
)
from app.modules.social_media_intelligence.crawler_engine import resilient_social_crawler

from app.modules.social_media_intelligence.service import social_media_service
from app.modules.social_media_intelligence.regional_engine import (
    regional_social_engine,
    RegionalNarrativeComparisonRequest,
    RegionalNarrativeComparisonResponse
)

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


@router.post("/regional/compare", response_model=RegionalNarrativeComparisonResponse)
async def compare_regional_narratives(
    req: RegionalNarrativeComparisonRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Executes cross-regional social narrative analysis across South India,
    North India, Pakistan, Bangladesh, and International regions with multilingual
    lexicon expansion and explicit sample size & framing limitation disclaimers.
    """
    return await regional_social_engine.compare_regional_narratives(req)


@router.post("/crawl-url", response_model=SocialCrawlResult)
async def crawl_social_media_url(
    req: SocialCrawlRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    High-assurance multi-tier social media and web page crawler.
    Extracts authentic content, captions, author profile, and media even when
    the target URL is protected by login-walls, HTTP 403 anti-bot barriers,
    or Cloudflare challenges using stealth headers and syndication fallbacks.
    """
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="Target URL is required for crawling.")

    result = await resilient_social_crawler.crawl_url(
        url=req.url.strip(),
        extract_media=req.extract_media,
        bypass_blocking=req.bypass_blocking,
        extract_comments=req.extract_comments,
        extract_entities=req.extract_entities
    )
    return result


class SocialAutoCrawlRequest(BaseModel):
    target: str
    investigation_id: Optional[str] = None
    limit: int = 15
    extract_comments: bool = True


@router.post("/auto-crawl")
async def auto_crawl_social_target(
    req: SocialAutoCrawlRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Automated zero-input social crawler.
    Searches and automatically crawls reels, videos, posts, and comment threads
    for the specified target query across all supported social platforms without
    requiring manual URL pasting. Automatically seals evidence into the investigation
    if an investigation_id is provided.
    """
    from app.core.logging import app_logger
    clean_target = (req.target or "").strip()
    if not clean_target:
        raise HTTPException(status_code=400, detail="Target query or handle is required for auto-crawling.")

    results = await social_media_service.auto_crawl_target(
        target=clean_target,
        limit=req.limit,
        extract_comments=req.extract_comments
    )

    # If investigation_id is provided, automatically seal newly extracted evidence and media
    if req.investigation_id and results:
        import uuid
        from datetime import datetime
        from app.infrastructure.mongodb.repositories import evidence_repo, investigation_repo, case_repo

        for p in results:
            post_id = p.get("id") or str(uuid.uuid4())
            ev_id = f"ev_soc_{uuid.uuid4().hex[:10]}"
            ev_data = {
                "id": ev_id,
                "tenant_id": current_user.tenant_id,
                "investigation_id": req.investigation_id,
                "source": f"{str(p.get('platform', 'Social')).upper()} Resilient Dispatch",
                "provider": str(p.get("platform", "social")).lower(),
                "module": "social_media_intelligence",
                "reference": p.get("url") or p.get("text", "")[:60],
                "confidence": p.get("credibility_score", 0.95) or 0.95,
                "raw_data": {
                    "post_id": post_id,
                    "platform": p.get("platform"),
                    "author": p.get("author"),
                    "text": p.get("text"),
                    "url": p.get("url"),
                    "created_at": p.get("created_at"),
                    "likes": p.get("likes_count", 0),
                    "views": p.get("views_count", 0),
                    "shares": p.get("shares_count", 0),
                    "comments_count": p.get("comments_count", 0),
                    "post_type": p.get("post_type", "post"),
                    "video_url": p.get("video_url"),
                    "comments": p.get("comments", []),
                    "entities": p.get("entities", [])
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            try:
                evidence_repo._sync_write(
                    {"hash": f"ev_soc_{post_id}", "tenant_id": current_user.tenant_id},
                    ev_data
                )
            except Exception as ev_err:
                app_logger.debug(f"Failed to seal auto-crawled evidence: {ev_err}")

            # Seal video / reel media record if video_url is present
            if p.get("video_url") or p.get("post_type") in ["reel", "video"]:
                m_url = p.get("video_url") or p.get("url")
                media_item = {
                    "id": f"med_soc_{uuid.uuid4().hex[:8]}",
                    "url": m_url,
                    "canonical_source_url": p.get("url"),
                    "media_type": "video",
                    "title": f"{str(p.get('platform', 'Social')).upper()} {str(p.get('post_type', 'Reel')).upper()}: {str(p.get('text', ''))[:60]}",
                    "description": p.get("text", ""),
                    "source_platform": p.get("platform"),
                    "source_provider": "social_media_intelligence",
                    "publication_date": p.get("created_at"),
                    "collection_date": datetime.utcnow().isoformat(),
                    "metadata": {
                        "post_type": p.get("post_type", "reel"),
                        "author": p.get("author"),
                        "comments_count": p.get("comments_count", 0)
                    }
                }
                try:
                    inv = investigation_repo.get(req.investigation_id, current_user.tenant_id)
                    if inv:
                        cur_media = inv.get("media", [])
                        if not any(m.get("url") == m_url for m in cur_media):
                            cur_media.append(media_item)
                            inv["media"] = cur_media
                            investigation_repo._sync_write({"id": req.investigation_id, "tenant_id": current_user.tenant_id}, inv)
                            case_repo._sync_write({"id": req.investigation_id, "tenant_id": current_user.tenant_id}, inv)
                except Exception as m_err:
                    app_logger.debug(f"Failed to seal auto-crawled media: {m_err}")

    return {
        "target": clean_target,
        "total": len(results),
        "results": results,
        "message": f"Successfully auto-crawled and extracted {len(results)} social dispatches, videos, and comments for '{clean_target}'."
    }


