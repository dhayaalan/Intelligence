import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus, EntityPayload, EntityType
from app.module_sdk.sdk import ModuleSDK

logger = logging.getLogger("sential.threat_intel.threatfox")


class ThreatFoxProvider(ProviderAdapter):
    """
    abuse.ch ThreatFox Community IOC & Malware Intelligence Provider.
    Queries abuse.ch ThreatFox public API for community-sourced Indicators of Compromise (IOCs),
    associated malware families, threat types, and confidence metrics.
    No API key required.
    """

    @property
    def provider_id(self) -> str:
        return "threatfox"

    @property
    def name(self) -> str:
        return "abuse.ch ThreatFox IOC Intelligence"

    @property
    def version(self) -> str:
        return "1.1.0"

    @property
    def timeout_seconds(self) -> float:
        return 8.0

    async def health_check(self) -> HealthCheckResult:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(
                    "https://threatfox-api.abuse.ch/api/v1/",
                    json={"query": "tag_info", "tag": "emotet"},
                    headers={"User-Agent": "SentialIntelligence/1.0"}
                )
                if res.status_code == 200:
                    data = res.json()
                    if data.get("query_status") in ("ok", "no_result"):
                        return HealthCheckResult(
                            status=ModuleHealthStatus.HEALTHY,
                            message="abuse.ch ThreatFox API is online and operational",
                            latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                        )
                elif res.status_code == 429:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.DEGRADED,
                        message="ThreatFox rate limit encountered",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"ThreatFox returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"ThreatFox health notice: {str(e)}",
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
                error="Empty query target."
            )

        api_url = "https://threatfox-api.abuse.ch/api/v1/"
        payload = {
            "query": "search_ioc",
            "search_term": target
        }
        headers = {"User-Agent": "SentialIntelligence/1.0 (investigations@sential.org)"}

        iocs: List[Dict[str, Any]] = []
        entities: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
                resp = await client.post(api_url, json=payload, headers=headers)
                duration = round((time.time() - start_time) * 1000, 2)

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="abuse.ch ThreatFox rate limit exceeded (HTTP 429)."
                    )
                elif resp.status_code >= 400:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"ThreatFox returned HTTP {resp.status_code}."
                    )

                data = resp.json()
                query_status = data.get("query_status")

                if query_status == "illegal_search_term":
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error="Illegal search term supplied to ThreatFox API."
                    )
                elif query_status not in ("ok", "no_result"):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        duration_ms=duration,
                        error=f"ThreatFox API query status: {query_status}"
                    )

                if query_status == "ok":
                    raw_matches = data.get("data", [])
                    for item in raw_matches[:20]:
                        ioc_val = item.get("ioc") or target
                        ioc_type = item.get("ioc_type", "unknown")
                        threat_type = item.get("threat_type_desc") or item.get("threat_type") or "IOC"
                        malware = item.get("malware_printable") or item.get("malware") or "Unknown Malware"
                        raw_conf = item.get("confidence_level")
                        conf_normalized = float(raw_conf) / 100.0 if raw_conf is not None else None
                        tags = item.get("tags") or []
                        first_seen = item.get("first_seen")
                        last_seen = item.get("last_seen")

                        ioc_record = {
                            "id": item.get("id"),
                            "ioc": ioc_val,
                            "ioc_value": ioc_val,
                            "ioc_type": ioc_type,
                            "threat_type": threat_type,
                            "malware_family": malware,
                            "malware_printable": malware,
                            "confidence_level": raw_conf,
                            "tags": tags,
                            "first_seen": first_seen,
                            "last_seen": last_seen,
                            "reporter": item.get("reporter"),
                            "reference": item.get("reference")
                        }
                        iocs.append(ioc_record)

                        # Determine correct entity type: IOC is NOT a vulnerability!
                        if ioc_type in ("ip:port", "ip"):
                            ent_type = EntityType.IP
                            ent_val = ioc_val.split(":")[0]
                        elif ioc_type in ("domain", "hostname"):
                            ent_type = EntityType.DOMAIN
                            ent_val = ioc_val
                        elif ioc_type in ("url",):
                            ent_type = EntityType.URL
                            ent_val = ioc_val
                        else:
                            ent_type = EntityType.THREAT_INDICATOR
                            ent_val = ioc_val

                        entities.append(EntityPayload(
                            type=ent_type,
                            value=ent_val,
                            confidence=conf_normalized if conf_normalized is not None else 0.80,
                            sources=[self.provider_id],
                            metadata={
                                "indicator_value": ioc_val,
                                "ioc_type": ioc_type,
                                "threat_type": threat_type,
                                "malware_family": malware,
                                "tags": tags,
                                "confidence_level": raw_conf,
                                "first_seen": first_seen,
                                "source": "abuse.ch ThreatFox",
                                "is_ioc": True
                            }
                        ).dict())

        except httpx.TimeoutException:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error="ThreatFox API request timed out."
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"ThreatFox search failed for '{target}': {e}")
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                duration_ms=duration,
                error=f"ThreatFox query error: {str(e)}"
            )

        duration = round((time.time() - start_time) * 1000, 2)
        ev = ModuleSDK.create_evidence(
            source="abuse.ch ThreatFox Community Threat Intel",
            provider=self.provider_id,
            module="threat_intelligence",
            raw_data={
                "target": target,
                "matches_count": len(iocs),
                "matched_iocs": iocs[:5]
            },
            reference=f"Target: {target} (ThreatFox API)"
        )

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            duration_ms=duration,
            raw_data={
                "target": target,
                "matches": iocs,
                "iocs": iocs,
                "count": len(iocs),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
