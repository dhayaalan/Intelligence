"""
Validation test suite for Platform Transformation:
1. Resilient Crawler Engine: 429 Retry-After parsing, jitter backoff, checkpointing, circuit breaking.
2. News Intelligence: Zero synthetic records honesty, provider status tracking.
3. Tool Executor: Authentic profile verification, CONFIG_REQUIRED state for credentialed platforms.
"""

import asyncio
import time
import httpx
import pytest
from unittest.mock import MagicMock

from app.modules.social_media_intelligence.crawler_engine import (
    resilient_crawler_engine,
    CollectorStatus,
    ProviderCircuitBreaker,
    CircuitState,
)
from app.modules.social_media_intelligence.models import (
    SocialPlatformType,
    SocialPost,
)
from app.modules.news_intelligence.search_engine import news_retrieval_engine
from app.modules.news_intelligence.models import NewsSearchRequest
from app.modules.tool_executor import tool_executor


def test_crawler_retry_after_parsing():
    """Verify Retry-After header parsing for seconds and invalid formats."""
    mock_resp_secs = MagicMock()
    mock_resp_secs.headers = {"Retry-After": "45"}
    parsed = resilient_crawler_engine.parse_retry_after(mock_resp_secs)
    assert parsed == 45.0

    mock_resp_none = MagicMock()
    mock_resp_none.headers = {}
    assert resilient_crawler_engine.parse_retry_after(mock_resp_none) is None


def test_crawler_jittered_backoff_bounds():
    """Verify backoff interval is strictly bounded within jitter parameters."""
    for attempt in range(4):
        delay = resilient_crawler_engine.calculate_jittered_backoff(attempt, base=1.0, max_backoff=20.0)
        assert 0.5 <= delay <= 20.0


def test_crawler_checkpoint_save_and_retrieve():
    """Verify crawler pagination continuation tokens persist and retrieve accurately."""
    job_id = "test_job_chk_01"
    platform = SocialPlatformType.BLUESKY
    resilient_crawler_engine.save_checkpoint(
        job_id=job_id,
        platform=platform,
        query="iaf telemetry",
        cursor="cur_page_tok_99",
        items_count=12,
        status=CollectorStatus.SUCCESS
    )

    cp = resilient_crawler_engine.get_checkpoint(job_id, platform)
    assert cp is not None
    assert cp.cursor == "cur_page_tok_99"
    assert cp.items_collected == 12
    assert cp.status == CollectorStatus.SUCCESS


def test_crawler_circuit_breaker_state_transitions():
    """Verify circuit breaker opens after failure threshold and protects downstream calls."""
    cb = ProviderCircuitBreaker(failure_threshold=3, reset_timeout_seconds=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_attempt() is True

    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.can_attempt() is True

    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_attempt() is False

    time.sleep(0.25)
    # After timeout, can attempt in HALF_OPEN
    assert cb.can_attempt() is True
    assert cb.state == CircuitState.HALF_OPEN

    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.consecutive_failures == 0


def test_crawler_deduplication():
    """Verify deduplication removes redundant posts with identical platform + ID."""
    p1 = SocialPost(
        id="post_abc",
        platform=SocialPlatformType.BLUESKY,
        author="@analyst",
        author_id="did:1",
        text="Sample post alpha",
        created_at="2026-10-14T00:00:00Z",
        url="https://bsky.app/p1"
    )
    p2 = SocialPost(
        id="post_abc",  # Duplicate ID
        platform=SocialPlatformType.BLUESKY,
        author="@analyst",
        author_id="did:1",
        text="Sample post alpha duplicate",
        created_at="2026-10-14T00:00:00Z",
        url="https://bsky.app/p1"
    )
    p3 = SocialPost(
        id="post_def",
        platform=SocialPlatformType.BLUESKY,
        author="@analyst",
        author_id="did:1",
        text="Sample post beta",
        created_at="2026-10-14T00:00:00Z",
        url="https://bsky.app/p2"
    )

    deduped = resilient_crawler_engine.deduplicate_posts([p1, p2, p3])
    assert len(deduped) == 2
    ids = [p.id for p in deduped]
    assert "post_abc" in ids
    assert "post_def" in ids


def test_news_search_zero_synthesis_honesty():
    """Verify that when providers return 0 results, engine returns 0 results with diagnostics (no fake articles)."""
    async def _test():
        # Query for a string with virtually no live matches
        req = NewsSearchRequest(query="zqx987_nonexistent_token_strictly_empty")
        res = await news_retrieval_engine.search(req)

        assert res.total_results == 0
        assert len(res.results) == 0
        assert res.investigator_advisory is not None
        assert "Zero synthetic records injected" in res.investigator_advisory
        assert "google_news_rss" in res.provider_statuses
    asyncio.run(_test())


def test_tool_executor_twitter_requires_config():
    """Verify Twitter intel returns CONFIG_REQUIRED when TWITTER_BEARER_TOKEN is not configured."""
    async def _test():
        res = await tool_executor.execute_tool(
            tool_id="tool_twitter_intel",
            target="analyst_test_target"
        )
        assert res.tool_id == "tool_twitter_intel"
        assert res.status == "CONFIG_REQUIRED"
        assert "TWITTER_BEARER_TOKEN" in (res.config_help or "")
    asyncio.run(_test())


def test_tool_executor_username_recon_empty_state():
    """Verify username recon does NOT claim false positive existence for random nonexistent targets."""
    async def _test():
        res = await tool_executor.execute_tool(
            tool_id="tool_username_prober",
            target="qzx987_impossible_fake_user_target_0102"
        )
        assert res.tool_id == "tool_username_prober"
        assert res.status == "SUCCESS_EMPTY"
        assert len(res.results) == 0
        assert "Zero verified public profiles" in res.summary
    asyncio.run(_test())
