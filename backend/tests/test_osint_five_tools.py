"""
Test Suite: Five OSINT Providers & Vehicle Intelligence Forensics
Tests SpiderFoot, Maltego, Shodan, theHarvester, Google Dorks,
and Vehicle/ANPR cryptographic forensics.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.module_sdk.provider_adapter import ProviderRequest
from app.module_sdk.models import ModuleHealthStatus
from app.modules.osint.providers.spiderfoot import spiderfoot_provider
from app.modules.osint.providers.theharvester import theharvester_provider, DOMAIN_REGEX
from app.modules.osint.providers.shodan import shodan_provider
from app.modules.osint.providers.google_dork import google_dork_provider
from app.modules.osint.providers.maltego import maltego_provider, map_to_maltego_type, generate_maltego_csv
from app.modules.osint.providers.vehicle_intelligence import lookup_nhtsa_vin, is_vin
from app.modules.camera_evidence.forensics import compute_media_sha256, compute_dhash, extract_exif_metadata
from app.modules.camera_evidence.models import ANPRDetectionRecord, ANPRMatchStatus


# ============================================================================
# 1. theHarvester: Strict Validation & Command Injection Prevention
# ============================================================================

def test_theharvester_domain_validation():
    # Valid domains
    assert DOMAIN_REGEX.match("example.com") is not None
    assert DOMAIN_REGEX.match("sub.domain.org") is not None
    assert DOMAIN_REGEX.match("target-corp.co.uk") is not None

    # Hostile / command injection payloads must fail regex validation
    assert DOMAIN_REGEX.match("example.com; rm -rf /") is None
    assert DOMAIN_REGEX.match("example.com && whoami") is None
    assert DOMAIN_REGEX.match("$(whoami).evil.com") is None
    assert DOMAIN_REGEX.match("`cat /etc/passwd`") is None
    assert DOMAIN_REGEX.match("http://example.com") is None


@pytest.mark.asyncio
async def test_theharvester_hostile_input_rejection():
    # Must reject malicious input cleanly with error
    req = ProviderRequest(query="malicious.target; id", target_type="domain")
    resp = await theharvester_provider.execute(req)
    assert resp.status == "skipped"
    assert "not a valid domain" in resp.error


@pytest.mark.asyncio
async def test_theharvester_valid_domain_execution():
    # Valid domain returns structured result
    req = ProviderRequest(query="example.com", target_type="domain")
    resp = await theharvester_provider.execute(req)
    assert resp.status == "success"
    assert resp.provider_id == "theharvester"
    assert "hosts" in resp.raw_data or "emails" in resp.raw_data


# ============================================================================
# 2. SpiderFoot: Provider Execution & Normalized Findings
# ============================================================================

@pytest.mark.asyncio
async def test_spiderfoot_provider_execution():
    req = ProviderRequest(query="example.com", target_type="domain")
    resp = await spiderfoot_provider.execute(req)
    assert resp.status == "success"
    assert resp.provider_id == "spiderfoot"
    assert "findings" in resp.raw_data
    assert isinstance(resp.raw_data["findings"], list)


@pytest.mark.asyncio
async def test_spiderfoot_health_check():
    health = await spiderfoot_provider.health_check()
    assert health.status in (ModuleHealthStatus.HEALTHY, ModuleHealthStatus.DEGRADED)
    assert len(health.message) > 0


# ============================================================================
# 3. Shodan: Dual Mode (InternetDB & Host API)
# ============================================================================

@pytest.mark.asyncio
async def test_shodan_keyless_internetdb():
    req = ProviderRequest(query="1.1.1.1", target_type="ip")
    resp = await shodan_provider.execute(req)
    assert resp.status == "success"
    assert resp.provider_id == "shodan"
    assert resp.raw_data["ip"] == "1.1.1.1"
    assert "ports" in resp.raw_data


@pytest.mark.asyncio
async def test_shodan_invalid_ip_rejection():
    req = ProviderRequest(query="not_a_valid_ip_or_unresolvable_xyz12345", target_type="ip")
    resp = await shodan_provider.execute(req)
    assert resp.status == "skipped"
    assert "could not be resolved" in resp.error


# ============================================================================
# 4. Google Dorks: Query Compilation & Execution
# ============================================================================

@pytest.mark.asyncio
async def test_google_dork_generation():
    req = ProviderRequest(query="acme-corp.com", target_type="domain")
    resp = await google_dork_provider.execute(req)
    assert resp.status == "success"
    assert resp.provider_id == "google_dork"
    assert "dorks" in resp.raw_data
    dorks = resp.raw_data["dorks"]
    assert len(dorks) >= 5
    has_site_operator = any("site:acme-corp.com" in d["query"] for d in dorks)
    assert has_site_operator is True
    assert all("browser_search_url" in d for d in dorks)


# ============================================================================
# 5. Maltego: RFC-4180 CSV Export & Entity Mapping
# ============================================================================

def test_maltego_entity_mapping():
    assert map_to_maltego_type("PERSON") == "maltego.Person"
    assert map_to_maltego_type("DOMAIN") == "maltego.Domain"
    assert map_to_maltego_type("IP") == "maltego.IPv4Address"
    assert map_to_maltego_type("EMAIL") == "maltego.EmailAddress"
    assert map_to_maltego_type("VEHICLE") == "maltego.Device"


def test_maltego_csv_generation():
    entities = [
        {"id": "e1", "type": "PERSON", "value": "John Doe", "confidence": 0.95},
        {"id": "e2", "type": "DOMAIN", "value": "target-corp.com", "confidence": 0.90},
    ]
    relationships = [
        {
            "id": "r1",
            "source_id": "e1",
            "target_id": "e2",
            "type": "OWNS",
            "confidence": 0.88
        }
    ]
    csv_out = generate_maltego_csv(entities, relationships)
    assert isinstance(csv_out, str)
    lines = csv_out.strip().split("\r\n") if "\r\n" in csv_out else csv_out.strip().split("\n")
    # Header check
    assert "Source Maltego Type" in lines[0]
    assert "Target Maltego Type" in lines[0]
    # Row check
    assert "maltego.Person" in lines[1]
    assert "maltego.Domain" in lines[1]
    assert "OWNS" in lines[1]


# ============================================================================
# 6. Vehicle Intelligence & NHTSA VIN Lookup
# ============================================================================

def test_vin_syntax_validation():
    # Valid 17-character VIN syntax (no I, O, Q)
    assert is_vin("1HGCR2F83HA000000") is True
    # Invalid lengths or forbidden characters
    assert is_vin("1HGCR2F83HA00000I") is False  # Contains 'I'
    assert is_vin("SHORTVIN123") is False


def test_nhtsa_vin_decoder():
    # Test keyless NHTSA API decoding for a standard Honda VIN
    test_vin = "1HGCR2F83HA000000"
    res = lookup_nhtsa_vin(test_vin)
    assert res is not None
    assert res["vin"] == test_vin
    assert "valid" in res
    assert "source" in res
    if res["valid"]:
        assert res.get("make") is not None or res.get("manufacturer") is not None


# ============================================================================
# 7. Media Cryptographic Forensics (SHA-256 & dHash)
# ============================================================================

def test_media_cryptographic_hashing():
    dummy_data = b"SENTIAL_MEDIA_TEST_PAYLOAD_IMAGE_FORENSICS_2026"
    sha = compute_media_sha256(dummy_data)
    assert len(sha) == 64
    assert all(c in "0123456789abcdef" for c in sha)


def test_dhash_computation():
    from PIL import Image
    import io

    img = Image.new("L", (9, 8), color=128)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    h = compute_dhash(buf.getvalue())
    assert len(h) == 64
    assert all(c in "01" for c in h)


# ============================================================================
# 8. ANPR Temporal Tracking & Confidence Separation
# ============================================================================

def test_anpr_detection_record_fields():
    rec = ANPRDetectionRecord(
        detection_id="det_test_01",
        camera_id="cam_001",
        camera_operator="Traffic Authority",
        camera_location_name="Intersection 4th & Main",
        video_reference="footage_001.mp4",
        frame_number=156,
        timecode_seconds=5.2,
        raw_ocr_text="TS 07 EA 1234",
        normalized_candidate_plate="TS07EA1234",
        target_plate="TS07EA1234",
        detection_confidence=0.96,
        ocr_confidence=0.91,
        confidence=0.935,
        match_status=ANPRMatchStatus.CANDIDATE_MATCH,
        temporal_track_id="trk_89b2c3d4",
        frame_count_tracked=5,
        temporal_timestamps=[4.8, 5.0, 5.2],
        media_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )

    assert rec.detection_confidence == 0.96
    assert rec.ocr_confidence == 0.91
    assert rec.temporal_track_id == "trk_89b2c3d4"
    assert rec.frame_count_tracked == 5
    assert len(rec.temporal_timestamps) == 3
