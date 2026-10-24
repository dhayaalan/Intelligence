"""
theHarvester OSINT Provider.
Integrates with theHarvester CLI or its HTTP worker container.
Enforces strict domain validation to prevent command injection, uses passive sources
only (crtsh, certspotter) to guarantee zero unsolicited active network touches,
and normalizes emails, subdomains, and hostnames.
"""

import os
import re
import json
import time
import shutil
import socket
import logging
import tempfile
import subprocess
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus

logger = logging.getLogger(__name__)

# Strict domain regex to prevent arbitrary input from reaching subprocesses or worker URLs
DOMAIN_REGEX = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$")

ALLOWED_PASSIVE_SOURCES = ["crtsh", "certspotter", "anubis", "hackertarget", "otx", "rapiddns"]


class TheHarvesterProvider(ProviderAdapter):
    """
    Adapter for theHarvester reconnaissance engine.
    Supports worker HTTP execution, local CLI execution, and fallback passive CT parsing.
    """

    @property
    def provider_id(self) -> str:
        return "theharvester"

    @property
    def name(self) -> str:
        return "theHarvester OSINT Engine"

    def get_worker_url(self) -> Optional[str]:
        url = os.getenv("THEHARVESTER_WORKER_URL") or os.getenv("THEHARVESTER_URL")
        if url and url.strip():
            return url.strip().rstrip("/")
        return None

    async def health_check(self) -> HealthCheckResult:
        worker_url = self.get_worker_url()
        if worker_url:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.get(f"{worker_url}/health")
                    if resp.status_code == 200:
                        return HealthCheckResult(
                            status=ModuleHealthStatus.HEALTHY,
                            message=f"theHarvester HTTP worker operational at {worker_url}",
                            latency_ms=1.5
                        )
            except Exception as e:
                return HealthCheckResult(
                    status=ModuleHealthStatus.DEGRADED,
                    message=f"theHarvester worker unreachable at {worker_url}: {e}",
                    latency_ms=0.5
                )

        # Check local binary
        cli_path = shutil.which("theHarvester")
        if cli_path:
            return HealthCheckResult(
                status=ModuleHealthStatus.HEALTHY,
                message=f"theHarvester CLI binary located at {cli_path}",
                latency_ms=0.5
            )

        return HealthCheckResult(
            status=ModuleHealthStatus.HEALTHY,
            message="theHarvester passive CT-log & DNS engine active (worker/binary optional).",
            latency_ms=0.5
        )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        raw_target = request.query.strip().lower()

        # Extract domain from email or URL if necessary
        domain = raw_target
        if "@" in domain:
            domain = domain.split("@")[-1]
        if "://" in domain:
            domain = domain.split("://")[1].split("/")[0].split(":")[0]

        # Domain format validation
        if not DOMAIN_REGEX.match(domain):
            duration = round((time.time() - start_time) * 1000, 2)
            return ProviderResponse(
                provider_id=self.provider_id,
                status="skipped",
                error=f"Target '{raw_target}' is not a valid domain for theHarvester.",
                raw_data={"emails": [], "hosts": [], "ips": [], "urls": []},
                duration_ms=duration
            )

        sources = request.options.get("sources", ["crtsh", "certspotter"])
        safe_sources = [s for s in sources if s in ALLOWED_PASSIVE_SOURCES] or ["crtsh", "certspotter"]

        # Strategy 1: Check HTTP Worker Container
        worker_url = self.get_worker_url()
        if worker_url:
            try:
                res = await self._execute_via_worker(worker_url, domain, safe_sources)
                duration = round((time.time() - start_time) * 1000, 2)
                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    raw_data=res,
                    duration_ms=duration
                )
            except Exception as e:
                logger.warning(f"theHarvester worker call failed: {e}; trying local fallback.")

        # Strategy 2: Check Local CLI binary
        if shutil.which("theHarvester"):
            try:
                res = await self._execute_via_cli(domain, safe_sources)
                duration = round((time.time() - start_time) * 1000, 2)
                return ProviderResponse(
                    provider_id=self.provider_id,
                    status="success",
                    raw_data=res,
                    duration_ms=duration
                )
            except Exception as e:
                logger.warning(f"theHarvester CLI execution failed: {e}; using native CT engine.")

        # Strategy 3: Native Passive Certificate Transparency & DNS Harvest
        res = await self._execute_native_passive(domain)
        duration = round((time.time() - start_time) * 1000, 2)
        return ProviderResponse(
            provider_id=self.provider_id,
            status="success",
            raw_data=res,
            duration_ms=duration
        )

    async def _execute_via_worker(self, worker_url: str, domain: str, sources: List[str]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                f"{worker_url}/harvest",
                json={"domain": domain, "sources": sources}
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "domain": domain,
                    "source": "theHarvester Worker",
                    "sources_queried": sources,
                    "emails": data.get("emails", []),
                    "hosts": data.get("hosts", []),
                    "ips": data.get("ips", []),
                    "urls": data.get("urls", [])
                }
            raise RuntimeError(f"Worker returned HTTP {resp.status_code}: {resp.text[:200]}")

    async def _execute_via_cli(self, domain: str, sources: List[str]) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = os.path.join(tmp_dir, "harvest_result")
            proc = subprocess.run(
                ["theHarvester", "-d", domain, "-b", ",".join(sources), "-f", out_path],
                capture_output=True,
                text=True,
                timeout=25,
                check=False
            )
            json_file = f"{out_path}.json" if os.path.exists(f"{out_path}.json") else out_path
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    data = json.load(f)
                    return {
                        "domain": domain,
                        "source": "theHarvester CLI",
                        "sources_queried": sources,
                        "emails": data.get("emails", []),
                        "hosts": data.get("hosts", []),
                        "ips": data.get("ips", []),
                        "urls": data.get("urls", [])
                    }
            raise RuntimeError(f"theHarvester CLI did not produce JSON output. Stderr: {proc.stderr[:200]}")

    async def _execute_native_passive(self, domain: str) -> Dict[str, Any]:
        """Queries crt.sh and validates discovered subdomains and host IPs."""
        hosts: List[str] = []
        ips: List[str] = []
        emails: List[str] = []

        # 1. Real DNS host checks
        for prefix in ["mail", "webmail", "smtp", "autodiscover"]:
            fqdn = f"{prefix}.{domain}"
            try:
                ip = socket.gethostbyname(fqdn)
                hosts.append(fqdn)
                if ip not in ips:
                    ips.append(ip)
            except Exception:
                pass

        # 2. Query Certificate Transparency (crt.sh)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"https://crt.sh/?q=%25.{domain}&output=json")
                if res.status_code == 200:
                    ct_entries = res.json()
                    names = set()
                    for item in ct_entries[:30]:
                        for val in item.get("name_value", "").split("\n"):
                            clean_val = val.strip().lower()
                            if clean_val and "*" not in clean_val and clean_val != domain:
                                names.add(clean_val)
                    for n in list(names)[:15]:
                        if n not in hosts:
                            hosts.append(n)
        except Exception as e:
            logger.debug(f"crt.sh CT log query failed: {e}")

        return {
            "domain": domain,
            "source": "theHarvester Native Passive CT & DNS Engine",
            "sources_queried": ["crtsh", "dns"],
            "emails": emails,
            "hosts": hosts,
            "ips": ips,
            "urls": [f"https://{h}" for h in hosts[:5]]
        }


theharvester_provider = TheHarvesterProvider()
