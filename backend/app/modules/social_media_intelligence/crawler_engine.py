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
