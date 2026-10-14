import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from app.core.logging import app_logger
from app.modules.social_media_intelligence.models import SocialPost, SocialPlatformType
from app.modules.social_media_intelligence.crawler_engine import (
    resilient_crawler_engine,
    CollectorStatus,
)

BSKY_PUBLIC_API = "https://public.api.bsky.app/xrpc"


class BlueskyCollector:
    """
    Bluesky (AT Protocol) collector utilizing the public XRPC AppView directory.
    Executes resilient collection with adaptive rate-limit detection (HTTP 429),
    cursor tracking, and strict zero-fake-data honesty.
    """

    async def search_posts(
        self,
        query: str,
        limit: int = 25,
        cursor: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[SocialPost]:
        posts: List[SocialPost] = []
        clean_query = query.strip()
        if not clean_query:
            return posts

        url = f"{BSKY_PUBLIC_API}/app.bsky.feed.searchPosts"
        params: Dict[str, Any] = {"q": clean_query, "limit": min(limit, 50)}
        if cursor:
            params["cursor"] = cursor

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp, status, msg = await resilient_crawler_engine.execute_request_with_resilience(
                platform=SocialPlatformType.BLUESKY,
                client=client,
                url=url,
                method="GET",
                params=params,
            )

            if status == CollectorStatus.SUCCESS and resp is not None:
                data = resp.json()
                next_cursor = data.get("cursor")
                for item in data.get("posts", []):
                    post = self._parse_post(item)
                    if post:
                        posts.append(post)

                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.BLUESKY,
                        query=clean_query,
                        cursor=next_cursor,
                        items_count=len(posts),
                        status=CollectorStatus.SUCCESS if posts else CollectorStatus.SUCCESS_EMPTY
                    )
            else:
                app_logger.info(
                    f"Bluesky collection for '{clean_query}' completed with status: {status.value}. Info: {msg}"
                )
                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.BLUESKY,
                        query=clean_query,
                        cursor=None,
                        items_count=0,
                        status=status
                    )

        return resilient_crawler_engine.deduplicate_posts(posts)

    async def get_author_feed(self, handle_or_did: str, limit: int = 20) -> List[SocialPost]:
        posts: List[SocialPost] = []
        actor = handle_or_did.strip().lstrip("@")
        if not actor:
            return posts

        url = f"{BSKY_PUBLIC_API}/app.bsky.feed.getAuthorFeed"
        params = {"actor": actor, "limit": min(limit, 30)}

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp, status, msg = await resilient_crawler_engine.execute_request_with_resilience(
                platform=SocialPlatformType.BLUESKY,
                client=client,
                url=url,
                method="GET",
                params=params,
            )
            if status == CollectorStatus.SUCCESS and resp is not None:
                data = resp.json()
                for feed_item in data.get("feed", []):
                    item = feed_item.get("post", {})
                    post = self._parse_post(item)
                    if post:
                        posts.append(post)
            else:
                app_logger.info(f"Bluesky author feed for '{actor}' returned status {status.value}: {msg}")

        return resilient_crawler_engine.deduplicate_posts(posts)

    def _parse_post(self, item: Dict[str, Any]) -> Optional[SocialPost]:
        try:
            uri = item.get("uri", "")
            rkey = uri.split("/")[-1] if "/" in uri else uri
            author_obj = item.get("author", {})
            handle = author_obj.get("handle") or author_obj.get("did") or "unknown.bsky.social"
            did = author_obj.get("did", handle)
            record = item.get("record", {})
            text = record.get("text", "")
            created_at = record.get("createdAt") or datetime.now(timezone.utc).isoformat()
            url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "https://bsky.app"

            links: List[str] = []
            for facet in record.get("facets", []):
                for feature in facet.get("features", []):
                    if feature.get("$type") == "app.bsky.richtext.facet#link":
                        uri_val = feature.get("uri")
                        if uri_val:
                            links.append(uri_val)

            entities = re.findall(r'@([a-zA-Z0-9_.-]+)', text) + re.findall(r'#([a-zA-Z0-9_]+)', text)

            return SocialPost(
                id=f"bsky_{rkey}",
                platform=SocialPlatformType.BLUESKY,
                author=f"@{handle}",
                author_id=did,
                text=text,
                created_at=created_at,
                url=url,
                langs=record.get("langs", ["en"]),
                links=links,
                likes_count=item.get("likeCount", 0),
                reposts_count=item.get("repostCount", 0),
                entities=list(set(entities)),
                credibility_score=None
            )
        except Exception as e:
            app_logger.warning(f"Failed to parse Bluesky post item: {e}")
            return None


bluesky_collector = BlueskyCollector()
