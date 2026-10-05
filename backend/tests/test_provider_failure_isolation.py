from fastapi.testclient import TestClient

def test_provider_failure_isolation(client: TestClient, analyst_headers):
    # Pass simulated Shodan failure in options
    res = client.post(
        "/api/v1/search",
        json={"query": "test-shodan-failure.com", "options": {"fail_shodan": True}},
        headers=analyst_headers
    )
    assert res.status_code == 200
    data = res.json()
    
    osint_job = next((j for j in data["module_jobs"] if j["module"] == "osint"), None)
    assert osint_job is not None
    # Module still succeeds or reports partial provider completion without crashing the search
    assert osint_job["status"] in ["completed", "partial"]
    assert "spiderfoot" in osint_job["sources"]
    assert "shodan" not in osint_job["sources"]
    
    # OSINT produced entities despite Shodan failing
    assert len(data["entities"]) > 0
