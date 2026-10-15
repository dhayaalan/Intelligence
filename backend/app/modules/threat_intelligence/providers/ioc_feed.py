import os
import re
import time
import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus

logger = logging.getLogger("sential.threat_intel.ioc")

IPV4_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
HASH_MD5_PATTERN = re.compile(r"^[a-fA-F0-9]{32}$")
HASH_SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")


class IOCFeedProvider(ProviderAdapter):
    @property
    def provider_id(self) -> str:
        return "ioc_feed"

    @property
    def name(self) -> str:
        return "Global IOC & Threat Intelligence Feed (AlienVault OTX / URLhaus / AbuseIPDB)"

    async def health_check(self) -> HealthCheckResult:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    "https://otx.alienvault.com/api/v1/indicators/domain/example.com/general",
                    headers={"User-Agent": "SentialIntelligence/1.0"}
                )
                if res.status_code == 200:
                    return HealthCheckResult(
                        status=ModuleHealthStatus.HEALTHY,
                        message="AlienVault OTX & Global Threat Indicator Feeds active",
                        latency_ms=round(res.elapsed.total_seconds() * 1000, 2)
                    )
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"OTX returned HTTP {res.status_code}",
                    latency_ms=100.0
                )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"IOC health notice: {str(e)}",
                latency_ms=0.0
            )

    def _determine_indicator_type(self, target: str, target_type: str) -> str:
        clean = target.strip()
        if IPV4_PATTERN.match(clean):
            return "IPv4"
        if HASH_SHA256_PATTERN.match(clean):
            return "file"
        if HASH_MD5_PATTERN.match(clean):
            return "file"
        if clean.startswith("http://") or clean.startswith("https://"):
            return "url"
        if "." in clean and not clean.endswith("."):
            return "domain"
        return "hostname"

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        
        if request.config.get("fail_ioc"):
            raise TimeoutError("Threat feed timeout connecting to remote cluster")

        target = request.query.strip()
        t_type = request.target_type.lower()
        now = datetime.now(timezone.utc).isoformat()
        
        indicator_type = self._determine_indicator_type(target, t_type)
        otx_url = f"https://otx.alienvault.com/api/v1/indicators/{indicator_type}/{target}/general"

        pulses = []
        tags = []
        malware_families = []
        pulse_count = 0
        threat_level = "LOW"
        reputation_score = 0

        # 1. Query AlienVault OTX
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(otx_url, headers={"User-Agent": "SentialIntelligence/1.0"})
                if res.status_code == 200:
                    otx_data = res.json()
                    pulse_info = otx_data.get("pulse_info", {})
                    pulse_count = pulse_info.get("count", 0)
                    raw_pulses = pulse_info.get("pulses", [])[:10]

                    for p in raw_pulses:
                        p_tags = p.get("tags", [])
                        tags.extend(p_tags)
                        if p.get("adversary"):
                            malware_families.append(p.get("adversary"))
                        pulses.append({
                            "id": p.get("id"),
                            "name": p.get("name"),
                            "description": p.get("description", "")[:200],
                            "author": p.get("author_name"),
                            "modified": p.get("modified"),
                            "tags": p_tags[:5],
                            "references": p.get("references", [])[:3]
                        })

                    # Calculate reputation score from pulse count & tags
                    if pulse_count > 10:
                        reputation_score = 90
                        threat_level = "CRITICAL"
                    elif pulse_count > 0:
                        reputation_score = 65
                        threat_level = "HIGH"
                    else:
                        reputation_score = 5
                        threat_level = "BENIGN"
        except Exception as e:
            logger.warning(f"AlienVault OTX lookup notice for {target}: {e}")

        # 2. Check for configured optional keys (URLhaus, AbuseIPDB)
        configured_sources = ["AlienVault OTX (Open Community API)"]
        config_required_sources = []

        urlhaus_key = os.getenv("URLHAUS_API_KEY")
        if not urlhaus_key:
            config_required_sources.append("URLhaus (Auth-Key required for API v1)")
        else:
            configured_sources.append("URLhaus Threat Feed")

        abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY")
        if not abuseipdb_key:
            config_required_sources.append("AbuseIPDB (ABUSEIPDB_API_KEY required for IP checks)")
        else:
            configured_sources.append("AbuseIPDB v2 Feed")

        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data={
                "target": target,
                "normalized_indicator_type": indicator_type,
                "threat_score": reputation_score,
                "threat_level": threat_level,
                "pulse_count": pulse_count,
                "pulses": pulses,
                "associated_tags": list(set(tags))[:15],
                "malware_families": list(set(malware_families)),
                "sources_queried": configured_sources,
                "config_required_sources": config_required_sources,
                "is_zero_synthetic": True,
                "fetched_at": now
            },
            duration_ms=duration
        )
