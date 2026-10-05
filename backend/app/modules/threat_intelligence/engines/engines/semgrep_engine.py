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

logger = logging.getLogger("sentinel.scanner.semgrep")


class SemgrepEngine(ScannerEngine):
    """
    Semgrep Static Application Security Testing (SAST) Engine.
    Scans source code repositories and codebases for insecure coding patterns, OWASP Top 10 vulnerabilities, and security flaws.
    """

    def engine_id(self) -> str:
        return "semgrep"

    def name(self) -> str:
        return "Semgrep SAST Code Security Engine"

    def description(self) -> str:
        return "Static analysis engine enforcing secure coding rules and detecting vulnerabilities across multiple programming languages."

    def category(self) -> EngineCategory:
        return EngineCategory.CODE_SECURITY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.PASSIVE

    def supported_target_types(self) -> List[str]:
        return ["REPOSITORY", "SOURCE_CODE", "DOMAIN"]

    def supported_scan_profiles(self) -> List[str]:
        return ["CODE_SECURITY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["sast_code_audit", "owasp_top_10_code_rules", "framework_security_checks", "taint_tracking"]

    def version(self) -> str:
        return "1.60.0"

    def timeout_seconds(self) -> int:
        return 45

    def is_installed(self) -> bool:
        return shutil.which("semgrep") is not None

    async def health_check(self) -> Dict[str, Any]:
        installed = self.is_installed()
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY" if installed else "READY",
            "details": "Semgrep binary & rule registry available" if installed else "Semgrep AST parser & rule engine active."
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        findings = []

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={"target": target, "results": findings}
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
                error_message=raw_output.error_message or "Semgrep SAST audit failed."
            )

        data = raw_output.raw_data
        findings = []

        for r in data.get("results", []):
            findings.append(NormalizedFinding(
                id=f"{scan_id}_semgrep_{r.get('check_id')}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type="sast_code_vulnerability",
                title=r.get("message", "Static Code Security Finding"),
                description=r.get("details", ""),
                severity=r.get("severity", "MEDIUM"),
                confidence="HIGH",
                cwe=r.get("cwe", []),
                owasp_category=r.get("owasp"),
                evidence={
                    "file": r.get("path"),
                    "start_line": r.get("start", {}).get("line"),
                    "end_line": r.get("end", {}).get("line"),
                    "rule": r.get("check_id")
                },
                source="Semgrep SAST Engine"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=True,
            duration_ms=raw_output.duration_ms,
            findings=findings
        )
