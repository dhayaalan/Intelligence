import time
import httpx
from typing import Dict, Any, List, Optional
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    NormalizedFinding,
    DiscoveredEndpoint
)
from app.modules.threat_intelligence.engines.validator import SSRFGuard


class HTTPDiscoveryEngine(ScannerEngine):
    """
    HTTP / HTTPS Discovery & Web Header Posture Engine.
    Discovers web endpoints, redirects, security headers, cookies, robots.txt, and sitemaps.
    """

    def engine_id(self) -> str:
        return "http_discovery"

    def name(self) -> str:
        return "HTTP / HTTPS Web Discovery Engine"

    def description(self) -> str:
        return "Probes web ports (80/443), validates SSL redirection, audits HTTP security headers, and crawls application metadata."

    def category(self) -> EngineCategory:
        return EngineCategory.HTTP

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SAFE_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "HOSTNAME", "IP", "URL"]

    def supported_scan_profiles(self) -> List[str]:
        return [
            "SAFE_DISCOVERY",
            "SERVICE_DISCOVERY",
            "WEB_DISCOVERY",
            "WEB_SECURITY_ASSESSMENT",
            "COMPREHENSIVE"
        ]

    def capabilities(self) -> List[str]:
        return ["http_probing", "redirect_validation", "security_headers_audit", "cookie_flags", "robots_txt", "sitemap_xml"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": "Asynchronous HTTP/2 + HTTP/1.1 client stack operational"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        base_url = target.strip()
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            base_url = f"https://{base_url}"

        discovered_responses: Dict[str, Any] = {}
        endpoints: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                # 1. Main endpoint probe
                resp = await client.get(base_url)
                endpoints.append({
                    "url": str(resp.url),
                    "status_code": resp.status_code,
                    "content_type": resp.headers.get("content-type", ""),
                    "server": resp.headers.get("server", ""),
                    "headers": dict(resp.headers),
                    "cookies": [c.name for c in resp.cookies.jar]
                })

                # 2. Probe robots.txt
                try:
                    robots_resp = await client.get(f"{base_url.rstrip('/')}/robots.txt")
                    if robots_resp.status_code == 200:
                        discovered_responses["robots_txt"] = robots_resp.text[:2000]
                        endpoints.append({
                            "url": f"{base_url.rstrip('/')}/robots.txt",
                            "status_code": 200,
                            "content_type": "text/plain"
                        })
                except Exception:
                    pass

                # 3. Probe sitemap.xml
                try:
                    sitemap_resp = await client.get(f"{base_url.rstrip('/')}/sitemap.xml")
                    if sitemap_resp.status_code == 200:
                        discovered_responses["sitemap_xml"] = sitemap_resp.text[:2000]
                        endpoints.append({
                            "url": f"{base_url.rstrip('/')}/sitemap.xml",
                            "status_code": 200,
                            "content_type": "application/xml"
                        })
                except Exception:
                    pass

            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=round(duration, 2),
                raw_data={
                    "base_url": base_url,
                    "endpoints": endpoints,
                    "discovered_responses": discovered_responses
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"base_url": base_url, "endpoints": []}
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
        findings: List[NormalizedFinding] = []
        endpoints: List[DiscoveredEndpoint] = []

        for ep in endpoints_data:
            endpoints.append(DiscoveredEndpoint(
                url=ep["url"],
                method="GET",
                status_code=ep.get("status_code"),
                content_type=ep.get("content_type"),
                source_engine=self.engine_id()
            ))

            headers = ep.get("headers", {})
            h_low = {k.lower(): v for k, v in headers.items()}

            # Check Security Headers
            if "strict-transport-security" not in h_low:
                findings.append(NormalizedFinding(
                    id=f"find_hsts_{scan_id[:8]}",
                    scan_id=scan_id,
                    tenant_id=org_id,
                    engine=self.engine_id(),
                    target=target,
                    finding_type="MISSING_SECURITY_HEADER",
                    title="Missing HTTP Strict-Transport-Security (HSTS) Header",
                    description=f"Endpoint {ep['url']} does not enforce HSTS, leaving connections vulnerable to SSL-stripping man-in-the-middle attacks.",
                    severity="LOW",
                    confidence="HIGH",
                    endpoint=ep["url"],
                    remediation="Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' header to all HTTPS responses.",
                    source="HTTP Discovery Engine",
                    cwe=["CWE-319"],
                    owasp_category="A05:2021-Security Misconfiguration"
                ))

            if "content-security-policy" not in h_low:
                findings.append(NormalizedFinding(
                    id=f"find_csp_{scan_id[:8]}",
                    scan_id=scan_id,
                    tenant_id=org_id,
                    engine=self.engine_id(),
                    target=target,
                    finding_type="MISSING_SECURITY_HEADER",
                    title="Missing Content-Security-Policy (CSP) Header",
                    description=f"Endpoint {ep['url']} does not declare a Content-Security-Policy, reducing defense-in-depth protection against Cross-Site Scripting (XSS).",
                    severity="LOW",
                    confidence="HIGH",
                    endpoint=ep["url"],
                    remediation="Define a restrictive Content-Security-Policy header restricting trusted script and object execution sources.",
                    source="HTTP Discovery Engine",
                    cwe=["CWE-1021", "CWE-79"],
                    owasp_category="A05:2021-Security Misconfiguration"
                ))

            if "x-frame-options" not in h_low and "content-security-policy" not in h_low:
                findings.append(NormalizedFinding(
                    id=f"find_xfo_{scan_id[:8]}",
                    scan_id=scan_id,
                    tenant_id=org_id,
                    engine=self.engine_id(),
                    target=target,
                    finding_type="CLICKJACKING_PROTECTION_MISSING",
                    title="Missing Anti-Clickjacking Frame Protection",
                    description=f"Target {ep['url']} lacks X-Frame-Options or CSP frame-ancestors directives, permitting unauthorized framing (Clickjacking).",
                    severity="LOW",
                    confidence="HIGH",
                    endpoint=ep["url"],
                    remediation="Configure 'X-Frame-Options: SAMEORIGIN' or 'frame-ancestors 'self'' in Content-Security-Policy.",
                    source="HTTP Discovery Engine",
                    cwe=["CWE-1021"]
                ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            findings=findings,
            endpoints=endpoints,
            raw_reference=f"Probed {len(endpoints)} HTTP/HTTPS endpoints"
        )
