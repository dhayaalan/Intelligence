import os
import time
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
        return "1.0.0"

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
                res = await client.get("https://urlscan.io/api/v1/search/?q=example.com&size=1", headers=headers)
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="urlscan.io search API is online and operational",
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
        parsed = urlparse(target if "://" in target else f"https://{target}")
        domain = (parsed.hostname or target).split(":")[0].strip().lower()

        if not domain or " " in domain:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=0.0,
                error="Target query is not a valid domain or host for urlscan."
            )

        api_key = os.getenv("URLSCAN_API_KEY") or request.config.get("api_key")
        headers = {"User-Agent": "SentialIntelligence/1.0"}
        if api_key:
            headers["API-Key"] = api_key

        query_term = f"domain:{domain}"
        search_url = f"https://urlscan.io/api/v1/search/?q={query_term}&size=10"

        scans_data: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.get(search_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    for item in results:
                        page = item.get("page", {})
                        task = item.get("task", {})
                        stats = item.get("stats", {})
                        report_id = item.get("_id")
                        scan_record = {
                            "id": report_id,
                            "url": page.get("url") or task.get("url"),
                            "domain": page.get("domain"),
                            "ip": page.get("ip"),
                            "asn": page.get("asn"),
                            "asn_name": page.get("asnname"),
                            "country": page.get("country"),
                            "server": page.get("server"),
                            "title": page.get("title"),
                            "status": page.get("status"),
                            "time": task.get("time"),
                            "screenshot_url": item.get("screenshot") or f"https://urlscan.io/screenshots/{report_id}.png" if report_id else None,
                            "result_url": item.get("result") or f"https://urlscan.io/result/{report_id}/" if report_id else None
                        }
                        scans_data.append(scan_record)

                        # Emit URL Entity
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
                                    "scan_time": scan_record.get("time")
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
                                    "country": scan_record.get("country")
                                }
                            ).dict())

                        # Emit Technology Entity if server header present
                        srv = scan_record["server"]
                        if srv:
                            entities.append(EntityPayload(
                                type=EntityType.TECHNOLOGY,
                                value=srv,
                                confidence=0.88,
                                sources=[self.provider_id],
                                metadata={"target_url": scan_url}
                            ).dict())

        except Exception as e:
            logger.warning(f"urlscan.io search failed for {domain}: {e}")

        duration = round((time.time() - start_time) * 1000, 2)
        ev = ModuleSDK.create_evidence(
            source="urlscan.io Public Scanner",
            provider=self.provider_id,
            module="osint",
            raw_data={
                "domain": domain,
                "scans_count": len(scans_data),
                "recent_scans": scans_data[:5]
            },
            reference=f"Target: {domain} (urlscan.io)"
        )

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            duration_ms=duration,
            raw_data={
                "target": domain,
                "scans": scans_data,
                "count": len(scans_data),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
