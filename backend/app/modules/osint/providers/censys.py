import os
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.osint.censys")


class CensysSearchProvider(ProviderAdapter):
    """
    Censys Platform Search API v2 Provider.
    Queries global Internet scanning telemetry for exposed hosts, open service ports,
    operating systems, TLS certificates, and software observation without synthetic records.
    Requires CENSYS_API_ID and CENSYS_API_SECRET; reports CONFIG_REQUIRED honestly when unconfigured.
    """

    @property
    def provider_id(self) -> str:
        return "censys"

    @property
    def name(self) -> str:
        return "Censys Platform Host & Service Intelligence API v2"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def timeout_seconds(self) -> float:
        return 10.0

    async def health_check(self) -> HealthCheckResult:
        api_id = os.getenv("CENSYS_API_ID")
        api_secret = os.getenv("CENSYS_API_SECRET")
        if not (api_id and api_secret):
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message="Censys API credentials missing (requires CENSYS_API_ID and CENSYS_API_SECRET)",
                latency_ms=0.0
            )

        try:
            auth = (api_id, api_secret)
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get("https://search.censys.io/api/v2/hosts/account", auth=auth)
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="Censys Platform API v2 operational",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="Censys rate limit exceeded (HTTP 429)",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"Censys API returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"Censys health check notice: {str(e)}",
                latency_ms=0.0
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        query = request.query.strip()
        if not query:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                duration_ms=0.0,
                error="Empty host query target."
            )

        api_id = os.getenv("CENSYS_API_ID") or request.config.get("api_id")
        api_secret = os.getenv("CENSYS_API_SECRET") or request.config.get("api_secret")

        if not (api_id and api_secret):
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="config_required",
                duration_ms=duration,
                error="Censys API credentials not configured. Set CENSYS_API_ID and CENSYS_API_SECRET in environment.",
                raw_data={
                    "target": query,
                    "requirement": "CENSYS_API_ID and CENSYS_API_SECRET",
                    "status": "CONFIG_REQUIRED"
                }
            )

        auth = (api_id, api_secret)
        # Check if query is IPv4/IPv6 or domain/search query
        is_ip = bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", query)) or ":" in query
        if is_ip:
            url = f"https://search.censys.io/api/v2/hosts/{query}"
            params = {}
        else:
            url = "https://search.censys.io/api/v2/hosts/search"
            params = {"q": query, "per_page": 10}

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                res = await client.get(url, auth=auth, params=params)
                duration = round((time.time() - start_time) * 1000, 2)

                if res.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="Censys API query limit exceeded (HTTP 429)."
                    )
                elif res.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="Censys API credentials invalid or entitlement quota exhausted."
                    )
                elif res.status_code == 404:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="not_found",
                        duration_ms=duration,
                        raw_data={
                            "target": query,
                            "count": 0,
                            "records": [],
                            "message": f"Host '{query}' not found in Censys Internet scan records."
                        }
                    )
                elif res.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"Censys API returned HTTP {res.status_code}."
                    )

                data = res.json()
                result_obj = data.get("result", {})
                hosts = []

                if is_ip and "services" in result_obj:
                    services = [
                        {
                            "port": s.get("port"),
                            "service_name": s.get("service_name"),
                            "transport_protocol": s.get("transport_protocol")
                        }
                        for s in result_obj.get("services", [])
                    ]
                    location = result_obj.get("location", {})
                    autonomous_system = result_obj.get("autonomous_system", {})
                    host_rec = {
                        "ip": result_obj.get("ip", query),
                        "services": services,
                        "location": location,
                        "autonomous_system": autonomous_system,
                        "last_observed_at": result_obj.get("last_observed_at"),
                        "source": "Censys Platform Search API v2"
                    }
                    hosts.append(host_rec)
                else:
                    hits = result_obj.get("hits", [])
                    for hit in hits:
                        hosts.append({
                            "ip": hit.get("ip"),
                            "services": hit.get("services", []),
                            "location": hit.get("location", {}),
                            "autonomous_system": hit.get("autonomous_system", {}),
                            "last_observed_at": hit.get("last_observed_at"),
                            "source": "Censys Platform Search API v2"
                        })

                entities = []
                for h in hosts:
                    entities.append(EntityPayload(
                        type=EntityType.IP,
                        value=h["ip"],
                        confidence=0.95,
                        sources=[self.provider_id],
                        metadata={
                            "ip": h["ip"],
                            "services_count": len(h.get("services", [])),
                            "country": h.get("location", {}).get("country"),
                            "asn": h.get("autonomous_system", {}).get("asn"),
                            "source": "Censys Platform API v2"
                        }
                    ).dict())

                ev = ModuleSDK.create_evidence(
                    source="Censys Platform Search API v2",
                    provider=self.provider_id,
                    module="osint",
                    raw_data={"target": query, "hosts_count": len(hosts), "hosts": hosts[:3]},
                    reference=f"Target: {query} (Censys API v2)"
                )

                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success" if hosts else "not_found",
                    duration_ms=duration,
                    raw_data={
                        "target": query,
                        "hosts": hosts,
                        "count": len(hosts),
                        "entities": entities,
                        "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
                    }
                )

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="Censys API request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Censys query failed for '{query}': {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"Censys query error: {str(e)}"
            )
