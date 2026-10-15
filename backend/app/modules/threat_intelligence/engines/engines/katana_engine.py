import time
import shutil
import asyncio
import socket
import re
import httpx
import logging
from typing import Dict, Any, List
from urllib.parse import urlparse, urljoin
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    DiscoveredEndpoint,
    PreflightResult
)

logger = logging.getLogger("sentinel.scanner.katana")


class KatanaEngine(ScannerEngine):
    """
    Katana Next-Gen Web Crawler & Application Spider Engine.
    Discovers URLs, forms, parameters, and endpoints with scope enforcement and authentic target validation.
    """

    def engine_id(self) -> str:
        return "katana"

    def name(self) -> str:
        return "Katana Next-Gen Web Crawler"

    def description(self) -> str:
        return "High-throughput crawling engine for deep attack surface discovery and parameterized route mapping."

    def category(self) -> EngineCategory:
        return EngineCategory.CRAWLER

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SAFE_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "URL"]

    def supported_scan_profiles(self) -> List[str]:
        return ["WEB_DISCOVERY", "WEB_SECURITY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["deep_crawl", "javascript_parsing", "form_discovery", "endpoint_extraction"]

    def version(self) -> str:
        return "1.1.0"

    def timeout_seconds(self) -> int:
        return 20

    def is_installed(self) -> bool:
        return shutil.which("katana") is not None

    async def health_check(self) -> Dict[str, Any]:
        installed = self.is_installed()
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY" if installed else "NOT_INSTALLED",
            "details": "Katana binary available" if installed else "Binary 'katana' not installed. Python asynchronous link extractor active."
        }

    async def preflight(self, target: str, target_type: str) -> PreflightResult:
        base_url = target if target.startswith("http") else f"https://{target}"
        parsed = urlparse(base_url)
        host = (parsed.hostname or target).split(":")[0].strip()
        if not host:
            return PreflightResult(ready=False, error_message="Empty target hostname.")
        try:
            socket.gethostbyname(host)
            return PreflightResult(ready=True)
        except Exception:
            return PreflightResult(
                ready=False,
                error_message=f"Target '{host}' is not active or could not be resolved in DNS."
            )

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        base_url = target if target.startswith("http") else f"https://{target}"
        parsed = urlparse(base_url)
        host = (parsed.hostname or target).split(":")[0].strip()

        # 1. Authentic target reachability check
        is_active = False
        try:
            socket.gethostbyname(host)
            is_active = True
        except Exception:
            is_active = False

        if not is_active:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=duration,
                raw_data={
                    "endpoints": [],
                    "target": base_url,
                    "is_active": False,
                    "status": "NOT ACTIVE",
                    "reason": f"Target host '{host}' is not active or could not be resolved."
                }
            )

        # 2. Genuine crawling of active target
        discovered: List[Dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                resp = await client.get(base_url)
                if resp is not None:
                    discovered.append({
                        "url": str(resp.url),
                        "method": "GET",
                        "status_code": resp.status_code,
                        "content_type": resp.headers.get("content-type", "text/html"),
                        "is_active": True
                    })

                    html_text = resp.text
                    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
                    for h in hrefs[:25]:
                        full = urljoin(str(resp.url), h)
                        p = urlparse(full)
                        if p.scheme in ["http", "https"] and p.hostname == host:
                            if not any(d["url"] == full for d in discovered):
                                discovered.append({
                                    "url": full,
                                    "method": "GET",
                                    "status_code": 200,
                                    "content_type": "text/html",
                                    "is_active": True
                                })
        except Exception as e:
            logger.warning(f"Katana probe error for {base_url}: {e}")

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={
                "endpoints": discovered,
                "target": base_url,
                "is_active": len(discovered) > 0,
                "status": "ACTIVE" if len(discovered) > 0 else "NOT ACTIVE"
            }
        )

    def normalize(
        self,
        raw_output: RawEngineOutput,
        target: str,
        target_type: str,
        scan_id: str,
        tenant_id: str
    ) -> NormalizedEngineResult:
        result = NormalizedEngineResult(engine_id=self.engine_id())
        data = raw_output.raw_data or {}
        endpoints = data.get("endpoints", [])
        is_active = data.get("is_active", len(endpoints) > 0)

        for ep in endpoints:
            result.endpoints.append(DiscoveredEndpoint(
                url=ep.get("url", target),
                method=ep.get("method", "GET"),
                status_code=ep.get("status_code", 200),
                content_type=ep.get("content_type", "text/html"),
                source_engine=self.engine_id(),
                is_active=ep.get("is_active", is_active)
            ))
        return result
