from fastapi.testclient import TestClient

def test_search_orchestration_automatic_target_detection(client: TestClient, analyst_headers):
    # Search domain without selecting modules or specifying target_type
    res = client.post("/api/v1/search", json={"query": "target-corp.io"}, headers=analyst_headers)
    assert res.status_code == 200
    data = res.json()
    
    assert data["target_type"] == "domain"
    # Both entitled modules executed automatically
    mod_ids = [j["module"] for j in data["module_jobs"]]
    assert "osint" in mod_ids
    assert "threat_intelligence" in mod_ids
    
    # Check entities and relationships are populated
    assert len(data["entities"]) > 0
    assert len(data["relationships"]) > 0
    assert len(data["evidence"]) > 0

def test_search_user_with_osint_only(client: TestClient, user_headers):
    # Investigator user who has only 'osint' assigned
    res = client.post("/api/v1/search", json={"query": "test-osint-only.com"}, headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    
    executed_mods = [j["module"] for j in data["module_jobs"]]
    assert "osint" in executed_mods
    assert "threat_intelligence" not in executed_mods

def test_search_orchestration_username_and_social_profiles(client: TestClient, analyst_headers):
    # Single main search with a username target
    res = client.post("/api/v1/search", json={"query": "@alex_osint"}, headers=analyst_headers)
    assert res.status_code == 200
    data = res.json()

    assert data["target_type"] == "username"
    assert data["intent"] == "USERNAME"
    executed_mods = [j["module"] for j in data["module_jobs"]]
    assert "osint" in executed_mods
    assert "social_media_intelligence" in executed_mods

    # Check that entities include social profile handles
    assert len(data["entities"]) > 0
    username_entities = [e for e in data["entities"] if e["type"] == "username" or "@" in e["value"]]
    assert len(username_entities) > 0

    # Check investigation snapshot contains social profiles count
    snapshot = data.get("investigation_snapshot")
    assert snapshot is not None
    assert "social_profiles_count" in snapshot

