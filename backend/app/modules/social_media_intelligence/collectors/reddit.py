import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from app.core.logging import app_logger
from app.modules.social_media_intelligence.models import SocialPost, SocialPlatformType
from app.modules.social_media_intelligence.crawler_engine import (
    resilient_crawler_engine,
    CollectorStatus,
)


class RedditCollector:
    """
    Reddit content and author search collector.
    Executes resilient collection with adaptive rate-limit detection (HTTP 429),
    cursor tracking ('after'), and strict zero-fake-data honesty.
    """

    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        self._access_token: Optional[str] = None

    async def search_posts(
        self,
        query: str,
        subreddit: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[SocialPost]:
        posts: List[SocialPost] = []
        clean_query = query.strip()
        if not clean_query:
            return posts

        base_url = f"https://www.reddit.com/r/{subreddit}/search.json" if subreddit else "https://www.reddit.com/search.json"
        params: Dict[str, Any] = {
            "q": clean_query,
            "sort": "relevance",
            "limit": min(limit, 50),
            "restrict_sr": bool(subreddit)
        }
        if cursor:
            params["after"] = cursor

        headers = {
            "User-Agent": "Sentinel-Intelligence-Recon/2.0 (Security & Forensic Analysis; contact: sec-audit@sential.io)"
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp, status, msg = await resilient_crawler_engine.execute_request_with_resilience(
                platform=SocialPlatformType.REDDIT,
                client=client,
                url=base_url,
                method="GET",
                headers=headers,
                params=params,
            )

            if status == CollectorStatus.SUCCESS and resp is not None:
                try:
                    data = resp.json()
                    after_token = data.get("data", {}).get("after")
                    children = data.get("data", {}).get("children", [])
                    for child in children:
                        post_data = child.get("data", {})
                        post = self._parse_reddit_post(post_data)
                        if post:
                            posts.append(post)

                    if job_id:
                        resilient_crawler_engine.save_checkpoint(
                            job_id=job_id,
                            platform=SocialPlatformType.REDDIT,
                            query=clean_query,
                            cursor=after_token,
                            items_count=len(posts),
                            status=CollectorStatus.SUCCESS if posts else CollectorStatus.SUCCESS_EMPTY
                        )
                except Exception as e:
                    app_logger.warning(f"Error parsing Reddit JSON response: {e}")
            else:
                retry_after_val = resilient_crawler_engine.parse_retry_after(resp) if resp is not None else None
                app_logger.info(
                    f"Reddit collection for '{clean_query}' completed with status: {status.value}. Info: {msg}"
                )
                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.REDDIT,
                        query=clean_query,
                        cursor=None,
                        items_count=0,
                        status=status,
                        retry_after_seconds=retry_after_val,
                        status_message=msg
                    )

        return resilient_crawler_engine.deduplicate_posts(posts)

    def _parse_reddit_post(self, data: Dict[str, Any]) -> Optional[SocialPost]:
        try:
            pid = data.get("id", "")
            title = data.get("title", "")
            selftext = data.get("selftext", "")
            author = data.get("author", "anonymous")
            permalink = data.get("permalink", "")
            created_utc = data.get("created_utc", 0)
            score = data.get("score", 0)
            num_comments = data.get("num_comments", 0)
            sub = data.get("subreddit", "all")

            created_at = (
                datetime.fromtimestamp(created_utc, timezone.utc).isoformat()
                if created_utc
                else datetime.now(timezone.utc).isoformat()
            )
            full_text = f"{title}\n\n{selftext}".strip()
            url = f"https://reddit.com{permalink}" if permalink else f"https://reddit.com/r/{sub}/comments/{pid}"

            links = re.findall(r'https?://[^\s()<>]+', full_text)
            entities = re.findall(r'r\/([a-zA-Z0-9_]+)', full_text) + re.findall(r'u\/([a-zA-Z0-9_]+)', full_text)

            return SocialPost(
                id=f"reddit_{pid}",
                platform=SocialPlatformType.REDDIT,
                author=f"u/{author}",
                author_id=f"reddit_user_{author}",
                text=full_text,
                created_at=created_at,
                url=url,
                langs=["en"],
                links=links,
                likes_count=score,
                reposts_count=num_comments,
                channel_name=f"r/{sub}",
                entities=list(set(entities)),
                credibility_score=None
            )
        except Exception as e:
            app_logger.warning(f"Failed to parse Reddit post: {e}")
            return None


reddit_collector = RedditCollector()
