import pytest
import os
import asyncio
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.infrastructure.mongodb.client import sanitize_mongo_uri, connect_to_mongo
from app.modules.osint.snapshot_service import profile_snapshot_service
from app.modules.osint.models import ProfileExtractionResult, ExtractionStatus
from app.modules.news_intelligence.search_engine import news_retrieval_engine
from app.modules.news_intelligence.models import InvestigateClaimRequest
from app.core.egress_controller import EgressController, EgressRouteType
from app.modules.social_media_intelligence.collectors.instagram import InstagramCollector


def test_production_config_validation_rejects_weak_or_default_secrets():
    """Validates that production environment fails fast if SECRET_KEY is weak or default."""
    # Test weak secret in production
    weak_settings = Settings(
        APP_ENV="production",
        SECRET_KEY="weak-secret",
        INITIAL_SUPER_ADMIN_PASSWORD="ValidProductionPassword123!#",
    )
    with pytest.raises(RuntimeError, match="at least 32 characters"):
        weak_settings.validate_production_configuration()

    # Test default placeholder secret in production
    placeholder_settings = Settings(
        APP_ENV="production",
        SECRET_KEY="changethisinproductiontoarandomlongsecretstringwithsufficiententropy123",
        INITIAL_SUPER_ADMIN_PASSWORD="ValidProductionPassword123!#",
    )
    with pytest.raises(RuntimeError, match="placeholder"):
        placeholder_settings.validate_production_configuration()

    # Test default super admin password in production
    default_pw_settings = Settings(
        APP_ENV="production",
        SECRET_KEY="a" * 48,
        INITIAL_SUPER_ADMIN_PASSWORD="SuperAdmin123!",
    )
    with pytest.raises(RuntimeError, match="default"):
        default_pw_settings.validate_production_configuration()

    # Test valid production configuration passes cleanly
    valid_settings = Settings(
        APP_ENV="production",
        SECRET_KEY="c" * 48,
        INITIAL_SUPER_ADMIN_PASSWORD="SecureProductionPassphrase987!#",
    )
    valid_settings.validate_production_configuration()


def test_sanitize_mongo_uri():
    """Confirms credentials in MongoDB connection URIs are masked before logging."""
    raw_uri = "mongodb://admin:SuperSecretPass123@mongo.internal:27017/sential_saas?authSource=admin"
    sanitized = sanitize_mongo_uri(raw_uri)
    assert "SuperSecretPass123" not in sanitized
    assert "@mongo.internal:27017" in sanitized

    # No password provided
    raw_no_pass = "mongodb://localhost:27017/sential_saas"
    assert sanitize_mongo_uri(raw_no_pass) == raw_no_pass


def test_production_mongo_unavailability_raises_runtime_error():
    """Ensures production startup fails if MongoDB is unreachable."""
    async def _test():
        with patch("app.infrastructure.mongodb.client.settings") as mock_settings:
            mock_settings.APP_ENV = "production"
            mock_settings.MONGODB_URI = "mongodb://127.0.0.1:29999/test_db"
            mock_settings.MONGODB_DATABASE = "test_db"

            with pytest.raises(RuntimeError, match="Operating in unverified in-memory fallback mode is strictly prohibited in production"):
                await connect_to_mongo()
    asyncio.run(_test())


def test_tenant_isolation_profile_snapshots():
    """Proves Tenant A's profile snapshots are inaccessible and invisible to Tenant B."""
    async def _test():
        tenant_a = "tenant_alpha"
        tenant_b = "tenant_beta"
        target_username = "suspect_operative_42"
        platform = "github"

        extraction = ProfileExtractionResult(
            platform_id=platform,
            platform_name="GitHub",
            username=target_username,
            canonical_url=f"https://github.com/{target_username}",
            status=ExtractionStatus.PROFILE_VALIDATED,
            bio="Private operative profile for tenant A",
            public_metrics={"followers": 150},
            fetched_at="2026-10-15T12:00:00Z",
        )

        # Tenant A records observation
        snap, changes = await profile_snapshot_service.record_observation(extraction, tenant_id=tenant_a)
        assert snap is not None

        # Tenant A can view the observation
        snaps_a = await profile_snapshot_service.get_snapshot_history(platform, target_username, tenant_id=tenant_a)
        assert len(snaps_a) >= 1

        # Tenant B querying the same target sees ZERO observations for Tenant B
        snaps_b = await profile_snapshot_service.get_snapshot_history(platform, target_username, tenant_id=tenant_b)
        assert len(snaps_b) == 0

        # Ensure in-memory cache doesn't leak between tenants
        snaps_b_cached = await profile_snapshot_service.get_snapshot_history(platform, target_username, tenant_id=tenant_b)
        assert len(snaps_b_cached) == 0

    asyncio.run(_test())


def test_news_source_registration_role_enforcement(client: TestClient, user_headers, analyst_headers):
    """Proves unprivileged USER cannot register news sources (403 Forbidden)."""
    payload = {
        "publisher_name": "Reuters Global News",
        "domain": "reuters.com",
        "country_code": "US",
        "is_verified": True,
    }

    # Regular USER receives 403
    res_user = client.post("/api/v1/news/sources", json=payload, headers=user_headers)
    assert res_user.status_code == 403

    # ANALYST is authorized
    res_analyst = client.post("/api/v1/news/sources", json=payload, headers=analyst_headers)
    assert res_analyst.status_code == 200
    data = res_analyst.json()
    assert data["status"] == "registered"
    # Non-superadmin registrations default to unverified
    assert data["is_verified"] is False


def test_news_source_registration_ssrf_rejection(client: TestClient, analyst_headers):
    """Proves private IPs, loopback addresses, and metadata endpoints are rejected with HTTP 400."""
    ssrf_domains = [
        "127.0.0.1",
        "localhost",
        "169.254.169.254",
        "10.0.0.1",
        "http://192.168.1.1/feed.rss",
    ]
    for target in ssrf_domains:
        payload = {
            "publisher_name": "Malicious Probe",
            "domain": target,
            "country_code": "US",
        }
        res = client.post("/api/v1/news/sources", json=payload, headers=analyst_headers)
        assert res.status_code == 400
        assert "SSRF Protection" in res.json()["detail"]


def test_unknown_article_returns_404(client: TestClient, analyst_headers):
    """Proves querying a non-existent article ID returns 404, eliminating synthetic fallback dossiers."""
    res = client.get("/api/v1/news/articles/completely-nonexistent-article-uuid", headers=analyst_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Article not found"

    # Direct search engine retrieval also returns None
    result = news_retrieval_engine.get_article("completely-nonexistent-article-uuid")
    assert result is None


def test_claim_investigation_returns_unverified_without_synthetic_contradictions():
    """Proves claim verification does not fabricate quotes or verdicts based on keyword matching."""
    from app.modules.news_intelligence.service import news_intelligence_service

    req = InvestigateClaimRequest(
        claim_text="Sensors were allegedly hacked by malicious cyber operatives during the drill.",
        context_article_id="nonexistent-context-id",
    )
    result = news_intelligence_service.investigate_claim(tenant_id="tenant_acme", req=req)

    # Must return INSUFFICIENT_EVIDENCE or UNVERIFIED, not a confident fabricated verdict
    assert result.verdict in ["INSUFFICIENT_EVIDENCE", "UNVERIFIED"]
    assert result.confidence <= 50.0

    # Ensure no fabricated quotes or synthetic personas
    all_text = " ".join([str(c.get("quote", "")) for c in result.contradicting_sources] + [str(s.get("quote", "")) for s in result.supporting_sources])
    assert "Dr. Aris Vance" not in all_text
    assert "Official Technical Audit Commission" not in all_text


def test_egress_controller_fail_closed_on_unverified_gateway():
    """Ensures that unverified/unhealthy regional routes fail closed and do not generate pseudo-IPs."""
    controller = EgressController()
    controller._allow_gateway_mocks = False

    # Attempting to get client for a regional route without a verified proxy fails closed
    with pytest.raises(RuntimeError, match="OPSEC Fail-Closed"):
        controller.get_httpx_client_for_route(
            route_type=EgressRouteType.REGIONAL_GATEWAY_APPROVED,
            gateway_name="south_asia_gateway",
        )


def test_instagram_collector_no_magic_account_id():
    """Proves missing INSTAGRAM_BUSINESS_ACCOUNT_ID reports CONFIG_REQUIRED and doesn't use hardcoded IDs."""
    async def _test():
        collector = InstagramCollector()
        collector._access_token = "valid_test_token"

        with patch.dict(os.environ, {}, clear=True):
            posts = await collector.search_posts(
                query="#threatintel",
                limit=5,
                job_id="test_job_123",
            )
            assert posts == []

    asyncio.run(_test())
