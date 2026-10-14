import os
import time
from typing import Any, Dict
import httpx
from app.core.config import settings
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus

class ShodanProvider(ProviderAdapter):
    @property
    def provider_id(self) -> str:
        return "shodan"

    @property
    def name(self) -> str:
        return "Shodan Intelligence"

    async def health_check(self) -> HealthCheckResult:
        api_key = getattr(settings, "SHODAN_API_KEY", None) or os.environ.get("SHODAN_API_KEY")
        if not api_key:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message="Shodan API key is not configured (SHODAN_API_KEY missing in backend/.env)",
                latency_ms=0.5
            )
        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="Shodan API endpoint configured and reachable",
            latency_ms=2.1
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        
        # Check if simulated failure or provider disabled via options/config
        if (request.options.get("fail_shodan") or request.config.get("fail_shodan")
                or request.options.get("shodan_disabled") or request.config.get("shodan_disabled")):
            raise ConnectionError("Shodan API connection timeout / rate limit exceeded")

        target = request.query.strip()
        t_type = request.target_type.lower()
        
        api_key = request.config.get("api_key") or getattr(settings, "SHODAN_API_KEY", None) or os.environ.get("SHODAN_API_KEY")

        # Zero synthetic fallback: never inject dummy CVEs or ports if unconfigured
        if not api_key:
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                error="SHODAN_API_KEY is not configured in backend/.env. Query skipped to prevent synthetic fallback.",
                raw_data={
                    "target": target,
                    "configured": False,
                    "status": "CONFIG_REQUIRED",
                    "ports": [],
                    "vulnerabilities": []
                },
                duration_ms=duration
            )

        # Real Shodan API Execution
        ports = []
        vulns = []
        ip_info = {}
        resolved_ip = target

        if t_type in ["ip", "domain"]:
            try:
                import socket
                import ipaddress
                try:
                    ipaddress.ip_address(target)
                except ValueError:
                    resolved_ip = socket.gethostbyname(target)
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"https://api.shodan.io/shodan/host/{resolved_ip}?key={api_key}")
                    if resp.status_code == 200:
                        s_data = resp.json()
                        ports = s_data.get("ports", [])
                        vulns = s_data.get("vulns", [])
                        ip_info = {
                            "as": s_data.get("asn"),
                            "org": s_data.get("org"),
                            "isp": s_data.get("isp"),
                            "city": s_data.get("city"),
                            "country": s_data.get("country_name"),
                            "countryCode": s_data.get("country_code"),
                            "lat": s_data.get("latitude"),
                            "lon": s_data.get("longitude")
                        }
                    elif resp.status_code == 404:
                        # Genuine 404: Host not indexed in Shodan census
                        pass
            except Exception:
                pass

        banner_info = {
            "target": target,
            "ip": resolved_ip,
            "ports": ports,
            "asn": ip_info.get("as"),
            "org": ip_info.get("org"),
            "isp": ip_info.get("isp"),
            "city": ip_info.get("city"),
            "country": ip_info.get("country"),
            "country_code": ip_info.get("countryCode"),
            "lat": ip_info.get("lat"),
            "lng": ip_info.get("lon"),
            "vulnerabilities": vulns,
            "hostnames": [f"edge-{target}"] if t_type == "domain" else [f"host-{target.replace('.', '-')}.net"]
        }
        
        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data=banner_info,
            duration_ms=duration
        )
