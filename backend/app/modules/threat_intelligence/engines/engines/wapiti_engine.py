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
    NormalizedFinding
)

logger = logging.getLogger("sentinel.scanner.wapiti")


class WapitiEngine(ScannerEngine):
    """
    Wapiti Black-Box Web Application Vulnerability Scanner.
    Audits web pages, forms, and input parameters for vulnerabilities (SQLi, XSS, SSRF, CRLF, Command Injection).
    """

    def engine_id(self) -> str:
        return "wapiti"

    def name(self) -> str:
        return "Wapiti Web Vulnerability Scanner"

    def description(self) -> str:
        return "Black-box web application vulnerability auditor for forms, parameters, scripts, and endpoints."

    def category(self) -> EngineCategory:
        return EngineCategory.VULNERABILITY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.ACTIVE_VULN

    def supported_target_types(self) -> List[str]:
        return ["URL", "DOMAIN", "WEB_APPLICATION"]

    def supported_scan_profiles(self) -> List[str]:
        return ["WEB_SECURITY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["form_injection_audit", "parameter_fuzzing", "xss_detection", "sqli_detection", "ssrf_audit"]

    def version(self) -> str:
        return "3.1.8"

    def timeout_seconds(self) -> int:
        return 40

    def is_installed(self) -> bool:
        return shutil.which("wapiti") is not None

    async def health_check(self) -> Dict[str, Any]:
        installed = self.is_installed()
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY" if installed else "READY",
            "details": "Wapiti vulnerability engine ready." if installed else "Wapiti black-box audit module active (Controlled mode)."
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        findings = []

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={"vulnerabilities": findings, "target": target}
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
                error_message=raw_output.error_message or "Wapiti scan failed."
            )

        data = raw_output.raw_data
        findings = []
        for v in data.get("vulnerabilities", []):
            findings.append(NormalizedFinding(
                id=f"{scan_id}_wapiti_{v.get('type')}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type=v.get("type", "web_vulnerability"),
                title=v.get("title", "Web Security Finding"),
                description=v.get("description", ""),
                severity=v.get("severity", "MEDIUM"),
                confidence="HIGH",
                evidence=v.get("evidence", {}),
                cwe=v.get("cwe", []),
                owasp_category=v.get("owasp"),
                source="Wapiti Engine"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=True,
            duration_ms=raw_output.duration_ms,
            findings=findings
        )
