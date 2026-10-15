import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.modules.threat_intelligence.engines.base import (
    ScannerEngine,
    EngineCategory,
    ExecutionMode,
    RawEngineOutput,
    NormalizedEngineResult,
    NormalizedFinding
)
from app.core.database import db as memory_store
from app.infrastructure.mongodb.client import mongo_manager



class ThreatIntelligenceCorrelationEngine(ScannerEngine):
    """
    Threat Intelligence & Vulnerability Correlation Engine.
    Correlates target assets, indicators, and observed technologies with CISA KEV, STIX/TAXII threat feeds, and known threat actors.
    """

    def engine_id(self) -> str:
        return "threat_intelligence_correlation"

    def name(self) -> str:
        return "Threat Intelligence & CVE Correlation Engine"

    def description(self) -> str:
        return "Matches observed target perimeter indicators and technologies against CISA KEV, APT actor infrastructure, and STIX/TAXII feeds."

    def category(self) -> EngineCategory:
        return EngineCategory.THREAT_INTEL

    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.PASSIVE

    def supported_target_types(self) -> List[str]:
        return ["DOMAIN", "SUBDOMAIN", "IP", "URL", "HASH", "EMAIL", "CVE", "HOSTNAME", "USERNAME", "PERSON", "KEYWORD", "ORGANIZATION", "IOC"]

    def supported_scan_profiles(self) -> List[str]:
        return [
            "PASSIVE_ONLY",
            "SAFE_DISCOVERY",
            "SERVICE_DISCOVERY",
            "THREAT_EXPOSURE",
            "WEB_DISCOVERY",
            "WEB_SECURITY_ASSESSMENT",
            "COMPREHENSIVE"
        ]

    def capabilities(self) -> List[str]:
        return ["cve_correlation", "cisa_kev_lookup", "threat_actor_attribution", "malware_correlation", "stix_taxii_matching"]

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "version": self.version(),
            "details": "Threat intelligence graph & CISA KEV matching engine online"
        }

    async def execute(self, target: str, target_type: str, context: Dict[str, Any]) -> RawEngineOutput:
        start_time = time.time()
        t_clean = target.strip().lower()
        now = datetime.now(timezone.utc).isoformat()

        matched_actors: List[Dict[str, Any]] = []
        matched_malware: List[Dict[str, Any]] = []
        matched_campaigns: List[Dict[str, Any]] = []
        matched_vulnerabilities: List[Dict[str, Any]] = []
        indicators: List[Dict[str, Any]] = []

        # Indicators passed from previous pipeline stages
        prior_indicators = context.get("indicators", [])

        # Retrieve threat data from MongoDB collections or fallback to memory store
        threat_actors = []
        malware_items = []
        campaign_items = []
        vulnerabilities = []

        if mongo_manager.sync_db is not None:
            try:
                threat_actors = list(mongo_manager.sync_db["ti_threat_actors"].find({}))
                malware_items = list(mongo_manager.sync_db["ti_malware"].find({}))
                campaign_items = list(mongo_manager.sync_db["ti_campaigns"].find({}))
                vulnerabilities = list(mongo_manager.sync_db["ti_vulnerabilities"].find({}))
            except Exception:
                pass

        if not threat_actors and hasattr(memory_store, "ti_threat_actors"):
            threat_actors = list(memory_store.ti_threat_actors.values())
        if not malware_items and hasattr(memory_store, "ti_malware"):
            malware_items = list(memory_store.ti_malware.values())
        if not campaign_items and hasattr(memory_store, "ti_campaigns"):
            campaign_items = list(memory_store.ti_campaigns.values())
        if not vulnerabilities and hasattr(memory_store, "ti_vulnerabilities"):
            vulnerabilities = list(memory_store.ti_vulnerabilities.values())

        # Match against threat actors
        for actor in threat_actors:
            infra = [str(inf).lower() for inf in actor.get("infrastructure_indicators", [])]
            if t_clean in infra or any(i.get("value", "").lower() in infra for i in prior_indicators):
                matched_actors.append(actor)

        # Match against malware
        for mal in malware_items:
            if t_clean in str(mal).lower() or any(i.get("value", "").lower() in str(mal).lower() for i in prior_indicators):
                matched_malware.append(mal)

        # Match against campaigns
        for camp in campaign_items:
            if t_clean in str(camp).lower():
                matched_campaigns.append(camp)

        # Match against vulnerabilities
        for vuln in vulnerabilities:
            if t_clean in str(vuln).lower():
                matched_vulnerabilities.append(vuln)

        duration = (time.time() - start_time) * 1000
        return RawEngineOutput(
            engine_id=self.engine_id(),
            success=True,
            duration_ms=round(duration, 2),
            raw_data={
                "target": target,
                "threat_actors": matched_actors,
                "malware": matched_malware,
                "campaigns": matched_campaigns,
                "vulnerabilities": matched_vulnerabilities
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
        data = raw_output.raw_data or {}
        findings: List[NormalizedFinding] = []

        # Convert matched vulnerabilities into normalized findings
        for v in data.get("vulnerabilities", []):
            findings.append(NormalizedFinding(
                id=f"find_cve_{scan_id[:8]}_{v.get('cve_id', 'cve')}",
                scan_id=scan_id,
                tenant_id=org_id,
                engine=self.engine_id(),
                target=target,
                finding_type="KNOWN_VULNERABILITY",
                title=f"Matched Known Vulnerability: {v.get('cve_id')}",
                description=v.get("description", "Vulnerability matched against threat intelligence registry."),
                severity=v.get("severity", "HIGH"),
                confidence="HIGH",
                cve=[v.get("cve_id")] if v.get("cve_id") else [],
                remediation=v.get("mitigation", "Apply official vendor security patch immediately."),
                source="CISA KEV / NVD Threat Intelligence",
                owasp_category="A06:2021-Vulnerable and Outdated Components"
            ))

        return NormalizedEngineResult(
            engine_id=self.engine_id(),
            category=self.category(),
            execution_mode=self.execution_mode(),
            success=raw_output.success,
            duration_ms=raw_output.duration_ms,
            findings=findings,
            raw_reference=f"Correlated {len(data.get('threat_actors', []))} threat actors, {len(data.get('malware', []))} malware families, {len(findings)} CVEs"
        )
