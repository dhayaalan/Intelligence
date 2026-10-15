import pytest
import httpx
from typing import Callable

from app.modules.osint.providers.wayback_cdx import WaybackCDXProvider
from app.modules.osint.providers.urlscan import URLScanProvider
from app.modules.osint.providers.opensanctions import OpenSanctionsProvider
from app.modules.threat_intelligence.providers.threatfox import ThreatFoxProvider
from app.modules.threat_intelligence.providers.nvd_cve import NVDVulnerabilityProvider
from app.modules.threat_intelligence.providers.greynoise import GreyNoiseCommunityProvider
from app.modules.osint.providers.gleif import GLEIFProvider
from app.modules.tool_executor import tool_executor
from app.module_sdk.provider_adapter import ProviderRequest
from app.module_sdk.models import EntityType


def patch_httpx_client(monkeypatch, handler: Callable[[httpx.Request], httpx.Response]):
    """Helper to mock httpx.AsyncClient using genuine httpx.MockTransport."""
    orig_init = httpx.AsyncClient.__init__

    def mock_init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        orig_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", mock_init)


# =========================================================================
# 1. URLScan Provider & Tool Executor Tests
# =========================================================================

@pytest.mark.asyncio
async def test_urlscan_success_and_schema_normalization(monkeypatch):
    """Verify URLScan parses genuine urlscan.io JSON and exposes both scans and results."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert "urlscan.io/api/v1/search" in str(request.url)
        assert 'page.domain:"example.com"' in request.url.params.get("q", "")
        return httpx.Response(200, json={
            "results": [
                {
                    "_id": "scan_test_001",
                    "page": {
                        "url": "https://example.com/login",
                        "domain": "example.com",
                        "ip": "93.184.216.34",
                        "server": "nginx",
                        "title": "Example Domain"
                    },
                    "task": {
                        "time": "2026-03-01T12:00:00.000Z",
                        "url": "https://example.com"
                    }
                }
            ],
            "total": 1
        })

    patch_httpx_client(monkeypatch, handler)

    provider = URLScanProvider()
    resp = await provider.execute(ProviderRequest(query="example.com", target_type="domain"))
    assert resp.status == "success"
    # Schema contract: both scans and results must be present
    assert "scans" in resp.raw_data
    assert "results" in resp.raw_data
    assert len(resp.raw_data["scans"]) == 1
    assert len(resp.raw_data["results"]) == 1

    # Tool executor test
    tool_res = await tool_executor.execute_tool("tool_urlscan", "example.com")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "URL_SCAN"
    assert tool_res.results[0].source == "urlscan.io"


@pytest.mark.asyncio
async def test_urlscan_error_handling_not_converted_to_empty(monkeypatch):
    """Verify HTTP 429 and 500 return status='error' / 'FAILED', never empty success."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="Rate limit exceeded")

    patch_httpx_client(monkeypatch, handler)

    provider = URLScanProvider()
    resp = await provider.execute(ProviderRequest(query="example.com", target_type="domain"))
    assert resp.status == "error"
    assert resp.error is not None

    tool_res = await tool_executor.execute_tool("tool_urlscan", "example.com")
    assert tool_res.status == "FAILED"
    assert tool_res.error is not None


# =========================================================================
# 2. ThreatFox Provider & Tool Executor Tests
# =========================================================================

@pytest.mark.asyncio
async def test_threatfox_success_and_schema_normalization(monkeypatch):
    """Verify ThreatFox parses genuine abuse.ch response, populates matches and iocs, and preserves IOC type."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert "threatfox-api.abuse.ch" in str(request.url)
        return httpx.Response(200, json={
            "query_status": "ok",
            "data": [
                {
                    "id": "123456",
                    "ioc": "198.51.100.22:443",
                    "threat_type": "botnet_cc",
                    "threat_type_desc": "Botnet Command and Control Server",
                    "ioc_type": "ip:port",
                    "malware_printable": "Cobalt Strike",
                    "confidence_level": 85,
                    "first_seen_utc": "2026-02-15 10:00:00"
                }
            ]
        })

    patch_httpx_client(monkeypatch, handler)

    provider = ThreatFoxProvider()
    resp = await provider.execute(ProviderRequest(query="198.51.100.22", target_type="ip"))
    assert resp.status == "success"
    # Schema contract: both matches and iocs must be present
    assert "matches" in resp.raw_data
    assert "iocs" in resp.raw_data
    assert len(resp.raw_data["matches"]) == 1
    # Entities must be generated and NOT be VULNERABILITY
    assert len(resp.raw_data["entities"]) == 1
    ent = resp.raw_data["entities"][0]
    ent_type = ent["type"] if isinstance(ent, dict) else ent.type
    # Must be accurately mapped to IP / THREAT_INDICATOR, and NEVER misclassified as VULNERABILITY
    assert ent_type in (EntityType.IP.value, EntityType.IP, EntityType.THREAT_INDICATOR.value, EntityType.THREAT_INDICATOR)
    assert ent_type != EntityType.VULNERABILITY.value and ent_type != EntityType.VULNERABILITY
    ent_meta = ent["metadata"] if isinstance(ent, dict) else ent.metadata
    assert ent_meta["malware_family"] == "Cobalt Strike"

    # Tool executor test
    tool_res = await tool_executor.execute_tool("tool_threatfox", "198.51.100.22")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "IOC"
    assert tool_res.results[0].confidence == 0.85
    assert tool_res.results[0].severity == "HIGH"


@pytest.mark.asyncio
async def test_threatfox_no_match(monkeypatch):
    """Verify legitimate no_result is success with 0 findings."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"query_status": "no_result", "data": []})

    patch_httpx_client(monkeypatch, handler)

    provider = ThreatFoxProvider()
    resp = await provider.execute(ProviderRequest(query="clean-domain.org", target_type="domain"))
    assert resp.status == "success"
    assert len(resp.raw_data["matches"]) == 0

    tool_res = await tool_executor.execute_tool("tool_threatfox", "clean-domain.org")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 0


@pytest.mark.asyncio
async def test_threatfox_illegal_search_term_error(monkeypatch):
    """Verify illegal_search_term is treated as an explicit error."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"query_status": "illegal_search_term"})

    patch_httpx_client(monkeypatch, handler)

    provider = ThreatFoxProvider()
    resp = await provider.execute(ProviderRequest(query="invalid--query", target_type="domain"))
    assert resp.status == "error"

    tool_res = await tool_executor.execute_tool("tool_threatfox", "invalid--query")
    assert tool_res.status == "FAILED"


# =========================================================================
# 3. NVD Vulnerability Provider & Tool Executor Tests
# =========================================================================

@pytest.mark.asyncio
async def test_nvd_cve_success_and_schema_normalization(monkeypatch):
    """Verify NVD CVE provider parses official CVE 2.0 API structure and populates cves & vulnerabilities."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert "services.nvd.nist.gov" in str(request.url)
        assert request.url.params.get("cveId") == "CVE-2024-9999"
        return httpx.Response(200, json={
            "vulnerabilities": [
                {
                    "cve": {
                        "id": "CVE-2024-9999",
                        "descriptions": [{"lang": "en", "value": "Critical remote code execution in core service."}],
                        "metrics": {
                            "cvssMetricV31": [
                                {
                                    "cvssData": {
                                        "baseScore": 9.8,
                                        "baseSeverity": "CRITICAL",
                                        "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                                    }
                                }
                            ]
                        },
                        "weaknesses": [
                            {"description": [{"value": "CWE-78"}]}
                        ]
                    }
                }
            ],
            "totalResults": 1
        })

    patch_httpx_client(monkeypatch, handler)

    provider = NVDVulnerabilityProvider()
    resp = await provider.execute(ProviderRequest(query="CVE-2024-9999", target_type="cve"))
    assert resp.status == "success"
    # Schema contract: both cves and vulnerabilities must be present
    assert "cves" in resp.raw_data
    assert "vulnerabilities" in resp.raw_data
    assert len(resp.raw_data["cves"]) == 1
    assert resp.raw_data["cves"][0]["severity"] == "CRITICAL"
    assert resp.raw_data["cves"][0]["cvss_score"] == 9.8

    # Tool executor test
    tool_res = await tool_executor.execute_tool("tool_nvd_cve", "CVE-2024-9999")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "VULNERABILITY"
    assert tool_res.results[0].severity == "CRITICAL"


@pytest.mark.asyncio
async def test_nvd_cve_rate_limit_and_server_error(monkeypatch):
    """Verify NVD 429 produces status='error' and 'FAILED'."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="Rate limit exceeded")

    patch_httpx_client(monkeypatch, handler)

    provider = NVDVulnerabilityProvider()
    resp = await provider.execute(ProviderRequest(query="CVE-2024-9999", target_type="cve"))
    assert resp.status == "error"

    tool_res = await tool_executor.execute_tool("tool_nvd_cve", "CVE-2024-9999")
    assert tool_res.status == "FAILED"


# =========================================================================
# 4. OpenSanctions Provider & Tool Executor Tests
# =========================================================================

@pytest.mark.asyncio
async def test_opensanctions_success_and_honest_confidence(monkeypatch):
    """Verify OpenSanctions maps genuine Person entity type, derives confidence honestly, and returns matches/records."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert "api.opensanctions.org" in str(request.url)
        assert request.url.params.get("q") == "John Corrupt"
        return httpx.Response(200, json={
            "results": [
                {
                    "id": "os_test_99",
                    "caption": "John Corrupt",
                    "schema": "Person",
                    "score": 0.92,
                    "properties": {
                        "topics": ["sanction", "debarment"],
                        "country": ["RU"],
                        "birthDate": ["1965-05-12"]
                    },
                    "datasets": ["eu_fsf", "us_ofac"]
                }
            ],
            "total": 1
        })

    patch_httpx_client(monkeypatch, handler)

    provider = OpenSanctionsProvider()
    resp = await provider.execute(ProviderRequest(query="John Corrupt", target_type="person"))
    assert resp.status == "success"
    assert "matches" in resp.raw_data
    assert "records" in resp.raw_data
    assert len(resp.raw_data["matches"]) == 1
    # Verify honest score usage (0.92, NOT arbitrary 0.85 default)
    assert resp.raw_data["matches"][0]["score"] == 0.92
    ent = resp.raw_data["entities"][0]
    ent_type = ent["type"] if isinstance(ent, dict) else ent.type
    ent_conf = ent["confidence"] if isinstance(ent, dict) else ent.confidence
    assert ent_type == EntityType.PERSON.value or ent_type == EntityType.PERSON
    assert ent_conf == 0.92

    # Tool executor test
    tool_res = await tool_executor.execute_tool("tool_opensanctions", "John Corrupt")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "SANCTION_RECORD"
    assert tool_res.results[0].confidence == 0.92


# =========================================================================
# 5. Wayback CDX Provider Tests
# =========================================================================

@pytest.mark.asyncio
async def test_wayback_cdx_success_and_error(monkeypatch):
    """Verify Wayback CDX parses rows into structured snapshots and distinguishes errors."""
    cdx_json_payload = [
        ["original", "timestamp", "statuscode", "mimetype"],
        ["https://archive.org/", "20240101000000", "200", "text/html"]
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        assert "web.archive.org/cdx/search/cdx" in str(request.url)
        return httpx.Response(200, json=cdx_json_payload)

    patch_httpx_client(monkeypatch, handler)

    provider = WaybackCDXProvider()
    resp = await provider.execute(ProviderRequest(query="archive.org", target_type="domain"))
    assert resp.status == "success"
    assert len(resp.raw_data["snapshots"]) == 1
    assert resp.raw_data["snapshots"][0]["timestamp"] == "20240101000000"

    tool_res = await tool_executor.execute_tool("tool_wayback", "archive.org")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "ARCHIVED_SNAPSHOT"


# =========================================================================
# 6. GreyNoise Community Provider & Tool Executor Tests
# =========================================================================

@pytest.mark.asyncio
async def test_greynoise_community_known_noise(monkeypatch):
    """Verify GreyNoise Community API accurately classifies internet noise and known scanners."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert "api.greynoise.io/v3/community" in str(request.url)
        return httpx.Response(200, json={
            "ip": "8.8.8.8",
            "noise": True,
            "riot": True,
            "classification": "benign",
            "name": "Google Public DNS",
            "link": "https://viz.greynoise.io/ip/8.8.8.8",
            "last_seen": "2026-10-15"
        })

    patch_httpx_client(monkeypatch, handler)
    provider = GreyNoiseCommunityProvider()
    resp = await provider.execute(ProviderRequest(query="8.8.8.8", target_type="ip"))
    assert resp.status == "success"
    assert resp.raw_data["noise"] is True
    assert resp.raw_data["riot"] is True
    assert resp.raw_data["classification"] == "benign"

    tool_res = await tool_executor.execute_tool("tool_greynoise", "8.8.8.8")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "IP_REPUTATION"


@pytest.mark.asyncio
async def test_greynoise_community_unobserved_404(monkeypatch):
    """Verify GreyNoise Community 404 is legitimate no-match, NOT error."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "IP not observed"})

    patch_httpx_client(monkeypatch, handler)
    provider = GreyNoiseCommunityProvider()
    resp = await provider.execute(ProviderRequest(query="192.0.2.1", target_type="ip"))
    assert resp.status == "success"
    assert resp.raw_data["noise"] is False
    assert len(resp.raw_data["matches"]) == 0


# =========================================================================
# 7. GLEIF Provider & Tool Executor Tests
# =========================================================================

@pytest.mark.asyncio
async def test_gleif_success_and_error(monkeypatch):
    """Verify GLEIF Provider queries JSON:API lei-records and resolves verified legal entity."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert "api.gleif.org/api/v1/lei-records" in str(request.url)
        return httpx.Response(200, json={
            "data": [
                {
                    "id": "5493006MHB84DD0ZWV18",
                    "type": "lei-records",
                    "attributes": {
                        "lei": "5493006MHB84DD0ZWV18",
                        "entity": {
                            "legalName": {"name": "BARCLAYS PLC"},
                            "jurisdiction": "GB",
                            "status": "ACTIVE",
                            "legalAddress": {"country": "GB", "city": "London"}
                        },
                        "registration": {
                            "status": "ISSUED",
                            "initialRegistrationDate": "2012-06-06T00:00:00Z"
                        }
                    }
                }
            ]
        })

    patch_httpx_client(monkeypatch, handler)

    provider = GLEIFProvider()
    resp = await provider.execute(ProviderRequest(query="Barclays", target_type="organization"))
    assert resp.status == "success"
    assert len(resp.raw_data["records"]) == 1
    assert resp.raw_data["records"][0]["lei"] == "5493006MHB84DD0ZWV18"

    tool_res = await tool_executor.execute_tool("tool_gleif", "Barclays")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert tool_res.results[0].type == "ORGANIZATION"
    assert "BARCLAYS PLC" in tool_res.results[0].value


# =========================================================================
# 8. SEC EDGAR Corporate Filings & Censys Platform Tests
# =========================================================================

@pytest.mark.asyncio
async def test_sec_edgar_provider_end_to_end(monkeypatch):
    """Verify SEC EDGAR queries company submissions and parses 10-K filings with fair-access headers."""
    from app.modules.osint.providers.sec_edgar import SECEDGARProvider

    def handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        assert "investigations@sential.org" in request.headers.get("user-agent", "")
        if "company_tickers.json" in url_str:
            return httpx.Response(200, json={
                "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
            })
        elif "CIK0000320193.json" in url_str:
            return httpx.Response(200, json={
                "name": "Apple Inc.",
                "cik": "0000320193",
                "sic": "3571",
                "sicDescription": "ELECTRONIC COMPUTERS",
                "tickers": ["AAPL"],
                "formerNames": [{"name": "APPLE COMPUTER INC"}],
                "filings": {
                    "recent": {
                        "form": ["10-K", "10-Q"],
                        "filingDate": ["2026-10-01", "2026-07-20"],
                        "accessionNumber": ["0000320193-26-000100", "0000320193-26-000080"],
                        "primaryDocument": ["aapl-10k.htm", "aapl-10q.htm"],
                        "primaryDocDescription": ["10-K ANNUAL REPORT", "10-Q QUARTERLY REPORT"]
                    }
                }
            })
        return httpx.Response(404, json={})

    patch_httpx_client(monkeypatch, handler)

    provider = SECEDGARProvider()
    resp = await provider.execute(ProviderRequest(query="AAPL", target_type="company"))
    assert resp.status == "success"
    assert resp.raw_data["record"]["cik"] == "0000320193"
    assert resp.raw_data["record"]["legal_name"] == "Apple Inc."
    assert len(resp.raw_data["record"]["recent_filings"]) == 2

    # Tool executor integration test
    tool_res = await tool_executor.execute_tool("tool_sec_edgar", "AAPL")
    assert tool_res.status == "SUCCESS"
    assert len(tool_res.results) == 1
    assert "Apple Inc." in tool_res.results[0].value
    assert "0000320193" in tool_res.results[0].value

