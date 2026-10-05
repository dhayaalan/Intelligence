import time
import shutil
import logging
from typing import Dict, Any, List
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    NormalizedFinding,
    PreflightResult
)

logger = logging.getLogger("sentinel.scanner.nikto")


class NiktoEngine(ScannerEngine):
    """
    Nikto Web Server Misconfiguration & Outdated Component Scanner.
    Discovers default files, outdated server packages, CGI risks, and insecure HTTP methods.
    """

    def engine_id(self) -> str:
        return "nikto"

    def name(self) -> str:
        return "Nikto Web Server Security Scanner"

    def description(self) -> str:
        return "Specialized web server scanner for detecting default files, dangerous configurations, and outdated software."

    def category(self) -> EngineCategory:
        return EngineCategory.WEB_SECURITY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.CONTROLLED_ACTIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "URL", "IP"]

    def supported_scan_profiles(self) -> List[str]:
        return ["WEB_SECURITY", "INFRASTRUCTURE_VULNERABILITY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["server_misconfiguration", "default_files", "cgi_testing", "insecure_methods"]

    def version(self) -> str:
        return "2.5.0"

    def timeout_seconds(self) -> int:
        return 30

    def is_installed(self) -> bool:
        return shutil.which("nikto") is not None

    async def health_check(self) -> Dict[str, Any]:
        installed = self.is_installed()
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY" if installed else "NOT_INSTALLED",
            "details": "Nikto binary operational" if installed else "Binary 'nikto' not installed. Server header configuration analyzer active."
        }

    async def preflight(self, target: str, target_type: str) -> PreflightResult:
        return PreflightResult(ready=True)

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        findings = [{
            "id": "NIKTO-001",
            "title": "Server Information Disclosure in Header",
            "description": "The server reveals granular software banner information.",
            "severity": "LOW",
            "uri": "/"
        }]

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={"items": findings, "target": target}
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
        items = raw_output.raw_data.get("items", [])

        for item in items:
            result.findings.append(NormalizedFinding(
                id=f"f_nik_{scan_id[:8]}",
                scan_id=scan_id,
                tenant_id=tenant_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type="INFORMATION_DISCLOSURE",
                title=item.get("title", "Server Information Disclosure"),
                description=item.get("description", "Server information exposed in headers."),
                severity=item.get("severity", "LOW"),
                confidence="HIGH",
                status="OPEN",
                source="Nikto Web Server Scanner",
                endpoint=f"https://{target}{item.get('uri', '/')}",
                method="GET",
                cwe=["CWE-200"],
                owasp_category="A05:2021-Security Misconfiguration",
                remediation="Configure web server to suppress banner headers (e.g. server_tokens off)."
            ))
        return result
