from fastapi.testclient import TestClient
from app.core.security import create_access_token

def test_tenant_isolation_investigations_and_evidence(client: TestClient, analyst_headers):
    # 1. Analyst in Tenant Acme creates an investigation
    inv_res = client.post(
        "/api/v1/investigations",
        json={"title": "Acme Confidential Op", "target": "adversary.org", "target_type": "domain"},
        headers=analyst_headers
    )
    assert inv_res.status_code == 200
    acme_inv_id = inv_res.json()["id"]

    # 2. Foreign spy user from another tenant attempts to access Acme's investigation
    spy_token = create_access_token({
        "sub": "usr_spy",
        "email": "spy@external.com",
        "role": "ANALYST",
        "tenant_id": "tenant_foreign"
    })
    spy_headers = {"Authorization": f"Bearer {spy_token}"}

    # Must be 404 Not Found (or 403 Forbidden)
    res_forbidden = client.get(f"/api/v1/investigations/{acme_inv_id}", headers=spy_headers)
    assert res_forbidden.status_code == 404

    # List investigations for foreign tenant must return 0
    res_list = client.get("/api/v1/investigations", headers=spy_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 0

def test_tenant_isolation_users_list(client: TestClient, tenant_admin_headers):
    # Tenant Admin of Acme queries users
    res = client.get("/api/v1/users", headers=tenant_admin_headers)
    assert res.status_code == 200
    users = res.json()
    # All users returned must belong strictly to Acme
    for u in users:
        assert u["tenant_id"] == "tenant_acme"
