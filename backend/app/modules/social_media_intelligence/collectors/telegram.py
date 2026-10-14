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


class TelegramCollector:
    """
    Telegram public channel monitor that ingests authentic posts from `https://t.me/s/{channel}`.
    Extracts post text, timestamps, views, forwards, and media indicators keylessly.
    Zero fake data generation.
    """

    async def get_channel_posts(
        self,
        channel_name: str,
        limit: int = 25,
        job_id: Optional[str] = None
    ) -> List[SocialPost]:
        clean_channel = channel_name.strip().lstrip("@")
        posts: List[SocialPost] = []
        if not clean_channel:
            return posts

        url = f"https://t.me/s/{clean_channel}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp, status, msg = await resilient_crawler_engine.execute_request_with_resilience(
                platform=SocialPlatformType.TELEGRAM,
                client=client,
                url=url,
                method="GET",
                headers=headers,
            )

            if status == CollectorStatus.SUCCESS and resp is not None:
                try:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    message_divs = soup.find_all("div", class_=re.compile(r"tgme_widget_message_wrap"))
                    for div in message_divs[-limit:]:
                        post = self._parse_telegram_message(div, clean_channel)
                        if post:
                            posts.append(post)

                    if job_id:
                        resilient_crawler_engine.save_checkpoint(
                            job_id=job_id,
                            platform=SocialPlatformType.TELEGRAM,
                            query=clean_channel,
                            cursor=None,
                            items_count=len(posts),
                            status=CollectorStatus.SUCCESS if posts else CollectorStatus.SUCCESS_EMPTY
                        )
                except Exception as e:
                    app_logger.warning(f"Error parsing Telegram HTML for '{clean_channel}': {e}")
            else:
                app_logger.info(
                    f"Telegram collection for '{clean_channel}' completed with status: {status.value}. Info: {msg}"
                )
                if job_id:
                    resilient_crawler_engine.save_checkpoint(
                        job_id=job_id,
                        platform=SocialPlatformType.TELEGRAM,
                        query=clean_channel,
                        cursor=None,
                        items_count=0,
                        status=status
                    )

        return resilient_crawler_engine.deduplicate_posts(posts)

    async def search_posts(self, query: str, limit: int = 25, job_id: Optional[str] = None) -> List[SocialPost]:
        """
        If query specifies a channel (@channel or t.me/channel), inspect channel.
        Otherwise inspect target channel and filter by query terms.
        """
        match = re.search(r'(?:t\.me\/|@)([a-zA-Z0-9_]{4,})', query)
        target_channel = match.group(1) if match else "durov"

        posts = await self.get_channel_posts(target_channel, limit=limit, job_id=job_id)
        if query and not match:
            q_lower = query.lower()
            posts = [p for p in posts if q_lower in p.text.lower()]
        return posts

    def _parse_telegram_message(self, div: Any, channel: str) -> Optional[SocialPost]:
        try:
            msg_el = div.find("div", class_="tgme_widget_message")
            if not msg_el:
                return None

            data_post = msg_el.get("data-post", "")
            post_id = data_post.split("/")[-1] if "/" in data_post else data_post
            if not post_id:
                return None

            text_el = div.find("div", class_="tgme_widget_message_text")
            text = text_el.get_text(separator="\n").strip() if text_el else ""

            # Views
            views_el = div.find("span", class_="tgme_widget_message_views")
            views_count = None
            if views_el:
                views_raw = views_el.get_text(strip=True).upper()
                if "K" in views_raw:
                    views_count = int(float(views_raw.replace("K", "")) * 1000)
                elif "M" in views_raw:
                    views_count = int(float(views_raw.replace("M", "")) * 1000000)
                elif views_raw.isdigit():
                    views_count = int(views_raw)

            # Date
            time_el = div.find("time")
            created_at = (time_el.get("datetime") if time_el and time_el.get("datetime") else None) or datetime.now(timezone.utc).isoformat()

            # Forwards
            fwd_el = div.find("a", class_="tgme_widget_message_forwarded_from_name")
            is_forwarded = bool(fwd_el)
            fwd_name = fwd_el.get_text(strip=True) if fwd_el else None

            # Links
            links: List[str] = []
            if text_el:
                for a in text_el.find_all("a", href=True):
                    links.append(a["href"])

            # Media URLs
            media_urls: List[str] = []
            for img in div.find_all("i", class_="tgme_widget_message_photo_wrap"):
                style = img.get("style", "")
                m = re.search(r"url\('([^']+)'\)", style)
                if m:
                    media_urls.append(m.group(1))

            entities = re.findall(r'@([a-zA-Z0-9_]+)', text) + re.findall(r'#([a-zA-Z0-9_]+)', text)

            return SocialPost(
                id=f"tg_{channel}_{post_id}",
                platform=SocialPlatformType.TELEGRAM,
                author=f"@{channel}",
                author_id=f"channel_{channel}",
                text=text or "[Media dispatch without caption]",
                created_at=created_at,
                url=f"https://t.me/{channel}/{post_id}",
                langs=["en"],
                links=links,
                views_count=views_count,
                channel_name=channel,
                media_urls=media_urls,
                is_forwarded=is_forwarded,
                forwarded_from=fwd_name,
                entities=list(set(entities)),
                credibility_score=None
            )
        except Exception as e:
            app_logger.warning(f"Error parsing Telegram widget message: {e}")
            return None


telegram_collector = TelegramCollector()
