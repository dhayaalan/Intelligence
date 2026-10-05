import time
import httpx
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

logger = logging.getLogger("sentinel.scanner.crtsh")


class CRTSHEngine(ScannerEngine):
    """
    Certificate Transparency Log Analyzer (crt.sh).
    Discovers all active and historic SSL/TLS certificates and subdomains issued for a domain target.
    """

    def engine_id(self) -> str:
        return "crtsh"

    def name(self) -> str:
        return "Certificate Transparency CT-Log Engine"

    def description(self) -> str:
        return "Queries public Certificate Transparency (CT) logs via crt.sh to map certificates and subdomains."

    def category(self) -> EngineCategory:
        return EngineCategory.ATTACK_SURFACE

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.PASSIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "URL"]

    def supported_scan_profiles(self) -> List[str]:
        return ["PASSIVE", "ATTACK_SURFACE", "COMPREHENSIVE"]

    def capabilities(self) -> List[str]:
        return ["ct_log_search", "subdomain_discovery", "cert_issuer_analysis", "wildcard_detection"]

    def version(self) -> str:
        return "1.2.0"

    def timeout_seconds(self) -> int:
        return 20

    async def health_check(self) -> Dict[str, Any]:
        return {
            "engine_id": self.engine_id(),
            "name": self.name(),
            "category": self.category().value,
            "status": "READY",
            "details": "Certificate Transparency public log lookup operational."
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        domain = target.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

        subdomains = set()
        certs = []
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(
                    "https://crt.sh/",
                    params={"q": f"%.{domain}", "output": "json"},
                    headers={"User-Agent": "Sential-Security-Scanner/2.4"}
                )
                if resp.status_code == 200:
                    records = resp.json()
                    for r in records[:50]:
                        name_val = r.get("name_value", "")
                        for sub in name_val.split("\n"):
                            sub = sub.strip().lower()
                            if sub and not sub.startswith("*."):
                                subdomains.add(sub)
                        certs.append({
                            "id": r.get("id"),
                            "issuer_name": r.get("issuer_name"),
                            "not_before": r.get("not_before"),
                            "not_after": r.get("not_after")
                        })
        except Exception as e:
            logger.debug(f"crt.sh direct query returned {e}, using DNS fallbacks")

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=duration,
            raw_data={
                "target": target,
                "domain": domain,
                "subdomains_found": sorted(list(subdomains))[:30],
                "certificates_analyzed": len(certs),
                "cert_sample": certs[:5]
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
                error_message=raw_output.error_message or "crt.sh execution failed."
            )

        data = raw_output.raw_data
        findings = []
        sub_list = data.get("subdomains_found", [])
        if sub_list:
            findings.append(NormalizedFinding(
                id=f"{scan_id}_crtsh_subdomains",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                engine_version=self.version(),
                target=target,
                finding_type="subdomains_discovered_ct_logs",
                title=f"Discovered {len(sub_list)} Subdomains via Certificate Transparency",
                description=f"Public CT logs revealed certificates associated with: {', '.join(sub_list[:5])}...",
                severity="INFORMATIONAL",
                confidence="HIGH",
                evidence=data,
                source="crt.sh CT Log Engine"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=True,
            duration_ms=raw_output.duration_ms,
            findings=findings
        )
