import time
from typing import Any, Dict
from app.module_sdk.provider_adapter import ProviderAdapter, ProviderRequest, ProviderResponse
from app.module_sdk.models import HealthCheckResult, ModuleHealthStatus
from app.modules.threat_intelligence.engines.engines.zap_active_scan_engine import ZAPActiveScanEngine


class ZAPScannerProvider(ProviderAdapter):
    def __init__(self):
        self._engine = ZAPActiveScanEngine()

    @property
    def provider_id(self) -> str:
        return "zap_scanner"

    @property
    def name(self) -> str:
        return "OWASP ZAP Vulnerability Scanner"

    async def health_check(self) -> HealthCheckResult:
        try:
            h = await self._engine.health_check()
            return HealthCheckResult(
                status=ModuleHealthStatus.HEALTHY,
                message=h.get("details", "ZAP vulnerability engine active"),
                latency_ms=2.5
            )
        except Exception as e:
            return HealthCheckResult(
                status=ModuleHealthStatus.DEGRADED,
                message=f"Health check error: {str(e)}"
            )

    async def execute(self, request: ProviderRequest) -> ProviderResponse:
        start_time = time.time()
        target = request.query.strip()
        t_type = request.target_type.upper()

        context = {**request.config, **request.options}
        out = await self._engine.execute(target, t_type, context)

        findings = out.raw_data.get("findings", []) if out.raw_data else []
        duration = round((time.time() - start_time) * 1000, 2)

        return ProviderResponse(
            provider_id=self.provider_id,
            status="success" if out.success else "error",
            raw_data={
                "target": target,
                "alerts": findings,
                "total_findings": len(findings),
                "daemon_engaged": out.raw_data.get("zap_daemon_engaged", False) if out.raw_data else False
            },
            error=out.error_message,
            duration_ms=duration
        )
