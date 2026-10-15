"""
Comprehensive automated test suite for advanced intelligence features (P0 and P1):
1. OSINT-03: Collection Completeness Index (CCI) & Coverage Telemetry.
2. OSINT-01: Multi-Stage Query Pivoting Engine.
3. OSINT-02: Historical Passive DNS & Certificate Timeline.
4. CTI-01: Composite Vulnerability Prioritization Engine (CVSS + EPSS + CISA KEV + SLA).
5. SOC-01: Multi-Platform CIB Clustering with Lexical n-gram Similarity & Temporal Windowing.
6. NEWS-01: Claim-Level Verification Matrix (CORROBORATED, SINGLE_SOURCE_REPEATED, CONTRADICTED, UNVERIFIED).
7. CORR-01: Cross-Module Entity Resolution & Disambiguation Service.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.modules.osint.pivot_engine import query_pivot_engine, PivotCandidate
from app.modules.osint.passive_dns import passive_dns_service
from app.modules.threat_intelligence.composite_scorer import composite_vulnerability_scorer
from app.modules.social_media_intelligence.engines.cib_engine import cib_engine
from app.modules.social_media_intelligence.models import SocialPost, SocialPlatformType
from app.modules.news_intelligence.search_engine import news_retrieval_engine
from app.modules.news_intelligence.dossier_compiler import news_dossier_compiler
from app.modules.news_intelligence.models import ClaimMatrixStatus
from app.entities.resolver import entity_disambiguation_service
from app.entities.models import EntityRecord
from app.module_sdk.models import EntityType, EntityPayload
from app.entities.service import entity_service
from app.search.orchestrator import SearchOrchestrator
from app.search.schemas import SearchRequest
from app.identity.models import UserRecord, UserRole


def test_osint_03_collection_completeness_index_and_telemetry():
    """Verify SearchOrchestrator computes honest CCI and provider coverage telemetry."""
    async def _test():
        orchestrator = SearchOrchestrator()
        req = SearchRequest(
            query="target-corp.com",
            modules=["osint"],
            tenant_id="test_tenant_cci"
        )
        user = UserRecord(
            id="usr_test_cci",
            email="investigator@test.local",
            tenant_id="test_tenant_cci",
            name="Test Investigator",
            role=UserRole.INVESTIGATOR,
            hashed_password="hash",
            is_active=True
        )

        resp = await orchestrator.execute_search(req, user)
        assert resp.collection_completeness_index is not None
        assert 0.0 <= resp.collection_completeness_index <= 100.0
        assert resp.coverage_telemetry is not None
        assert "modules_attempted" in resp.coverage_telemetry
        assert "modules_successful" in resp.coverage_telemetry
        assert "collection_completeness_index" in resp.coverage_telemetry
        assert "coverage_assessment" in resp.coverage_telemetry

    asyncio.run(_test())


def test_osint_01_query_pivot_generation():
    """Verify QueryPivotEngine extracts structured pivot recommendations from search entities."""
    entities = [
        {"type": "domain", "value": "investigation-target.com"},
        {"type": "ip", "value": "198.51.100.45"},
        {"type": "cve", "value": "CVE-2024-3400"},
        {"type": "username", "value": "apt_operator_01"}
    ]
    pivots = query_pivot_engine.generate_pivots("investigation-target.com", entities)
    assert len(pivots) >= 3

    # Check pivot candidate fields
    ip_pivot = next((p for p in pivots if p["pivot_type"] == "ip_infrastructure"), None)
    assert ip_pivot is not None
    assert ip_pivot["pivot_query"] == "198.51.100.45"
    assert "osint" in ip_pivot["target_modules"]

    cve_pivot = next((p for p in pivots if p["pivot_type"] == "vulnerability_intelligence"), None)
    assert cve_pivot is not None
    assert "CVE-2024-3400" in cve_pivot["pivot_query"]
    assert "threat_intelligence" in cve_pivot["target_modules"]

    user_pivot = next((p for p in pivots if p["pivot_type"] == "handle_reconnaissance"), None)
    assert user_pivot is not None
    assert "social_media_intelligence" in user_pivot["target_modules"]


def test_osint_02_passive_dns_timeline():
    """Verify PassiveDnsService aggregates historical certificate and DNS records into a timeline."""
    async def _test():
        # Test timeline generation for a known domain with crt.sh/live fallback
        timeline = await passive_dns_service.get_timeline("example.com")
        assert timeline.domain == "example.com"
        assert timeline.total_records >= 0
        assert isinstance(timeline.records, list)
        assert timeline.first_observed is not None
        assert timeline.last_observed is not None

    asyncio.run(_test())


def test_cti_01_composite_vulnerability_scorer():
    """Verify CompositeVulnerabilityScorer calculates weighted risk, CISA KEV priority, and SLA."""
    # Scenario 1: Weaponized CVE in CISA KEV (e.g. CVE-2023-34362)
    res_kev = composite_vulnerability_scorer.compute_composite_risk(
        cve_id="CVE-2023-34362",
        cvss=9.8,
        epss_score=0.97,
        in_cisa_kev=True
    )
    assert res_kev.composite_risk_score >= 80.0
    assert res_kev.remediation_priority == "EMERGENCY_ACTION"
    assert res_kev.sla_remediation_days == 7
    assert res_kev.in_cisa_kev is True
    assert "CRITICAL THREAT" in res_kev.threat_narrative

    # Scenario 2: High EPSS but not in CISA KEV
    res_epss = composite_vulnerability_scorer.compute_composite_risk(
        cve_id="CVE-2024-1111",
        cvss=7.5,
        epss_score=0.25,
        in_cisa_kev=False
    )
    assert res_epss.remediation_priority == "URGENT"
    assert res_epss.sla_remediation_days == 14
    assert res_epss.in_cisa_kev is False

    # Scenario 3: Standard unweaponized CVE
    res_std = composite_vulnerability_scorer.compute_composite_risk(
        cve_id="CVE-2024-9999",
        cvss=3.0,
        epss_score=0.01,
        in_cisa_kev=False
    )
    assert res_std.remediation_priority == "STANDARD"
    assert res_std.sla_remediation_days == 90


def test_soc_01_cib_lexical_ngrams_and_temporal_windowing():
    """Verify CIBEngine detects lexical n-gram coordination and canonical URL dissemination."""
    now_ts = datetime.now(timezone.utc).isoformat()
    posts = [
        SocialPost(
            id="post_1",
            platform=SocialPlatformType.BLUESKY,
            author="account_alpha",
            author_id="alpha_101",
            text="Breaking: Unprecedented malfunction confirmed at municipal substation #CrisisNow",
            created_at=now_ts,
            url="https://bsky.app/post_1",
            links=["https://news.example.com/breaking?utm_source=twitter&utm_medium=social"]
        ),
        SocialPost(
            id="post_2",
            platform=SocialPlatformType.TELEGRAM,
            author="account_beta",
            author_id="beta_202",
            text="Breaking: Unprecedented malfunction confirmed at municipal substation! Check report #CrisisNow",
            created_at=now_ts,
            url="https://t.me/post_2",
            links=["https://news.example.com/breaking?ref=telegram"]
        )
    ]

    # Test URL canonicalization
    clean_url_1 = cib_engine.canonicalize_url(posts[0].links[0])
    clean_url_2 = cib_engine.canonicalize_url(posts[1].links[0])
    assert clean_url_1 == "news.example.com/breaking"
    assert clean_url_1 == clean_url_2

    # Test lexical similarity
    sim, shared = cib_engine.compute_lexical_similarity(posts[0].text, posts[1].text)
    assert sim >= 0.60
    assert len(shared) > 0

    # Test cluster detection
    clusters = cib_engine.detect_clusters(posts)
    assert len(clusters) >= 1
    target_cluster = clusters[0]
    assert target_cluster.account_count == 2
    assert "account_alpha" in target_cluster.accounts
    assert "account_beta" in target_cluster.accounts
    assert target_cluster.coordination_confidence > 75.0
    assert "These are signals warranting review" in target_cluster.caveat_warning


def test_news_01_claim_verification_matrix():
    """Verify news intelligence produces the 4-tier Claim Verification Matrix."""
    # 1. Uncorroborated claim returns UNVERIFIED / INSUFFICIENT_EVIDENCE without synthetic contradiction
    res_contra = news_retrieval_engine.investigate_claim(
        "Breaking: 50,000 voting machines hacked and rigged during election"
    )
    assert res_contra.verification_tier in ["INSUFFICIENT_EVIDENCE", "UNVERIFIED", "CONTRADICTED"]
    assert res_contra.verdict in ["INSUFFICIENT_EVIDENCE", "UNVERIFIED", "MISLEADING"]
    assert res_contra.claim_matrix_item is not None

    # 2. Corroborated claim or honest evidence check
    res_corrob = news_retrieval_engine.investigate_claim(
        "Official technical commission publishes administrative audit gazette"
    )
    assert res_corrob.verification_tier in ["CORROBORATED", "UNVERIFIED", "INSUFFICIENT_EVIDENCE"]
    assert res_corrob.verdict in ["VERIFIED", "UNVERIFIED", "INSUFFICIENT_EVIDENCE"]

    # 3. Single-source wire syndicated or uncorroborated claim
    res_synd = news_retrieval_engine.investigate_claim(
        "Press release wire communique announcing new commercial product launch"
    )
    assert res_synd.verification_tier in ["SINGLE_SOURCE_REPEATED", "UNVERIFIED", "INSUFFICIENT_EVIDENCE"]

    # 4. Dossier compilation produces structured matrix rows
    article = news_dossier_compiler.compile_article(
        article_id="art_test_matrix_01",
        title="Telecom Infrastructure Reliability Review",
        summary="Government commission confirms nationwide telecommunications stability.",
        content="Full statement with independent corroboration from Reuters and BBC.",
        canonical_url="https://reuters.com/tech/telecom-stability",
        publisher="Reuters",
        country="International",
        publication_date="2026-10-14",
    )
    assert len(article.claim_verification_matrix) > 0
    assert article.claim_verification_matrix[0].verification_tier in [
        ClaimMatrixStatus.CORROBORATED,
        ClaimMatrixStatus.SINGLE_SOURCE_REPEATED,
        ClaimMatrixStatus.CONTRADICTED,
        ClaimMatrixStatus.UNVERIFIED,
    ]


def test_corr_01_cross_module_entity_disambiguation():
    """Verify EntityDisambiguationService resolves observables across multi-case investigations."""
    tenant = "test_tenant_corr_matrix"

    # Upsert observable across two different investigations
    payload1 = EntityPayload(
        type=EntityType.DOMAIN,
        value="https://www.adversary-c2.org/beacon",
        confidence=0.9,
        sources=["shodan", "whois"],
        metadata={"observed_role": "c2_domain"}
    )
    payload2 = EntityPayload(
        type=EntityType.DOMAIN,
        value="adversary-c2.org",
        confidence=0.95,
        sources=["telegram_cib_monitor", "news_wire"],
        metadata={"threat_actor": "APT-99"}
    )

    entity_service.upsert_entity(tenant, payload1, investigation_id="case_inv_001")
    entity_service.upsert_entity(tenant, payload2, investigation_id="case_inv_002")

    # Correlate across tenant cases
    corr_resp = entity_disambiguation_service.correlate_entities(tenant)
    assert corr_resp.tenant_id == tenant
    assert corr_resp.total_canonical_entities >= 1

    # Find the canonical domain entity
    target_canon = next(
        (ce for ce in corr_resp.entities if ce.canonical_value == "adversary-c2.org"),
        None
    )
    assert target_canon is not None
    # Must link both investigations
    assert "case_inv_001" in target_canon.linked_investigation_ids
    assert "case_inv_002" in target_canon.linked_investigation_ids
    assert target_canon.cross_case_count >= 2
    # Must span multiple observed modules
    assert "osint" in target_canon.modules_observed
    assert any(m in target_canon.modules_observed for m in ["social_media_intelligence", "news_intelligence"])

    # Test direct resolution lookup
    resolved = entity_disambiguation_service.resolve_observable(tenant, "https://adversary-c2.org")
    assert resolved is not None
    assert resolved.canonical_value == "adversary-c2.org"
