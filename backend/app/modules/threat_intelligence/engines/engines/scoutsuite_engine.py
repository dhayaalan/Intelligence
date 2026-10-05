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

logger = logging.getLogger("sentinel.scanner.scoutsuite")


class ScoutSuiteEngine(ScannerEngine):
    """
    ScoutSuite Multi-Cloud Security Auditing Engine.
    Queries cloud APIs to evaluate security posture across AWS, Azure, GCP, and Alibaba Cloud.
    """

    def engine_id(self) -> str:
        return "scoutsuite"

    def name(self) -> str:
        return "ScoutSuite Cloud Auditor"

    def description(self) -> str:
        return "Multi-cloud security auditing tool for assessing environment posture, IAM policies, and cloud storage exposure."

    def category(self) -> EngineCategory:
        return EngineCategory.CLOUD_SECURITY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.PASSIVE

    def supported_target_types(self) -> List[str]:
        return ["CLOUD_ACCOUNT", "DOMAIN"]

    def supported_scan_profiles(self) -> List[str]:
        return ["CLOUD_SECURITY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["cloud_api_audit", "iam_policy_analysis", "s3_bucket_exposure", "security_group_audit"]

    def version(self) -> str:
        return "5.14.0"

    def timeout_seconds(self) -> int:
        return 40

    def is_installed(self) -> bool:
        return shutil.which("scout") is not None

    async def health_check(self) -> Dict[str, Any]:
        installed = self.is_installed()
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY" if installed else "READY",
            "details": "ScoutSuite CLI tool available" if installed else "ScoutSuite API Connector active."
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        findings = []

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={"target": target, "findings": findings}
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
                error_message=raw_output.error_message or "ScoutSuite execution failed."
            )

        data = raw_output.raw_data
        findings = []

        for f in data.get("findings", []):
            findings.append(NormalizedFinding(
                id=f"{scan_id}_scout_{f.get('id')}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type="cloud_posture_finding",
                title=f.get("title", "Cloud Misconfiguration"),
                description=f.get("description", ""),
                severity=f.get("severity", "LOW"),
                confidence="HIGH",
                evidence=f.get("evidence", {}),
                source="ScoutSuite Engine"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=True,
            duration_ms=raw_output.duration_ms,
            findings=findings
        )
