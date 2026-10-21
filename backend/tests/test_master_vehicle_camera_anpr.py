"""
Comprehensive End-to-End Tests for Master Vehicle Registration,
Public Camera Catalog, Video Ingestion, ANPR Pipeline, and Human Review.
"""

import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.modules.osint.providers.vehicle_intelligence import (
    VehicleRegistrationProvider, OfficialVahanRegistryClient
)
from app.modules.camera_evidence.models import (
    CameraSourceRecord, CameraFeedType, ANPRMatchStatus, ANPRDetectionRecord
)
from app.modules.camera_evidence.catalog import camera_catalog_service
from app.modules.camera_evidence.anpr_service import anpr_service
from app.modules.geo_intelligence.service import geo_intelligence_service
from app.modules.geo_intelligence.models import TimeFilterRange

client = TestClient(app)


# analyst_headers is provided by conftest.py fixture:
# sub: usr_analyst, tenant_id: tenant_acme, role: ANALYST


# ==============================================================================
# SECTION A: VEHICLE REGISTRATION TESTS
# ==============================================================================

def test_vehicle_plate_syntax_parsing_and_attribution():
    provider = VehicleRegistrationProvider()
    res = provider.execute_lookup("TN34MA8562")

    assert res["status"] == "SUCCESS"
    assert res["plate_number"] == "TN34MA8562"
    assert res["jurisdiction"] == "IN"
    assert res["live_registry_status"] == "CONFIG_REQUIRED"
    assert res["official_registry_executed"] is False

    # Check primary vehicle entity
    v_ents = [e for e in res["entities"] if str(e.type).lower().endswith("vehicle")]
    assert len(v_ents) == 1
    v_meta = v_ents[0].metadata
    assert v_meta["country"] == "India"
    assert v_meta["state"] == "Tamil Nadu"
    assert "Namakkal" in v_meta["rto_office"]
    assert v_meta["jurisdiction_attribution_mode"] == "FORMAT_PREFIX_INFERENCE"
    assert v_meta["live_registration_record"] == "CONFIG_REQUIRED"
    assert v_meta["registered_ownership"] == "NOT_AVAILABLE_WITHOUT_AUTHORIZED_CREDENTIAL"


def test_vehicle_unconfigured_registry_client():
    client = OfficialVahanRegistryClient(api_key=None, client_id=None)
    assert client.is_configured() is False


# ==============================================================================
# SECTION B: PUBLIC CAMERA CATALOG TESTS
# ==============================================================================

def test_camera_catalog_sources_and_metadata(analyst_headers):
    resp = client.get("/api/v1/camera-evidence/catalog", headers=analyst_headers)
    assert resp.status_code == 200
    catalog = resp.json()
    assert len(catalog) >= 5

    # Check UK TfL JamCams
    tfl = next((c for c in catalog if c["source_id"] == "cam_tfl_jamcams"), None)
    assert tfl is not None
    assert tfl["operator"] == "Transport for London (TfL)"
    assert tfl["feed_type"] == "SNAPSHOT_SERIES"
    assert "Open Government Licence" in tfl["licensing_status"]
    assert tfl["is_public_catalog"] is True

    # Check India NHAI restricted feed
    nhai = next((c for c in catalog if c["source_id"] == "cam_in_nhai_tms"), None)
    assert nhai is not None
    assert nhai["availability"] == "CONFIGURATION_REQUIRED"
    assert "Authorized" in nhai["auth_requirements"] or "Restricted" in nhai["licensing_status"]


def test_camera_catalog_filtering(analyst_headers):
    resp_uk = client.get("/api/v1/camera-evidence/catalog?jurisdiction=UK", headers=analyst_headers)
    assert resp_uk.status_code == 200
    uk_cams = resp_uk.json()
    assert all(c["metadata"].get("jurisdiction") == "UK" or "UK" in c["geographic_coverage"] for c in uk_cams)


# ==============================================================================
# SECTION C: VIDEO INGESTION, ANPR DECODING, AND OCR TESTS
# ==============================================================================

def test_synthetic_test_clip_generation_and_anpr_processing():
    test_clip_path = "/tmp/test_anpr_synthetic_TN34MA8562.mp4"
    generated_path = anpr_service.create_synthetic_authorized_test_clip(test_clip_path, "TN34MA8562")
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 1000

    cam = camera_catalog_service.get_source("cam_tfl_jamcams")
    assert cam is not None

    detections = anpr_service.process_video_footage(
        video_path=generated_path,
        target_plate="TN34MA8562",
        camera=cam,
        investigation_id="inv_test_e2e_01",
        tenant_id="tenant_forensic"
    )

    assert len(detections) > 0
    det = detections[0]
    assert det.target_plate == "TN34MA8562"
    assert det.match_status in [ANPRMatchStatus.CANDIDATE_MATCH, ANPRMatchStatus.POSSIBLE_MATCH]
    assert det.confidence >= 0.70
    assert det.frame_preview_data.startswith("data:image/jpeg;base64,")
    assert det.plate_crop_data.startswith("data:image/jpeg;base64,")
    assert det.timecode_seconds >= 0.0
    assert det.detector_version.startswith("OpenCV")


# ==============================================================================
# SECTION D: HUMAN REVIEW AND GEOSPATIAL OBSERVATION INTEGRATION
# ==============================================================================

def test_anpr_human_review_workflow_and_geo_persistence(analyst_headers):
    # Process test clip via API
    resp = client.post(
        "/api/v1/camera-evidence/process-anpr",
        json={
            "source_id": "cam_tfl_jamcams",
            "target_plate": "TN34MA8562",
            "investigation_id": "inv_test_geo_link",
            "sample_interval_seconds": 1.0,
            "max_duration_seconds": 10.0
        },
        headers=analyst_headers
    )
    assert resp.status_code == 200
    detections = resp.json()
    assert len(detections) > 0
    det_id = detections[0]["detection_id"]

    # Submit human confirmation
    review_resp = client.post(
        f"/api/v1/camera-evidence/detections/{det_id}/review",
        json={
            "decision": "CONFIRM",
            "notes": "Analyst verified plate characters against camera crop."
        },
        headers=analyst_headers
    )
    assert review_resp.status_code == 200
    reviewed = review_resp.json()
    assert reviewed["match_status"] == "HUMAN_CONFIRMED"
    assert reviewed["confidence"] == 1.0
    assert reviewed["human_reviewer_id"] == "usr_analyst"

    from app.modules.geo_intelligence.models import GeoFilterParams
    # Verify that a discrete observation was injected into Geo Intelligence
    observations = geo_intelligence_service.search_observations(
        query="TN34MA8562",
        filters=GeoFilterParams(),
        tenant_id="tenant_acme"
    )
    matching_obs = [o for o in observations if o.associated_entity_value == "TN34MA8562"]
    assert len(matching_obs) >= 1
    obs = matching_obs[0]
    assert obs.observation_type.value == "DIRECTLY_OBSERVED"
    assert obs.relationship_to_entity == "SIGHTED_AT"
    assert obs.latitude is not None
    assert obs.longitude is not None
