import time
import re
import httpx
from typing import Dict, Any, List, Optional
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    DiscoveredTechnology
)


TECH_SIGNATURES = [
    # Web Servers
    {"name": "Nginx", "category": "Web Server", "headers": {"server": r"nginx(?:/([0-9.]+))?"}},
    {"name": "Apache HTTP Server", "category": "Web Server", "headers": {"server": r"apache(?:/([0-9.]+))?"}},
    {"name": "Caddy", "category": "Web Server", "headers": {"server": r"caddy"}},
    {"name": "Microsoft IIS", "category": "Web Server", "headers": {"server": r"microsoft-iis(?:/([0-9.]+))?"}},
    {"name": "Cloudflare", "category": "CDN / Reverse Proxy", "headers": {"server": r"cloudflare", "cf-ray": r".*"}},
    {"name": "Amazon CloudFront", "category": "CDN", "headers": {"via": r"cloudfront", "x-amz-cf-id": r".*"}},
    {"name": "Akamai", "category": "CDN / WAF", "headers": {"x-akamai-transformed": r".*"}},

    # Frameworks & Runtimes
    {"name": "FastAPI", "category": "Web Framework", "headers": {"server": r"uvicorn"}, "body": r"fastapi"},
    {"name": "Django", "category": "Web Framework", "headers": {"x-frame-options": r"SAMEORIGIN", "set-cookie": r"csrftoken="}},
    {"name": "Next.js", "category": "JavaScript Framework", "headers": {"x-powered-by": r"next\.js"}, "body": r"/_next/static/"},
    {"name": "React", "category": "JavaScript Framework", "body": r"(?:react\.production\.min\.js|__NEXT_DATA__|data-reactroot)"},
    {"name": "Vue.js", "category": "JavaScript Framework", "body": r"(?:vue\.runtime|data-v-[a-f0-9]+)"},
    {"name": "Express", "category": "Web Framework", "headers": {"x-powered-by": r"express"}},
    {"name": "Laravel", "category": "PHP Framework", "headers": {"set-cookie": r"laravel_session="}},
    {"name": "WordPress", "category": "CMS", "body": r"/wp-content/|/wp-includes/"},
]


class TechnologyDetectionEngine(ScannerEngine):
    """
    Technology Detection Engine.
    Fingerprints web servers, application frameworks, CMS, CDNs, and security controls with confidence scoring.
    """

    def engine_id(self) -> str:
        return "tech_detection"

    def name(self) -> str:
        return "Application & Technology Fingerprinting Engine"

    def description(self) -> str:
        return "Extracts web server versions, frameworks, CMS, CDN layers, and security middleware using fingerprint heuristics."

    def category(self) -> EngineCategory:
        return EngineCategory.TECHNOLOGY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SAFE_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "HOSTNAME", "URL", "IP"]

    def supported_scan_profiles(self) -> List[str]:
        return [
            "SAFE_DISCOVERY",
            "SERVICE_DISCOVERY",
            "THREAT_EXPOSURE",
            "WEB_DISCOVERY",
            "WEB_SECURITY_ASSESSMENT",
            "COMPREHENSIVE"
        ]

    def capabilities(self) -> List[str]:
        return ["server_fingerprint", "framework_detection", "cms_detection", "cdn_waf_identification", "version_extraction"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": f"Loaded {len(TECH_SIGNATURES)} active technology fingerprints"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        url = target.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"https://{url}"

        detected = []
        try:
            async with httpx.AsyncClient(timeout=4.0, verify=False, follow_redirects=True) as client:
                resp = await client.get(url)
                headers_dict = {k.lower(): v for k, v in resp.headers.items()}
                body_sample = resp.text[:50000]

                for sig in TECH_SIGNATURES:
                    matched = False
                    version = None
                    evidence = ""

                    # Check headers
                    if "headers" in sig:
                        for h_key, h_pattern in sig["headers"].items():
                            if h_key in headers_dict:
                                val = headers_dict[h_key]
                                match = re.search(h_pattern, val, re.IGNORECASE)
                                if match:
                                    matched = True
                                    evidence = f"Header '{h_key}: {val}'"
                                    if match.groups() and match.group(1):
                                        version = match.group(1)
                                    break

                    # Check body
                    if not matched and "body" in sig:
                        match = re.search(sig["body"], body_sample, re.IGNORECASE)
                        if match:
                            matched = True
                            evidence = f"Body pattern '{match.group(0)}'"

                    if matched:
                        detected.append({
                            "name": sig["name"],
                            "category": sig["category"],
                            "version": version,
                            "confidence": "HIGH",
                            "evidence": evidence
                        })

            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=round(duration, 2),
                raw_data={"target": url, "technologies": detected}
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=False,
                duration_ms=round(duration, 2),
                error_message=str(e),
                raw_data={"target": url, "technologies": []}
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
        tech_list = data.get("technologies", [])
        technologies: List[DiscoveredTechnology] = []

        for t in tech_list:
            technologies.append(DiscoveredTechnology(
                name=t["name"],
                category=t["category"],
                version=t.get("version"),
                confidence=t.get("confidence", "HIGH"),
                evidence=t.get("evidence")
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            technologies=technologies,
            raw_reference=f"Identified {len(technologies)} components in technology stack"
        )
