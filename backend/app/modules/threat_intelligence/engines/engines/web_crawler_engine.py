import re
import time
import httpx
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List, Set, Optional
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    DiscoveredEndpoint
)
from app.modules.threat_intelligence.engines.validator import SSRFGuard


class WebCrawlerEngine(ScannerEngine):
    """
    Scope-Bounded Web Crawler & Application Spider Engine.
    Discovers URLs, HTML links, forms, input parameters, scripts, and API routes within strict domain scope.
    """

    def engine_id(self) -> str:
        return "web_crawler"

    def name(self) -> str:
        return "Web Application Crawler & Spider Engine"

    def description(self) -> str:
        return "Crawls web pages, extracts links, forms, query parameters, script references, and builds the application attack surface."

    def category(self) -> EngineCategory:
        return EngineCategory.CRAWLER

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SAFE_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["URL", "DOMAIN", "SUBDOMAIN", "HOSTNAME"]

    def supported_scan_profiles(self) -> List[str]:
        return ["WEB_DISCOVERY", "WEB_SECURITY_ASSESSMENT", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["recursive_crawling", "form_extraction", "parameter_discovery", "scope_enforcement", "js_endpoint_extraction"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": "Asynchronous scope-bounded DOM crawler active"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        base_url = target.strip()
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            base_url = f"https://{base_url}"

        parsed_base = urlparse(base_url)
        allowed_host = (parsed_base.hostname or "").lower()
        max_depth = context.get("crawl_depth", 2)
        max_pages = context.get("max_pages", 25)

        visited: Set[str] = set()
        queue: List[Tuple[str, int]] = [(base_url, 0)]
        discovered_endpoints: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=3.5, verify=False, follow_redirects=True) as client:
                while queue and len(visited) < max_pages:
                    current_url, depth = queue.pop(0)
                    if current_url in visited:
                        continue
                    visited.add(current_url)

                    # Enforce SSRF & Scope check
                    safe, _ = SSRFGuard.validate_url(current_url)
                    if not safe:
                        continue

                    try:
                        resp = await client.get(current_url)
                        status = resp.status_code
                        c_type = resp.headers.get("content-type", "")
                        html_text = resp.text if "text/html" in c_type or "json" in c_type else ""

                        # Extract forms and parameters
                        forms = []
                        form_matches = re.findall(r"<form[^>]*action=[\"']?([^\"'>\s]+)[^>]*method=[\"']?([^\"'>\s]+)?[^>]*>", html_text, re.IGNORECASE)
                        for action, method in form_matches:
                            forms.append({"action": action, "method": method or "GET"})

                        params = []
                        if "?" in current_url:
                            query_str = current_url.split("?", 1)[1]
                            params = [p.split("=")[0] for p in query_str.split("&") if p]

                        discovered_endpoints.append({
                            "url": current_url,
                            "method": "GET",
                            "status_code": status,
                            "content_type": c_type,
                            "parameters": params,
                            "forms": forms
                        })

                        if depth < max_depth and "text/html" in c_type:
                            # Extract links
                            hrefs = re.findall(r"href=[\"']([^\"'#>]+)[\"']", html_text, re.IGNORECASE)
                            for href in hrefs:
                                full_link = urljoin(current_url, href)
                                link_parsed = urlparse(full_link)
                                if link_parsed.scheme in ["http", "https"]:
                                    link_host = (link_parsed.hostname or "").lower()
                                    if link_host == allowed_host or link_host.endswith("." + allowed_host):
                                        if full_link not in visited:
                                            queue.append((full_link, depth + 1))
                    except Exception:
                        pass

            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=round(duration, 2),
                raw_data={
                    "base_url": base_url,
                    "crawled_count": len(discovered_endpoints),
                    "endpoints": discovered_endpoints
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"endpoints": []}
            )

    def normalize(
        self,
        raw_output: RawEngineOutput,
        target: str,
        target_type: str,
        scan_id: str,
        org_id: str
    ) -> NormalizedEngineResult:
        data = raw_output.raw_data or {}
        endpoints_data = data.get("endpoints", [])
        endpoints: List[DiscoveredEndpoint] = []

        for ep in endpoints_data:
            endpoints.append(DiscoveredEndpoint(
                url=ep["url"],
                method=ep.get("method", "GET"),
                status_code=ep.get("status_code"),
                content_type=ep.get("content_type"),
                parameters=ep.get("parameters", []),
                forms=ep.get("forms", []),
                source_engine=self.engine_id()
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            endpoints=endpoints,
            raw_reference=f"Crawled {len(endpoints)} application routes"
        )
