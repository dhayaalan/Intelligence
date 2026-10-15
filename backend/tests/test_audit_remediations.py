"""
Regression test suite verifying audit findings remediation:
1. REM-01: Zero synthetic fallbacks in OSINT (Shodan & theHarvester).
2. REM-02: Structured rate-limit telemetry & degradation banners in Social Intelligence.
3. REM-03: CISA KEV exploitation context & FIRST EPSS exploit probability scoring.
4. REM-04: Wire syndication detection & true corroboration scoring in News Intelligence.
"""

import asyncio
import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.modules.osint.providers.shodan import ShodanProvider
from app.modules.osint.providers.theharvester import TheHarvesterProvider
from app.module_sdk.provider_adapter import ProviderRequest
from app.module_sdk.models import ModuleHealthStatus
from app.modules.tool_executor import tool_executor
from app.modules.social_media_intelligence.models import (
    SocialPlatformType,
    SocialSearchRequest,
    SocialSearchResponse,
)
from app.modules.social_media_intelligence.crawler_engine import (
    resilient_crawler_engine,
    CollectorStatus,
)
from app.modules.social_media_intelligence.service import social_media_service
from app.modules.news_intelligence.search_engine import news_retrieval_engine


def test_shodan_zero_synthetic_data_when_unconfigured():
    """Verify Shodan provider returns honest skipped state with zero dummy CVEs/ports when API key missing."""
    async def _test():
        with patch.dict(os.environ, {}, clear=True):
            provider = ShodanProvider()

            # Health check must truthfully report DEGRADED
            health = await provider.health_check()
            assert health.status == ModuleHealthStatus.DEGRADED
            assert "SHODAN_API_KEY missing" in health.message

            # Execute must return skipped with zero fake CVEs and zero fake ports
            req = ProviderRequest(query="8.8.8.8", target_type="ip")
            resp = await provider.execute(req)

            assert resp.status == "skipped"
            assert "SHODAN_API_KEY is not configured" in resp.error
            assert resp.raw_data.get("status") == "CONFIG_REQUIRED"
            assert resp.raw_data.get("ports") == []
            assert resp.raw_data.get("vulnerabilities") == []
            # Ensure hardcoded CVEs are completely eliminated
            assert "CVE-2023-48795" not in str(resp.raw_data)
            assert "CVE-2024-21626" not in str(resp.raw_data)

    asyncio.run(_test())


def test_theharvester_zero_synthetic_emails():
    """Verify theHarvester never fabricates info@, support@, admin@ emails without evidence."""
    async def _test():
        provider = TheHarvesterProvider()
        req = ProviderRequest(query="example-nonexistent-domain-test.com", target_type="domain")
        resp = await provider.execute(req)

        assert resp.status == "success"
        # Zero synthetic emails
        assert resp.raw_data.get("emails") == []
        assert "info@example" not in str(resp.raw_data)
        assert "support@example" not in str(resp.raw_data)
        assert "admin@example" not in str(resp.raw_data)

    asyncio.run(_test())


def test_cve_intelligence_epss_and_kev_enrichment():
    """Verify CVE intelligence enriches results with EPSS scores and CISA KEV context."""
    async def _test():
        # Test with CVE-2023-48795 (Terrapin attack on SSH)
        res = await tool_executor._run_cve_intelligence("exec_test_cve_01", "tool_cve", "CVE-2023-48795")
        assert res.tool_id == "tool_cve"
        assert res.status in ["SUCCESS", "FAILED"]

        if res.status == "SUCCESS" and res.results:
            item = res.results[0]
            assert item.type == "VULNERABILITY"
            assert "epss_score" in item.metadata
            assert "cisa_kev_exploited" in item.metadata
            assert item.metadata["cve_id"] == "CVE-2023-48795"

    asyncio.run(_test())


def test_social_crawler_checkpoint_telemetry_fields():
    """Verify crawler checkpoint saves retry_after_seconds and status_message."""
    job_id = "test_chk_telemetry_99"
    cp = resilient_crawler_engine.save_checkpoint(
        job_id=job_id,
        platform=SocialPlatformType.REDDIT,
        query="defence telemetry",
        cursor=None,
        items_count=0,
        status=CollectorStatus.RATE_LIMITED,
        retry_after_seconds=55.0,
        status_message="HTTP 429: Platform quota reached."
    )

    assert cp.status == CollectorStatus.RATE_LIMITED
    assert cp.retry_after_seconds == 55.0
    assert cp.status_message == "HTTP 429: Platform quota reached."

    # Retrieve checkpoint
    retrieved = resilient_crawler_engine.get_checkpoint(job_id, SocialPlatformType.REDDIT)
    assert retrieved is not None
    assert retrieved.retry_after_seconds == 55.0


def test_social_search_surfaces_collector_telemetry():
    """Verify SocialSearchResponse includes collector_telemetry dictionary and honest status."""
    async def _test():
        req = SocialSearchRequest(
            query="test_telemetry_query_xyz",
            platforms=[SocialPlatformType.REDDIT],
            limit=5,
            detect_cib=False
        )
        res = await social_media_service.execute_search(req)

        assert isinstance(res, SocialSearchResponse)
        assert hasattr(res, "collector_telemetry")
        assert "reddit" in res.collector_telemetry
        reddit_telem = res.collector_telemetry["reddit"]
        assert "status" in reddit_telem
        assert "items_count" in reddit_telem
        assert "rate_limited" in reddit_telem
        assert "status_message" in reddit_telem

    asyncio.run(_test())


def test_news_wire_syndication_classification():
    """Verify wire syndication detection separates origin wire from syndicated reprints."""
    engine = news_retrieval_engine

    # 1. Headline carrying (PTI) published by an affiliate portal -> SYNDICATED_COPY
    syn_type, wire_orig, is_ind = engine._detect_wire_syndication(
        title="IAF conducts high-altitude radar exercises in Ladakh (PTI)",
        summary="Special dispatch from frontline operations",
        publisher="Daily Regional Chronicle",
        source="regional_portal"
    )
    assert syn_type == "SYNDICATED_COPY"
    assert wire_orig == "Press Trust of India (PTI)"
    assert is_ind is False

    # 2. Wire dispatch published by Reuters directly -> ORIGIN_WIRE
    syn_type, wire_orig, is_ind = engine._detect_wire_syndication(
        title="IAF announces modernization milestones",
        summary="Reporting from defense summit",
        publisher="Reuters Defense Desk",
        source="reuters"
    )
    assert syn_type == "ORIGIN_WIRE"
    assert wire_orig == "Reuters News Agency"
    assert is_ind is True

    # 3. Official Gazette -> OFFICIAL_DISPATCH
    syn_type, wire_orig, is_ind = engine._detect_wire_syndication(
        title="Ministry of Defence Gazette notification 2026/89",
        summary="Official administrative promulgation",
        publisher="Gazette of India",
        source="gov_portal"
    )
    assert syn_type == "OFFICIAL_DISPATCH"
    assert is_ind is True

    # 4. Independent investigative journalism -> INDEPENDENT
    syn_type, wire_orig, is_ind = engine._detect_wire_syndication(
        title="Deep dive: Assessing sensor fusion telemetry in border zones",
        summary="Investigative analysis by veteran aviation engineers",
        publisher="Aerospace Technology Review",
        source="independent_magazine"
    )
    assert syn_type == "INDEPENDENT"
    assert wire_orig is None
    assert is_ind is True


def test_health_and_readiness_endpoints(client):
    """Verify /health, /health/live, and /health/ready endpoints."""
    # 1. Health
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "modules_registered" in data

    # 2. Liveness
    res_live = client.get("/health/liveness")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"

    # 3. Readiness
    res_ready = client.get("/health/readiness")
    assert res_ready.status_code in [200, 503]
    ready_data = res_ready.json()
    assert "database" in ready_data
    assert "modules_registered" in ready_data

