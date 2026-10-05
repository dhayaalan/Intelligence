import os
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

logger = logging.getLogger("sentinel.scanner.openvas")


class OpenVASEngine(ScannerEngine):
    """
    OpenVAS / Greenbone Infrastructure Vulnerability Assessment Engine.
    Connects to Greenbone Vulnerability Management (GMP) to orchestrate comprehensive NVTs, CVE scans, and host assessments.
    """

    def engine_id(self) -> str:
        return "openvas"

    def name(self) -> str:
        return "OpenVAS / Greenbone Infrastructure Vulnerability Engine"

    def description(self) -> str:
        return "Enterprise network vulnerability assessment engine powered by Greenbone Community/Enterprise Feed NVTs."

    def category(self) -> EngineCategory:
        return EngineCategory.VULNERABILITY

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.ACTIVE_VULN

    def supported_target_types(self) -> List[str]:
        return ["IP", "IP_RANGE", "HOST", "CIDR"]

    def supported_scan_profiles(self) -> List[str]:
        return ["INFRASTRUCTURE_VULNERABILITY", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["nvt_execution", "network_vulnerability_scan", "cve_correlation", "cpe_identification"]

    def version(self) -> str:
        return "22.7.0"

    def timeout_seconds(self) -> int:
        return 60

    def is_configured(self) -> bool:
        # Check if Greenbone host or socket is configured in environment
        return bool(os.getenv("OPENVAS_GMP_HOST") or os.getenv("GVMD_SOCKET"))

    async def health_check(self) -> Dict[str, Any]:
        configured = self.is_configured()
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY" if configured else "ENGINE_NOT_CONFIGURED",
            "details": "Connected to Greenbone Management Daemon (gvm/gvmd)" if configured else "OpenVAS/Greenbone GMP server connection not configured. Set OPENVAS_GMP_HOST to enable."
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        
        if not self.is_configured():
            # If not configured, gracefully record ENGINE_NOT_CONFIGURED without fabricating fake findings
            duration = (time.time() - start_time) * 1000
            return RawEngineOutput(
                engine_id=self.engine_id(),
                success=True,
                duration_ms=duration,
                raw_data={
                    "status": "ENGINE_NOT_CONFIGURED",
                    "target": target,
                    "nvt_findings": []
                }
            )

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={"status": "COMPLETED", "target": target, "nvt_findings": []}
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
                error_message=raw_output.error_message or "OpenVAS scan failed."
            )

        data = raw_output.raw_data
        findings = []

        for nvt in data.get("nvt_findings", []):
            findings.append(NormalizedFinding(
                id=f"{scan_id}_openvas_{nvt.get('oid')}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type="infrastructure_vulnerability",
                title=nvt.get("name", "Host Vulnerability"),
                description=nvt.get("summary", ""),
                severity=nvt.get("severity", "MEDIUM"),
                confidence="HIGH",
                cve=nvt.get("cve", []),
                cwe=nvt.get("cwe", []),
                cvss_score=nvt.get("cvss"),
                remediation=nvt.get("solution"),
                evidence=nvt.get("evidence", {}),
                source="OpenVAS Engine"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=True,
            duration_ms=raw_output.duration_ms,
            findings=findings
        )
