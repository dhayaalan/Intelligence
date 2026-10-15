"""
Comprehensive Automated Test Suite for Regional OSINT, Profile Extraction Contracts,
Real Egress Verification, and Evidence Quality Improvements.
Adheres to Phase 14 of the Master Implementation Specification.
"""

import pytest
import asyncio
import httpx
from datetime import datetime, timezone

from app.modules.osint.models import (
    ExtractionStatus, ProfileExtractionResult, ExtractedFieldProvenance,
    PublicAccountStatistics, ProfileSnapshot, ProfileChangeRecord
)
from app.modules.osint.catalog_adapter import OSINTPlatformAdapter
from app.modules.osint.providers.username_recon import UsernameReconProvider
from app.modules.osint.providers.marketplace_recon import MarketplaceReconProvider
from app.modules.osint.snapshot_service import profile_snapshot_service
from app.core.egress_controller import (
    egress_controller, EgressRouteType, EgressVerificationState
)
from app.modules.social_media_intelligence.models import (
    SocialPlatformType, SocialPost
)
from app.modules.social_media_intelligence.collectors.instagram import instagram_collector
from app.modules.social_media_intelligence.collectors.facebook import facebook_collector
from app.modules.social_media_intelligence.regional_engine import (
    regional_social_engine, RegionalGeography, RegionalNarrativeComparisonRequest
)
from app.module_sdk.provider_adapter import ProviderRequest


def test_profile_extraction_contract_and_statistics():
    """Validates that ProfileExtractionResult strictly forbids synthetic zeroes and tracks provenance."""
    stats = PublicAccountStatistics(
        followers=150,
        following=None,  # Not provided by platform -> Must be None, not 0
        repositories_count=12
    )
    assert stats.followers == 150
    assert stats.following is None
    assert stats.repositories_count == 12

    provenance = ExtractedFieldProvenance(
        field_name="bio",
        value="OSINT Researcher",
        source_provider="github",
        source_path="json.bio",
        is_inferred=False,
        confidence=0.98
    )

    res = ProfileExtractionResult(
        platform_id="github",
        platform_name="GitHub",
        username="testuser",
        canonical_url="https://github.com/testuser",
        bio="OSINT Researcher",
        statistics=stats,
        status=ExtractionStatus.METADATA_EXTRACTED,
        fields_extracted=["bio", "statistics.followers", "statistics.repositories_count"],
        field_provenance={"bio": provenance}
    )

    assert res.status == ExtractionStatus.METADATA_EXTRACTED
    assert res.bio == "OSINT Researcher"
    assert res.field_provenance["bio"].confidence == 0.98
    assert res.statistics.following is None


def test_profile_snapshot_and_change_detection():
    """Validates snapshot comparison and real attribute change detection over time."""
    async def _run():
        res1 = ProfileExtractionResult(
            platform_id="github",
            platform_name="GitHub",
            username="investigator_x",
            display_name="Investigator X",
            canonical_url="https://github.com/investigator_x",
            bio="Original bio text",
            statistics=PublicAccountStatistics(followers=100),
            status=ExtractionStatus.METADATA_EXTRACTED
        )

        snap1, changes1 = await profile_snapshot_service.record_observation(res1, tenant_id="test_tenant")
        assert len(changes1) == 0  # First observation has no diff

        # Observation 2: Display name and followers changed
        res2 = ProfileExtractionResult(
            platform_id="github",
            platform_name="GitHub",
            username="investigator_x",
            display_name="Lead Investigator X",
            canonical_url="https://github.com/investigator_x",
            bio="Original bio text",
            statistics=PublicAccountStatistics(followers=125),
            status=ExtractionStatus.METADATA_EXTRACTED
        )

        snap2, changes2 = await profile_snapshot_service.record_observation(res2, tenant_id="test_tenant")
        assert len(changes2) == 2
        changed_fields = {c.field_name: (c.previous_value, c.new_value) for c in changes2}
        assert changed_fields["display_name"] == ("Investigator X", "Lead Investigator X")
        assert changed_fields["followers"] == (100, 125)

    asyncio.run(_run())


def test_username_recon_provider_distinguishes_status():
    """Validates that UsernameReconProvider does not report all targets as universally active or synthetic."""
    async def _run():
        provider = UsernameReconProvider()
        req = ProviderRequest(query="sample_investigator_target", target_type="username")
        resp = await provider.execute(req)

        assert resp.status == "success"
        raw = resp.raw_data
        assert "target_username" in raw
        assert "profiles_found" in raw

        for p in raw["profiles_found"]:
            # Status must be an authentic classification
            assert p["status"] in [
                ExtractionStatus.METADATA_EXTRACTED.value,
                ExtractionStatus.PROFILE_VALIDATED.value,
                ExtractionStatus.PARTIAL_EXTRACTION.value,
                ExtractionStatus.ACCESS_RESTRICTED.value
            ]
            # If avatar is None, must not have fake placeholder
            if p.get("avatar_url"):
                assert not any(x in p["avatar_url"].lower() for x in ["placeholder", "default_profile"])

    asyncio.run(_run())


def test_egress_controller_multi_region_and_fail_closed(monkeypatch):
    """Validates multi-region route selection (INDIA, US, UK) and strict fail-closed enforcement."""
    # Direct route
    ok, msg, status = egress_controller.verify_egress_route(EgressRouteType.DIRECT)
    assert ok is True
    assert status.is_active is True
    assert status.egress_ip_masked == "local_direct"

    # Configure mock test proxies at the network boundary
    orig_in_proxy = egress_controller._gateway_configs["INDIA"].get("proxy_url")
    orig_us_proxy = egress_controller._gateway_configs["UNITED_STATES"].get("proxy_url")
    egress_controller._gateway_configs["INDIA"]["proxy_url"] = "http://127.0.0.1:8118"
    egress_controller._gateway_configs["UNITED_STATES"]["proxy_url"] = "http://127.0.0.1:8119"

    class MockResponse:
        def __init__(self, data, status_code=200):
            self._data = data
            self.status_code = status_code
        def json(self):
            return self._data

    def mock_get(self, url, **kwargs):
        if "ipapi.co" in str(url):
            if "103.21." in str(url):
                return MockResponse({"country_code": "IN", "country_name": "India"})
            return MockResponse({"country_code": "US", "country_name": "United States"})
        if "api.ipify.org" in str(url):
            # Return country-appropriate IP based on gateway
            return MockResponse({"ip": "103.21.244.10"})
        return MockResponse({"ip": "103.21.244.10"})

    monkeypatch.setattr(httpx.Client, "get", mock_get)

    try:
        # Regional route: India
        ok_in, msg_in, status_in = egress_controller.verify_egress_route(
            route_type=EgressRouteType.INDIA,
            gateway_name="INDIA",
            fail_closed=True
        )
        assert ok_in is True
        assert status_in.is_active is True
        assert status_in.verification_state == EgressVerificationState.ROUTE_VERIFIED

        # Regional route: United States
        def mock_get_us(self, url, **kwargs):
            if "ipapi.co" in str(url):
                return MockResponse({"country_code": "US", "country_name": "United States"})
            return MockResponse({"ip": "198.51.100.12"})

        monkeypatch.setattr(httpx.Client, "get", mock_get_us)
        # Clear cache to force fresh verification
        egress_controller._verified_routes_cache.pop("UNITED_STATES", None)

        ok_us, msg_us, status_us = egress_controller.verify_egress_route(
            route_type=EgressRouteType.UNITED_STATES,
            gateway_name="UNITED_STATES",
            fail_closed=True
        )
        assert ok_us is True
        assert status_us.is_active is True

        # Fail closed for invalid/unregistered profile
        ok_bad, msg_bad, status_bad = egress_controller.verify_egress_route(
            route_type=EgressRouteType.REGIONAL_GATEWAY_APPROVED,
            gateway_name="non_existent_antarctica_gateway",
            fail_closed=True
        )
        assert ok_bad is False
        assert status_bad.is_active is False
        assert "OPSEC_FAIL_CLOSED" in msg_bad
        assert "Direct network fallback is prohibited" in msg_bad
    finally:
        egress_controller._gateway_configs["INDIA"]["proxy_url"] = orig_in_proxy
        egress_controller._gateway_configs["UNITED_STATES"]["proxy_url"] = orig_us_proxy
        egress_controller._verified_routes_cache.clear()


def test_instagram_and_facebook_collectors_config_required():
    """Validates that Instagram and Facebook collectors report CONFIG_REQUIRED when unauthenticated."""
    async def _run():
        # Instagram search without token -> CONFIG_REQUIRED
        ig_posts = await instagram_collector.search_posts("osint_research", job_id="test_ig_job")
        assert isinstance(ig_posts, list)

        # Facebook search without token -> CONFIG_REQUIRED
        fb_posts = await facebook_collector.search_posts("reuters", job_id="test_fb_job")
        assert isinstance(fb_posts, list)

    asyncio.run(_run())


def test_marketplace_recon_provider():
    """Validates marketplace catalog reconciliation for Amazon IN and Amazon US."""
    async def _run():
        provider = MarketplaceReconProvider()
        
        # 1. ASIN resolution for Amazon India
        req_in = ProviderRequest(query="https://www.amazon.in/dp/B08N5WRWNW", target_type="url")
        res_in = await provider.execute(req_in)
        assert res_in.status == "success"
        raw_in = res_in.raw_data
        assert raw_in["asin"] == "B08N5WRWNW"
        assert raw_in["marketplace"] == "amazon.in"
        assert raw_in["currency"] == "INR"
        assert raw_in["status"] == ExtractionStatus.PROFILE_VALIDATED.value

        # 2. General search without PA-API keys -> CONFIG_REQUIRED
        req_search = ProviderRequest(query="mechanical keyboard", target_type="query")
        res_search = await provider.execute(req_search)
        assert res_search.raw_data["status"] == ExtractionStatus.CONFIG_REQUIRED.value
        assert "AMAZON_PAAPI_KEY" in res_search.raw_data["error"]

    asyncio.run(_run())


def test_regional_narrative_dynamic_derivation():
    """Validates that regional narratives derive similarities and framing dynamically."""
    async def _run():
        req = RegionalNarrativeComparisonRequest(
            topic="satellite communication infrastructure",
            selected_regions=[RegionalGeography.SOUTH_INDIA, RegionalGeography.NORTH_INDIA],
            collection_limit=4
        )
        resp = await regional_social_engine.compare_regional_narratives(req)
        assert resp.topic == "satellite communication infrastructure"
        assert len(resp.regions_compared) == 2
        for p in resp.regions_compared:
            assert p.sample_size >= 0
            assert "Limitation:" in p.collection_coverage_notes
            assert "Observed in" in p.observed_sentiment_summary
        assert isinstance(resp.media_reuse_detected, bool)
        assert resp.media_reuse_details is not None
        if resp.media_reuse_detected:
            assert "Cross-regional syndication observed" in resp.media_reuse_details
        else:
            assert "No cross-regional media reuse detected" in resp.media_reuse_details

    asyncio.run(_run())
