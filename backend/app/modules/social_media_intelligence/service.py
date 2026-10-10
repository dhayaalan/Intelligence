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
from app.modules.social_media_intelligence.engines.cib_engine import cib_engine
from app.modules.social_media_intelligence.engines.credibility_engine import credibility_engine


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
            SocialPlatformType.YOUTUBE
        ]

        tasks = []
        if SocialPlatformType.BLUESKY in requested_platforms:
            tasks.append(bluesky_collector.search_posts(query, limit=request.limit))
        if SocialPlatformType.TELEGRAM in requested_platforms:
            tasks.append(telegram_collector.search_posts(query, limit=request.limit))
        if SocialPlatformType.REDDIT in requested_platforms:
            tasks.append(reddit_collector.search_posts(query, limit=request.limit))
        if SocialPlatformType.MASTODON in requested_platforms:
            tasks.append(mastodon_collector.search_posts(query, limit=request.limit))
        if SocialPlatformType.YOUTUBE in requested_platforms:
            tasks.append(youtube_collector.search_posts(query, limit=min(request.limit, 10)))

        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        all_posts: List[SocialPost] = []
        for res in results_lists:
            if isinstance(res, list):
                all_posts.extend(res)
            elif isinstance(res, Exception):
                app_logger.warning(f"Social collector subtask raised error: {res}")

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
