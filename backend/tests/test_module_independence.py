from fastapi.testclient import TestClient
from app.module_registry.registry import module_registry

def test_module_independence_disable_osint(client: TestClient, super_admin_headers, analyst_headers):
    # 1. Disable OSINT via Module Registry
    module_registry.disable_module("osint")
    assert not module_registry.is_module_enabled("osint")
    
    # 2. Login & Profile works
    res_me = client.get("/api/v1/auth/me", headers=analyst_headers)
    assert res_me.status_code == 200
    
    # 3. Search executes cleanly without OSINT, Threat Intelligence succeeds
    search_res = client.post("/api/v1/search", json={"query": "target-corp.com"}, headers=analyst_headers)
    assert search_res.status_code == 200
    data = search_res.json()
    
    executed_mods = [job["module"] for job in data["module_jobs"]]
    assert "osint" not in executed_mods
    assert "threat_intelligence" in executed_mods
    assert data["status"] in ["completed", "partial"]
    
    # 4. Investigation works
    inv_res = client.post(
        "/api/v1/investigations",
        json={"title": "Test Investigation", "target": "target-corp.com", "target_type": "domain"},
        headers=analyst_headers
    )
    assert inv_res.status_code == 200
    
    # Re-enable OSINT
    module_registry.enable_module("osint")
    assert module_registry.is_module_enabled("osint")

def test_module_independence_disable_threat_intelligence(client: TestClient, super_admin_headers, analyst_headers):
    # 1. Disable Threat Intelligence via Module Registry
    module_registry.disable_module("threat_intelligence")
    assert not module_registry.is_module_enabled("threat_intelligence")
    
    # 2. Search executes cleanly with OSINT, Threat Intelligence is skipped
    search_res = client.post("/api/v1/search", json={"query": "security-target.com"}, headers=analyst_headers)
    assert search_res.status_code == 200
    data = search_res.json()
    
    executed_mods = [job["module"] for job in data["module_jobs"]]
    assert "threat_intelligence" not in executed_mods
    assert "osint" in executed_mods
    assert len(data["entities"]) > 0
    
    # Re-enable Threat Intelligence
    module_registry.enable_module("threat_intelligence")
    assert module_registry.is_module_enabled("threat_intelligence")
