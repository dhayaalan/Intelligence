import time
import json
import httpx
from urllib.parse import urljoin
from typing import Dict, Any, List, Optional
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    DiscoveredEndpoint,
    NormalizedFinding
)


COMMON_API_DOC_PATHS = [
    "/openapi.json",
    "/swagger.json",
    "/v1/openapi.json",
    "/v2/swagger.json",
    "/api/docs",
    "/docs",
    "/api-docs",
    "/v3/api-docs",
    "/swagger-ui.html",
    "/redoc"
]


class OpenAPIDiscoveryEngine(ScannerEngine):
    """
    OpenAPI / Swagger & REST API Schema Discovery Engine.
    Probes exposed documentation endpoints, extracts API paths, HTTP methods, parameters, and authentication schemes.
    """

    def engine_id(self) -> str:
        return "openapi_discovery"

    def name(self) -> str:
        return "OpenAPI & API Documentation Discovery Engine"

    def description(self) -> str:
        return "Discovers publicly exposed OpenAPI/Swagger specifications, parses route schemas, parameters, and authentication policies."

    def category(self) -> EngineCategory:
        return EngineCategory.API_DISCOVERY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SAFE_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["URL", "DOMAIN", "SUBDOMAIN", "HOSTNAME"]

    def supported_scan_profiles(self) -> List[str]:
        return ["WEB_DISCOVERY", "WEB_SECURITY_ASSESSMENT", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["openapi_schema_parsing", "swagger_extraction", "api_endpoint_enumeration", "auth_scheme_detection"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": f"Active API discovery prober ({len(COMMON_API_DOC_PATHS)} standard schema routes)"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        base_url = target.strip()
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            base_url = f"https://{base_url}"

        discovered_apis: List[Dict[str, Any]] = []
        exposed_docs: List[Dict[str, Any]] = []

        try:
            async with httpx.AsyncClient(timeout=3.0, verify=False, follow_redirects=True) as client:
                for path in COMMON_API_DOC_PATHS:
                    target_endpoint = urljoin(base_url, path)
                    try:
                        resp = await client.get(target_endpoint)
                        if resp.status_code == 200:
                            content_type = resp.headers.get("content-type", "")
                            is_json_spec = "json" in content_type or path.endswith(".json")

                            if is_json_spec:
                                try:
                                    spec_data = resp.json()
                                    paths = spec_data.get("paths", {})
                                    title = spec_data.get("info", {}).get("title", "API Specification")
                                    version = spec_data.get("info", {}).get("version", "1.0")

                                    exposed_docs.append({
                                        "url": target_endpoint,
                                        "title": title,
                                        "version": version,
                                        "routes_count": len(paths)
                                    })

                                    for route_path, methods in paths.items():
                                        if isinstance(methods, dict):
                                            for method, method_details in methods.items():
                                                if method.lower() in ["get", "post", "put", "delete", "patch", "options"]:
                                                    param_list = []
                                                    if isinstance(method_details, dict):
                                                        for p in method_details.get("parameters", []):
                                                            if isinstance(p, dict) and "name" in p:
                                                                param_list.append(p["name"])

                                                    full_api_url = urljoin(base_url, route_path.lstrip("/"))
                                                    discovered_apis.append({
                                                        "url": full_api_url,
                                                        "path": route_path,
                                                        "method": method.upper(),
                                                        "parameters": param_list,
                                                        "auth_required": bool(method_details.get("security", [])) if isinstance(method_details, dict) else False
                                                    })
                                except Exception:
                                    pass
                            elif "html" in content_type:
                                exposed_docs.append({
                                    "url": target_endpoint,
                                    "title": f"Interactive API Documentation ({path})",
                                    "version": "HTML UI",
                                    "routes_count": 0
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
                    "exposed_docs": exposed_docs,
                    "discovered_apis": discovered_apis
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"discovered_apis": [], "exposed_docs": []}
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
        api_list = data.get("discovered_apis", [])
        docs_list = data.get("exposed_docs", [])
        endpoints: List[DiscoveredEndpoint] = []
        findings: List[NormalizedFinding] = []

        for api in api_list:
            endpoints.append(DiscoveredEndpoint(
                url=api["url"],
                method=api.get("method", "GET"),
                parameters=api.get("parameters", []),
                source_engine=self.engine_id()
            ))

        for doc in docs_list:
            findings.append(NormalizedFinding(
                id=f"find_api_doc_{scan_id[:8]}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                target=target,
                finding_type="EXPOSED_API_DOCUMENTATION",
                title=f"Publicly Accessible API Documentation ({doc.get('title')})",
                description=f"Public API documentation endpoint discovered at {doc.get('url')}. Discloses schema endpoints, parameters, and internal method names.",
                severity="LOW",
                confidence="HIGH",
                endpoint=doc.get("url"),
                remediation="Ensure public API documentation is intentionally exposed or gate behind enterprise authentication if internal-only.",
                source="OpenAPI Discovery Engine",
                cwe=["CWE-200"],
                owasp_category="A01:2021-Broken Access Control"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            findings=findings,
            endpoints=endpoints,
            raw_reference=f"Extracted {len(endpoints)} API routes from {len(docs_list)} exposed schema documents"
        )
