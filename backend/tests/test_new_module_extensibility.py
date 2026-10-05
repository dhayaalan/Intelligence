from fastapi.testclient import TestClient
from app.module_registry.registry import module_registry
from app.modules.test_intelligence.module import test_intelligence_module

def test_dynamic_new_module_registration(client: TestClient, super_admin_headers):
    # Verify test_intelligence module is registered dynamically
    mod = module_registry.get_module("test_intelligence")
    assert mod is not None
    assert mod.manifest.id == "test_intelligence"
    assert mod.manifest.name == "Test Intelligence (Plugin)"

    # Execute search as Super Admin (who has entitlement to test_intelligence)
    res = client.post("/api/v1/search", json={"query": "plugin-demo.org"}, headers=super_admin_headers)
    assert res.status_code == 200
    data = res.json()
    
    executed_mods = [j["module"] for j in data["module_jobs"]]
    assert "test_intelligence" in executed_mods
    
    # Evidence and entities produced by the new pluggable module should be unified by core correlation
    test_entities = [e for e in data["entities"] if "test_intelligence" in e["sources"]]
    assert len(test_entities) > 0
    assert "Verified Organization for plugin-demo.org" in test_entities[0]["value"]
