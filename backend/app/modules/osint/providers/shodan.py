"""
Shodan OSINT Intelligence Provider.
Integrates both:
1. Shodan InternetDB (100% Keyless, free API providing ports, vulns/CVEs, CPEs, hostnames, and tags).
2. Authoritative Shodan Host API (when SHODAN_API_KEY is configured) for detailed service banners,
   SSL certificates, ASN, and vulnerability enrichment.

Note: Shodan is an internet exposure index for exposed hosts and services.
It is NOT a search engine for private video surveillance or arbitrary CCTV streams.
"""

import os
import time
import socket
import ipaddress
import logging
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus

logger = logging.getLogger(__name__)


class ShodanHostFinding(BaseModel):
    ip: str
    ports: List[int] = Field(default_factory=list)
    hostnames: List[str] = Field(default_factory=list)
    cpes: List[str] = Field(default_factory=list)
    vulns: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    asn: Optional[str] = None
    org: Optional[str] = None
    isp: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    source: str = "Shodan InternetDB"


class ShodanProvider(ProviderAdapter):
    """
    Adapter for Shodan Internet Exposure and Vulnerability Census.
    Supports keyless InternetDB queries and keyed Shodan Host API calls.
    """

    @property
    def provider_id(self) -> str:
        return "shodan"

    @property
    def name(self) -> str:
        return "Shodan Exposure & Vulnerability Census"

    def get_api_key(self) -> Optional[str]:
        return os.getenv("SHODAN_API_KEY") or getattr(settings, "SHODAN_API_KEY", None)

    async def health_check(self) -> HealthCheckResult:
        # Check InternetDB keyless endpoint
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get("https://internetdb.shodan.io/1.1.1.1")
                latency = round((time.time() - start) * 1000, 2)
                api_key = self.get_api_key()
                key_status = "Configured (Full API + InternetDB)" if api_key else "Keyless InternetDB Active (Free Tier)"
                return HealthCheckResult(
                    status=ModuleHealthStatus.HEALTHY,
                    message=f"Shodan operational: {key_status}",
                    latency_ms=latency
                )
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"Shodan InternetDB connection degraded: {str(e)}",
                latency_ms=latency
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        t_type = request.target_type.lower()
        api_key = request.config.get("api_key") or self.get_api_key()

        # Resolve IP address safely
        resolved_ip: Optional[str] = None
        try:
            ipaddress.ip_address(target)
            resolved_ip = target
        except ValueError:
            try:
                resolved_ip = socket.gethostbyname(target)
            except Exception:
                resolved_ip = None

        if not resolved_ip:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                error=f"Target '{target}' could not be resolved to a routable IP address for Shodan.",
                raw_data={"target": target, "ports": [], "vulns": []},
                duration_ms=duration
            )

        finding = ShodanHostFinding(ip=resolved_ip)

        # 1. Query Keyless Shodan InternetDB
        internetdb_queried = False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"https://internetdb.shodan.io/{resolved_ip}")
                if res.status_code == 200:
                    data = res.json()
                    finding.ports = data.get("ports", [])
                    finding.hostnames = data.get("hostnames", [])
                    finding.cpes = data.get("cpes", [])
                    finding.vulns = data.get("vulns", [])
                    finding.tags = data.get("tags", [])
                    internetdb_queried = True
        except Exception as e:
            logger.debug(f"Shodan InternetDB query for {resolved_ip} failed: {e}")

        # 2. If SHODAN_API_KEY is available, enrich with Host API
        if api_key:
            try:
                async with httpx.AsyncClient(timeout=6.0) as client:
                    resp = await client.get(f"https://api.shodan.io/shodan/host/{resolved_ip}?key={api_key}")
                    if resp.status_code == 200:
                        s_data = resp.json()
                        finding.ports = sorted(list(set(finding.ports + s_data.get("ports", []))))
                        finding.vulns = sorted(list(set(finding.vulns + s_data.get("vulns", []))))
                        finding.hostnames = sorted(list(set(finding.hostnames + s_data.get("hostnames", []))))
                        finding.asn = s_data.get("asn")
                        finding.org = s_data.get("org")
                        finding.isp = s_data.get("isp")
                        finding.city = s_data.get("city")
                        finding.country = s_data.get("country_name")
                        finding.source = "Shodan Full API & InternetDB"
            except Exception as e:
                logger.debug(f"Shodan Keyed API enrichment failed: {e}")

        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data={
                "target": target,
                "ip": resolved_ip,
                "source": finding.source,
                "ports": finding.ports,
                "vulns": finding.vulns,
                "hostnames": finding.hostnames,
                "cpes": finding.cpes,
                "tags": finding.tags,
                "asn": finding.asn,
                "org": finding.org,
                "isp": finding.isp,
                "city": finding.city,
                "country": finding.country,
                "api_key_configured": bool(api_key),
            },
            duration_ms=duration
        )


shodan_provider = ShodanProvider()
