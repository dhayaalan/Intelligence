from fastapi.testclient import TestClient
from app.module_registry.registry import module_registry
from app.modules.example_intelligence.module import example_module
from app.identity.models import UserRole
from app.identity.schemas import UserCreateRequest
from app.identity.service import identity_service
from app.core.security import create_access_token

def test_example_intelligence_pluggability(client: TestClient, super_admin_headers):
    """Verifies that ExampleModule and ExampleProvider can be registered,
    entitled to a tenant, assigned to a user, and executed in Search
    WITHOUT modifying Core Search, OSINT, Threat Intelligence, Investigations, or Auth!
    """
    # 1. Verify module is discovered and registered in Module Registry
    mod_item = module_registry.get_module_info("example_intelligence")
    assert mod_item is not None
    assert mod_item.name == "Example Intelligence (Plugin)"
    assert "example_verifier" in mod_item.providers
    assert mod_item.health_status == "healthy"

    # 2. Entitle module to a new tenant without modifying Core
    tenant_res = client.post(
        "/api/v1/tenants",
        json={
            "name": "Plug & Play Org",
            "slug": "plug-play-org",
            "entitled_modules": ["example_intelligence"]  # Only the new pluggable module!
        },
        headers=super_admin_headers
    )
    assert tenant_res.status_code == 200
    new_tenant_id = tenant_res.json()["id"]

    # 3. Create a user with access to example_intelligence without modifying Core
    super_admin_user = identity_service.get_user_by_id("usr_super_admin")
    created_user = identity_service.create_user(
        creator=super_admin_user,
        tenant_id=new_tenant_id,
        request=UserCreateRequest(
            email="plugin_analyst@plugplay.com",
            name="Plugin Analyst",
            role=UserRole.ANALYST,
            assigned_modules=["example_intelligence"]
        )
    )
    assert created_user.id is not None
    assert "example_intelligence" in created_user.assigned_modules

    # 4. Generate token for this user and execute Search
    token = create_access_token({
        "sub": created_user.id,
        "email": created_user.email,
        "role": created_user.role.value,
        "tenant_id": new_tenant_id
    })
    headers = {"Authorization": f"Bearer {token}"}

    search_res = client.post("/api/v1/search", json={"query": "pluggable-domain.io"}, headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()

    # Core Search dynamically executed ONLY the pluggable module!
    executed_mods = [j["module"] for j in search_data["module_jobs"]]
    assert "example_intelligence" in executed_mods
    assert "osint" not in executed_mods
    assert "threat_intelligence" not in executed_mods

    # Correlated entity was created by the new pluggable module
    verified_entities = [e for e in search_data["entities"] if "example_intelligence" in e["sources"]]
    assert len(verified_entities) > 0
    assert "Verified Organization for pluggable-domain.io" in verified_entities[0]["value"]
