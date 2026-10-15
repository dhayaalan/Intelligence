import os
import time
import ipaddress
import httpx
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.osint.urlscan")


class URLScanProvider(ProviderAdapter):
    """
    urlscan.io Historical Scan & Technology Discovery Provider.
    Queries urlscan.io public search API for historical scans, technologies, server banners, IP/ASN, and screenshots.
    Works keylessly for search; supports URLSCAN_API_KEY for higher quota.
    """

    @property
    def provider_id(self) -> str:
        return "urlscan"

    @property
    def name(self) -> str:
        return "urlscan.io Historical Scan & Technology Discovery"

    @property
    def version(self) -> str:
        return "1.1.0"

    @property
    def timeout_seconds(self) -> float:
        return 8.0

    async def health_check(self) -> HealthCheckResult:
        try:
            api_key = os.getenv("URLSCAN_API_KEY")
            headers = {"User-Agent": "SentialIntelligence/1.0"}
            if api_key:
                headers["API-Key"] = api_key

            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    "https://urlscan.io/api/v1/search/",
                    params={"q": "page.domain:example.com", "size": 1},
                    headers=headers
                )
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="urlscan.io search API is online and operational",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="urlscan.io rate limit encountered",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"urlscan.io returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"urlscan.io health notice: {str(e)}",
                latency_ms=0.0
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        if not target:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=0.0,
                error="Empty query target for urlscan."
            )

        # Precision target classification
        is_ip = False
        try:
            ipaddress.ip_address(target)
            is_ip = True
        except ValueError:
            is_ip = False

        is_full_url = target.startswith("http://") or target.startswith("https://")

        if is_ip:
            query_term = f'page.ip:"{target}"'
            canonical_target = target
        elif is_full_url:
            query_term = f'page.url:"{target}"'
            canonical_target = target
        else:
            # Domain or hostname
            parsed = urlparse(f"https://{target}")
            domain = (parsed.hostname or target).split(":")[0].strip().lower()
            if not domain or " " in domain:
                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="skipped",
                    duration_ms=0.0,
                    error="Target query is not a valid domain, IP, or URL for urlscan."
                )
            query_term = f'page.domain:"{domain}"'
            canonical_target = domain

        api_key = os.getenv("URLSCAN_API_KEY") or request.config.get("api_key")
        headers = {"User-Agent": "SentialIntelligence/1.0"}
        if api_key:
            headers["API-Key"] = api_key

        scans_data: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.get(
                    "https://urlscan.io/api/v1/search/",
                    params={"q": query_term, "size": 10},
                    headers=headers
                )
                duration = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="urlscan.io rate limit exceeded (HTTP 429). Please retry later or provide URLSCAN_API_KEY."
                    )
                elif resp.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"urlscan.io access denied or invalid credentials (HTTP {resp.status_code})."
                    )
                elif resp.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"urlscan.io returned HTTP {resp.status_code} for query '{query_term}'."
                    )

                data = resp.json()
                results = data.get("results", [])
                for item in results:
                    page = item.get("page", {})
                    task = item.get("task", {})
                    report_id = item.get("_id")
                    scan_record = {
                        "id": report_id,
                        "url": page.get("url") or task.get("url") or canonical_target,
                        "domain": page.get("domain") or canonical_target,
                        "ip": page.get("ip"),
                        "asn": page.get("asn"),
                        "asn_name": page.get("asnname"),
                        "country": page.get("country"),
                        "server": page.get("server"),
                        "title": page.get("title"),
                        "status": page.get("status"),
                        "time": task.get("time"),
                        "screenshot_url": item.get("screenshot") or (f"https://urlscan.io/screenshots/{report_id}.png" if report_id else None),
                        "result_url": item.get("result") or (f"https://urlscan.io/result/{report_id}/" if report_id else None)
                    }
                    scans_data.append(scan_record)

                    # Emit URL Entity with explicit historical qualification
                    scan_url = scan_record["url"]
                    if scan_url:
                        entities.append(EntityPayload(
                            type=EntityType.URL,
                            value=scan_url,
                            confidence=0.92,
                            sources=[self.provider_id],
                            metadata={
                                "title": scan_record.get("title"),
                                "server": scan_record.get("server"),
                                "asn": scan_record.get("asn"),
                                "country": scan_record.get("country"),
                                "screenshot": scan_record.get("screenshot_url"),
                                "report_url": scan_record.get("result_url"),
                                "scan_time": scan_record.get("time"),
                                "is_historical_observation": True
                            }
                        ).dict())

                    # Emit IP Entity
                    ip_val = scan_record["ip"]
                    if ip_val and ip_val != "0.0.0.0":
                        entities.append(EntityPayload(
                            type=EntityType.IP,
                            value=ip_val,
                            confidence=0.90,
                            sources=[self.provider_id],
                            metadata={
                                "asn": scan_record.get("asn"),
                                "asn_name": scan_record.get("asn_name"),
                                "country": scan_record.get("country"),
                                "observed_via": "urlscan_historical_scan"
                            }
                        ).dict())

                    # Emit Technology Entity if server banner exists
                    srv = scan_record["server"]
                    if srv:
                        entities.append(EntityPayload(
                            type=EntityType.TECHNOLOGY,
                            value=srv,
                            confidence=0.85,
                            sources=[self.provider_id],
                            metadata={
                                "target_url": scan_url,
                                "observed_via": "urlscan_http_banner"
                            }
                        ).dict())

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="urlscan.io request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"urlscan.io query error for {canonical_target}: {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"urlscan.io query error: {str(e)}"
            )

        duration = round((time.time() - start_time) * 1000, 2)
        ev = ModuleSDK.create_evidence(
            source="urlscan.io Public Scanner",
            provider=self.provider_id,
            module="osint",
            raw_data={
                "target": canonical_target,
                "scans_count": len(scans_data),
                "recent_scans": scans_data[:5]
            },
            reference=f"Target: {canonical_target} (urlscan.io)"
        )

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            duration_ms=duration,
            raw_data={
                "target": canonical_target,
                "scans": scans_data,
                "results": scans_data,
                "count": len(scans_data),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
