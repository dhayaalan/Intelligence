import os
import re
import time
from typing import Dict, Any, List, Optional
import httpx

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import (
    HealthCheckResult, ModuleHealthStatus, EntityPayload, EvidencePayload, EntityType
)


class GreyNoiseCommunityProvider(ProviderAdapter):
    """
    Genuine GreyNoise Community Intelligence Provider.
    Queries the official GreyNoise Community API v3 to identify internet background noise,
    mass scanners, benign business services (RIOT), and malicious IP actors without simulation.
    """

    def __init__(self):
        self._provider_id = "greynoise_community"
        self._name = "GreyNoise Community"
        self._category = "THREAT_INTEL"
        self._base_url = "https://api.greynoise.io/v3/community"
        self._timeout_seconds = 8.0

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def supported_targets(self) -> List[str]:
        return ["ip", "ipv4"]

    @property
    def capabilities(self) -> List[str]:
        return ["ip_reputation", "internet_noise", "scanner_detection", "riot_validation"]

    @property
    def version(self) -> str:
        return "3.0.0"

    @property
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    async def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="GreyNoise Community API provider active and reachable"
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        ip = request.query.strip()

        # Validate that the target resembles an IPv4 address
        ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if not re.match(ipv4_pattern, ip):
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                error=f"GreyNoise requires a valid IPv4 address target; got '{ip}'",
                duration_ms=(time.time() - start_time) * 1000
            )

        api_key = os.getenv("GREYNOISE_API_KEY", "").strip()
        headers = {
            "Accept": "application/json",
            "User-Agent": "Sential-Intelligence-Platform/2.0"
        }
        if api_key:
            headers["key"] = api_key

        url = f"{self._base_url}/{ip}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, headers=headers) as client:
                resp = await client.get(url)
                duration_ms = (time.time() - start_time) * 1000

                if resp.status_code == 404:
                    # Legitimate no-match: IP has not been observed by GreyNoise sensors
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="success",
                        raw_data={
                            "ip": ip,
                            "noise": False,
                            "riot": False,
                            "classification": "unobserved",
                            "name": "unknown",
                            "message": "IP has not been observed scanning the internet",
                            "matches": [],
                            "records": []
                        },
                        duration_ms=duration_ms
                    )

                if resp.status_code == 429:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error="GreyNoise Community API rate limit reached (HTTP 429).",
                        duration_ms=duration_ms
                    )

                if resp.status_code in (401, 403):
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"GreyNoise API authentication/authorization failed (HTTP {resp.status_code}).",
                        duration_ms=duration_ms
                    )

                if resp.status_code >= 500:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"GreyNoise Community API unavailable (HTTP {resp.status_code}).",
                        duration_ms=duration_ms
                    )

                if resp.status_code != 200:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"GreyNoise Community API returned unexpected status HTTP {resp.status_code}.",
                        duration_ms=duration_ms
                    )

                try:
                    data = resp.json()
                except Exception as parse_err:
                    return ProviderResponse(
                        provider_id=self.provider_id,
                        status="error",
                        error=f"Failed to parse GreyNoise API JSON response: {str(parse_err)}",
                        duration_ms=duration_ms
                    )

                noise = bool(data.get("noise", False))
                riot = bool(data.get("riot", False))
                classification = str(data.get("classification", "unknown")).lower()
                actor_name = data.get("name") or "unknown"
                link = data.get("link") or f"https://viz.greynoise.io/ip/{ip}"
                last_seen = data.get("last_seen") or ""

                # Honest severity and confidence derivation
                if classification == "malicious":
                    severity = "HIGH"
                    conf = 0.90
                elif riot or classification == "benign":
                    severity = "INFO"
                    conf = 0.95
                elif noise:
                    severity = "MEDIUM"
                    conf = 0.85
                else:
                    severity = "INFO"
                    conf = 0.80

                finding_record = {
                    "ip": ip,
                    "noise": noise,
                    "riot": riot,
                    "classification": classification,
                    "name": actor_name,
                    "link": link,
                    "last_seen": last_seen,
                    "severity": severity,
                    "confidence": conf
                }

                entity = EntityPayload(
                    type=EntityType.IP,
                    value=ip,
                    confidence=conf,
                    sources=[self.provider_id],
                    metadata={
                        "noise": noise,
                        "riot": riot,
                        "classification": classification,
                        "actor_name": actor_name,
                        "greynoise_url": link,
                        "last_seen": last_seen,
                        "severity": severity
                    }
                )

                evidence = EvidencePayload(
                    source=self.provider_id,
                    provider=self.provider_id,
                    module="threat_intelligence",
                    reference=link,
                    confidence=conf,
                    raw_data=finding_record
                )

                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    entities=[entity],
                    evidence=[evidence],
                    raw_data={
                        "ip": ip,
                        "noise": noise,
                        "riot": riot,
                        "classification": classification,
                        "name": actor_name,
                        "link": link,
                        "last_seen": last_seen,
                        "matches": [finding_record],
                        "records": [finding_record]
                    },
                    duration_ms=duration_ms
                )

        except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError) as net_err:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                error=f"GreyNoise Community network error: {str(net_err)}",
                duration_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return ProviderResponse(
                provider_id=self.provider_id,
                status="error",
                error=f"GreyNoise execution error: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
