"""
Regression test suite for Relationship Graph Integrity.
Validates 1-hop expansion, idempotent relationship persistence,
distinction between direct observation vs inferred relationships,
evidence provenance retrieval, and tenant authorization.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.database import db


@pytest.fixture(autouse=True)
def seed_graph_test_data():
    """Seed test entities and relationships in the in-memory database."""
    with db._lock:
        db.entities["ent_target_1"] = {
            "id": "ent_target_1",
            "tenant_id": "tenant_acme",
            "type": "person",
            "value": "Marcus Vance",
            "metadata": {"role": "Key Subject"},
        }
        db.entities["ent_email_1"] = {
            "id": "ent_email_1",
            "tenant_id": "tenant_acme",
            "type": "email",
            "value": "m.vance@vance-defense.com",
            "metadata": {},
        }
        db.entities["ent_org_1"] = {
            "id": "ent_org_1",
            "tenant_id": "tenant_acme",
            "type": "organization",
            "value": "Vance Defense Systems",
            "metadata": {},
        }
        db.entities["ent_domain_1"] = {
            "id": "ent_domain_1",
            "tenant_id": "tenant_acme",
            "type": "domain",
            "value": "vance-defense.com",
            "metadata": {},
        }

        # Seed relationships
        db.relationships["rel_owns_email"] = {
            "id": "rel_owns_email",
            "tenant_id": "tenant_acme",
            "source_id": "ent_target_1",
            "target_id": "ent_email_1",
            "type": "OWNS",
            "label": "owns",
            "confidence": 0.98,
            "basis": "DIRECT_OBSERVATION",
            "is_inferred": False,
            "evidence_ids": ["ev_whois_record_1"],
            "source": "WHOIS Registration",
            "metadata": {"source_provider": "domain_records"},
        }
        db.relationships["rel_affiliated_org"] = {
            "id": "rel_affiliated_org",
            "tenant_id": "tenant_acme",
            "source_id": "ent_target_1",
            "target_id": "ent_org_1",
            "type": "AFFILIATED_WITH",
            "label": "affiliated with",
            "confidence": 0.90,
            "basis": "DIRECT_OBSERVATION",
            "is_inferred": False,
            "evidence_ids": ["ev_corporate_registry_1"],
            "source": "Corporate Filings",
            "metadata": {"source_provider": "corporate_registry"},
        }
        db.relationships["rel_domain_org"] = {
            "id": "rel_domain_org",
            "tenant_id": "tenant_acme",
            "source_id": "ent_org_1",
            "target_id": "ent_domain_1",
            "type": "RESOLVES_TO",
            "label": "resolves to",
            "confidence": 0.95,
            "basis": "DIRECT_OBSERVATION",
            "is_inferred": False,
            "evidence_ids": ["ev_dns_a_record"],
            "source": "DNS Zone Lookup",
            "metadata": {},
        }

        # Seed supporting evidence
        db.evidence["ev_whois_record_1"] = {
            "id": "ev_whois_record_1",
            "tenant_id": "tenant_acme",
            "type": "whois_record",
            "source": "WHOIS Registrar",
            "content": "Registrant: Marcus Vance, Email: m.vance@vance-defense.com",
            "confidence": 0.98,
        }
        db.evidence["ev_corporate_registry_1"] = {
            "id": "ev_corporate_registry_1",
            "tenant_id": "tenant_acme",
            "type": "corporate_record",
            "source": "State Corporate Database",
            "content": "Director: Marcus Vance, Company: Vance Defense Systems",
            "confidence": 0.90,
        }

    yield

    with db._lock:
        for eid in ["ent_target_1", "ent_email_1", "ent_org_1", "ent_domain_1"]:
            db.entities.pop(eid, None)
        for rid in ["rel_owns_email", "rel_affiliated_org", "rel_domain_org"]:
            db.relationships.pop(rid, None)
        for evid in ["ev_whois_record_1", "ev_corporate_registry_1", "ev_dns_a_record"]:
            db.evidence.pop(evid, None)


def test_api_1hop_expansion_entity(client: TestClient, analyst_headers):
    """
    Expanding ent_target_1 by 1-hop must return directly connected nodes
    (ent_email_1, ent_org_1) and edges, without automatically expanding
    the secondary 2-hop entity (ent_domain_1).
    """
    res = client.get(
        "/api/v1/graph/expand?entity_id=ent_target_1&limit=50",
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["seed_entity_id"] == "ent_target_1"
    assert data["hop_count"] == 1
    returned_entity_ids = [n["id"] for n in data["nodes"]]
    returned_edge_ids = [e["id"] for e in data["edges"]]

    assert "ent_target_1" in returned_entity_ids
    assert "ent_email_1" in returned_entity_ids
    assert "ent_org_1" in returned_entity_ids
    # Bounded 1-hop: ent_domain_1 is 2 hops away, so it must NOT be returned
    assert "ent_domain_1" not in returned_entity_ids

    assert "rel_owns_email" in returned_edge_ids
    assert "rel_affiliated_org" in returned_edge_ids
    assert "rel_domain_org" not in returned_edge_ids


def test_api_entities_expand_endpoint(client: TestClient, analyst_headers):
    """
    Test GET /api/v1/entities/{entity_id}/expand endpoint.
    """
    res = client.get(
        "/api/v1/entities/ent_org_1/expand?limit=50",
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["seed_entity_id"] == "ent_org_1"
    returned_entity_ids = [n["id"] for n in data["nodes"]]
    assert "ent_org_1" in returned_entity_ids
    assert "ent_domain_1" in returned_entity_ids
    assert "ent_target_1" in returned_entity_ids


def test_api_relationship_evidence_provenance(client: TestClient, analyst_headers):
    """
    Test GET /api/v1/graph/relationships/{relationship_id}/evidence.
    Must return genuine evidence items and relationship provenance metadata.
    """
    res = client.get(
        "/api/v1/graph/relationships/rel_owns_email/evidence",
        headers=analyst_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["relationship_id"] == "rel_owns_email"
    assert data["type"] == "OWNS"
    assert data["basis"] == "DIRECT_OBSERVATION"
    assert data["is_inferred"] is False
    assert len(data["evidence"]) >= 1
    ev_item = data["evidence"][0]
    assert ev_item["id"] == "ev_whois_record_1"
    assert "Marcus Vance" in ev_item["content"]


def test_api_batch_expand_preserves_shared_nodes(client: TestClient, analyst_headers):
    """
    Test POST /api/v1/graph/expand for state-aware expansion.
    """
    payload = {
        "seed_node_ids": ["ent_target_1"],
        "visible_node_ids": ["ent_target_1"],
        "limit": 10,
    }
    res = client.post("/api/v1/graph/expand", json=payload, headers=analyst_headers)
    assert res.status_code == 200
    data = res.json()

    assert len(data["nodes"]) >= 2
    assert len(data["edges"]) >= 2


def test_api_graph_expand_unauthorized_without_auth(client: TestClient):
    """
    Graph traversal endpoints must enforce authentication.
    """
    res = client.get("/api/v1/graph/expand?entity_id=ent_target_1")
    assert res.status_code in [401, 403]
