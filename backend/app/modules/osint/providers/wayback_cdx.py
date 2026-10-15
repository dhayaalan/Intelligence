import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.osint.wayback")


class WaybackCDXProvider(ProviderAdapter):
    """
    Internet Archive Wayback Machine CDX API Provider.
    Discovers historical URL snapshots, archives, status codes, and timestamps for target domains and URLs.
    No API key required. Authoritative historical evidence.
    """

    @property
    def provider_id(self) -> str:
        return "wayback_cdx"

    @property
    def name(self) -> str:
        return "Internet Archive Wayback Machine CDX API"

    @property
    def version(self) -> str:
        return "2.1.0"

    @property
    def timeout_seconds(self) -> float:
        return 8.0

    async def health_check(self) -> HealthCheckResult:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    "https://web.archive.org/cdx/search/cdx",
                    params={"url": "example.com", "limit": 1, "output": "json"},
                    headers={"User-Agent": "SentialIntelligence/1.0 (investigations@sential.org)"}
                )
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="Internet Archive CDX API is reachable and operational",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="Wayback CDX rate limit encountered",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"Wayback CDX returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"Wayback CDX health notice: {str(e)}",
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
                error="Invalid domain target for Wayback CDX lookup."
            )

        cdx_params = {
            "url": f"{domain}/*",
            "output": "json",
            "fl": "original,timestamp,statuscode,mimetype",
            "collapse": "urlkey",
            "limit": 30
        }
        headers = {"User-Agent": "SentialIntelligence/1.0 (investigations@sential.org)"}

        discovered_snapshots: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.get("https://web.archive.org/cdx/search/cdx", params=cdx_params, headers=headers)
                duration = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="Internet Archive Wayback CDX rate limit exceeded (HTTP 429)."
                    )
                elif resp.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"Wayback CDX API returned HTTP {resp.status_code}."
                    )

                try:
                    rows = resp.json()
                    if isinstance(rows, list) and len(rows) > 1:
                        for row in rows[1:]:
                            if len(row) >= 4:
                                orig, ts, code, mime = row[0], row[1], row[2], row[3]
                                archive_url = f"https://web.archive.org/web/{ts}/{orig}"
                                snap = {
                                    "original_url": orig,
                                    "timestamp": ts,
                                    "status_code": code,
                                    "mimetype": mime,
                                    "archive_url": archive_url
                                }
                                discovered_snapshots.append(snap)
                                entities.append(EntityPayload(
                                    type=EntityType.URL,
                                    value=orig,
                                    confidence=0.88,
                                    sources=[self.provider_id],
                                    metadata={
                                        "archive_url": archive_url,
                                        "snapshot_timestamp": ts,
                                        "status_code": code,
                                        "mimetype": mime,
                                        "source": "Internet Archive Wayback Machine",
                                        "is_historical_archive": True
                                    }
                                ).dict())
                except Exception as parse_err:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"Failed to parse CDX JSON from Wayback: {str(parse_err)}"
                    )

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="Wayback CDX API request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Wayback CDX query failed for {domain}: {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"Wayback CDX query error: {str(e)}"
            )

        duration = round((time.time() - start_time) * 1000, 2)
        ev = ModuleSDK.create_evidence(
            source="Internet Archive Wayback Machine",
            provider=self.provider_id,
            module="osint",
            raw_data={
                "domain": domain,
                "snapshot_count": len(discovered_snapshots),
                "snapshots": discovered_snapshots[:15]
            },
            reference=f"Target: {domain} (Wayback CDX API)"
        )

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            duration_ms=duration,
            raw_data={
                "target": domain,
                "snapshots": discovered_snapshots,
                "count": len(discovered_snapshots),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
