import pytest
from app.infrastructure.neo4j.client import neo4j_client
from app.infrastructure.neo4j.service import neo4j_graph_service

@pytest.mark.asyncio
async def test_neo4j_connectivity_and_schema():
    """Verify Neo4j connectivity and idempotent schema initialization."""
    is_connected = await neo4j_client.verify_connectivity()
    if not is_connected:
        pytest.skip("Neo4j database is not reachable in current environment")

    schema_ok = await neo4j_client.init_schema()
    assert schema_ok is True

@pytest.mark.asyncio
async def test_neo4j_idempotent_upsert_and_expansion():
    """Verify entity and relationship insertion and 1-hop traversal in Neo4j."""
    is_connected = await neo4j_client.verify_connectivity()
    if not is_connected:
        pytest.skip("Neo4j database is not reachable in current environment")

    tenant_id = "test_tenant_neo4j_suite"

    # Upsert entity 1 (Person)
    ok1 = await neo4j_graph_service.upsert_entity(
        tenant_id=tenant_id,
        entity_data={
            "id": "ent_alice_sec",
            "type": "person",
            "value": "Alice Sec",
            "confidence": 0.98,
            "sources": ["osint_intel"]
        }
    )
    assert ok1 is True

    # Upsert entity 2 (Domain)
    ok2 = await neo4j_graph_service.upsert_entity(
        tenant_id=tenant_id,
        entity_data={
            "id": "ent_dark_infra",
            "type": "domain",
            "value": "darkinfra.org",
            "confidence": 0.95,
            "sources": ["whois_record"]
        }
    )
    assert ok2 is True

    # Upsert relationship
    rel_ok = await neo4j_graph_service.upsert_relationship(
        tenant_id=tenant_id,
        rel_data={
            "id": "rel_alice_owns_darkinfra",
            "type": "OWNS",
            "source_id": "ent_alice_sec",
            "target_id": "ent_dark_infra",
            "confidence": 0.96,
            "basis": "DIRECT_OBSERVATION",
            "is_inferred": False,
            "evidence_ids": ["ev_whois_proof_01"]
        }
    )
    assert rel_ok is True

    # Expand from Alice
    exp = await neo4j_graph_service.expand_entity_1hop(
        tenant_id=tenant_id,
        entity_id_or_val="ent_alice_sec"
    )
    assert exp is not None
    assert exp["seed_entity_id"] == "ent_alice_sec"
    assert len(exp["edges"]) >= 1
    edge = exp["edges"][0]
    assert edge["type"] == "OWNS"
    assert edge["confidence"] == 0.96
    assert edge["basis"] == "DIRECT_OBSERVATION"

@pytest.mark.asyncio
async def test_neo4j_tenant_isolation():
    """Verify entities and edges are strictly partitioned by tenant_id."""
    is_connected = await neo4j_client.verify_connectivity()
    if not is_connected:
        pytest.skip("Neo4j database is not reachable in current environment")

    tenant_a = "tenant_alpha_investigations"
    tenant_b = "tenant_beta_investigations"

    # Insert secret entity for Tenant A
    await neo4j_graph_service.upsert_entity(
        tenant_id=tenant_a,
        entity_data={
            "id": "ent_classified_target",
            "type": "organization",
            "value": "Classified Corp",
            "confidence": 1.0
        }
    )
    await neo4j_graph_service.upsert_relationship(
        tenant_id=tenant_a,
        rel_data={
            "id": "rel_classified_edge",
            "type": "AFFILIATED_WITH",
            "source_id": "ent_classified_target",
            "target_id": "ent_some_sub",
            "confidence": 0.9
        }
    )

    # Tenant B tries to expand the same entity ID
    exp_b = await neo4j_graph_service.expand_entity_1hop(
        tenant_id=tenant_b,
        entity_id_or_val="ent_classified_target"
    )
    assert exp_b is not None
    assert len(exp_b["edges"]) == 0
    assert len(exp_b["nodes"]) == 0

@pytest.mark.asyncio
async def test_neo4j_injection_safety():
    """Verify that arbitrary or malicious relationship types are sanitized."""
    sanitized = neo4j_graph_service._sanitize_rel_type("OWNS; DROP CONSTRAINT;")
    assert sanitized == "RELATED"
    valid = neo4j_graph_service._sanitize_rel_type("OWNS")
    assert valid == "OWNS"
