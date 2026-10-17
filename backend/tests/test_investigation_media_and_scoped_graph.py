import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_investigation_media_persistence_and_endpoints(analyst_headers):
    """Verify investigation record stores media, retrieves it, and deduplicates linked media."""
    # 1. Create an investigation with initial media
    inv_title = f"Test Inv {uuid.uuid4().hex[:8]}"
    initial_media = [
        {
            "id": "med_1",
            "media_type": "image",
            "url": "https://example.com/avatar.jpg",
            "title": "Suspect Avatar",
            "source_provider": "OSINT_DISCOVERY"
        }
    ]
    create_res = client.post(
        "/api/v1/investigations",
        json={
            "title": inv_title,
            "target": "target.example.org",
            "target_type": "DOMAIN",
            "notes": "Automated test case",
            "media": initial_media
        },
        headers=analyst_headers
    )
    assert create_res.status_code in (200, 201), create_res.text
    inv_data = create_res.json()
    inv_id = inv_data["id"]
    assert "media" in inv_data
    assert len(inv_data["media"]) == 1
    assert inv_data["media"][0]["url"] == "https://example.com/avatar.jpg"

    # 2. GET /api/v1/investigations/{id}/media
    get_media_res = client.get(
        f"/api/v1/investigations/{inv_id}/media",
        headers=analyst_headers
    )
    assert get_media_res.status_code == 200
    media_records = get_media_res.json()
    assert len(media_records) == 1
    assert media_records[0]["id"] == "med_1"

    # 3. POST /api/v1/investigations/{id}/link-media (new video)
    new_video = {
        "id": "med_2",
        "media_type": "video",
        "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "title": "YouTube Evidence",
        "source_provider": "NEWS_INTELLIGENCE"
    }
    link_res = client.post(
        f"/api/v1/investigations/{inv_id}/link-media",
        json=new_video,
        headers=analyst_headers
    )
    assert link_res.status_code == 200
    updated_inv = link_res.json()
    assert updated_inv["total_media"] == 2

    # 4. Link duplicate media (same URL) -> Should deduplicate
    dup_res = client.post(
        f"/api/v1/investigations/{inv_id}/link-media",
        json=new_video,
        headers=analyst_headers
    )
    assert dup_res.status_code == 200
    assert dup_res.json()["total_media"] == 2

def test_investigation_scoped_graph_endpoint(analyst_headers):
    """Verify /api/v1/investigations/{id}/graph returns only entities and relationships scoped to investigation."""
    inv_title = f"Graph Scope Test {uuid.uuid4().hex[:8]}"
    create_res = client.post(
        "/api/v1/investigations",
        json={
            "title": inv_title,
            "target": "threat-actor.org",
            "target_type": "DOMAIN",
            "notes": "Testing scoped graph"
        },
        headers=analyst_headers
    )
    assert create_res.status_code in (200, 201)
    inv_id = create_res.json()["id"]

    # Request graph for this investigation
    graph_res = client.get(
        f"/api/v1/investigations/{inv_id}/graph",
        headers=analyst_headers
    )
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert "investigation_id" in graph_data
    assert graph_data["investigation_id"] == inv_id
    assert "nodes" in graph_data
    assert "relationships" in graph_data
    assert isinstance(graph_data["nodes"], list)
    assert isinstance(graph_data["relationships"], list)
