import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from bs4 import BeautifulSoup

from app.core.logging import app_logger
from app.modules.social_media_intelligence.models import SocialPost, SocialPlatformType
from app.modules.social_media_intelligence.crawler_engine import (
    resilient_crawler_engine,
    CollectorStatus,
)

MASTODON_DEFAULT_INSTANCES = [
    "https://mastodon.social",
    "https://infosec.exchange"
]


class MastodonCollector:
    """
    Mastodon / Fediverse intelligence collector.
    Searches public status timelines and hashtag feeds across decentralized instances.
    Executes resilient collection with 429 adaptive throttling, cursor tracking,
    and zero fake data generation.
    """

    async def search_posts(
        self,
        query: str,
        limit: int = 25,
        cursor: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[SocialPost]:
        posts: List[SocialPost] = []
        clean_query = query.strip().lstrip("#")
        if not clean_query:
            return posts

        instance = MASTODON_DEFAULT_INSTANCES[0]
        tag_url = f"{instance}/api/v1/timelines/tag/{clean_query}"
        params: Dict[str, Any] = {"limit": min(limit, 40)}
        if cursor:
            params["max_id"] = cursor

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp, status, msg = await resilient_crawler_engine.execute_request_with_resilience(
                platform=SocialPlatformType.MASTODON,
                client=client,
                url=tag_url,
                method="GET",
                params=params,
            )

            if status == CollectorStatus.SUCCESS and resp is not None:
                try:
                    statuses = resp.json()
                    last_id = None
                    for s in statuses:
                        post = self._parse_mastodon_status(s)
                        if post:
                            posts.append(post)
                            last_id = str(s.get("id"))

                    if not posts:
                        # Fallback to general search API
                        search_url = f"{instance}/api/v2/search"
                        s_resp, s_status, _ = await resilient_crawler_engine.execute_request_with_resilience(
                            platform=SocialPlatformType.MASTODON,
                            client=client,
                            url=search_url,
                            method="GET",
                            params={"q": clean_query, "type": "statuses", "limit": min(limit, 30)},
                        )
                        if s_status == CollectorStatus.SUCCESS and s_resp is not None:
                            search_statuses = s_resp.json().get("statuses", [])
                            for s in search_statuses:
                                post = self._parse_mastodon_status(s)
                                if post:
                                    posts.append(post)

                    if job_id:
                        resilient_crawler_engine.save_checkpoint(
                            job_id=job_id,
                            platform=SocialPlatformType.MASTODON,
                            query=clean_query,
                            cursor=last_id,
                            items_count=len(posts),
                            status=CollectorStatus.SUCCESS if posts else CollectorStatus.SUCCESS_EMPTY
                        )
                except Exception as e:
                    app_logger.warning(f"Error parsing Mastodon response: {e}")
            else:
                app_logger.info(
                    f"Mastodon search for '{clean_query}' completed with status: {status.value}. Info: {msg}"
                )
                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.MASTODON,
                        query=clean_query,
                        cursor=None,
                        items_count=0,
                        status=status
                    )

        return resilient_crawler_engine.deduplicate_posts(posts)

    def _parse_mastodon_status(self, item: Dict[str, Any]) -> Optional[SocialPost]:
        try:
            sid = str(item.get("id", ""))
            account = item.get("account", {})
            username = account.get("username", "user")
            acct = account.get("acct", username)
            account_id = str(account.get("id", acct))
            created_at = item.get("created_at") or datetime.now(timezone.utc).isoformat()
            url = item.get("url") or f"https://mastodon.social/@{acct}/{sid}"

            raw_html = item.get("content", "")
            soup = BeautifulSoup(raw_html, "html.parser")
            text = soup.get_text(separator="\n").strip()

            reblogs_count = item.get("reblogs_count", 0)
            favourites_count = item.get("favourites_count", 0)

            links: List[str] = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if not href.startswith("https://mastodon.social/tags/"):
                    links.append(href)

            tags = [t.get("name") for t in item.get("tags", []) if t.get("name")]

            return SocialPost(
                id=f"masto_{sid}",
                platform=SocialPlatformType.MASTODON,
                author=f"@{acct}",
                author_id=f"masto_acc_{account_id}",
                text=text,
                created_at=created_at,
                url=url,
                langs=[item.get("language", "en") or "en"],
                links=links,
                likes_count=favourites_count,
                reposts_count=reblogs_count,
                entities=tags,
                credibility_score=None
            )
        except Exception as e:
            app_logger.warning(f"Failed to parse Mastodon status: {e}")
            return None


mastodon_collector = MastodonCollector()
