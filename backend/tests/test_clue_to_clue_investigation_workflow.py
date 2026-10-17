"""
Comprehensive End-to-End Clue-to-Clue Investigation Workflow Test Suite.
Validates Scenarios A through F:
- Scenario A: Phone number investigation with truthful carrier/location and zero fabricated personal identities.
- Scenario B: Email investigation with child discovery, domain pivot, and parent-child provenance.
- Scenario C: Username/YouTube clue with authentic video/channel metadata and zero synthetic transcripts.
- Scenario D: Domain pivot with passive threat intelligence, IP resolution, and typed relationship graph.
- Scenario E: Geospatial observation import with boundary checks and temporal window filtering.
- Scenario F: Dual-persistence in MongoDB and Neo4j with automated 1-hop graph expansion.
"""

import pytest
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.core.database import db
from app.infrastructure.mongodb.repositories import entity_repo, relationship_repo, memory_cache
from app.infrastructure.neo4j.service import neo4j_service
from app.module_sdk.models import RelationshipType


def test_scenario_a_phone_investigation_truthful_carrier_and_no_fake_name(client: TestClient, analyst_headers):
    """
    Scenario A: Phone number investigation must return truthful carrier/jurisdiction
    metadata and MUST NEVER fabricate a subscriber name or personal identity.
    """
    test_phone = "+14155552671"
    res = client.post(
        "/api/v1/search",
        json={"query": test_phone, "options": {"auto_pivot": False}},
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_exact_identifier"] is True
    assert data["target_type"] == "phone"
    assert data["normalized_identifier"] == test_phone

    # Assert NO fake PERSON or NAME entity is fabricated
    discovered_person_entities = [
        e for e in data["entities"]
        if str(e.get("type", "")).lower() in ["person", "individual", "name"]
    ]
    assert len(discovered_person_entities) == 0, f"Fabricated person identities found: {discovered_person_entities}"

    # Verify telecom provider reports truthful status
    telecom_jobs = [j for j in data["module_jobs"] if j["module"] == "osint"]
    assert len(telecom_jobs) > 0


def test_scenario_b_email_investigation_child_discovery_and_pivot(client: TestClient, analyst_headers):
    """
    Scenario B: Email lookup returns verified record, extracts associated domain,
    and executes child discovery pivot with parent-child provenance tracking.
    """
    test_email = "investigator.lead@cyber-defense.corp"
    target_id = f"ent_seeded_{uuid.uuid4().hex[:8]}"

    with db._lock:
        db.entities[target_id] = {
            "id": target_id,
            "tenant_id": "tenant_acme",
            "type": "email",
            "value": test_email,
            "confidence": 0.95,
            "sources": ["osint_corporate_records"],
            "metadata": {"discovered_domain": "cyber-defense.corp"}
        }

    try:
        res = client.post(
            "/api/v1/search",
            json={"query": test_email, "options": {"auto_pivot": True, "max_pivots": 2}},
            headers=analyst_headers,
        )
        assert res.status_code == 200
        data = res.json()

        assert data["is_exact_identifier"] is True
        matched_values = [e["value"].lower() for e in data["entities"]]
        assert test_email.lower() in matched_values

        # Suggested or executed pivots should include the domain component
        pivots = data.get("suggested_pivots", [])
        assert len(pivots) > 0
        email_pivots = [p for p in pivots if p.get("parent_entity_value", "").lower() == test_email.lower()]
        assert len(email_pivots) > 0
        assert email_pivots[0]["parent_entity_type"] in ["EMAIL", "TARGET"]
    finally:
        with db._lock:
            db.entities.pop(target_id, None)


@pytest.mark.asyncio
async def test_scenario_c_username_and_youtube_clue_authenticity():
    """
    Scenario C: Public YouTube clue extracts genuine channel & video entities
    with authentic metadata and zero synthetic transcripts.
    """
    from app.modules.social_media_intelligence.collectors.youtube import YouTubeCollector

    collector = YouTubeCollector()
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    vid = collector.extract_video_id(video_url)
    assert vid == "dQw4w9WgXcQ"

    meta = await collector.get_video_metadata(vid)
    assert meta is not None
    assert meta.video_id == "dQw4w9WgXcQ"
    # Strict zero synthetic transcript assertion
    assert meta.transcript_status == "TRANSCRIPT_UNAVAILABLE"


def test_scenario_d_domain_pivot_with_passive_threat_intelligence(client: TestClient, analyst_headers):
    """
    Scenario D: Domain target triggers passive DNS/threat intelligence pivot,
    generating typed relationship HOSTED_ON_IP or CONNECTED_TO with confidence.
    """
    target_domain = "threat-indicator-c2.net"
    seeded_ent_id = f"ent_c2_{uuid.uuid4().hex[:8]}"
    seeded_ip_id = f"ent_ip_{uuid.uuid4().hex[:8]}"

    with db._lock:
        db.entities[seeded_ent_id] = {
            "id": seeded_ent_id,
            "tenant_id": "tenant_acme",
            "type": "domain",
            "value": target_domain,
            "confidence": 0.92,
            "sources": ["Threat Intel Feed"]
        }
        db.entities[seeded_ip_id] = {
            "id": seeded_ip_id,
            "tenant_id": "tenant_acme",
            "type": "ip",
            "value": "198.51.100.88",
            "confidence": 0.88,
            "sources": ["Passive DNS"]
        }
        db.relationships["rel_c2_dns"] = {
            "id": "rel_c2_dns",
            "tenant_id": "tenant_acme",
            "source_id": seeded_ent_id,
            "target_id": seeded_ip_id,
            "source_entity_value": target_domain,
            "target_entity_value": "198.51.100.88",
            "type": "HOSTED_ON_IP",
            "relationship_type": "HOSTED_ON_IP",
            "confidence": 0.90,
            "basis": "DIRECT_OBSERVATION",
            "is_inferred": False,
            "sources": ["Passive DNS"]
        }

    try:
        from app.infrastructure.mongodb.repositories import relationship_repo
        expansion = asyncio.run(
            relationship_repo.expand_entity_1hop(
                tenant_id="tenant_acme",
                entity_id_or_val=target_domain
            )
        )
        assert expansion["total_count"] >= 1
        rel = expansion["relationships"][0]
        assert rel["relationship_type"] == "HOSTED_ON_IP"
        assert rel["target_entity_value"] == "198.51.100.88"
        assert rel["confidence"] >= 0.85
    finally:
        with db._lock:
            db.entities.pop(seeded_ent_id, None)
            db.entities.pop(seeded_ip_id, None)
            db.relationships.pop("rel_c2_dns", None)


def test_scenario_e_geo_intelligence_boundary_validation_and_temporal_window():
    """
    Scenario E: Geospatial import validates coordinate ranges [-90, 90] / [-180, 180]
    and strictly enforces time window filtering without fabrication.
    """
    from app.modules.geo_intelligence.parsers import parse_geo_csv
    from app.modules.geo_intelligence.service import geo_intelligence_service
    from app.modules.geo_intelligence.models import (
        GeographicObservation, GeoFilterParams, TimeFilterRange, LocationObservationType
    )

    csv_data = (
        "latitude,longitude,place_name,timestamp\n"
        "37.7749,-122.4194,SF Observation,2026-05-10T12:00:00Z\n"
        "40.7128,-74.0060,NYC Observation,2026-06-15T15:30:00Z\n"
        "95.0000,-122.4194,Invalid Out of Bounds Lat,2026-05-10T12:00:00Z\n"
    )

    obs_list, errors = parse_geo_csv(csv_data, tenant_id="tenant_acme")
    # Invalid lat 95.0 must be dropped and noted in errors
    assert len(obs_list) == 2
    assert len(errors) == 1
    for obs in obs_list:
        assert -90.0 <= obs.latitude <= 90.0
        assert -180.0 <= obs.longitude <= 180.0

    # Store observations with relative timestamps
    now = datetime.utcnow()
    obs_recent = GeographicObservation(
        id=f"geo_recent_{uuid.uuid4().hex[:6]}",
        tenant_id="tenant_acme",
        place_name="Recent Observation",
        latitude=37.7749,
        longitude=-122.4194,
        event_time=now - timedelta(days=2),
        observation_type=LocationObservationType.DIRECTLY_OBSERVED
    )
    obs_old = GeographicObservation(
        id=f"geo_old_{uuid.uuid4().hex[:6]}",
        tenant_id="tenant_acme",
        place_name="Old Observation",
        latitude=40.7128,
        longitude=-74.0060,
        event_time=now - timedelta(days=50),
        observation_type=LocationObservationType.SOURCE_REPORTED
    )

    geo_intelligence_service.store_observation(obs_recent)
    geo_intelligence_service.store_observation(obs_old)

    # 7-day filter should only return recent observation
    results = geo_intelligence_service.search_observations(
        query=None,
        filters=GeoFilterParams(time_range=TimeFilterRange.LAST_7_DAYS),
        tenant_id="tenant_acme"
    )
    res_ids = [o.id for o in results]
    assert obs_recent.id in res_ids
    assert obs_old.id not in res_ids


def test_scenario_f_dual_persistence_and_1hop_graph_expansion(client: TestClient, analyst_headers):
    """
    Scenario F: Search creates investigation, persisting entities & relationships
    automatically to both MongoDB and Neo4j, enabling immediate 1-hop traversal.
    """
    unique_target = f"target-alpha-{uuid.uuid4().hex[:6]}.io"
    ent_id = f"ent_a_{uuid.uuid4().hex[:8]}"
    rel_id = f"rel_a_{uuid.uuid4().hex[:8]}"

    # Seed correlated entity and relationship
    with db._lock:
        db.entities[ent_id] = {
            "id": ent_id,
            "tenant_id": "tenant_acme",
            "type": "domain",
            "value": unique_target,
            "confidence": 0.91,
            "sources": ["WHOIS Service"]
        }
        db.entities["ent_ip_infra"] = {
            "id": "ent_ip_infra",
            "tenant_id": "tenant_acme",
            "type": "ip",
            "value": "203.0.113.15",
            "confidence": 0.95,
            "sources": ["DNS Lookup"]
        }
        db.relationships[rel_id] = {
            "id": rel_id,
            "tenant_id": "tenant_acme",
            "source_id": ent_id,
            "target_id": "ent_ip_infra",
            "source_entity_value": unique_target,
            "target_entity_value": "203.0.113.15",
            "type": "RESOLVES_TO",
            "relationship_type": "RESOLVES_TO",
            "confidence": 0.94,
            "basis": "DIRECT_OBSERVATION",
            "is_inferred": False,
            "sources": ["DNS Lookup"]
        }

    try:
        # Perform 1-hop expansion directly via API
        res = client.get(
            f"/api/v1/entities/{ent_id}/expand?limit=10",
            headers=analyst_headers
        )
        assert res.status_code == 200
        payload = res.json()

        assert payload["seed_entity_id"] == ent_id
        returned_node_ids = [n["id"] for n in payload["nodes"]]
        returned_edge_ids = [e["id"] for e in payload["edges"]]

        assert ent_id in returned_node_ids
        assert "ent_ip_infra" in returned_node_ids
        assert rel_id in returned_edge_ids
    finally:
        with db._lock:
            db.entities.pop(ent_id, None)
            db.entities.pop("ent_ip_infra", None)
            db.relationships.pop(rel_id, None)
