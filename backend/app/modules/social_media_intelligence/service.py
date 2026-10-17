import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.core.logging import app_logger
from app.modules.social_media_intelligence.models import (
    SocialPost,
    SocialPlatformType,
    SocialSearchRequest,
    SocialSearchResponse,
    CibCluster,
    CredibilityScore,
    YouTubeInvestigationResult
)
from app.modules.social_media_intelligence.collectors.bluesky import bluesky_collector
from app.modules.social_media_intelligence.collectors.telegram import telegram_collector
from app.modules.social_media_intelligence.collectors.reddit import reddit_collector
from app.modules.social_media_intelligence.collectors.mastodon import mastodon_collector
from app.modules.social_media_intelligence.collectors.youtube import youtube_collector
from app.modules.social_media_intelligence.collectors.instagram import instagram_collector
from app.modules.social_media_intelligence.collectors.facebook import facebook_collector
from app.modules.social_media_intelligence.engines.cib_engine import cib_engine
from app.modules.social_media_intelligence.engines.credibility_engine import credibility_engine
from app.modules.social_media_intelligence.crawler_engine import resilient_crawler_engine, CollectorStatus


class SocialMediaIntelligenceService:
    """
    Central orchestration service for social media intelligence collection,
    multi-platform aggregation, CIB detection, and video forensics.
    """

    async def execute_search(self, request: SocialSearchRequest) -> SocialSearchResponse:
        start_time = time.time()
        search_id = f"soc_{uuid.uuid4().hex[:10]}"
        query = request.query.strip()
        requested_platforms = request.platforms or [
            SocialPlatformType.BLUESKY,
            SocialPlatformType.TELEGRAM,
            SocialPlatformType.REDDIT,
            SocialPlatformType.MASTODON,
            SocialPlatformType.YOUTUBE,
            SocialPlatformType.INSTAGRAM,
            SocialPlatformType.FACEBOOK
        ]

        tasks = []
        platform_keys = []
        if SocialPlatformType.BLUESKY in requested_platforms:
            tasks.append(bluesky_collector.search_posts(query, limit=request.limit, job_id=search_id))
            platform_keys.append(SocialPlatformType.BLUESKY)
        if SocialPlatformType.TELEGRAM in requested_platforms:
            tasks.append(telegram_collector.search_posts(query, limit=request.limit, job_id=search_id))
            platform_keys.append(SocialPlatformType.TELEGRAM)
        if SocialPlatformType.REDDIT in requested_platforms:
            tasks.append(reddit_collector.search_posts(query, limit=request.limit, job_id=search_id))
            platform_keys.append(SocialPlatformType.REDDIT)
        if SocialPlatformType.MASTODON in requested_platforms:
            tasks.append(mastodon_collector.search_posts(query, limit=request.limit, job_id=search_id))
            platform_keys.append(SocialPlatformType.MASTODON)
        if SocialPlatformType.YOUTUBE in requested_platforms:
            tasks.append(youtube_collector.search_posts(query, limit=min(request.limit, 10)))
            platform_keys.append(SocialPlatformType.YOUTUBE)
        if SocialPlatformType.INSTAGRAM in requested_platforms:
            tasks.append(instagram_collector.search_posts(query, limit=request.limit, job_id=search_id))
            platform_keys.append(SocialPlatformType.INSTAGRAM)
        if SocialPlatformType.FACEBOOK in requested_platforms:
            tasks.append(facebook_collector.search_posts(query, limit=request.limit, job_id=search_id))
            platform_keys.append(SocialPlatformType.FACEBOOK)

        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        all_posts: List[SocialPost] = []
        provider_statuses: Dict[str, str] = {}
        collector_telemetry: Dict[str, Dict[str, Any]] = {}

        for idx, res in enumerate(results_lists):
            plat = platform_keys[idx]
            plat_name = plat.value
            cp = resilient_crawler_engine.get_checkpoint(search_id, plat)
            if isinstance(res, list):
                if res:
                    all_posts.extend(res)
                    provider_statuses[plat_name] = f"SUCCESS ({len(res)} authentic posts)"
                    collector_telemetry[plat_name] = {
                        "status": "SUCCESS",
                        "items_count": len(res),
                        "rate_limited": False,
                        "retry_after_seconds": None,
                        "status_message": f"Retrieved {len(res)} authentic posts."
                    }
                else:
                    if cp and cp.status == CollectorStatus.CONFIG_REQUIRED:
                        provider_statuses[plat_name] = "CONFIG_REQUIRED (Access credentials required to query this platform)"
                        collector_telemetry[plat_name] = {
                            "status": "CONFIG_REQUIRED",
                            "items_count": 0,
                            "rate_limited": False,
                            "retry_after_seconds": None,
                            "status_message": "Platform API requires credentials (access token) not configured in environment."
                        }
                    elif cp and cp.status == CollectorStatus.ACCESS_DENIED:
                        provider_statuses[plat_name] = "ACCESS_DENIED (HTTP 403: Platform policy restricts unauthenticated requests)"
                        collector_telemetry[plat_name] = {
                            "status": "ACCESS_DENIED",
                            "items_count": 0,
                            "rate_limited": False,
                            "retry_after_seconds": None,
                            "status_message": cp.status_message or "Access restricted by platform policy."
                        }
                    elif cp and cp.status == CollectorStatus.RATE_LIMITED:
                        retry_str = f", Retry-After: {cp.retry_after_seconds:.1f}s" if cp.retry_after_seconds else ""
                        provider_statuses[plat_name] = f"RATE_LIMITED (HTTP 429: Platform quota reached{retry_str})"
                        collector_telemetry[plat_name] = {
                            "status": "RATE_LIMITED",
                            "items_count": 0,
                            "rate_limited": True,
                            "retry_after_seconds": cp.retry_after_seconds,
                            "status_message": cp.status_message or "Rate limit exceeded."
                        }
                    elif cp and cp.status == CollectorStatus.UNAVAILABLE:
                        provider_statuses[plat_name] = "UNAVAILABLE (Platform network or endpoint error)"
                        collector_telemetry[plat_name] = {
                            "status": "UNAVAILABLE",
                            "items_count": 0,
                            "rate_limited": False,
                            "retry_after_seconds": None,
                            "status_message": cp.status_message or "Platform unreachable."
                        }
                    else:
                        provider_statuses[plat_name] = "EMPTY (Zero authentic matches found)"
                        collector_telemetry[plat_name] = {
                            "status": "EMPTY",
                            "items_count": 0,
                            "rate_limited": False,
                            "retry_after_seconds": None,
                            "status_message": "Zero matching records discovered."
                        }
            elif isinstance(res, Exception):
                app_logger.warning(f"Social collector subtask raised error: {res}")
                provider_statuses[plat_name] = f"ERROR ({type(res).__name__})"
                collector_telemetry[plat_name] = {
                    "status": "ERROR",
                    "items_count": 0,
                    "rate_limited": False,
                    "retry_after_seconds": None,
                    "status_message": str(res)
                }

        # Filter by min_credibility if specified
        if request.min_credibility > 0:
            all_posts = [p for p in all_posts if (p.credibility_score or 100.0) >= request.min_credibility]

        # Sort by creation date descending
        all_posts.sort(key=lambda p: p.created_at, reverse=True)

        # CIB cluster detection if enabled
        cib_clusters: List[CibCluster] = []
        if request.detect_cib and len(all_posts) >= 2:
            try:
                cib_clusters = cib_engine.detect_clusters(all_posts)
            except Exception as e:
                app_logger.warning(f"Error executing CIB cluster analysis: {e}")

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return SocialSearchResponse(
            search_id=search_id,
            query=query,
            total_results=len(all_posts),
            results=all_posts,
            cib_clusters=cib_clusters,
            provider_statuses=provider_statuses,
            collector_telemetry=collector_telemetry,
            execution_time_ms=elapsed_ms
        )


    async def analyze_cib(self, posts: List[SocialPost]) -> List[CibCluster]:
        return cib_engine.detect_clusters(posts)

    def analyze_credibility(
        self,
        target_handle: str,
        platform: SocialPlatformType,
        posts: List[SocialPost]
    ) -> CredibilityScore:
        return credibility_engine.score_account(
            target_handle=target_handle,
            platform=platform,
            posts=posts
        )

    async def investigate_youtube_video(self, url_or_id: str) -> Optional[YouTubeInvestigationResult]:
        return await youtube_collector.investigate_video(url_or_id)


social_media_service = SocialMediaIntelligenceService()
