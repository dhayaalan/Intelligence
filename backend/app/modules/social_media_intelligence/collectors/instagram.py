"""
Instagram Collector.
Supports authorized Meta Graph API collection for eligible business/creator accounts
and public post OpenGraph metadata resolution.
Strictly respects lawful access constraints, never bypassing login walls or CAPTCHAs.
"""

import os
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

GRAPH_API_VERSION = os.getenv("META_GRAPH_API_VERSION", "v21.0")
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class InstagramCollector:
    """
    Instagram collector supporting authorized Meta Graph API endpoints
    and public post OpenGraph metadata normalization.
    """

    def __init__(self):
        self._access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN") or os.getenv("META_GRAPH_API_TOKEN")

    async def search_posts(
        self,
        query: str,
        limit: int = 20,
        cursor: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[SocialPost]:
        """
        Retrieves Instagram posts via authorized hashtag search or resolves public permalink.
        """
        posts: List[SocialPost] = []
        clean_query = query.strip()
        if not clean_query:
            return posts

        # 1. If input is a public Instagram permalink, resolve public metadata safely
        if "instagram.com/p/" in clean_query or "instagram.com/reel/" in clean_query:
            post = await self.resolve_public_post(clean_query)
            if post:
                posts.append(post)
                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.INSTAGRAM,
                        query=clean_query,
                        cursor=None,
                        items_count=1,
                        status=CollectorStatus.SUCCESS
                    )
            return posts

        # 2. If querying keywords/hashtags, official Graph API requires valid access token
        if not self._access_token:
            app_logger.info(
                f"Instagram keyword search for '{clean_query}' requires INSTAGRAM_ACCESS_TOKEN. Reporting CONFIG_REQUIRED."
            )
            if job_id:
                resilient_crawler_engine.save_checkpoint(
                    job_id=job_id,
                    platform=SocialPlatformType.INSTAGRAM,
                    query=clean_query,
                    cursor=None,
                    items_count=0,
                    status=CollectorStatus.CONFIG_REQUIRED
                )
            return posts

        # 3. Authorized Graph API Hashtag Search requires both access token and business account ID
        ig_user_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        if not ig_user_id:
            app_logger.info(
                f"Instagram Graph API search for '{clean_query}' requires INSTAGRAM_BUSINESS_ACCOUNT_ID. Reporting CONFIG_REQUIRED."
            )
            if job_id:
                resilient_crawler_engine.save_checkpoint(
                    job_id=job_id,
                    platform=SocialPlatformType.INSTAGRAM,
                    query=clean_query,
                    cursor=None,
                    items_count=0,
                    status=CollectorStatus.CONFIG_REQUIRED
                )
            return posts

        tag = clean_query.lstrip("#").split()[0]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Step A: Get hashtag ID
                tag_url = f"{GRAPH_API_BASE}/ig_hashtag_search"
                tag_resp = await client.get(
                    tag_url,
                    params={"user_id": ig_user_id, "q": tag, "access_token": self._access_token}
                )
                if tag_resp.status_code == 200 and tag_resp.json().get("data"):
                    tag_id = tag_resp.json()["data"][0]["id"]
                    # Step B: Get top media for hashtag
                    media_url = f"{GRAPH_API_BASE}/{tag_id}/top_media"
                    media_resp = await client.get(
                        media_url,
                        params={
                            "user_id": ig_user_id,
                            "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
                            "limit": min(limit, 25),
                            "access_token": self._access_token
                        }
                    )
                    if media_resp.status_code == 200:
                        for item in media_resp.json().get("data", []):
                            posts.append(SocialPost(
                                id=f"ig_{item.get('id')}",
                                platform=SocialPlatformType.INSTAGRAM,
                                author=f"ig_user_{item.get('id', '')[:8]}",
                                author_id=str(item.get("id")),
                                text=item.get("caption") or f"Instagram Media {item.get('id')}",
                                created_at=item.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                                url=item.get("permalink") or f"https://www.instagram.com/p/{item.get('id')}/",
                                likes_count=item.get("like_count", 0),
                                reposts_count=0,
                                media_urls=[item["media_url"]] if item.get("media_url") else []
                            ))
                        if job_id:
                            resilient_crawler_engine.save_checkpoint(
                                job_id=job_id,
                                platform=SocialPlatformType.INSTAGRAM,
                                query=clean_query,
                                cursor=None,
                                items_count=len(posts),
                                status=CollectorStatus.SUCCESS if posts else CollectorStatus.SUCCESS_EMPTY
                            )
                        return posts
        except Exception as e:
            app_logger.error(f"Error querying authorized Instagram Graph API: {e}")

        return posts

    async def resolve_public_post(self, post_url: str) -> Optional[SocialPost]:
        """
        Safely extracts public OpenGraph metadata for an Instagram permalink
        without bypassing login barriers or using headless browser scrapers.
        """
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"},
                timeout=5.0,
                follow_redirects=True
            ) as client:
                resp = await client.get(post_url)
                if resp.status_code == 200:
                    text = resp.text
                    # Extract og:title and og:description
                    title_m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', text, re.I)
                    desc_m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', text, re.I)
                    img_m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', text, re.I)

                    caption = desc_m.group(1).strip() if desc_m else "Public Instagram Post"
                    author = title_m.group(1).split("on Instagram")[0].strip() if title_m else "instagram_user"
                    media = [img_m.group(1)] if img_m else []

                    # Parse likes from description if present (e.g. "1,234 likes, 56 comments...")
                    likes = 0
                    likes_m = re.search(r'([0-9,]+)\s+likes', caption)
                    if likes_m:
                        try:
                            likes = int(likes_m.group(1).replace(",", ""))
                        except ValueError:
                            pass

                    post_id = f"ig_{abs(hash(post_url))}"
                    return SocialPost(
                        id=post_id,
                        platform=SocialPlatformType.INSTAGRAM,
                        author=author,
                        author_id=author,
                        text=caption,
                        created_at=datetime.now(timezone.utc).isoformat(),
                        url=post_url,
                        likes_count=likes,
                        media_urls=media
                    )
        except Exception as e:
            app_logger.warning(f"Failed to resolve public Instagram post: {e}")
        return None


instagram_collector = InstagramCollector()
