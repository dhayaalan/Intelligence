from fastapi.testclient import TestClient
from app.core.security import create_access_token

def test_tenant_admin_cannot_create_super_admin(client: TestClient, tenant_admin_headers):
    # Tenant Admin tries to create a SUPER_ADMIN -> 403 Forbidden
    res = client.post(
        "/api/v1/users",
        json={
            "email": "hacker@acme.com",
            "name": "Malicious Admin",
            "role": "SUPER_ADMIN",
            "assigned_modules": ["osint"]
        },
        headers=tenant_admin_headers
    )
    assert res.status_code == 403

def test_tenant_admin_cannot_create_tenant_admin(client: TestClient, tenant_admin_headers):
    # Tenant Admin tries to create another TENANT_ADMIN -> 403 Forbidden
    res = client.post(
        "/api/v1/users",
        json={
            "email": "second_admin@acme.com",
            "name": "Second Admin",
            "role": "TENANT_ADMIN",
            "assigned_modules": ["osint"]
        },
        headers=tenant_admin_headers
    )
    assert res.status_code == 403

def test_tenant_admin_can_create_analyst(client: TestClient, tenant_admin_headers):
    # Tenant Admin successfully creates an Analyst in their own tenant
    res = client.post(
        "/api/v1/users",
        json={
            "email": "new_analyst@acme.com",
            "name": "Fresh Analyst",
            "role": "ANALYST",
            "assigned_modules": ["osint", "threat_intelligence"]
        },
        headers=tenant_admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "new_analyst@acme.com"
    assert data["role"] == "ANALYST"
    assert data["tenant_id"] == "tenant_acme"

def test_tenant_without_threat_intel_cannot_assign_threat_intel(client: TestClient):
    # Token for admin of tenant_basic which is entitled to OSINT only
    basic_admin_token = create_access_token({
        "sub": "usr_basic_admin",
        "email": "admin@basic-recon.com",
        "role": "TENANT_ADMIN",
        "tenant_id": "tenant_basic"
    })
    headers = {"Authorization": f"Bearer {basic_admin_token}"}
    
    # Try to assign Threat Intelligence to created user
    res = client.post(
        "/api/v1/users",
        json={
            "email": "basic_user@basic-recon.com",
            "name": "Basic User",
            "role": "USER",
            "assigned_modules": ["osint", "threat_intelligence"] # Threat intel not entitled
        },
        headers=headers
    )
    assert res.status_code == 200
    user_data = res.json()
    # Threat intelligence must be filtered out!
    assert "osint" in user_data["assigned_modules"]
    assert "threat_intelligence" not in user_data["assigned_modules"]
