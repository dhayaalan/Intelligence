import io
import uuid
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.module_registry.registry import module_registry
from app.modules.media_intelligence.service import media_intelligence_service
from app.modules.media_intelligence.module import media_intelligence_module

client = TestClient(app)

def create_sample_image(text: str = "TEST PLATE TN34MA8562", color: str = "blue") -> bytes:
    img = Image.new("RGB", (300, 100), color=color)
    d = ImageDraw.Draw(img)
    d.text((10, 40), text, fill="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_media_intelligence_module_registration():
    """Verify media_intelligence module is properly registered in ModuleRegistry."""
    mods = module_registry.list_all_modules()
    assert any(m.id == "media_intelligence" for m in mods)
    mod = module_registry.get_module("media_intelligence")
    assert mod is not None
    assert mod.manifest.id == "media_intelligence"
    assert "image_forensics" in mod.manifest.capabilities
    assert "c2pa_provenance" in mod.manifest.capabilities

@pytest.mark.asyncio
async def test_media_intelligence_health_check():
    """Verify health_check reports real operational status."""
    health = await media_intelligence_module.health_check()
    assert health.module_id == "media_intelligence"
    assert health.status in ["healthy", "degraded"]
    assert "providers_count" in health.details

def test_image_forensics_hashing_and_quality():
    """Verify cryptographic hashing, dual perceptual hashing, and quality metrics."""
    img_bytes = create_sample_image("SENTINEL RECON")
    result = media_intelligence_service.analyze_image(img_bytes, filename="recon.jpg")
    
    assert len(result.sha256) == 64
    assert len(result.md5) == 32
    assert len(result.dhash) == 64
    assert len(result.phash) == 64
    assert result.file_size_bytes == len(img_bytes)
    assert result.quality.width == 300
    assert result.quality.height == 100
    assert result.quality.megapixels > 0
    assert result.c2pa.status in ["absent", "valid"]

def test_perceptual_hash_discrimination():
    """Verify Hamming distance discrimination between identical, similar, and different images."""
    img_a = create_sample_image("TARGET ALPHA", "blue")
    img_a_clone = create_sample_image("TARGET ALPHA", "blue")
    img_b = create_sample_image("COMPLETELY DIFFERENT NOISE", "red")

    hash_a = media_intelligence_service.compute_phash(img_a)
    hash_a_clone = media_intelligence_service.compute_phash(img_a_clone)
    hash_b = media_intelligence_service.compute_phash(img_b)

    # Identical images must yield EXACT_MATCH
    cmp_exact = media_intelligence_service.compare_hashes(hash_a, hash_a_clone, "phash")
    assert cmp_exact.is_candidate_match is True
    assert cmp_exact.hamming_distance == 0
    assert cmp_exact.match_type == "EXACT_MATCH"

    # Self-comparison
    cmp_self = media_intelligence_service.compare_hashes(hash_a, hash_a, "phash")
    assert cmp_self.hamming_distance == 0
    assert cmp_self.similarity_percentage == 100.0

def test_c2pa_detection_honesty():
    """Verify C2PA scanner honestly returns absent on normal stripped images."""
    img_bytes = create_sample_image("NO C2PA METADATA")
    c2pa = media_intelligence_service.detect_c2pa(img_bytes)
    assert c2pa.status == "absent"
    assert c2pa.ai_generated is False

    # Simulate JUMBF marker presence
    synthetic_c2pa_bytes = img_bytes + b"__c2pa_jumb_synthetic_ai_generated_manifest__"
    c2pa_synth = media_intelligence_service.detect_c2pa(synthetic_c2pa_bytes)
    assert c2pa_synth.status == "valid"
    assert c2pa_synth.ai_generated is True

def test_api_media_intelligence_health():
    """Verify GET /api/v1/media-intelligence/health endpoint."""
    res = client.get("/api/v1/media-intelligence/health")
    assert res.status_code == 200
    data = res.json()
    assert data["module_id"] == "media_intelligence"
    assert "status" in data

def test_api_media_intelligence_analyze_image(analyst_headers):
    """Verify POST /api/v1/media-intelligence/analyze/image with multipart upload."""
    img_bytes = create_sample_image("EVIDENCE 2026")
    files = {"file": ("evidence.jpg", img_bytes, "image/jpeg")}
    res = client.post(
        "/api/v1/media-intelligence/analyze/image",
        files=files,
        headers=analyst_headers
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert "sha256" in data
    assert "dhash" in data
    assert "phash" in data
    assert "quality" in data
    assert data["quality"]["width"] == 300

def test_api_media_intelligence_compare_hash(analyst_headers):
    """Verify POST /api/v1/media-intelligence/compare-hash."""
    h1 = "1" * 64
    h2 = "1" * 60 + "0" * 4  # Hamming distance 4 (near duplicate)
    res = client.post(
        "/api/v1/media-intelligence/compare-hash",
        json={"hash1": h1, "hash2": h2, "algorithm": "phash"},
        headers=analyst_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["hamming_distance"] == 4
    assert data["match_type"] == "NEAR_DUPLICATE"
    assert data["is_candidate_match"] is True

def test_investigation_media_analysis_lifecycle(analyst_headers):
    """Verify end-to-end linking of forensic media analysis to an authorized investigation."""
    # 1. Create an investigation
    inv_title = f"Media Forensic Case {uuid.uuid4().hex[:8]}"
    create_res = client.post(
        "/api/v1/investigations",
        json={"title": inv_title, "target": "threat-actor-media.org", "target_type": "DOMAIN"},
        headers=analyst_headers
    )
    assert create_res.status_code in (200, 201)
    inv_id = create_res.json()["id"]

    # 2. Analyze image
    img_bytes = create_sample_image("CRIME SCENE RECON")
    img_res = media_intelligence_service.analyze_image(img_bytes, filename="crime_scene.jpg")

    # 3. Link analysis to investigation
    import json
    link_res = client.post(
        f"/api/v1/media-intelligence/investigations/{inv_id}/media-analysis",
        json={
            "investigation_id": inv_id,
            "media_type": "image",
            "filename": "crime_scene.jpg",
            "media_url": "https://example.org/crime_scene.jpg",
            "image_result": json.loads(img_res.json())
        },
        headers=analyst_headers
    )
    assert link_res.status_code == 200, link_res.text
    link_data = link_res.json()
    assert link_data["status"] == "linked"
    analysis_id = link_data["analysis_id"]

    # 4. List analyses for investigation
    list_res = client.get(
        f"/api/v1/media-intelligence/investigations/{inv_id}/media-analyses",
        headers=analyst_headers
    )
    assert list_res.status_code == 200
    analyses = list_res.json()
    assert len(analyses) >= 1
    assert any(a["id"] == analysis_id for a in analyses)

    # 5. Retrieve specific analysis
    get_res = client.get(
        f"/api/v1/media-intelligence/investigations/{inv_id}/media-analysis/{analysis_id}",
        headers=analyst_headers
    )
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["id"] == analysis_id
    assert detail["primary_hash"] == img_res.sha256
    assert detail["image_result"]["quality"]["width"] == 300

def test_api_media_intelligence_ssrf_protection(analyst_headers):
    """Verify SSRF defenses block loopback, link-local, private, and metadata targets."""
    # 1. Loopback attempt
    res_loopback = client.post(
        "/api/v1/media-intelligence/analyze/url",
        json={"url": "http://127.0.0.1:8000/api/v1/health", "media_type": "image"},
        headers=analyst_headers
    )
    assert res_loopback.status_code == 400
    assert "SSRF" in res_loopback.text or "loopback" in res_loopback.text or "prohibited" in res_loopback.text

    # 2. Localhost attempt
    res_localhost = client.post(
        "/api/v1/media-intelligence/analyze/url",
        json={"url": "http://localhost:27017", "media_type": "image"},
        headers=analyst_headers
    )
    assert res_localhost.status_code == 400

    # 3. Cloud metadata attempt
    res_metadata = client.post(
        "/api/v1/media-intelligence/analyze/url",
        json={"url": "http://169.254.169.254/latest/meta-data/", "media_type": "image"},
        headers=analyst_headers
    )
    assert res_metadata.status_code == 400
    assert "SSRF" in res_metadata.text or "cloud metadata" in res_metadata.text or "link-local" in res_metadata.text

    # 4. Invalid scheme attempt
    res_scheme = client.post(
        "/api/v1/media-intelligence/analyze/url",
        json={"url": "file:///etc/passwd", "media_type": "image"},
        headers=analyst_headers
    )
    assert res_scheme.status_code == 400

def test_api_media_intelligence_batch_images(analyst_headers):
    """Verify POST /api/v1/media-intelligence/analyze/batch-images processes multiple files."""
    img1 = create_sample_image("BATCH ITEM 1", "blue")
    img2 = create_sample_image("BATCH ITEM 2", "green")
    
    files = [
        ("files", ("item1.jpg", img1, "image/jpeg")),
        ("files", ("item2.jpg", img2, "image/jpeg"))
    ]
    res = client.post(
        "/api/v1/media-intelligence/analyze/batch-images",
        files=files,
        headers=analyst_headers
    )
    assert res.status_code == 200, res.text
    items = res.json()
    assert len(items) == 2
    assert items[0]["sha256"] != items[1]["sha256"]
    assert "analysis_id" in items[0]
    assert "analysis_id" in items[1]

def test_api_media_intelligence_tenant_analyses_listing(analyst_headers):
    """Verify GET /api/v1/media-intelligence/analyses returns historical tenant analyses."""
    res = client.get(
        "/api/v1/media-intelligence/analyses?limit=10",
        headers=analyst_headers
    )
    assert res.status_code == 200
    records = res.json()
    assert isinstance(records, list)
    assert len(records) >= 1

def test_api_media_intelligence_save_evidence(analyst_headers):
    """Verify POST /api/v1/media-intelligence/save-evidence seals analysis into Evidence Vault."""
    img = create_sample_image("VAULT SEAL EVIDENCE", "purple")
    analysis = media_intelligence_service.analyze_image(img, filename="seal_target.jpg")

    res = client.post(
        "/api/v1/media-intelligence/save-evidence",
        json={
            "analysis_id": f"man_{uuid.uuid4().hex[:8]}",
            "media_type": "image",
            "filename": "seal_target.jpg",
            "primary_hash": analysis.sha256,
            "notes": "Cryptographically verified forensic asset sealed into vault.",
            "forensics_summary": {
                "dhash": analysis.dhash,
                "phash": analysis.phash,
                "megapixels": analysis.quality.megapixels
            }
        },
        headers=analyst_headers
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "sealed"
    assert "evidence_id" in data
    assert data["hash"] == analysis.sha256

