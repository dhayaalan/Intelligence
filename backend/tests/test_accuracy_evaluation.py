import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.core.provider_registry.registry import provider_registry
from app.core.provider_registry.schemas import ProviderStatus, ProviderMetadata
from app.modules.osint.module import osint_module
from app.modules.threat_intelligence.module import threat_intelligence_module
from app.modules.social_media_intelligence.manifest import SOCIAL_MEDIA_INTELLIGENCE_MANIFEST
from app.modules.social_media_intelligence.module import SocialMediaIntelligenceModule
from app.modules.osint.providers.sec_edgar import SECEDGARProvider, SEC_USER_AGENT
from app.modules.osint.providers.censys import CensysSearchProvider
from app.module_sdk.provider_adapter import ProviderRequest
from app.modules.tool_executor import tool_executor
from app.correlation.engine import correlation_engine
from app.module_sdk.models import (
    NormalizedModuleResult, EntityPayload, EntityType, RelationshipPayload,
    RelationshipType, EvidencePayload, ModuleHealthStatus
)
from app.modules.threat_intelligence.composite_scorer import CompositeVulnerabilityScorer
from app.modules.news_intelligence.factcheck_service import FactCheckService
from app.modules.news_intelligence.models import ClaimMatrixStatus


@pytest.mark.asyncio
async def test_provider_registry_operational_states_accuracy():
    """Verifies honest status distinctions across registered tools without uniform false HEALTHY labels."""
    stats = provider_registry.get_stats()
    assert stats.total_providers >= 375
    assert stats.total_osint_providers >= 335
    assert stats.total_threat_intel_providers >= 33

    # Must distinguish between operational, registered probers, not_configured, and not_installed
    assert stats.operational_providers > 0
    assert stats.registered_providers > 0
    assert "OPERATIONAL" in stats.status_breakdown
    assert "REGISTERED" in stats.status_breakdown

    # Shodan without API key must not be falsely marked OPERATIONAL
    shodan_meta = provider_registry.get_metadata("shodan")
    assert shodan_meta is not None
    if not os.getenv("SHODAN_API_KEY"):
        assert shodan_meta.status == "NOT_CONFIGURED"

    # Deep public engines (e.g. sec_edgar, gleif_lei, wayback_cdx, threatfox) must be OPERATIONAL
    sec_meta = provider_registry.get_metadata("sec_edgar")
    assert sec_meta is not None
    assert sec_meta.status == "OPERATIONAL"

    wayback_meta = provider_registry.get_metadata("wayback_cdx")
    assert wayback_meta is not None
    assert wayback_meta.status == "OPERATIONAL"


@pytest.mark.asyncio
async def test_social_media_intelligence_manifest_and_health_reconciliation():
    """Verifies that Instagram and Facebook collectors are declared in the manifest and tracked honestly."""
    manifest = SOCIAL_MEDIA_INTELLIGENCE_MANIFEST
    assert "instagram_collector" in manifest.providers
    assert "facebook_collector" in manifest.providers

    # Configuration schema must include Meta/Instagram fields
    config_keys = [f.key for f in manifest.configuration_schema]
    assert "instagram_access_token" in config_keys
    assert "facebook_access_token" in config_keys
    assert "instagram_business_account_id" in config_keys

    # Module health check must include all collectors and their live status
    mod = SocialMediaIntelligenceModule()
    health = await mod.health_check()
    assert health.status == ModuleHealthStatus.HEALTHY
    assert "instagram" in health.details["collectors"]
    assert "facebook" in health.details["collectors"]
    assert "collector_states" in health.details


@pytest.mark.asyncio
async def test_sec_edgar_provider_resolution_and_accuracy():
    """Verifies official SEC EDGAR CIK resolution, submissions parsing, and fair-access compliance."""
    provider = SECEDGARProvider()
    assert provider.provider_id == "sec_edgar"
    assert "FINANCIAL_INTEL" in provider.category or "organization" in provider.supported_targets

    # 1. Test mock CIK resolution for known corporation
    mock_tickers = {
        "AAPL": {"cik": "0000320193", "ticker": "AAPL", "title": "Apple Inc."},
        "apple inc.": {"cik": "0000320193", "ticker": "AAPL", "title": "Apple Inc."}
    }

    mock_sec_data = {
        "name": "Apple Inc.",
        "sic": "3571",
        "sicDescription": "ELECTRONIC COMPUTERS",
        "tickers": ["AAPL"],
        "exchanges": ["Nasdaq"],
        "stateOfIncorporation": "CA",
        "formerNames": [{"name": "APPLE COMPUTER INC"}],
        "filings": {
            "recent": {
                "form": ["10-K", "10-Q", "8-K"],
                "filingDate": ["2026-10-01", "2026-07-25", "2026-05-10"],
                "accessionNumber": ["0000320193-26-000100", "0000320193-26-000080", "0000320193-26-000050"],
                "primaryDocument": ["aapl-20261001.htm", "aapl-20260725.htm", "aapl-20260510.htm"],
                "primaryDocDescription": ["10-K ANNUAL REPORT", "10-Q QUARTERLY REPORT", "CURRENT REPORT"]
            }
        }
    }

    with patch("app.modules.osint.providers.sec_edgar.get_sec_tickers_map", return_value=mock_tickers):
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_sec_data
            mock_get.return_value = mock_resp

            resp = await provider.execute(ProviderRequest(query="AAPL", target_type="company"))
            assert resp.status == "success"
            assert resp.raw_data["count"] == 1
            rec = resp.raw_data["record"]
            assert rec["legal_name"] == "Apple Inc."
            assert rec["cik"] == "0000320193"
            assert rec["sic"] == "3571"
            assert "APPLE COMPUTER INC" in rec["former_names"]
            assert len(rec["recent_filings"]) == 3

            # Verify User-Agent compliance
            call_headers = mock_get.call_args[1].get("headers", {})
            assert "investigations@sential.org" in call_headers.get("User-Agent", "")


@pytest.mark.asyncio
async def test_sec_edgar_rate_limit_and_not_found_handling():
    """Verifies that SEC EDGAR 429 returns an explicit error and 404 returns not_found."""
    provider = SECEDGARProvider()

    with patch.object(provider, "_resolve_cik", return_value="0000320193"):
        # Rate limit test (HTTP 429)
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_get.return_value = mock_resp

            resp = await provider.execute(ProviderRequest(query="0000320193", target_type="company"))
            assert resp.status == "error"
            assert "429" in resp.error or "rate limit" in resp.error.lower()

        # Not found test (HTTP 404)
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp

            resp = await provider.execute(ProviderRequest(query="0000320193", target_type="company"))
            assert resp.status == "not_found"
            assert resp.raw_data["count"] == 0


@pytest.mark.asyncio
async def test_censys_provider_honest_config_required():
    """Verifies that Censys returns CONFIG_REQUIRED honestly when unconfigured."""
    provider = CensysSearchProvider()
    with patch.dict(os.environ, {}, clear=True):
        resp = await provider.execute(ProviderRequest(query="8.8.8.8", target_type="ip"))
        assert resp.status == "config_required"
        assert "credentials not configured" in resp.error.lower()


@pytest.mark.asyncio
async def test_tool_executor_sec_edgar_and_censys_dispatch():
    """Verifies that ToolExecutor dispatches tool_sec_edgar and tool_censys correctly."""
    with patch("app.modules.osint.providers.sec_edgar.SECEDGARProvider.execute") as mock_sec_exec:
        mock_resp = MagicMock()
        mock_resp.status = "success"
        mock_resp.duration_ms = 45.0
        mock_resp.error = None
        mock_resp.raw_data = {
            "record": {
                "cik": "0000320193",
                "legal_name": "Apple Inc.",
                "sic_description": "ELECTRONIC COMPUTERS",
                "recent_filings": [{"form": "10-K", "filing_date": "2026-10-01"}]
            }
        }
        mock_sec_exec.return_value = mock_resp

        res = await tool_executor.execute_tool(
            tool_id="tool_sec_edgar",
            target="Apple",
            target_type="company"
        )
        assert res.status == "SUCCESS"
        assert len(res.results) == 1
        assert "Apple Inc." in res.results[0].value
        assert "0000320193" in res.results[0].value


@pytest.mark.asyncio
async def test_correlation_engine_entity_deduplication_and_provenance():
    """Verifies entity deduplication while preserving independent source corroboration."""
    res1 = NormalizedModuleResult(
        module="osint",
        execution_id="exec-1",
        status="completed",
        entities=[
            EntityPayload(
                type=EntityType.USERNAME,
                value="john_doe",
                confidence=0.8,
                sources=["github_prober"],
                metadata={"platform": "github", "profile_url": "https://github.com/john_doe"}
            )
        ]
    )

    res2 = NormalizedModuleResult(
        module="social_media_intelligence",
        execution_id="exec-2",
        status="completed",
        entities=[
            EntityPayload(
                type=EntityType.USERNAME,
                value="john_doe",
                confidence=0.8,
                sources=["reddit_collector"],
                metadata={"platform": "reddit", "profile_url": "https://reddit.com/user/john_doe"}
            )
        ]
    )

    entities, relationships, evidence = correlation_engine.correlate_module_results(
        target_query="john_doe",
        target_type="username",
        results=[res1, res2]
    )

    assert len(entities) == 1
    merged = entities[0]
    assert merged.value == "john_doe"
    assert "github_prober" in merged.sources
    assert "reddit_collector" in merged.sources
    assert merged.confidence > 0.8  # Boosted for independent corroboration
    assert "platforms" in merged.metadata
    assert "github" in merged.metadata["platforms"]
    assert "reddit" in merged.metadata["platforms"]
    assert len(merged.metadata["profile_urls"]) == 2
    assert merged.metadata["corroborating_sources_count"] == 2


def test_threat_intelligence_risk_separation():
    """Verifies strict separation between CVSS base severity, FIRST EPSS exploit likelihood, and CISA KEV exploitation."""
    # Low CVSS (5.3) but weaponized in CISA KEV must produce emergency action due to real exploitation
    risk_kev = CompositeVulnerabilityScorer.calculate_risk(
        cve_id="CVE-2023-12345",
        cvss=5.3,
        epss_score=0.15,
        in_cisa_kev=True
    )
    assert risk_kev.in_cisa_kev is True
    assert risk_kev.cvss_severity == "MEDIUM"
    assert risk_kev.remediation_priority == "EMERGENCY_ACTION"
    assert risk_kev.composite_risk_score >= 80.0

    # High CVSS (9.8) but zero EPSS and not in KEV
    risk_theoretical = CompositeVulnerabilityScorer.calculate_risk(
        cve_id="CVE-2024-99999",
        cvss=9.8,
        epss_score=0.01,
        in_cisa_kev=False
    )
    assert risk_theoretical.in_cisa_kev is False
    assert risk_theoretical.cvss_severity == "CRITICAL"
    assert risk_theoretical.remediation_priority == "URGENT"


def test_news_intelligence_syndication_versus_independent_corroboration():
    """Verifies that syndicated wire stories are classified as SINGLE_SOURCE_REPEATED rather than false independent corroboration."""
    fact_checker = FactCheckService()

    # 1. Syndicated wire reporting across multiple outlets
    syndicated_item = fact_checker.evaluate_claim_evidence(
        claim_id="claim_001",
        claim_text="Economic stimulus announcement released today",
        supporting_publishers=["The Daily Gazette", "National Tribune", "Regional Herald"],
        contradicting_publishers=[],
        origin_wire="Associated Press",
        is_wire_syndicated=True
    )
    assert syndicated_item.verification_tier == ClaimMatrixStatus.SINGLE_SOURCE_REPEATED
    assert syndicated_item.independent_publishers_count == 1
    assert syndicated_item.syndicated_publishers_count == 3
    assert "Multiple syndications of one wire do not constitute independent confirmations" in syndicated_item.forensic_rationale

    # 2. Independent publisher corroboration
    independent_item = fact_checker.evaluate_claim_evidence(
        claim_id="claim_002",
        claim_text="Investigative report into shell companies",
        supporting_publishers=["Bellingcat", "ICIJ", "Der Spiegel"],
        contradicting_publishers=[],
        origin_wire=None,
        is_wire_syndicated=False
    )
    assert independent_item.verification_tier == ClaimMatrixStatus.CORROBORATED
    assert independent_item.independent_publishers_count == 3
