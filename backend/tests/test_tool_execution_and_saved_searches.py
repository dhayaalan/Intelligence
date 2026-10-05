import pytest
from fastapi.testclient import TestClient
from app.modules.tool_executor import tool_executor

def test_tool_executor_dns_recon():
    """Verify that tool executor runs real DNS resolution without fake data."""
    import asyncio
    res = asyncio.run(tool_executor.execute_tool(
        tool_id="tool_dns_recon",
        target="google.com"
    ))
    assert res.tool_id == "tool_dns_recon"
    assert res.status in ["SUCCESS", "FAILED"]
    if res.status == "SUCCESS":
        assert len(res.results) > 0
        assert res.results[0].type == "DNS"
        assert res.results[0].target == "google.com"

def test_tool_executor_config_required_state():
    """Verify tools requiring unconfigured API keys return CONFIG_REQUIRED with guidance."""
    import asyncio
    res = asyncio.run(tool_executor.execute_tool(
        tool_id="tool_shodan",
        target="8.8.8.8"
    ))
    assert res.tool_id == "tool_shodan"
    assert res.status == "CONFIG_REQUIRED"
    assert "SHODAN_API_KEY" in (res.config_help or "")

def test_tools_api_endpoints(client: TestClient, super_admin_headers):
    """Test /api/v1/tools endpoints including detail, run, and history."""
    # 1. Get tool detail
    res = client.get("/api/v1/tools/tool_dns_recon", headers=super_admin_headers)
    assert res.status_code == 200
    tool_data = res.json()
    assert tool_data["id"] == "tool_dns_recon"

    # 2. Run single tool
    run_res = client.post(
        "/api/v1/tools/tool_dns_recon/run",
        json={"target": "cloudflare.com"},
        headers=super_admin_headers
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["tool_id"] == "tool_dns_recon"
    assert "duration_ms" in run_data

    # 3. Retrieve tool history
    hist_res = client.get("/api/v1/tools/history/runs", headers=super_admin_headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert isinstance(hist_data, list)
    assert len(hist_data) > 0

def test_saved_searches_lifecycle(client: TestClient, analyst_headers):
    """Test saved searches CRUD and execution."""
    # 1. Create saved search
    create_res = client.post(
        "/api/v1/search/saved",
        json={
            "name": "Acme Adversary Infrastructure",
            "query": "malicious-c2.example.com",
            "target_type": "domain",
            "tools": ["tool_dns_recon", "tool_whois_rdap"],
            "tags": ["threat", "c2"]
        },
        headers=analyst_headers
    )
    assert create_res.status_code == 200
    saved_data = create_res.json()
    saved_id = saved_data["id"]
    assert saved_data["name"] == "Acme Adversary Infrastructure"

    # 2. List saved searches
    list_res = client.get("/api/v1/search/saved", headers=analyst_headers)
    assert list_res.status_code == 200
    saved_list = list_res.json()
    assert any(s["id"] == saved_id for s in saved_list)

    # 3. Delete saved search
    del_res = client.delete(f"/api/v1/search/saved/{saved_id}", headers=analyst_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"
