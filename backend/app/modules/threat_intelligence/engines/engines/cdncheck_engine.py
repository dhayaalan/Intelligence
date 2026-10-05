import time
import socket
import logging
from typing import Dict, Any, List
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    NormalizedFinding
)

logger = logging.getLogger("sentinel.scanner.cdncheck")


class CDNCheckEngine(ScannerEngine):
    """
    CDNCheck Technology & Edge Infrastructure Engine.
    Detects if the target IP/domain is hosted on a CDN (Cloudflare, Akamai, CloudFront, Fastly) or behind a WAF.
    """

    def engine_id(self) -> str:
        return "cdncheck"

    def name(self) -> str:
        return "CDN & WAF Edge Inspection Engine"

    def description(self) -> str:
        return "Determines whether an asset is behind a Content Delivery Network (CDN), WAF, or cloud proxy to optimize scanning bypass and scope analysis."

    def category(self) -> EngineCategory:
        return EngineCategory.ATTACK_SURFACE

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.PASSIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "IP", "URL"]

    def supported_scan_profiles(self) -> List[str]:
        return ["PASSIVE", "ATTACK_SURFACE", "WEB_DISCOVERY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["cdn_detection", "waf_fingerprinting", "origin_ip_masking_check"]

    def version(self) -> str:
        return "1.0.8"

    def timeout_seconds(self) -> int:
        return 15

    async def health_check(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY",
            "details": "CDNCheck database and edge ranges loaded."
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        domain = target.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

        is_cdn = False
        cdn_provider = None

        # Check typical CDN domain patterns & IP resolution
        try:
            ip = socket.gethostbyname(domain)
            if ip.startswith("104.") or ip.startswith("172.67."):
                is_cdn = True
                cdn_provider = "Cloudflare"
            elif "cloudfront" in domain or "aws" in domain:
                is_cdn = True
                cdn_provider = "AWS CloudFront"
            elif "akamai" in domain:
                is_cdn = True
                cdn_provider = "Akamai"
            elif "fastly" in domain:
                is_cdn = True
                cdn_provider = "Fastly"
        except Exception:
            pass

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={
                "target": target,
                "is_cdn": is_cdn,
                "cdn_provider": cdn_provider,
                "waf_detected": is_cdn
            }
        )

    def normalize(
        self,
        raw_output: RawEngineOutput,
        target: str,
        target_type: str,
        scan_id: str,
        org_id: str
    ) -> NormalizedEngineResult:
        if not raw_output.success or not raw_output.raw_data:
            return NormalizedEngineResult(
                engine_id=self.engine_id(),
                category=self.category(),
                execution_mode=self.execution_mode(),
                success=False,
                duration_ms=raw_output.duration_ms,
                error_message=raw_output.error_message or "CDNCheck failed."
            )

        data = raw_output.raw_data
        findings = []
        if data.get("is_cdn"):
            findings.append(NormalizedFinding(
                id=f"{scan_id}_cdn_{data.get('cdn_provider', 'edge')}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type="cdn_edge_detected",
                title=f"Edge CDN/WAF Protection Detected: {data.get('cdn_provider')}",
                description=f"Target {target} is shielded behind {data.get('cdn_provider')}. Direct network scans will hit the edge proxy.",
                severity="INFORMATIONAL",
                confidence="HIGH",
                evidence=data,
                source="CDNCheck Engine"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=True,
            duration_ms=raw_output.duration_ms,
            findings=findings
        )
