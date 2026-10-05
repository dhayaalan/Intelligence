from fastapi.testclient import TestClient

def test_role_security_investigator_cannot_call_admin_apis(client: TestClient, analyst_headers, user_headers):
    # Analyst tries to list tenants -> 403 Forbidden
    res_tenants = client.get("/api/v1/tenants", headers=analyst_headers)
    assert res_tenants.status_code == 403

    # User tries to toggle modules -> 403 Forbidden
    res_mod = client.post("/api/v1/modules/osint/toggle", json={"enabled": False}, headers=user_headers)
    assert res_mod.status_code == 403

    # Analyst tries to view platform audit logs -> 403 Forbidden
    res_audit = client.get("/api/v1/audit", headers=analyst_headers)
    assert res_audit.status_code == 403

def test_super_admin_has_global_access(client: TestClient, super_admin_headers):
    # Super Admin can list tenants
    res = client.get("/api/v1/tenants", headers=super_admin_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
