import asyncio
import io
import pytest
from PIL import Image
from app.modules.social_media_intelligence.regional_engine import (
    regional_social_engine,
    RegionalTarget,
    RegionalNarrativeComparisonRequest,
)
from app.core.egress_controller import (
    egress_controller,
    EgressRouteType,
)
from app.modules.threat_intelligence.engines.scope_enforcer import (
    vapt_scope_enforcer,
    ScanImpactLevel,
    ScopePermit,
)
from app.modules.news_intelligence.multimodal_engine import (
    multimodal_engine,
)


def test_regional_lexicon_expansion_and_transliteration():
    """Validates regional terminology expansion across South India, North India, Pakistan, and Bangladesh."""
    expanded = regional_social_engine.expand_regional_lexicon(
        base_topic="election",
        target_region=RegionalTarget.SOUTH_INDIA
    )
    assert "தேர்தல்" in expanded or "election" in expanded
    assert len(expanded) >= 2

    pk_expanded = regional_social_engine.expand_regional_lexicon(
        base_topic="iaf",
        target_region=RegionalTarget.PAKISTAN
    )
    assert any("فضائیہ" in t or "PAF" in t or "IAF" in t for t in pk_expanded)


def test_regional_narrative_comparison_sample_disclosure():
    """Validates regional narrative comparison returns honest sample size disclaimers and framing differences."""
    async def _run():
        req = RegionalNarrativeComparisonRequest(
            topic="semiconductor manufacturing ecosystem",
            selected_regions=[RegionalTarget.SOUTH_INDIA, RegionalTarget.NORTH_INDIA],
            collection_limit=5
        )
        res = await regional_social_engine.compare_regional_narratives(req)
        assert res.topic == "semiconductor manufacturing ecosystem"
        assert len(res.regions_compared) == 2
        for report in res.regions_compared:
            assert "Observed in" in report.observed_sentiment_summary
            assert "Limitation:" in report.collection_coverage_notes
            assert report.sample_size >= 0
        assert "do not conflate sample observations with aggregate population sentiment" in res.investigator_advisory

    asyncio.run(_run())


def test_fail_closed_egress_blocking():
    """Validates fail-closed behavior: never fall back to direct network when gateway required."""
    is_ok, msg, status = egress_controller.verify_egress_route(
        route_type=EgressRouteType.REGIONAL_GATEWAY_APPROVED,
        gateway_name="non_existent_gateway_profile",
        fail_closed=True
    )
    assert is_ok is False
    assert status.is_active is False
    assert status.fail_closed is True
    assert "OPSEC_FAIL_CLOSED" in msg
    assert "Direct network fallback is prohibited" in msg


def test_egress_credential_sanitization():
    """Validates that proxy/VPN credentials and bearer tokens are never leaked in logs."""
    dirty_text = "Connecting via https://admin:password='SuperSecretPass123' with token bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyzToken"
    sanitized = egress_controller.sanitize_log_content(dirty_text)
    assert "SuperSecretPass123" not in sanitized
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyzToken" not in sanitized
    assert "[REDACTED_CREDENTIAL]" in sanitized


def test_multimodal_perceptual_dhash():
    """Tests 64-bit difference hash (dHash) and Hamming distance for identical and similar images."""
    img1 = Image.new("RGB", (100, 100), color=(0, 0, 0))
    for x in range(30, 70):
        for y in range(30, 70):
            img1.putpixel((x, y), (255, 255, 255))

    img2 = img1.copy()
    img3 = Image.new("RGB", (100, 100), color=(255, 255, 255))

    h1 = multimodal_engine.calculate_image_dhash(img1)
    h2 = multimodal_engine.calculate_image_dhash(img2)
    h3 = multimodal_engine.calculate_image_dhash(img3)

    assert len(h1) == 16  # 64-bit hex = 16 characters
    assert h1 == h2  # Identical images must have identical dHash

    dist_identical = multimodal_engine.calculate_hamming_distance(h1, h2)
    dist_different = multimodal_engine.calculate_hamming_distance(h1, h3)

    assert dist_identical == 0
    assert dist_different > 0


def test_vapt_scope_enforcement_allowlist_and_ssrf_rejection():
    """Validates VA/PT scope permit authorization gates and rejection of private IPs / cloud metadata."""
    # 1. Cloud metadata IP must be strictly rejected
    res_metadata = vapt_scope_enforcer.validate_scope_authorization(
        target="169.254.169.254",
        requested_impact=ScanImpactLevel.PASSIVE_RECON,
        tenant_id="tenant_alpha"
    )
    assert res_metadata.is_authorized is False
    assert "Blocked special-use/cloud metadata IP" in res_metadata.rejection_reason or "blocked" in res_metadata.rejection_reason.lower()

    # 2. Localhost / Loopback must be strictly rejected
    res_loopback = vapt_scope_enforcer.validate_scope_authorization(
        target="127.0.0.1",
        requested_impact=ScanImpactLevel.PASSIVE_RECON,
        tenant_id="tenant_alpha"
    )
    assert res_loopback.is_authorized is False

    # 3. Active port probe on an unpermitted public target must be rejected
    res_unpermitted = vapt_scope_enforcer.validate_scope_authorization(
        target="93.184.216.34",
        requested_impact=ScanImpactLevel.ACTIVE_PORT_PROBE,
        tenant_id="tenant_alpha"
    )
    assert res_unpermitted.is_authorized is False
    assert "No approved Scope Permit" in res_unpermitted.rejection_reason

    # 4. Register a Scope Permit for the target and verify authorization passes
    permit = ScopePermit(
        permit_id="permit_test_001",
        tenant_id="tenant_alpha",
        authorized_target="93.184.216.34",
        target_type="IP",
        max_impact_level=ScanImpactLevel.ACTIVE_PORT_PROBE,
        approved_by="security-lead@agency.gov",
        valid_until="2027-10-14T00:00:00Z",
        permit_token="sig_test_token_123"
    )
    vapt_scope_enforcer.register_scope_permit(permit)

    res_permitted = vapt_scope_enforcer.validate_scope_authorization(
        target="93.184.216.34",
        requested_impact=ScanImpactLevel.ACTIVE_PORT_PROBE,
        tenant_id="tenant_alpha"
    )
    assert res_permitted.is_authorized is True


def test_vapt_emergency_abort_scan():
    """Validates that scan kill-switch terminates active jobs and logs containment."""
    abort_res = vapt_scope_enforcer.abort_scan(
        job_id="job_nuclei_9921",
        reason="Target entered out-of-bounds production maintenance window"
    )
    assert abort_res["status"] == "ABORTED"
    assert abort_res["job_id"] == "job_nuclei_9921"
    assert "Target entered out-of-bounds" in abort_res["reason"]
