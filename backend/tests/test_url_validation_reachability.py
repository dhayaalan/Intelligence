import pytest
import asyncio
from app.modules.threat_intelligence.engines.engines.katana_engine import KatanaEngine
from app.modules.threat_intelligence.engines.engines.httpx_engine import HTTPXEngine
from app.modules.threat_intelligence.scanner_adapter import ThreatIntelEngineAdapter
from app.module_sdk.provider_adapter import ProviderRequest


def test_katana_engine_unreachable_target_reports_not_active():
    async def _run():
        engine = KatanaEngine()
        # Test unresolvable domain
        out = await engine.execute("non-existent-domain-xyz-12345.test", "DOMAIN", {})
        assert out.success is True
        assert out.raw_data.get("is_active") is False
        assert out.raw_data.get("status") == "NOT ACTIVE"
        # Must NOT contain hardcoded fake endpoints
        assert len(out.raw_data.get("endpoints", [])) == 0

    asyncio.run(_run())


def test_httpx_engine_unreachable_target_reports_not_active():
    async def _run():
        engine = HTTPXEngine()
        out = await engine.execute("non-existent-domain-xyz-12345.test", "DOMAIN", {})
        assert out.success is True
        assert out.raw_data.get("is_active") is False
        assert out.raw_data.get("status") == "NOT ACTIVE"
        assert out.raw_data.get("status_code") is None

        norm = engine.normalize(out, "non-existent-domain-xyz-12345.test", "DOMAIN", "test_scan", "test_tenant")
        assert len(norm.endpoints) == 1
        assert norm.endpoints[0].is_active is False
        assert norm.endpoints[0].status_code is None
        # Must NOT report fake CSP findings or fake web servers for dead targets
        assert len(norm.findings) == 0
        assert len(norm.technologies) == 0

    asyncio.run(_run())


def test_scanner_adapter_skips_unresolvable_targets():
    async def _run():
        engine = HTTPXEngine()
        adapter = ThreatIntelEngineAdapter(engine)
        req = ProviderRequest(
            query="non-existent-domain-xyz-12345.test",
            target_type="DOMAIN",
            config={},
            options={}
        )
        resp = await adapter.execute(req)
        # Unresolvable targets are honestly skipped at preflight
        assert resp.status == "skipped"
        assert "not active or could not be resolved" in resp.error

    asyncio.run(_run())


def test_scanner_adapter_tags_inactive_http_endpoints():
    async def _run():
        engine = HTTPXEngine()
        adapter = ThreatIntelEngineAdapter(engine)
        # Port 59876 is unallocated and will refuse connection
        req = ProviderRequest(
            query="http://127.0.0.1:59876",
            target_type="URL",
            config={},
            options={}
        )
        resp = await adapter.execute(req)
        assert resp.status == "success"
        entities = resp.raw_data.get("entities", [])
        assert len(entities) >= 1
        url_ent = entities[0]
        assert str(url_ent["type"]).lower().endswith("url")
        assert url_ent["metadata"]["is_active"] is False
        assert url_ent["metadata"]["status"] == "NOT ACTIVE"
        assert url_ent["metadata"]["reachability"] == "NOT ACTIVE"

    asyncio.run(_run())
