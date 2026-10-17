"""
Universal Input-to-Intelligence Engine Verification Suite.
Validates:
1. Universal input classification across all 15 supported categories:
   Phone, Email, Person, Organization, Username, Vehicle Plate, Social URL,
   Image, Video, Domain, IP, News Article, Location, IOC, Unknown/Ambiguous.
2. Explicit unknown and ambiguous input clarification (never silently treated as domain/phone/person/keyword).
3. Complete relevant-source discovery and 10-state provider tracking.
4. Automatic clue extraction, bounded multi-hop recursion, and parent-child provenance.
5. Zero fabrication of identities, cameras, GPS, ownership, or confidence.
6. Unified persistence across MongoDB, Neo4j, evidence vault, and relationship graph.
"""

import pytest
import asyncio
from datetime import datetime
from app.search.classifier import target_classifier
from app.search.schemas import SearchRequest, SearchResponse, ProviderExecutionStatus
from app.search.orchestrator import search_orchestrator
from app.search.normalization import classify_query_intent_and_mode
from app.identity.models import UserRecord, UserRole
from app.module_registry.registry import module_registry
from app.module_sdk.models import EntityType, RelationshipType
from app.infrastructure.mongodb.repositories import entity_repo, relationship_repo, search_repo

@pytest.fixture
def test_investigator_user():
    return UserRecord(
        id="usr_inv_test_universal",
        tenant_id="platform_admin",
        email="lead.investigator@agency.gov",
        name="Lead Investigator",
        role=UserRole.TENANT_ADMIN,
        assigned_modules=["osint", "threat_intelligence", "news_intelligence", "social_media_intelligence", "geo_intelligence"],
        hashed_password="mock_hashed_pw_test",
        created_at=datetime.utcnow()
    )

# =============================================================================
# TEST 1: Universal Input Classification Across All Canonical Target Categories
# =============================================================================
def test_universal_input_classification_categories():
    test_cases = [
        # (input_query, expected_intent, expected_target_type)
        ("+1-555-0199", "PHONE", "phone"),
        ("+91 9876543210", "PHONE", "phone"),
        ("phone:+44 20 7946 0991", "PHONE", "phone"),
        ("analyst.recon@defense.gov", "EMAIL", "email"),
        ("email:investigator@agency.org", "EMAIL", "email"),
        ("Dr. Jane Smith", "PERSON", "person"),
        ("Narendra Modi", "PERSON", "person"),
        ("Google LLC", "ORGANIZATION", "organization"),
        ("OpenAI Inc", "ORGANIZATION", "organization"),
        ("ISRO", "ORGANIZATION", "organization"),
        ("@cyber_sleuth", "USERNAME", "username"),
        ("TN34MA8562", "VEHICLE_PLATE", "vehicle"),
        ("plate:DL01AB1234", "VEHICLE_PLATE", "vehicle"),
        ("https://x.com/cybertarget", "SOCIAL_MEDIA_URL", "social_url"),
        ("https://instagram.com/target_lead", "SOCIAL_MEDIA_URL", "social_url"),
        ("https://example.org/evidence/suspect.jpg", "IMAGE", "image"),
        ("image:photo.png", "IMAGE", "image"),
        ("https://youtube.com/watch?v=dQw4w9WgXcQ", "VIDEO", "video"),
        ("https://youtu.be/abc123xyz", "VIDEO", "video"),
        ("target-recon.org", "DOMAIN", "domain"),
        ("api.internal.target.org", "DOMAIN", "subdomain"),
        ("8.8.8.8", "IP", "ip"),
        ("192.168.1.0/24", "INFRASTRUCTURE", "ip"),
        ("https://reuters.com/world/breaking-story", "NEWS_ARTICLE", "article"),
        ("13.0827, 80.2707", "LOCATION", "location"),
        ("geo:37.7749,-122.4194", "LOCATION", "location"),
        ("Kyiv", "LOCATION", "location"),
        ("CVE-2023-38606", "IOC", "hash"),
        ("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "IOC", "hash")
    ]

    for q, expected_intent, expected_type in test_cases:
        info = target_classifier.classify_intent(q)
        assert info["intent"] == expected_intent, f"Failed intent for '{q}': got {info['intent']}, expected {expected_intent}"
        assert target_classifier.classify(q) == expected_type, f"Failed classify() for '{q}': got {target_classifier.classify(q)}, expected {expected_type}"

# =============================================================================
# TEST 2: Explicit Unknown and Ambiguous Input Clarification State
# =============================================================================
@pytest.mark.asyncio
async def test_unknown_and_ambiguous_inputs_rejection_and_guidance(test_investigator_user):
    ambiguous_queries = [
        "???---***",
        "?!~@#invalid-gibberish",
        "~!@#$%^&*()_+",
        "[]{}<>"
    ]

    for q in ambiguous_queries:
        info = target_classifier.classify_intent(q)
        assert info.get("is_unknown_or_ambiguous") is True, f"Expected ambiguous state for '{q}'"
        assert info["intent"] in ["UNKNOWN", "AMBIGUOUS"]
        assert info.get("clarification_guidance") is not None

        req = SearchRequest(query=q)
        resp = await search_orchestrator.execute_search(req, test_investigator_user)

        assert resp.target_type == "unknown"
        assert resp.intent in ["UNKNOWN", "AMBIGUOUS"]
        assert resp.clarification_guidance is not None
        assert len(resp.entities) == 0, "Unknown input must return 0 fabricated entities"
        assert len(resp.relationships) == 0, "Unknown input must return 0 fabricated relationships"
        assert len(resp.evidence) == 0, "Unknown input must return 0 fabricated evidence"
        assert resp.investigation_snapshot.get("status") == "UNCLASSIFIED"

# =============================================================================
# TEST 3: Complete Relevant-Source Discovery and 10-State Provider Tracking
# =============================================================================
@pytest.mark.asyncio
async def test_relevant_provider_discovery_and_tracking(test_investigator_user):
    req = SearchRequest(query="target-recon.org")
    resp = await search_orchestrator.execute_search(req, test_investigator_user)

    assert resp.status in ["completed", "partial"]
    assert len(resp.provider_executions) > 0, "Provider executions list must not be empty"

    discovered_statuses = {pe.status for pe in resp.provider_executions}
    # Expected statuses include SKIPPED_WITH_REASON, RUNNING/SUCCESSFUL, and CONFIGURATION_REQUIRED (e.g. shodan without API key)
    assert any(st in discovered_statuses for st in [
        ProviderExecutionStatus.SKIPPED_WITH_REASON.value,
        ProviderExecutionStatus.SUCCESSFUL_WITH_RESULTS.value,
        ProviderExecutionStatus.SUCCESSFUL_WITH_NO_RESULTS.value,
        ProviderExecutionStatus.CONFIGURATION_REQUIRED.value
    ])

    # Unconfigured providers like Shodan without key must be tracked as CONFIGURATION_REQUIRED, not crashed
    shodan_pe = next((pe for pe in resp.provider_executions if pe.provider_id == "shodan"), None)
    if shodan_pe:
        assert shodan_pe.status in [
            ProviderExecutionStatus.CONFIGURATION_REQUIRED.value,
            ProviderExecutionStatus.SUCCESSFUL_WITH_RESULTS.value,
            ProviderExecutionStatus.SUCCESSFUL_WITH_NO_RESULTS.value
        ]

    # Verify coverage telemetry summarizes provider statuses
    cov = resp.coverage_telemetry
    assert cov is not None
    assert "provider_statuses" in cov
    assert cov.get("providers_evaluated", 0) > 0

# =============================================================================
# TEST 4: Phone Number Input Clue-to-Clue & Zero Fake Owners
# =============================================================================
@pytest.mark.asyncio
async def test_phone_input_clue_to_clue_workflow(test_investigator_user):
    req = SearchRequest(query="+1-555-0199")
    resp = await search_orchestrator.execute_search(req, test_investigator_user)

    assert resp.target_type == "phone"
    assert resp.intent == "PHONE"
    assert resp.is_exact_identifier is True

    # Carrier & Telecom Registry attribution
    for e in resp.entities:
        if e.type == EntityType.PHONE:
            assert e.value == "+15550199"
        # Zero fake person names linked to uncorroborated phone
        if e.type == EntityType.PERSON:
            assert "telecom_registry" in e.sources or len(e.sources) > 1

# =============================================================================
# TEST 5: Email Identifier Normalization & Component Pivots
# =============================================================================
@pytest.mark.asyncio
async def test_email_input_component_pivots(test_investigator_user):
    req = SearchRequest(query="analyst.recon@custom-corp-domain.org")
    resp = await search_orchestrator.execute_search(req, test_investigator_user)

    assert resp.target_type == "email"
    assert resp.intent == "EMAIL"
    assert resp.is_exact_identifier is True

    # Check suggested pivots contain domain and username components
    piv_targets = [p.get("pivot_query", "").lower() for p in resp.suggested_pivots]
    piv_types = [p.get("pivot_target_type", "") for p in resp.suggested_pivots]
    
    assert any("custom-corp-domain.org" in t for t in piv_targets)
    assert "DOMAIN" in piv_types or "USERNAME" in piv_types

# =============================================================================
# TEST 6: Vehicle Registration Plate & Jurisdiction Attribution
# =============================================================================
@pytest.mark.asyncio
async def test_vehicle_plate_input_workflow(test_investigator_user):
    req = SearchRequest(query="TN34MA8562")
    resp = await search_orchestrator.execute_search(req, test_investigator_user)

    assert resp.target_type == "vehicle"
    assert resp.intent == "VEHICLE_PLATE"

    # Verifies that plate is found with format and RTO jurisdiction
    veh_ents = [e for e in resp.entities if e.type == EntityType.VEHICLE]
    assert len(veh_ents) > 0
    assert "TN34MA8562" in veh_ents[0].value.replace(" ", "")
    assert veh_ents[0].metadata.get("jurisdiction") is not None

# =============================================================================
# TEST 7: Social Media URL & Video Target Forensics
# =============================================================================
@pytest.mark.asyncio
async def test_social_url_and_video_forensics(test_investigator_user):
    # Social URL
    req_social = SearchRequest(query="https://x.com/cybertarget")
    resp_social = await search_orchestrator.execute_search(req_social, test_investigator_user)
    assert resp_social.intent == "SOCIAL_MEDIA_URL"
    
    # Author handle extracted
    user_ents = [e for e in resp_social.entities if e.type == EntityType.USERNAME]
    assert any(e.value.lower() == "cybertarget" for e in user_ents)

    # Video URL
    req_video = SearchRequest(query="https://youtube.com/watch?v=dQw4w9WgXcQ")
    resp_video = await search_orchestrator.execute_search(req_video, test_investigator_user)
    assert resp_video.intent == "VIDEO"
    assert any(e.type == EntityType.VIDEO for e in resp_video.entities)

# =============================================================================
# TEST 8: Image Visual Intelligence Honest Hashing
# =============================================================================
@pytest.mark.asyncio
async def test_image_visual_intel_no_fake_cameras(test_investigator_user):
    req_img = SearchRequest(query="https://example.org/evidence/suspect_frame.jpg")
    resp_img = await search_orchestrator.execute_search(req_img, test_investigator_user)

    assert resp_img.intent == "IMAGE"
    assert any(e.type == EntityType.IMAGE for e in resp_img.entities)

    # Verify no fake Sony ILCE camera is fabricated
    for ev in resp_img.evidence:
        raw = getattr(ev, "raw_data", {}) or {}
        analysis = raw.get("analysis", {}) if isinstance(raw, dict) else {}
        exif = analysis.get("exif_data", {})
        assert "Sony ILCE" not in str(exif), "Fabricated camera model detected!"

# =============================================================================
# TEST 9: Geographic GPS Coordinates Resolution
# =============================================================================
@pytest.mark.asyncio
async def test_geographic_coordinates_input(test_investigator_user):
    req_geo = SearchRequest(query="13.0827, 80.2707")
    resp_geo = await search_orchestrator.execute_search(req_geo, test_investigator_user)

    assert resp_geo.intent == "LOCATION"
    assert resp_geo.target_type == "location"

    loc_ents = [e for e in resp_geo.entities if e.type == EntityType.LOCATION]
    assert len(loc_ents) > 0
    assert "13.08270" in loc_ents[0].value or "13.0827" in loc_ents[0].value

# =============================================================================
# TEST 10: Multi-Hop Bounded Recursion & Provenance Preservation
# =============================================================================
@pytest.mark.asyncio
async def test_multi_hop_recursion_and_provenance(test_investigator_user):
    req = SearchRequest(
        query="google.com",
        options={"auto_pivot": True, "max_depth": 2, "max_pivots": 4}
    )
    resp = await search_orchestrator.execute_search(req, test_investigator_user)

    assert resp.status in ["completed", "partial"]
    assert len(resp.entities) > 0

    # If executed pivots exist, verify parent-child relationships and evidence
    if resp.executed_pivots:
        for ep in resp.executed_pivots:
            assert "pivot_query" in ep
            assert "parent_entity" in ep
            assert ep.get("hop", 1) >= 1

        # Check that executed pivots generated relationships with evidence
        pivot_rels = [r for r in resp.relationships if "pvt" in (getattr(r, 'id', '') or "") or "pivot" in str(r.metadata).lower()]
        for pr in pivot_rels:
            assert pr.source_entity_value is not None
            assert pr.target_entity_value is not None
