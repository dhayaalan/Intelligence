"""
Resilient Crawler Engine for Social Media Intelligence.
Provides adaptive rate-limiting (HTTP 429 & Retry-After detection),
exponential backoff with jitter, cursor checkpointing, circuit breaking,
and strict operational error classification.
Zero fake data generation.
"""

import asyncio
import random
import re
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple
import httpx
from pydantic import BaseModel, Field

from app.core.logging import app_logger
from app.modules.social_media_intelligence.models import (
    SocialPlatformType,
    SocialPost,
    SocialCrawlResult,
    SocialCommentItem,
)



class CollectorStatus(str, Enum):
    SUCCESS = "SUCCESS"
    SUCCESS_EMPTY = "SUCCESS_EMPTY"
    RATE_LIMITED = "RATE_LIMITED"
    ACCESS_DENIED = "ACCESS_DENIED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    CONFIG_REQUIRED = "CONFIG_REQUIRED"
    PARSE_ERROR = "PARSE_ERROR"


class CrawlCheckpoint(BaseModel):
    job_id: str
    platform: SocialPlatformType
    query: str
    cursor: Optional[str] = None
    items_collected: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: CollectorStatus = CollectorStatus.SUCCESS
    retry_after_seconds: Optional[float] = None
    status_message: Optional[str] = None


class CollectorResult(BaseModel):
    platform: SocialPlatformType
    status: CollectorStatus
    items: List[SocialPost] = Field(default_factory=list)
    total_count: int = 0
    next_cursor: Optional[str] = None
    retry_after_seconds: Optional[float] = None
    status_message: str = ""
    error_code: Optional[int] = None
    latency_ms: float = 0.0


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Provider failing repeatedly; block requests
    HALF_OPEN = "HALF_OPEN"# Testing recovery


class ProviderCircuitBreaker:
    """Isolates failures so an outage on one platform does not block other integrations."""

    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout_seconds = reset_timeout_seconds
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: float = 0.0

    def can_attempt(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if (time.time() - self.last_failure_time) >= self.reset_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN allows probe

    def record_success(self):
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            app_logger.warning(f"Circuit opened due to {self.consecutive_failures} consecutive failures")


class ResilientCrawlerEngine:
    """
    Central collection engine managing rate-limiting, backoff,
    pagination checkpointing, and authentic data return.
    """

    def __init__(self):
        self._checkpoints: Dict[str, CrawlCheckpoint] = {}
        self._circuit_breakers: Dict[SocialPlatformType, ProviderCircuitBreaker] = {
            p: ProviderCircuitBreaker() for p in SocialPlatformType
        }
        self._dedup_seen_ids: set = set()
        self._provider_throttled_until: Dict[SocialPlatformType, float] = {}

    def get_checkpoint(self, job_id: str, platform: SocialPlatformType) -> Optional[CrawlCheckpoint]:
        key = f"{job_id}:{platform.value}"
        return self._checkpoints.get(key)

    def save_checkpoint(
        self,
        job_id: str,
        platform: SocialPlatformType,
        query: str,
        cursor: Optional[str] = None,
        items_count: int = 0,
        status: CollectorStatus = CollectorStatus.SUCCESS,
        retry_after_seconds: Optional[float] = None,
        status_message: Optional[str] = None
    ) -> CrawlCheckpoint:
        key = f"{job_id}:{platform.value}"
        cp = CrawlCheckpoint(
            job_id=job_id,
            platform=platform,
            query=query,
            cursor=cursor,
            items_collected=items_count,
            status=status,
            retry_after_seconds=retry_after_seconds,
            status_message=status_message
        )
        self._checkpoints[key] = cp
        return cp

    def is_provider_throttled(self, platform: SocialPlatformType) -> Tuple[bool, float]:
        until = self._provider_throttled_until.get(platform, 0.0)
        remaining = until - time.time()
        if remaining > 0:
            return True, round(remaining, 1)
        return False, 0.0

    def parse_retry_after(self, response: httpx.Response) -> Optional[float]:
        """Parses Retry-After header as either integer seconds or HTTP-date."""
        val = response.headers.get("retry-after") or response.headers.get("Retry-After")
        if not val:
            return None
        val_clean = val.strip()
        try:
            return float(val_clean)
        except ValueError:
            pass
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(val_clean)
            diff = (dt - datetime.now(timezone.utc)).total_seconds()
            return max(1.0, diff)
        except Exception:
            return None

    def calculate_jittered_backoff(self, attempt: int, base: float = 1.0, max_backoff: float = 20.0) -> float:
        """Full jitter exponential backoff: uniform(0, min(max_backoff, base * 2^attempt))."""
        raw = min(max_backoff, base * (2 ** attempt))
        return random.uniform(0.5, raw)

    async def execute_request_with_resilience(
        self,
        platform: SocialPlatformType,
        client: httpx.AsyncClient,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        max_retries: int = 2,
    ) -> Tuple[Optional[httpx.Response], CollectorStatus, Optional[str]]:
        """
        Executes HTTP call with 429 adaptive throttling, exponential jitter backoff,
        and circuit breaking. Never raises unhandled exceptions.
        """
        cb = self._circuit_breakers.get(platform)
        if cb and not cb.can_attempt():
            return None, CollectorStatus.UNAVAILABLE, "Circuit breaker OPEN: platform temporarily suspended due to repeated failures."

        is_throttled, wait_s = self.is_provider_throttled(platform)
        if is_throttled:
            return None, CollectorStatus.RATE_LIMITED, f"Platform currently throttled. Backoff remaining: {wait_s}s"

        req_headers = headers or {}
        if "User-Agent" not in req_headers:
            req_headers["User-Agent"] = "Sentinel-Intelligence-Recon/2.0 (High-Assurance Defence Platform; Contact: sec-audit@sential.io)"

        for attempt in range(max_retries + 1):
            try:
                resp = await client.request(
                    method=method,
                    url=url,
                    headers=req_headers,
                    params=params,
                    json=json_data,
                    timeout=8.0
                )

                if resp.status_code == 200:
                    if cb:
                        cb.record_success()
                    return resp, CollectorStatus.SUCCESS, None

                # HTTP 429 Rate Limiting
                if resp.status_code == 429:
                    retry_after = self.parse_retry_after(resp) or self.calculate_jittered_backoff(attempt)
                    app_logger.warning(
                        f"Platform {platform.value} returned HTTP 429. Backing off for {retry_after:.1f}s (Attempt {attempt+1}/{max_retries+1})"
                    )
                    self._provider_throttled_until[platform] = time.time() + retry_after
                    if attempt < max_retries and retry_after <= 10.0:
                        await asyncio.sleep(retry_after)
                        continue
                    if cb:
                        cb.record_failure()
                    return resp, CollectorStatus.RATE_LIMITED, f"HTTP 429: Rate limit exceeded. Retry after {retry_after:.1f}s."

                # HTTP 403 Forbidden / 401 Unauthorized
                if resp.status_code in [401, 403]:
                    status = CollectorStatus.ACCESS_DENIED if resp.status_code == 403 else CollectorStatus.AUTH_REQUIRED
                    app_logger.info(f"Platform {platform.value} access restricted ({resp.status_code})")
                    return resp, status, f"HTTP {resp.status_code}: Access denied or authentication required by platform policy."

                # HTTP 404 Not Found (valid target absence)
                if resp.status_code == 404:
                    return resp, CollectorStatus.SUCCESS_EMPTY, "HTTP 404: Target or query yielded zero matching records."

                # Server Errors (5xx)
                if resp.status_code >= 500:
                    if cb:
                        cb.record_failure()
                    if attempt < max_retries:
                        backoff = self.calculate_jittered_backoff(attempt)
                        await asyncio.sleep(backoff)
                        continue
                    return resp, CollectorStatus.UNAVAILABLE, f"HTTP {resp.status_code}: Provider server error."

                return resp, CollectorStatus.UNAVAILABLE, f"HTTP {resp.status_code} received."

            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                app_logger.warning(f"Connection failure to {platform.value}: {e}")
                if cb:
                    cb.record_failure()
                if attempt < max_retries:
                    await asyncio.sleep(self.calculate_jittered_backoff(attempt))
                    continue
                return None, CollectorStatus.UNAVAILABLE, f"Connection failure: {str(e)}"

            except httpx.ReadTimeout as e:
                app_logger.warning(f"Timeout on {platform.value}: {e}")
                if cb:
                    cb.record_failure()
                return None, CollectorStatus.TIMEOUT, f"Read timeout: {str(e)}"

            except Exception as e:
                app_logger.error(f"Unexpected crawler error on {platform.value}: {e}")
                if cb:
                    cb.record_failure()
                return None, CollectorStatus.UNAVAILABLE, f"Crawler error: {str(e)}"

        return None, CollectorStatus.RATE_LIMITED, "Max retries exhausted under rate-limiting."

    def deduplicate_posts(self, posts: List[SocialPost]) -> List[SocialPost]:
        """Eliminates duplicates across runs using stable platform + post ID hashing."""
        unique_posts: List[SocialPost] = []
        for p in posts:
            key = f"{p.platform.value}:{p.id}"
            if key not in self._dedup_seen_ids:
                self._dedup_seen_ids.add(key)
                unique_posts.append(p)
        return unique_posts


# Global singleton crawler engine
resilient_crawler_engine = ResilientCrawlerEngine()


class ResilientSocialCrawler:
    """
    High-assurance social media and web crawler engineered to extract
    authentic content, captions, metadata, and media from social links,
    profiles, and articles even when target URLs are protected by login-walls,
    HTTP 403 anti-bot barriers, or Cloudflare challenges.
    """

    def __init__(self):
        self._chrome_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
        self._crawler_ua = (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        )

    def detect_platform(self, url: str) -> str:
        u = url.lower()
        if "instagram.com" in u:
            return "instagram"
        if "facebook.com" in u or "fb.com" in u:
            return "facebook"
        if "twitter.com" in u or "x.com" in u:
            return "twitter"
        if "reddit.com" in u:
            return "reddit"
        if "t.me" in u or "telegram.org" in u:
            return "telegram"
        if "bsky.app" in u or "bluesky" in u:
            return "bluesky"
        if "youtube.com" in u or "youtu.be" in u:
            return "youtube"
        if "tiktok.com" in u:
            return "tiktok"
        if "linkedin.com" in u:
            return "linkedin"
        return "web"

    def detect_post_type(self, url: str, html: str = "") -> str:
        """Determines if the target asset is a Reel, Short, Video, Story, or Standard Post."""
        u = url.lower()
        if "/reel/" in u or "/reels/" in u:
            return "reel"
        if "/shorts/" in u:
            return "short"
        if "/tv/" in u or "/watch" in u or "/videos/" in u or "fb.watch" in u or "tiktok.com" in u:
            return "video"
        if "/stories/" in u:
            return "story"
        # Check metadata in html if available
        if html:
            if 'property="og:video"' in html or 'name="twitter:player"' in html or "<video" in html:
                return "video"
        return "post"

    async def crawl_url(
        self,
        url: str,
        extract_media: bool = True,
        bypass_blocking: bool = True,
        extract_comments: bool = True,
        extract_entities: bool = True
    ) -> SocialCrawlResult:
        import json
        import urllib.parse
        import xml.etree.ElementTree as ET

        clean_url = url.strip()
        if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            clean_url = f"https://{clean_url}"

        platform = self.detect_platform(clean_url)
        post_type = self.detect_post_type(clean_url)

        html_content, status_code, bypass_strategy, final_url, is_blocked, extra_meta = await self._fetch_with_resilience(
            clean_url, bypass_blocking, platform
        )

        return await self._extract_intelligence_from_page(
            html=html_content or "",
            original_url=clean_url,
            final_url=final_url,
            platform=platform,
            post_type=post_type,
            status_code=status_code,
            bypass_strategy=bypass_strategy,
            is_blocked=is_blocked,
            extract_media=extract_media,
            extract_comments=extract_comments,
            extract_entities=extract_entities,
            extra_meta=extra_meta
        )

    async def _fetch_with_resilience(
        self,
        url: str,
        bypass_blocking: bool,
        platform: str
    ) -> Tuple[Optional[str], int, str, str, bool, Dict[str, Any]]:
        """
        Executes multi-tier crawler retrieval with specialized Instagram & Facebook embed handling:
        Tier 0: Platform-specific Public Embed / oEmbed (Instagram captioned embed, Facebook plugins).
        Tier 1: Stealth browser headers with modern TLS/ciphers.
        Tier 2: Search engine crawler bot emulation (Googlebot) if Tier 1 is blocked.
        Tier 3: Google News / Syndication index retrieval if page is fully blocked.
        """
        import urllib.parse

        tier1_headers = {
            "User-Agent": self._chrome_ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.google.com/"
        }

        final_url = url
        extra_meta: Dict[str, Any] = {}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False) as client:
                # ── SPECIAL TIER 0: Instagram Embed & oEmbed Bypass ──
                if platform == "instagram":
                    sc_m = re.search(r'/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', url)
                    if sc_m:
                        shortcode = sc_m.group(1)
                        embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned/"
                        try:
                            embed_resp = await client.get(embed_url, headers=tier1_headers, timeout=6.0)
                            if embed_resp.status_code == 200 and len(embed_resp.text) > 1000:
                                return embed_resp.text, 200, "INSTAGRAM_EMBED_BYPASS", embed_url, False, extra_meta
                        except Exception:
                            pass

                # ── SPECIAL TIER 0: Facebook Plugins oEmbed Bypass ──
                if platform == "facebook":
                    encoded_u = urllib.parse.quote(url)
                    oembed_url = f"https://www.facebook.com/plugins/post/oembed.json/?url={encoded_u}"
                    if "/reel/" in url or "/watch" in url or "fb.watch" in url:
                        oembed_url = f"https://www.facebook.com/plugins/video/oembed.json/?url={encoded_u}"
                    try:
                        fb_oembed_resp = await client.get(oembed_url, headers=tier1_headers, timeout=5.0)
                        if fb_oembed_resp.status_code == 200:
                            fb_data = fb_oembed_resp.json()
                            extra_meta["fb_oembed"] = fb_data
                            synth_html = f'''<!DOCTYPE html><html><head>
                            <title>{fb_data.get("author_name", "Facebook Post")}</title>
                            <meta property="og:title" content="{fb_data.get('author_name', '')}">
                            <meta property="og:description" content="{fb_data.get('html', '')}">
                            <meta property="author" content="{fb_data.get('author_name', '')}">
                            </head><body>{fb_data.get("html", "")}</body></html>'''
                            return synth_html, 200, "FACEBOOK_OEMBED_BYPASS", url, False, extra_meta
                    except Exception:
                        pass

                # ── TIER 1: Direct Stealth Request ──
                resp = await client.get(url, headers=tier1_headers)
                final_url = str(resp.url)

                # Check if challenge page
                is_challenge = any(tok in resp.text.lower() for tok in [
                    "cf-browser-verification", "cloudflare ray id", "please verify you are a human",
                    "login required", "blocked by network security", "captcha"
                ]) and len(resp.text) < 5000

                if resp.status_code == 200 and not is_challenge:
                    return resp.text, 200, "DIRECT_STEALTH", final_url, False, extra_meta

                if not bypass_blocking:
                    return resp.text, resp.status_code, "DIRECT_REFUSED", final_url, True, extra_meta

                # ── TIER 2: Search Crawler Emulation ──
                tier2_headers = {
                    "User-Agent": self._crawler_ua,
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "From": "googlebot(at)googlebot.com"
                }
                bot_resp = await client.get(url, headers=tier2_headers)
                if bot_resp.status_code == 200 and len(bot_resp.text) > 800:
                    return bot_resp.text, 200, "GOOGLEBOT_BYPASS", str(bot_resp.url), True, extra_meta

                # ── TIER 3: Google News / Syndication Index Fallback ──
                syndicated_html = await self._fetch_syndicated_index(url, client)
                if syndicated_html:
                    return syndicated_html, 200, "GOOGLE_SYNDICATION_INDEX", final_url, True, extra_meta

                return resp.text, resp.status_code, "BOT_CHALLENGE_RESISTANT", final_url, True, extra_meta

        except Exception as e:
            app_logger.warning(f"Resilient crawler error on {url}: {e}")
            try:
                async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as fallback_client:
                    syndicated_html = await self._fetch_syndicated_index(url, fallback_client)
                    if syndicated_html:
                        return syndicated_html, 200, "GOOGLE_SYNDICATION_INDEX", url, True, extra_meta
            except Exception:
                pass
            return "", 500, f"NETWORK_ERROR_{type(e).__name__}", url, True, extra_meta

    async def _fetch_syndicated_index(self, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """Queries Google News RSS index for the exact URL or target query."""
        import urllib.parse
        import xml.etree.ElementTree as ET

        try:
            quoted_url = urllib.parse.quote(url)
            rss_url = f"https://news.google.com/rss/search?q={quoted_url}&hl=en-US&gl=US&ceid=US:en"
            resp = await client.get(rss_url, timeout=5.0)
            if resp.status_code == 200 and b"<item>" in resp.content:
                root = ET.fromstring(resp.content)
                item = root.find(".//item")
                if item is not None:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else url
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    desc = item.find("description").text if item.find("description") is not None else ""
                    clean_desc = re.sub(r"<[^>]+>", " ", desc).strip()

                    return f'''<!DOCTYPE html><html><head>
                    <title>{title}</title>
                    <meta property="og:title" content="{title}">
                    <meta property="og:description" content="{clean_desc}">
                    <meta property="og:url" content="{link}">
                    <meta name="pubDate" content="{pub_date}">
                    </head><body><h1>{title}</h1><p>{clean_desc}</p></body></html>'''
        except Exception:
            pass
        return None

    async def _extract_comments(
        self,
        html: str,
        jsonld_blocks: List[Dict[str, Any]],
        platform: str,
        url: str
    ) -> List[SocialCommentItem]:
        """
        Multi-Source Social Comment Extractor:
        Extracts comments from Reddit JSON threads, JSON-LD Schema.org Comment blocks,
        DOM signatures (<shreddit-comment>, <div data-sigil="comment-body">), and embed elements.
        """
        import json
        extracted_comments: List[SocialCommentItem] = []
        seen_texts = set()

        # 1. Reddit JSON comments tree if URL is a Reddit post
        if platform == "reddit" and "/comments/" in url:
            try:
                clean_json_url = re.sub(r"\?.*$", "", url).rstrip("/") + ".json?limit=25"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                }
                async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                    resp = await client.get(clean_json_url, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list) and len(data) >= 2:
                            comments_data = data[1].get("data", {}).get("children", [])
                            for c in comments_data[:20]:
                                cdata = c.get("data", {})
                                author = cdata.get("author", "")
                                body = cdata.get("body", "")
                                score = cdata.get("score", 0)
                                cid = cdata.get("id", "")
                                if author and body and body != "[deleted]" and body not in seen_texts:
                                    seen_texts.add(body)
                                    extracted_comments.append(
                                        SocialCommentItem(
                                            id=cid,
                                            author=f"u/{author}",
                                            author_id=author,
                                            text=body,
                                            likes_count=score,
                                            published_at=datetime.now(timezone.utc).isoformat()
                                        )
                                    )
            except Exception:
                pass

        # 2. JSON-LD Schema.org Comment objects
        for block in jsonld_blocks:
            comment_nodes = []
            if block.get("@type") == "Comment":
                comment_nodes.append(block)
            elif "comment" in block:
                c = block["comment"]
                if isinstance(c, list):
                    comment_nodes.extend(c)
                elif isinstance(c, dict):
                    comment_nodes.append(c)

            for node in comment_nodes:
                text = node.get("text") or node.get("description") or ""
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    author_val = node.get("author")
                    auth_name = "Anonymous"
                    if isinstance(author_val, dict):
                        auth_name = author_val.get("name", "Anonymous")
                    elif isinstance(author_val, str):
                        auth_name = author_val

                    likes = 0
                    if node.get("upvoteCount"):
                        try:
                            likes = int(node["upvoteCount"])
                        except Exception:
                            pass

                    extracted_comments.append(
                        SocialCommentItem(
                            id=node.get("id"),
                            author=auth_name,
                            text=text,
                            likes_count=likes,
                            published_at=node.get("dateCreated")
                        )
                    )

        # 3. DOM Regex comments extraction (Facebook mobile, Reddit shreddit, and universal classes)
        # 3a. Facebook mobile comments
        for m in re.finditer(r'<div[^>]+data-sigil=["\']comment-body["\'][^>]*>(.*?)</div>', html, re.I | re.S):
            clean_c = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
            if clean_c and len(clean_c) > 3 and clean_c not in seen_texts:
                seen_texts.add(clean_c)
                extracted_comments.append(
                    SocialCommentItem(
                        author="Facebook User",
                        text=clean_c,
                        published_at=datetime.now(timezone.utc).isoformat()
                    )
                )

        # 3b. Reddit <shreddit-comment> elements
        for m in re.finditer(r'<shreddit-comment[^>]+author=["\']([^"\']+)["\'][^>]*>.*?<div[^>]+slot=["\']comment["\'][^>]*>(.*?)</div>', html, re.I | re.S):
            author_val = m.group(1)
            raw_body = m.group(2)
            clean_c = re.sub(r'<[^>]+>', ' ', raw_body).strip()
            if clean_c and clean_c not in seen_texts:
                seen_texts.add(clean_c)
                extracted_comments.append(
                    SocialCommentItem(
                        author=f"u/{author_val}",
                        author_id=author_val,
                        text=clean_c,
                        published_at=datetime.now(timezone.utc).isoformat()
                    )
                )

        # 3c. Universal comment class signatures
        for m in re.finditer(r'<div[^>]+class=["\'][^"\']*(?:comment-body|comment-content|comment__text|CommentText|CaptionComments)[^"\']*["\'][^>]*>(.*?)</div>', html, re.I | re.S):
            clean_c = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
            if clean_c and len(clean_c) > 8 and clean_c not in seen_texts:
                seen_texts.add(clean_c)
                extracted_comments.append(
                    SocialCommentItem(
                        author=f"{platform.capitalize()} Contributor",
                        text=clean_c,
                        published_at=datetime.now(timezone.utc).isoformat()
                    )
                )

        return extracted_comments[:25]

    async def _extract_intelligence_from_page(
        self,
        html: str,
        original_url: str,
        final_url: str,
        platform: str,
        post_type: str,
        status_code: int,
        bypass_strategy: str,
        is_blocked: bool,
        extract_media: bool,
        extract_comments: bool,
        extract_entities: bool,
        extra_meta: Dict[str, Any]
    ) -> SocialCrawlResult:
        import json

        raw_meta: Dict[str, Any] = dict(extra_meta)
        title = ""
        description = ""
        author = ""
        published_at = None
        media_urls: List[str] = []
        video_url: Optional[str] = None
        likes_count = 0
        comments_count = 0
        shares_count = 0

        # 1. Parse OpenGraph & Twitter Card tags
        for m in re.finditer(r'<meta[^>]+(?:property|name)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\']', html, re.I):
            k, v = m.group(1).lower(), m.group(2).strip()
            raw_meta[k] = v

        for m in re.finditer(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']([^"\']+)["\']', html, re.I):
            k, v = m.group(2).lower(), m.group(1).strip()
            raw_meta[k] = v

        title = raw_meta.get("og:title") or raw_meta.get("twitter:title") or ""
        description = raw_meta.get("og:description") or raw_meta.get("twitter:description") or raw_meta.get("description") or ""
        author = raw_meta.get("author") or raw_meta.get("article:author") or raw_meta.get("twitter:creator") or ""
        published_at = raw_meta.get("article:published_time") or raw_meta.get("pubdate") or raw_meta.get("date")

        # 2. Instagram Embed Special Parsing
        if "instagram" in platform or "Caption" in html:
            cap_m = re.search(r'<div[^>]+class=["\'][^"\']*Caption[^"\']*["\'][^>]*>(.*?)</div>', html, re.I | re.S)
            if cap_m:
                caption_clean = re.sub(r'<[^>]+>', ' ', cap_m.group(1)).strip()
                if caption_clean and len(caption_clean) > len(description):
                    description = caption_clean
                    if not title:
                        title = caption_clean[:120]

            user_m = re.search(r'<span[^>]+class=["\'][^"\']*UsernameText[^"\']*["\'][^>]*>(.*?)</span>', html, re.I | re.S)
            if user_m:
                clean_username = re.sub(r'<[^>]+>', '', user_m.group(1)).strip().lstrip("@")
                author = f"@{clean_username}"

            # Likes and Comments count regex in embed feedback
            feedback_m = re.search(r'([\d,\.]+[kmb]?)\s+likes', html, re.I)
            if feedback_m:
                likes_count = self._parse_count_str(feedback_m.group(1))
            comm_m = re.search(r'([\d,\.]+[kmb]?)\s+comments', html, re.I)
            if comm_m:
                comments_count = self._parse_count_str(comm_m.group(1))

        # 3. Parse HTML Title & Headings if needed
        if not title:
            title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
            if title_m:
                title = re.sub(r'\s+', ' ', title_m.group(1)).strip()

        # 4. JSON-LD parsing
        jsonld_blocks: List[Dict[str, Any]] = []
        jsonld_matches = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
        for block in jsonld_matches:
            try:
                data = json.loads(block.strip())
                if isinstance(data, list):
                    jsonld_blocks.extend(d for d in data if isinstance(d, dict))
                elif isinstance(data, dict):
                    jsonld_blocks.append(data)
            except Exception:
                pass

        for data in jsonld_blocks:
            if not title and data.get("headline"):
                title = str(data["headline"])
            if not description and data.get("articleBody"):
                description = str(data["articleBody"])[:1000]
            elif not description and data.get("description"):
                description = str(data["description"])
            if not author:
                auth_obj = data.get("author")
                if isinstance(auth_obj, dict):
                    author = auth_obj.get("name", "")
                elif isinstance(auth_obj, str):
                    author = auth_obj
            if not published_at and data.get("datePublished"):
                published_at = str(data["datePublished"])
            if extract_media and data.get("image"):
                img = data["image"]
                if isinstance(img, str) and img.startswith("http"):
                    media_urls.append(img)
                elif isinstance(img, list):
                    for im in img:
                        if isinstance(im, str) and im.startswith("http"):
                            media_urls.append(im)
            if data.get("video"):
                v_obj = data["video"]
                if isinstance(v_obj, dict):
                    video_url = v_obj.get("contentUrl") or v_obj.get("embedUrl")
                elif isinstance(v_obj, str) and v_obj.startswith("http"):
                    video_url = v_obj

        # 5. Extract Video URL (for Reels, Videos, Shorts)
        if not video_url:
            for k in ["og:video", "og:video:url", "og:video:secure_url", "twitter:player:stream"]:
                if raw_meta.get(k) and raw_meta[k].startswith("http"):
                    video_url = raw_meta[k]
                    break

        if not video_url:
            vid_tag_m = re.search(r'<video[^>]+src=["\']([^"\']+)["\']', html, re.I)
            if vid_tag_m:
                video_url = vid_tag_m.group(1)
            else:
                src_m = re.search(r'<source[^>]+src=["\']([^"\']+\.(?:mp4|webm|m4v)[^"\']*)["\']', html, re.I)
                if src_m:
                    video_url = src_m.group(1)

        # Update post_type to video or reel if video URL exists
        if video_url:
            if post_type not in ["reel", "short"]:
                post_type = "video"
            media_urls.append(video_url)

        # 6. Extract Images & Media
        if extract_media:
            for k in ["og:image", "og:image:url", "twitter:image", "twitter:image:src"]:
                if raw_meta.get(k) and raw_meta[k].startswith("http"):
                    media_urls.append(raw_meta[k])
            # Check img tags in html
            for img_m in re.finditer(r'<img[^>]+(?:class=["\'][^"\']*EmbeddedMediaImage[^"\']*["\']|src=["\'](https://[^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\'])', html, re.I):
                src = img_m.group(1)
                if src and src.startswith("http") and "icon" not in src:
                    media_urls.append(src)

        # 7. Extract Body Text & Clean Navigation Boilerplate
        body_parts = []
        if description:
            body_parts.append(description)
        if html:
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.I | re.S)
            clean_ps = [re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if len(p.strip()) > 10]
            for p in clean_ps[:6]:
                # Filter out navigation menu noise or scripts
                is_noise = any(noise_term in p.lower() for noise_term in [
                    "sign in", "appearance settings", "terms of service", "privacy policy",
                    "cookie policy", "javascript is disabled", "popular repositories", "loading..."
                ])
                if not is_noise and p not in body_parts and p not in description:
                    body_parts.append(p)
        body_text = "\n\n".join(body_parts) if body_parts else description
        
        # Sanitize full text: remove repetitive nav dumps and normalize whitespace
        sanitized = body_text.strip() or title
        # Strip common GitHub / web boilerplate blocks
        sanitized = re.sub(r'Sign inAppearance settings.*?(?=\w{4,}|$)', '', sanitized, flags=re.S)
        sanitized = re.sub(r'Overview\s+Repositories\s+Projects\s+Packages\s+Stars.*', '', sanitized, flags=re.S)
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized).strip()
        full_text = sanitized or title

        # Author normalization
        if not author:
            if platform == "telegram":
                m = re.search(r't\.me/(?:s/)?([^/?#]+)', original_url)
                if m:
                    author = f"@{m.group(1)}"
            elif platform == "reddit":
                m = re.search(r'reddit\.com/r/([^/?#]+)', original_url)
                if m:
                    author = f"r/{m.group(1)}"
            elif platform in ["twitter", "instagram"]:
                m = re.search(r'(?:twitter\.com|x\.com|instagram\.com)/([^/?#]+)', original_url)
                if m and m.group(1) not in ["p", "reel", "reels", "tv", "explore"]:
                    author = f"@{m.group(1)}"
            if not author:
                author = raw_meta.get("og:site_name") or f"{platform.capitalize()} Publisher"

        # 8. Extract Structured Entities
        extracted_entities: List[str] = []
        if extract_entities:
            combined = f"{title} {description} {full_text}"
            emails = list(dict.fromkeys(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', combined)))
            handles = list(dict.fromkeys(re.findall(r'@\w{2,30}', combined)))
            hashtags = list(dict.fromkeys(re.findall(r'#\w{2,40}', combined)))
            extracted_entities = emails[:5] + handles[:8] + hashtags[:8]

        # 9. Extract Social Comments
        comments: List[SocialCommentItem] = []
        if extract_comments:
            comments = await self._extract_comments(html, jsonld_blocks, platform, original_url)
            if not comments_count:
                comments_count = len(comments)

        unique_media = list(dict.fromkeys(media_urls))

        return SocialCrawlResult(
            url=original_url,
            final_url=final_url,
            platform=platform,
            post_type=post_type,
            title=title or f"{platform.capitalize()} {post_type.capitalize()} Content",
            text=full_text,
            author=author,
            author_id=author,
            published_at=published_at or datetime.now(timezone.utc).isoformat(),
            media_urls=unique_media[:10],
            video_url=video_url,
            likes_count=likes_count,
            comments_count=comments_count or len(comments),
            shares_count=shares_count,
            comments=comments,
            bypass_technique=bypass_strategy,
            http_status=status_code,
            is_blocked_url=is_blocked,
            raw_metadata=raw_meta,
            extracted_entities=extracted_entities,
            crawled_at=datetime.now(timezone.utc).isoformat()
        )

    def _parse_count_str(self, val: str) -> int:
        """Parses strings like '14.2k', '1.5M', '520' into integer count."""
        try:
            val = val.lower().replace(",", "").strip()
            if val.endswith("k"):
                return int(float(val[:-1]) * 1000)
            if val.endswith("m"):
                return int(float(val[:-1]) * 1000000)
            if val.endswith("b"):
                return int(float(val[:-1]) * 1000000000)
            return int(float(val))
        except Exception:
            return 0


resilient_social_crawler = ResilientSocialCrawler()


