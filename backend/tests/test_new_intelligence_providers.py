import pytest
from app.modules.osint.providers.wayback_cdx import WaybackCDXProvider
from app.modules.osint.providers.urlscan import URLScanProvider
from app.modules.osint.providers.opensanctions import OpenSanctionsProvider
from app.modules.threat_intelligence.providers.threatfox import ThreatFoxProvider
from app.modules.threat_intelligence.providers.nvd_cve import NVDVulnerabilityProvider
from app.modules.tool_executor import tool_executor
from app.module_sdk.provider_adapter import ProviderRequest, ProviderResponse


@pytest.mark.asyncio
async def test_wayback_cdx_provider_contract():
    provider = WaybackCDXProvider()
    assert provider.provider_id == "wayback_cdx"
    assert provider.name == "Internet Archive Wayback Machine CDX API"
    assert provider.timeout_seconds == 8.0

    # Input validation: empty domain
    res_invalid = await provider.execute(ProviderRequest(query="   ", target_type="domain"))
    assert res_invalid.status == "skipped"

    # Input validation: spaces in domain
    res_spaces = await provider.execute(ProviderRequest(query="invalid domain with spaces", target_type="domain"))
    assert res_spaces.status == "skipped"


@pytest.mark.asyncio
async def test_urlscan_provider_contract():
    provider = URLScanProvider()
    assert provider.provider_id == "urlscan"
    assert "urlscan.io" in provider.name
    assert provider.timeout_seconds == 8.0

    # Input validation: empty query
    res_invalid = await provider.execute(ProviderRequest(query="", target_type="domain"))
    assert res_invalid.status == "skipped"


@pytest.mark.asyncio
async def test_opensanctions_provider_contract():
    provider = OpenSanctionsProvider()
    assert provider.provider_id == "opensanctions"
    assert "OpenSanctions" in provider.name
    assert provider.timeout_seconds == 8.0

    # Input validation: empty query
    res_invalid = await provider.execute(ProviderRequest(query="", target_type="name"))
    assert res_invalid.status == "skipped"


@pytest.mark.asyncio
async def test_threatfox_provider_contract():
    provider = ThreatFoxProvider()
    assert provider.provider_id == "threatfox"
    assert "ThreatFox" in provider.name
    assert provider.timeout_seconds == 8.0

    # Input validation: empty query
    res_invalid = await provider.execute(ProviderRequest(query="", target_type="ioc"))
    assert res_invalid.status == "skipped"


@pytest.mark.asyncio
async def test_nvd_vulnerability_provider_contract():
    provider = NVDVulnerabilityProvider()
    assert provider.provider_id == "nvd_cve"
    assert "NVD" in provider.name
    assert provider.timeout_seconds == 10.0

    # Input validation: empty query
    res_invalid = await provider.execute(ProviderRequest(query="", target_type="cve"))
    assert res_invalid.status == "skipped"


@pytest.mark.asyncio
async def test_tool_executor_dispatch_new_providers(monkeypatch):
    """Verify tool_executor routes all 5 new tools and normalizes outputs without mock fabrication."""

    # 1. tool_wayback dispatch
    async def mock_wayback_exec(self, req):
        return ProviderResponse(
            provider_id="wayback_cdx",
            status="success",
            duration_ms=12.5,
            raw_data={
                "target": "example.com",
                "count": 1,
                "snapshots": [{
                    "original_url": "http://example.com/",
                    "timestamp": "20200101000000",
                    "status_code": "200",
                    "mimetype": "text/html",
                    "archive_url": "https://web.archive.org/web/20200101000000/http://example.com/"
                }]
            }
        )
    monkeypatch.setattr(WaybackCDXProvider, "execute", mock_wayback_exec)
    wb_res = await tool_executor.execute_tool("tool_wayback", "example.com")
    assert wb_res.status == "SUCCESS"
    assert len(wb_res.results) == 1
    assert wb_res.results[0].type == "ARCHIVED_SNAPSHOT"

    # 2. tool_urlscan dispatch
    async def mock_urlscan_exec(self, req):
        return ProviderResponse(
            provider_id="urlscan",
            status="success",
            duration_ms=25.0,
            raw_data={
                "target": "example.com",
                "results": [{
                    "_id": "scan_123",
                    "page": {"url": "https://example.com", "ip": "93.184.216.34", "server": "ECS"}
                }]
            }
        )
    monkeypatch.setattr(URLScanProvider, "execute", mock_urlscan_exec)
    us_res = await tool_executor.execute_tool("tool_urlscan", "example.com")
    assert us_res.status == "SUCCESS"
    assert len(us_res.results) == 1
    assert us_res.results[0].type == "URL_SCAN"

    # 3. tool_opensanctions dispatch
    async def mock_sanctions_exec(self, req):
        return ProviderResponse(
            provider_id="opensanctions",
            status="success",
            duration_ms=18.0,
            raw_data={
                "target": "Target Person",
                "matches": [{
                    "id": "os_123",
                    "caption": "Target Person",
                    "schema": "Person",
                    "score": 0.95,
                    "topics": ["sanction"],
                    "datasets": ["eu_fsf"]
                }]
            }
        )
    monkeypatch.setattr(OpenSanctionsProvider, "execute", mock_sanctions_exec)
    os_res = await tool_executor.execute_tool("tool_opensanctions", "Target Person")
    assert os_res.status == "SUCCESS"
    assert len(os_res.results) == 1
    assert os_res.results[0].type == "SANCTION_RECORD"
    assert os_res.results[0].severity == "HIGH"

    # 4. tool_threatfox dispatch
    async def mock_tf_exec(self, req):
        return ProviderResponse(
            provider_id="threatfox",
            status="success",
            duration_ms=15.0,
            raw_data={
                "target": "1.2.3.4",
                "iocs": [{
                    "id": "ioc_123",
                    "ioc_value": "1.2.3.4:443",
                    "threat_type": "botnet_cc",
                    "malware_printable": "Emotet",
                    "confidence_level": 90
                }]
            }
        )
    monkeypatch.setattr(ThreatFoxProvider, "execute", mock_tf_exec)
    tf_res = await tool_executor.execute_tool("tool_threatfox", "1.2.3.4")
    assert tf_res.status == "SUCCESS"
    assert len(tf_res.results) == 1
    assert tf_res.results[0].type == "IOC"
    assert tf_res.results[0].severity == "CRITICAL"

    # 5. tool_nvd_cve dispatch
    async def mock_nvd_exec(self, req):
        return ProviderResponse(
            provider_id="nvd_cve",
            status="success",
            duration_ms=30.0,
            raw_data={
                "target": "CVE-2021-44228",
                "vulnerabilities": [{
                    "cve_id": "CVE-2021-44228",
                    "severity": "CRITICAL",
                    "cvss_score": 10.0,
                    "description": "Apache Log4j2 JNDI RCE"
                }]
            }
        )
    monkeypatch.setattr(NVDVulnerabilityProvider, "execute", mock_nvd_exec)
    nvd_res = await tool_executor.execute_tool("tool_nvd_cve", "CVE-2021-44228")
    assert nvd_res.status == "SUCCESS"
    assert len(nvd_res.results) == 1
    assert nvd_res.results[0].type == "VULNERABILITY"
    assert nvd_res.results[0].severity == "CRITICAL"
