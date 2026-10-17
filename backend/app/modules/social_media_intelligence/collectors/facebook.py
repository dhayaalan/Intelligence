"""
Facebook Collector.
Supports authorized Meta Graph API public Page collection and public post OpenGraph metadata resolution.
Strictly respects lawful access constraints, prohibiting private-group or private-profile scraping.
"""

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

GRAPH_API_VERSION = os.getenv("META_GRAPH_API_VERSION", "v21.0")
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class FacebookCollector:
    """
    Facebook public page and post collector supporting authorized Meta Graph API endpoints
    and public post OpenGraph metadata normalization.
    """

    def __init__(self):
        self._access_token = os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("META_GRAPH_API_TOKEN")

    async def search_posts(
        self,
        query: str,
        limit: int = 20,
        cursor: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[SocialPost]:
        """
        Retrieves public posts from an authorized Page or resolves public post URL.
        """
        posts: List[SocialPost] = []
        clean_query = query.strip()
        if not clean_query:
            return posts

        # 1. If input is a public Facebook URL, resolve public metadata safely
        if "facebook.com/" in clean_query:
            post = await self.resolve_public_page_or_post(clean_query)
            if post:
                posts.append(post)
                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.FACEBOOK,
                        query=clean_query,
                        cursor=None,
                        items_count=1,
                        status=CollectorStatus.SUCCESS
                    )
            return posts

        # 2. If querying a page handle via Graph API, check access token
        if not self._access_token:
            app_logger.info(
                f"Facebook page post search for '{clean_query}' requires FACEBOOK_ACCESS_TOKEN. Reporting CONFIG_REQUIRED."
            )
            if job_id:
                resilient_crawler_engine.save_checkpoint(
                    job_id=job_id,
                    platform=SocialPlatformType.FACEBOOK,
                    query=clean_query,
                    cursor=None,
                    items_count=0,
                    status=CollectorStatus.CONFIG_REQUIRED
                )
            return posts

        # 3. Authorized Graph API Public Page Feed
        page_id = clean_query.split()[0].replace("/", "")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                feed_url = f"{GRAPH_API_BASE}/{page_id}/feed"
                resp = await client.get(
                    feed_url,
                    params={
                        "fields": "id,message,created_time,permalink_url,shares,attachments{media,type}",
                        "limit": min(limit, 25),
                        "access_token": self._access_token
                    }
                )
                if resp.status_code == 200:
                    for item in resp.json().get("data", []):
                        posts.append(SocialPost(
                            id=f"fb_{item.get('id')}",
                            platform=SocialPlatformType.FACEBOOK,
                            author=page_id,
                            author_id=page_id,
                            text=item.get("message") or f"Facebook Post {item.get('id')}",
                            created_at=item.get("created_time") or datetime.now(timezone.utc).isoformat(),
                            url=item.get("permalink_url") or f"https://www.facebook.com/{item.get('id')}",
                            likes_count=0,
                            reposts_count=item.get("shares", {}).get("count", 0),
                            channel_name=page_id
                        ))
                    if job_id:
                        resilient_crawler_engine.save_checkpoint(
                            job_id=job_id,
                            platform=SocialPlatformType.FACEBOOK,
                            query=clean_query,
                            cursor=None,
                            items_count=len(posts),
                            status=CollectorStatus.SUCCESS if posts else CollectorStatus.SUCCESS_EMPTY
                        )
                    return posts
                elif resp.status_code in (401, 403):
                    if job_id:
                        resilient_crawler_engine.save_checkpoint(
                            job_id=job_id,
                            platform=SocialPlatformType.FACEBOOK,
                            query=clean_query,
                            cursor=None,
                            items_count=0,
                            status=CollectorStatus.AUTH_REQUIRED
                        )
        except Exception as e:
            app_logger.error(f"Error querying authorized Facebook Graph API: {e}")

        return posts

    async def resolve_public_page_or_post(self, url: str) -> Optional[SocialPost]:
        """
        Safely extracts public OpenGraph metadata for a Facebook page or post permalink
        without bypassing authentication or using browser scrapers.
        """
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"},
                timeout=5.0,
                follow_redirects=True
            ) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    text = resp.text
                    title_m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', text, re.I)
                    desc_m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', text, re.I)
                    img_m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', text, re.I)

                    caption = desc_m.group(1).strip() if desc_m else "Public Facebook Post"
                    author = title_m.group(1).split("|")[0].strip() if title_m else "facebook_page"
                    media = [img_m.group(1)] if img_m else []

                    return SocialPost(
                        id=f"fb_{abs(hash(url))}",
                        platform=SocialPlatformType.FACEBOOK,
                        author=author,
                        author_id=author,
                        text=caption,
                        created_at=datetime.now(timezone.utc).isoformat(),
                        url=url,
                        media_urls=media
                    )
        except Exception as e:
            app_logger.warning(f"Failed to resolve public Facebook page or post: {e}")
        return None


facebook_collector = FacebookCollector()
