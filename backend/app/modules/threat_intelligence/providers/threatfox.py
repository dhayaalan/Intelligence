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
    Queries the ThreatFox public API for Indicators of Compromise (IOCs) including IP:ports, domains,
    URLs, and file hashes, returning malware family attribution, threat types, and confidence scores.
    Free community threat intelligence.
    """

    @property
    def provider_id(self) -> str:
        return "threatfox"

    @property
    def name(self) -> str:
        return "abuse.ch ThreatFox Community IOC & Malware Intelligence"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def timeout_seconds(self) -> float:
        return 8.0

    async def health_check(self) -> HealthCheckResult:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(
                    "https://threatfox-api.abuse.ch/api/v1/",
                    json={"query": "tag_info", "tag": "cobaltstrike", "limit": 1},
                    headers={"User-Agent": "SentialIntelligence/1.0"}
                )
                if res.status_code == 200:
                    data = res.json()
                    status_str = data.get("query_status", "")
                    if status_str in ["ok", "no_result"]:
                        return HealthCheckResult(
                            status=ModuleHealthStatus.HEALTHY,
                            message="abuse.ch ThreatFox API is active and operational",
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
                if resp.status_code == 200:
                    data = resp.json()
                    query_status = data.get("query_status")
                    if query_status == "ok":
                        raw_matches = data.get("data", [])
                        for item in raw_matches[:20]:
                            ioc_val = item.get("ioc")
                            threat_type = item.get("threat_type_desc") or item.get("threat_type")
                            malware = item.get("malware_printable") or item.get("malware")
                            confidence = item.get("confidence_level", 75)
                            tags = item.get("tags") or []
                            first_seen = item.get("first_seen")
                            last_seen = item.get("last_seen")

                            ioc_record = {
                                "id": item.get("id"),
                                "ioc": ioc_val,
                                "ioc_type": item.get("ioc_type"),
                                "threat_type": threat_type,
                                "malware_family": malware,
                                "confidence_level": confidence,
                                "tags": tags,
                                "first_seen": first_seen,
                                "last_seen": last_seen,
                                "reporter": item.get("reporter"),
                                "reference": item.get("reference")
                            }
                            iocs.append(ioc_record)

                            # Emit VULNERABILITY / MALWARE entity
                            entities.append(EntityPayload(
                                type=EntityType.VULNERABILITY,
                                value=f"ThreatFox: {malware or 'Malware IOC'} ({ioc_val})",
                                confidence=min(0.98, max(0.40, confidence / 100.0)),
                                sources=[self.provider_id],
                                metadata={
                                    "ioc": ioc_val,
                                    "ioc_type": item.get("ioc_type"),
                                    "threat_type": threat_type,
                                    "malware_family": malware,
                                    "tags": tags,
                                    "confidence": confidence,
                                    "first_seen": first_seen,
                                    "source": "abuse.ch ThreatFox"
                                }
                            ).dict())
        except Exception as e:
            logger.warning(f"ThreatFox search failed for '{target}': {e}")

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
                "count": len(iocs),
                "entities": entities,
                "evidence": [ev.dict() if hasattr(ev, "dict") else ev]
            }
        )
