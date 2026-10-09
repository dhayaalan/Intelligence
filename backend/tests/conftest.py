import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token, get_password_hash
from app.core.database import db
from app.module_registry.registry import module_registry
from app.modules.osint.module import osint_module
from app.modules.threat_intelligence.module import threat_intelligence_module
from app.modules.test_intelligence.module import test_intelligence_module
from app.modules.example_intelligence.module import example_module
from app.modules.news_intelligence.module import news_intelligence_module

@pytest.fixture(scope="session", autouse=True)
def init_app():
    # Register core modules & pluggable test/example modules
    module_registry.register(osint_module, default_enabled=True)
    module_registry.register(threat_intelligence_module, default_enabled=True)
    module_registry.register(news_intelligence_module, default_enabled=True)
    module_registry.register(test_intelligence_module, default_enabled=True)
    module_registry.register(example_module, default_enabled=True)
    
    # In-memory test tenant fixtures strictly for pytest isolated unit runs
    with db._lock:
        db.tenants["tenant_global"] = {"id": "tenant_global", "name": "Global Ops", "slug": "global", "entitled_modules": ["osint", "threat_intelligence", "test_intelligence", "news_intelligence"], "status": "active"}
        db.tenants["tenant_acme"] = {"id": "tenant_acme", "name": "Acme", "slug": "acme", "entitled_modules": ["osint", "threat_intelligence", "news_intelligence"], "status": "active"}
        db.tenants["tenant_basic"] = {"id": "tenant_basic", "name": "Basic", "slug": "basic", "entitled_modules": ["osint"], "status": "active"}
        db.users["usr_super_admin"] = {"id": "usr_super_admin", "email": "superadmin@sential.io", "hashed_password": get_password_hash("SuperAdmin123!"), "name": "Admin", "role": "SUPER_ADMIN", "tenant_id": "tenant_global", "assigned_modules": ["osint", "threat_intelligence", "news_intelligence"], "status": "active"}
        db.users["usr_tenant_admin"] = {"id": "usr_tenant_admin", "email": "admin@acme.com", "hashed_password": get_password_hash("TenantAdmin123!"), "name": "Tenant Admin", "role": "TENANT_ADMIN", "tenant_id": "tenant_acme", "assigned_modules": ["osint", "threat_intelligence", "news_intelligence"], "status": "active"}
        db.users["usr_analyst"] = {"id": "usr_analyst", "email": "analyst@acme.com", "hashed_password": get_password_hash("Analyst123!"), "name": "Analyst", "role": "ANALYST", "tenant_id": "tenant_acme", "assigned_modules": ["osint", "threat_intelligence", "news_intelligence"], "status": "active"}
        db.users["usr_investigator"] = {"id": "usr_investigator", "email": "user@acme.com", "hashed_password": get_password_hash("User123!"), "name": "User", "role": "USER", "tenant_id": "tenant_acme", "assigned_modules": ["osint", "news_intelligence"], "status": "active"}
        db.users["usr_basic_admin"] = {"id": "usr_basic_admin", "email": "admin@basic-recon.com", "hashed_password": get_password_hash("BasicAdmin123!"), "name": "Basic Admin", "role": "TENANT_ADMIN", "tenant_id": "tenant_basic", "assigned_modules": ["osint"], "status": "active"}
        db.tenants["tenant_foreign"] = {"id": "tenant_foreign", "name": "Foreign Ops", "slug": "foreign", "entitled_modules": ["osint"], "status": "active"}
        db.users["usr_spy"] = {"id": "usr_spy", "email": "spy@external.com", "hashed_password": get_password_hash("Spy123!"), "name": "Spy", "role": "ANALYST", "tenant_id": "tenant_foreign", "assigned_modules": ["osint"], "status": "active"}



@pytest.fixture(autouse=True)
def reset_modules_state():
    yield
    # Re-enable all modules after every test
    module_registry.enable_module("osint")
    module_registry.enable_module("threat_intelligence")
    module_registry.enable_module("news_intelligence")
    module_registry.enable_module("test_intelligence")
    module_registry.enable_module("example_intelligence")



@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def super_admin_headers():
    token = create_access_token({
        "sub": "usr_super_admin",
        "email": "superadmin@sential.io",
        "role": "SUPER_ADMIN",
        "tenant_id": "tenant_global"
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def tenant_admin_headers():
    token = create_access_token({
        "sub": "usr_tenant_admin",
        "email": "admin@acme.com",
        "role": "TENANT_ADMIN",
        "tenant_id": "tenant_acme"
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def analyst_headers():
    token = create_access_token({
        "sub": "usr_analyst",
        "email": "analyst@acme.com",
        "role": "ANALYST",
        "tenant_id": "tenant_acme"
    })
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_headers():
    token = create_access_token({
        "sub": "usr_investigator",
        "email": "user@acme.com",
        "role": "USER",
        "tenant_id": "tenant_acme"
    })
    return {"Authorization": f"Bearer {token}"}
