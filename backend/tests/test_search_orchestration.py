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
