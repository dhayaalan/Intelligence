import asyncio
import pytest
from app.modules.osint.providers.financial_intel import FinancialIntelProvider
from app.modules.osint.models import ExtractionStatus
from app.modules.threat_intelligence.providers.vulnerability_intel import VulnerabilityIntelProvider
from app.modules.threat_intelligence.providers.ioc_feed import IOCFeedProvider
from app.modules.threat_intelligence.composite_scorer import CompositeVulnerabilityScorer
from app.modules.news_intelligence.factcheck_service import FactCheckService
from app.modules.news_intelligence.models import ClaimMatrixStatus
from app.module_sdk.provider_adapter import ProviderRequest


def test_financial_intel_privacy_guardrail():
    """Verify that private personal financial queries (card numbers, PINs, passwords) are strictly blocked."""
    async def _run():
        provider = FinancialIntelProvider()

        # Test credit card pattern query
        req = ProviderRequest(
            query="4111 2222 3333 4444",
            target_type="card",
            config={}
        )
        res = await provider.execute(req)
        assert res.status == "rejected"
        assert res.raw_data.get("privacy_violation") is True
        assert res.raw_data.get("extraction_status") == ExtractionStatus.ACCESS_RESTRICTED.value
        assert "Strict Financial Privacy Guardrail" in res.raw_data.get("error", "")

        # Test PIN/password query
        req_pin = ProviderRequest(
            query="bank login customer password and atm pin",
            target_type="credential",
            config={}
        )
        res_pin = await provider.execute(req_pin)
        assert res_pin.status == "rejected"
        assert res_pin.raw_data.get("privacy_violation") is True

    asyncio.run(_run())


def test_financial_intel_public_organization_lookup():
    """Verify public corporate intelligence query for banks / institutions."""
    async def _run():
        provider = FinancialIntelProvider()

        req = ProviderRequest(
            query="Barclays",
            target_type="bank",
            config={}
        )
        res = await provider.execute(req)
        assert res.status in ["success", "not_found"]
        assert "sources_queried" in res.raw_data
        assert res.raw_data.get("privacy_boundary_enforced") is True

    asyncio.run(_run())


def test_threat_intel_vulnerability_epss_and_kev():
    """Verify VulnerabilityIntelProvider real FIRST EPSS and CISA KEV calculations."""
    async def _run():
        provider = VulnerabilityIntelProvider()

        req = ProviderRequest(
            query="CVE-2023-48795",
            target_type="cve",
            config={}
        )
        res = await provider.execute(req)
        assert res.status == "success"
        vulns = res.raw_data.get("vulnerabilities", [])
        assert len(vulns) >= 1
        v = vulns[0]
        assert v.get("cve_id") == "CVE-2023-48795"
        assert "epss_score" in v
        assert "composite_risk_score" in v
        assert "provenance" in v
        assert res.raw_data.get("is_zero_synthetic") is True

    asyncio.run(_run())


def test_composite_vulnerability_scorer_kev_enforcement():
    """Verify that CISA KEV membership guarantees high risk tier and accelerated SLA."""
    assessment = CompositeVulnerabilityScorer.calculate_risk(
        cve_id="CVE-2024-1234",
        cvss=6.5,
        epss_score=0.45,
        in_cisa_kev=True
    )
    assert assessment.in_cisa_kev is True
    assert assessment.composite_risk_score >= 80.0
    assert assessment.remediation_priority == "EMERGENCY_ACTION"
    assert assessment.sla_remediation_days == 7


def test_threat_intel_ioc_feed_provenance():
    """Verify IOCFeedProvider uses real OTX lookups and reports config requirements honestly."""
    async def _run():
        provider = IOCFeedProvider()

        req = ProviderRequest(
            query="8.8.8.8",
            target_type="ip",
            config={}
        )
        res = await provider.execute(req)
        assert res.status == "success"
        assert res.raw_data.get("normalized_indicator_type") == "IPv4"
        assert "sources_queried" in res.raw_data
        assert "config_required_sources" in res.raw_data
        assert res.raw_data.get("is_zero_synthetic") is True

    asyncio.run(_run())


def test_news_fact_check_evidence_evaluation():
    """Verify journalistic evidence evaluation tiers and syndication detection."""
    service = FactCheckService()

    # 1. Contradicted by prior fact check
    item_debunked = service.evaluate_claim_evidence(
        claim_id="claim-1",
        claim_text="The government banned all private vehicles.",
        supporting_publishers=["Random Blog"],
        contradicting_publishers=["Snopes"],
        fact_check_rating="False"
    )
    assert item_debunked.verification_tier == ClaimMatrixStatus.CONTRADICTED

    # 2. Corroborated across independent newsrooms
    item_corroborated = service.evaluate_claim_evidence(
        claim_id="claim-2",
        claim_text="Central bank adjusts interest rates by 25 basis points.",
        supporting_publishers=["Reuters", "Bloomberg", "Financial Times"],
        contradicting_publishers=[],
        is_wire_syndicated=False
    )
    assert item_corroborated.verification_tier == ClaimMatrixStatus.CORROBORATED
    assert item_corroborated.independent_publishers_count == 3

    # 3. Disputed by conflicting reports
    item_disputed = service.evaluate_claim_evidence(
        claim_id="claim-3",
        claim_text="Peace treaty negotiations concluded yesterday.",
        supporting_publishers=["Outlet A"],
        contradicting_publishers=["Outlet B"],
        is_wire_syndicated=False
    )
    assert item_disputed.verification_tier == ClaimMatrixStatus.DISPUTED

    # 4. Syndication detected: multiple outlets repeating one wire does not equal independent corroboration
    item_syndicated = service.evaluate_claim_evidence(
        claim_id="claim-4",
        claim_text="New port facility inaugurated today.",
        supporting_publishers=["Publisher X", "Publisher Y", "Publisher Z"],
        contradicting_publishers=[],
        origin_wire="Associated Press Wire",
        is_wire_syndicated=True
    )
    assert item_syndicated.verification_tier == ClaimMatrixStatus.SINGLE_SOURCE_REPEATED
    assert item_syndicated.independent_publishers_count == 1
    assert "Syndication detected" in item_syndicated.forensic_rationale

    # 5. Insufficient evidence
    item_empty = service.evaluate_claim_evidence(
        claim_id="claim-5",
        claim_text="Secret moonbase discovered.",
        supporting_publishers=[],
        contradicting_publishers=[]
    )
    assert item_empty.verification_tier == ClaimMatrixStatus.INSUFFICIENT_EVIDENCE
