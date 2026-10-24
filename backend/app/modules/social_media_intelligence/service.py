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

    async def auto_crawl_target(
        self,
        target: str,
        limit: int = 15,
        extract_comments: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Automatically crawls and extracts social posts, video streams, reels,
        and comment threads for the target across all platforms without requiring
        manual URL input from the user.
        """
        clean_target = (target or "").strip()
        if not clean_target:
            return []

        from app.modules.social_media_intelligence.crawler_engine import resilient_social_crawler

        # 1. Search authentic posts across all operational social collectors
        search_req = SocialSearchRequest(query=clean_target, limit=limit, detect_cib=True)
        search_resp = await self.execute_search(search_req)
        posts = search_resp.results

        # 2. Automatically deep-crawl the top posts with valid URLs to extract nested comment trees & video streams
        enriched_posts: List[Dict[str, Any]] = []

        async def _deep_crawl_single(p: SocialPost) -> Dict[str, Any]:
            post_dict = {
                "id": p.id,
                "platform": p.platform.value if hasattr(p.platform, "value") else str(p.platform),
                "author": p.author,
                "author_id": p.author_id,
                "text": p.text,
                "created_at": p.created_at,
                "url": p.url,
                "likes_count": p.likes_count,
                "views_count": p.views_count or 0,
                "shares_count": p.reposts_count,
                "comments_count": getattr(p, "comments_count", 0),
                "post_type": getattr(p, "post_type", "post"),
                "video_url": getattr(p, "video_url", None),
                "media_urls": p.media_urls,
                "comments": [c.dict() if hasattr(c, "dict") else dict(c) for c in getattr(p, "comments", [])],
                "entities": p.entities,
                "credibility_score": p.credibility_score
            }

            if p.url and p.url.startswith(("http://", "https://")):
                try:
                    crawl_res = await resilient_social_crawler.crawl_url(
                        url=p.url,
                        extract_comments=extract_comments,
                        extract_media=True,
                        bypass_blocking=True
                    )
                    if crawl_res:
                        post_dict["post_type"] = crawl_res.post_type or post_dict["post_type"]
                        if crawl_res.video_url:
                            post_dict["video_url"] = crawl_res.video_url
                        if crawl_res.media_urls:
                            post_dict["media_urls"] = list(set(post_dict["media_urls"] + crawl_res.media_urls))
                        if crawl_res.comments:
                            post_dict["comments"] = [c.dict() if hasattr(c, "dict") else dict(c) for c in crawl_res.comments]
                            post_dict["comments_count"] = len(post_dict["comments"])
                        if crawl_res.likes_count:
                            post_dict["likes_count"] = max(post_dict["likes_count"], crawl_res.likes_count)
                        if crawl_res.extracted_entities:
                            post_dict["entities"] = list(set(post_dict["entities"] + crawl_res.extracted_entities))
                except Exception as crawl_err:
                    app_logger.debug(f"Auto-crawl deep resolution skipped for {p.url}: {crawl_err}")

            return post_dict

        if posts:
            tasks = [_deep_crawl_single(p) for p in posts[:min(len(posts), 10)]]
            crawl_results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in crawl_results:
                if isinstance(res, dict):
                    enriched_posts.append(res)

        return enriched_posts

    async def investigate_youtube_video(self, url_or_id: str) -> Optional[YouTubeInvestigationResult]:
        return await youtube_collector.investigate_video(url_or_id)


social_media_service = SocialMediaIntelligenceService()
