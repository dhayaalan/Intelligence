from fastapi.testclient import TestClient

def test_module_failure_isolation_returns_partial(client: TestClient, analyst_headers):
    # Instruct Threat Intelligence module to throw an unhandled exception
    res = client.post(
        "/api/v1/search",
        json={"query": "resilience-test.com", "options": {"force_failure_threat_intelligence": True}},
        headers=analyst_headers
    )
    # The whole search MUST NOT return 500! It must return 200 with partial intelligence
    assert res.status_code == 200
    data = res.json()
    
    assert data["status"] == "partial"
    assert "partial intelligence" in data["partial_warning"].lower()
    
    ti_job = next((j for j in data["module_jobs"] if j["module"] == "threat_intelligence"), None)
    osint_job = next((j for j in data["module_jobs"] if j["module"] == "osint"), None)
    
    assert ti_job is not None
    assert ti_job["status"] == "failed"
    assert "unreachable" in ti_job["error"].lower()
    
    assert osint_job is not None
    assert osint_job["status"] in ["completed", "partial"]
    assert len(data["entities"]) > 0
