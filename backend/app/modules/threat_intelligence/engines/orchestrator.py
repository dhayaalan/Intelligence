import time
import uuid
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
try:
    from app.core.database import db as store
except Exception:
    store = None

try:
    from app.infrastructure.mongodb.client import get_database as mongo_manager
except Exception:
    mongo_manager = None

try:
    from app.audit.logger import audit_logger as audit_service
except Exception:
    class DummyAudit:
        def log(self, *args, **kwargs): pass
        async def log_event(self, *args, **kwargs): pass
    audit_service = DummyAudit()

from app.modules.threat_intelligence.engines.base import (
    RawEngineOutput,
    NormalizedEngineResult,
    NormalizedFinding,
    DiscoveredService,
    DiscoveredEndpoint,
    DiscoveredTechnology
)
from app.modules.threat_intelligence.engines.registry import scanner_registry
from app.modules.threat_intelligence.engines.planner import ScanPlan, ScanPlanner
from app.modules.threat_intelligence.engines.normalizer import FindingNormalizer, RiskCalculationEngine

logger = logging.getLogger("sentinel.scanner.orchestrator")


class MultiEngineScanOrchestrator:
    """
    Multi-Engine Security Scanning Orchestrator.
    Manages parallel and sequential execution of specialized scanner engines,
    real-time progress tracking, normalized finding correlation, risk scoring,
    and persistent storage.
    """

    @classmethod
    async def execute_plan(
        cls,
        plan: ScanPlan,
        org_id: str,
        ws_id: str,
        user_name: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        scan_id = plan.scan_id
        target = plan.target
        target_type = plan.target_type
        now = datetime.now(timezone.utc).isoformat()

        # Audit scan start
        audit_service.log(
            tenant_id=org_id,
            actor_user_id=user_id or "usr_analyst",
            actor_role="SECURITY_ANALYST",
            actor_name=user_name,
            action="TI_SCAN_STARTED",
            resource_type="TI_SCAN",
            resource_id=scan_id,
            module="THREAT_INTEL",
            status="SUCCESS",
            details={
                "target": target,
                "target_type": target_type,
                "scan_profile": plan.scan_profile,
                "engines_count": len(plan.engines),
                "is_active_authorized": plan.is_active_authorized
            }
        )

        # Initialize progress structure
        stage_names = {s["stage_id"]: "PENDING" for s in plan.stages}
        engine_execution_log: Dict[str, Dict[str, Any]] = {}

        for eid in plan.engines:
            engine_execution_log[eid] = {
                "status": "QUEUED",
                "duration_ms": 0,
                "findings_count": 0,
                "error": None
            }

        scan_record = {
            "id": scan_id,
            "organization_id": org_id,
            "workspace_id": ws_id,
            "target": target,
            "target_type": target_type,
            "scan_profile": plan.scan_profile,
            "scope_id": plan.scope_id,
            "status": "RUNNING",
            "started_at": now,
            "owner": user_name,
            "is_active_authorized": plan.is_active_authorized,
            "engines_planned": plan.engines,
            "engine_execution_log": engine_execution_log,
            "progress": {
                "current_stage": "INITIALIZATION",
                "percent": 5,
                "stages": stage_names
            }
        }
        store.ti_scans[scan_id] = scan_record

        # Aggregated telemetry collectors
        all_raw_outputs: List[RawEngineOutput] = []
        all_normalized_results: List[NormalizedEngineResult] = []
        pipeline_context: Dict[str, Any] = {"target": target, "indicators": []}

        # Execute stages sequentially according to plan
        total_stages = max(1, len(plan.stages))
        for stage_idx, stage in enumerate(plan.stages):
            stage_id = stage["stage_id"]
            scan_record["progress"]["current_stage"] = stage_id.upper()
            scan_record["progress"]["stages"][stage_id] = "RUNNING"
            scan_record["progress"]["percent"] = min(90, int(((stage_idx + 1) / total_stages) * 85))

            if stage_id == "correlation_and_risk":
                scan_record["progress"]["stages"][stage_id] = "COMPLETED"
                continue

            stage_engine_ids = stage["engines"]
            stage_tasks = []

            for eid in stage_engine_ids:
                eng = scanner_registry.get(eid)
                if not eng:
                    engine_execution_log[eid]["status"] = "NOT_INSTALLED"
                    continue

                engine_execution_log[eid]["status"] = "RUNNING"
                stage_tasks.append(cls._run_single_engine(eng, target, target_type, pipeline_context, scan_id, org_id))

            if stage_tasks:
                stage_results = await asyncio.gather(*stage_tasks, return_exceptions=True)
                for res in stage_results:
                    if isinstance(res, tuple):
                        raw_out, norm_res = res
                        all_raw_outputs.append(raw_out)
                        all_normalized_results.append(norm_res)
                        eid = raw_out.engine_id
                        engine_execution_log[eid]["status"] = "COMPLETED" if raw_out.success else "FAILED"
                        engine_execution_log[eid]["duration_ms"] = raw_out.duration_ms
                        engine_execution_log[eid]["findings_count"] = len(norm_res.findings)
                        engine_execution_log[eid]["error"] = raw_out.error_message

                        # Feed indicators / subdomains into pipeline context for downstream stages
                        if norm_res.subdomains:
                            pipeline_context["subdomains"] = norm_res.subdomains
                        if norm_res.indicators:
                            pipeline_context["indicators"].extend(norm_res.indicators)

            scan_record["progress"]["stages"][stage_id] = "COMPLETED"

        # --------------------------------------------------------------------------
        # SYNTHESIS: Finding Normalization, Deduplication, Risk Scoring
        # --------------------------------------------------------------------------
        scan_record["progress"]["current_stage"] = "SYNTHESIS_AND_CORRELATION"
        scan_record["progress"]["percent"] = 92

        aggregated_findings: List[NormalizedFinding] = []
        aggregated_services: List[DiscoveredService] = []
        aggregated_endpoints: List[DiscoveredEndpoint] = []
        aggregated_technologies: List[DiscoveredTechnology] = []
        aggregated_certificates: List[Dict[str, Any]] = []
        aggregated_dns_records: List[Dict[str, Any]] = []
        aggregated_subdomains: List[str] = [target]
        aggregated_ip_hosts: List[Dict[str, Any]] = []

        for norm in all_normalized_results:
            aggregated_findings.extend(norm.findings)
            aggregated_services.extend(norm.services)
            aggregated_endpoints.extend(norm.endpoints)
            aggregated_technologies.extend(norm.technologies)
            aggregated_certificates.extend(norm.certificates)
            aggregated_dns_records.extend(norm.dns_records)
            aggregated_subdomains.extend(norm.subdomains)
            aggregated_ip_hosts.extend(norm.ip_hosts)

        # Content-addressed deduplication
        deduped_findings = FindingNormalizer.deduplicate_findings(aggregated_findings)

        # Threat intel matches
        threat_actors = []
        malware = []
        campaigns = []
        vulnerabilities = []

        for norm in all_normalized_results:
            if norm.engine_id == "threat_intelligence_correlation":
                raw_d = next((r.raw_data for r in all_raw_outputs if r.engine_id == "threat_intelligence_correlation"), {})
                if isinstance(raw_d, dict):
                    threat_actors = raw_d.get("threat_actors", [])
                    malware = raw_d.get("malware", [])
                    campaigns = raw_d.get("campaigns", [])
                    vulnerabilities = raw_d.get("vulnerabilities", [])

        # Risk scoring
        risk_overview = RiskCalculationEngine.calculate_scan_risk(
            findings=deduped_findings,
            discovered_services=aggregated_services,
            discovered_technologies=aggregated_technologies,
            threat_actors=threat_actors,
            malware=malware
        )

        completed_at = datetime.now(timezone.utc).isoformat()

        # Evidence records
        evidence_records = [
            {
                "id": f"ev_scan_{uuid.uuid4().hex[:8]}",
                "scan_id": scan_id,
                "title": f"Multi-Engine Discovery Evidence for {target}",
                "provider": "Sentinel Security Orchestrator",
                "source": "Aggregated Multi-Engine Pipeline",
                "confidence": "HIGH",
                "retrieved_at": completed_at,
                "observed_at": completed_at,
                "raw_reference": f"{len(plan.engines)} engines executed across {len(plan.stages)} pipeline stages",
                "sha256": hashlib.sha256(f"{scan_id}_{target}".encode()).hexdigest()
            }
        ]

        # Historical Comparison against previous scans of same target
        prior_scans = [
            s for s in store.ti_scans.values()
            if s.get("organization_id") == org_id and s.get("target") == target and s.get("id") != scan_id and s.get("status") == "COMPLETED"
        ]

        changes = {
            "new_findings": len(deduped_findings),
            "resolved_findings": 0,
            "changed_findings": 0,
            "new_services": len(aggregated_services),
            "new_endpoints": len(aggregated_endpoints),
            "has_prior_scan": len(prior_scans) > 0,
            "prior_scan_id": prior_scans[0]["id"] if prior_scans else None
        }

        # Build final completed scan document
        scan_record["status"] = "COMPLETED"
        scan_record["completed_at"] = completed_at
        scan_record["threat_score"] = risk_overview["threat_score"]
        scan_record["overall_severity"] = risk_overview["overall_severity"]
        scan_record["threat_overview"] = risk_overview
        scan_record["findings"] = [f.dict() for f in deduped_findings]
        scan_record["findings_count"] = len(deduped_findings)
        scan_record["indicators"] = [
            {"id": f"ioc_{uuid.uuid4().hex[:8]}", "type": "TARGET", "value": target, "canonical_value": target, "severity": risk_overview["overall_severity"], "confidence": "HIGH"}
        ]
        scan_record["indicators_count"] = 1
        scan_record["threat_actors"] = threat_actors
        scan_record["malware"] = malware
        scan_record["campaigns"] = campaigns
        scan_record["vulnerabilities"] = vulnerabilities
        scan_record["infrastructure"] = {
            "dns": {"records": aggregated_dns_records, "records_count": len(aggregated_dns_records)},
            "certificates": aggregated_certificates,
            "subdomains": list(set(aggregated_subdomains)),
            "ip_hosts": aggregated_ip_hosts,
            "technologies": [t.dict() for t in aggregated_technologies],
            "services": [s.dict() for s in aggregated_services],
            "endpoints": [e.dict() for e in aggregated_endpoints]
        }
        scan_record["sources"] = [
            {"provider": "Sentinel Multi-Engine Security Scanner", "status": "COMPLETED", "confidence": "HIGH", "last_sync": completed_at}
        ]
        scan_record["evidence"] = evidence_records
        scan_record["changes"] = changes
        scan_record["raw_engine_outputs"] = [
            {"engine_id": r.engine_id, "success": r.success, "duration_ms": r.duration_ms, "error": r.error_message} for r in all_raw_outputs
        ]
        scan_record["progress"] = {
            "current_stage": "REPORT_READY",
            "percent": 100,
            "stages": {s["stage_id"]: "COMPLETED" for s in plan.stages}
        }

        # Persist to memory store
        store.ti_scans[scan_id] = scan_record

        # Persist to MongoDB
        if mongo_manager.is_connected and mongo_manager.sync_db is not None:
            try:
                clean_doc = {k: v for k, v in scan_record.items() if k != "_id"}
                mongo_manager.sync_db.threat_intelligence_scans.update_one(
                    {"id": scan_id}, {"$set": clean_doc}, upsert=True
                )
            except Exception as e:
                logger.warning(f"Error persisting scan {scan_id} to MongoDB: {e}")

        # Persist / update asset record
        ast_id = f"ast_{uuid.uuid4().hex[:8]}"
        asset_doc = {
            "id": ast_id,
            "tenant_id": org_id,
            "name": f"{target} Monitored Perimeter",
            "type": target_type,
            "value": target,
            "criticality": "HIGH",
            "threat_severity": risk_overview["overall_severity"],
            "overall_risk": risk_overview["overall_severity"],
            "owner": user_name,
            "environment": "PRODUCTION",
            "business_unit": "Perimeter Intelligence",
            "tags": ["multi-engine-scanned", plan.scan_profile.lower()],
            "ip_addresses": [h.get("ip") for h in aggregated_ip_hosts if h.get("ip")],
            "open_ports": [s.port for s in aggregated_services],
            "technologies": [t.name for t in aggregated_technologies],
            "certificates": aggregated_certificates,
            "last_scan_id": scan_id,
            "created_at": now,
            "updated_at": completed_at
        }
        store.ti_assets[ast_id] = asset_doc

        # Audit scan completion
        audit_service.log(
            tenant_id=org_id,
            actor_user_id=user_id or "usr_analyst",
            actor_role="SECURITY_ANALYST",
            actor_name=user_name,
            action="TI_SCAN_COMPLETED",
            resource_type="TI_SCAN",
            resource_id=scan_id,
            module="THREAT_INTEL",
            status="SUCCESS",
            details={
                "target": target,
                "threat_score": risk_overview["threat_score"],
                "overall_severity": risk_overview["overall_severity"],
                "findings_count": len(deduped_findings),
                "engines_executed": len(plan.engines)
            }
        )

        return scan_record

    @classmethod
    async def _run_single_engine(
        cls,
        engine,
        target: str,
        target_type: str,
        context: Dict[str, Any],
        scan_id: str,
        org_id: str
    ) -> Tuple[RawEngineOutput, NormalizedEngineResult]:
        try:
            raw_out = await asyncio.wait_for(
                engine.execute(target, target_type, context),
                timeout=float(engine.timeout_seconds())
            )
        except asyncio.TimeoutError:
            raw_out = RawEngineOutput(
                engine_id=engine.engine_id(),
                success=False,
                duration_ms=float(engine.timeout_seconds() * 1000),
                error_message=f"Engine '{engine.name()}' timed out after {engine.timeout_seconds()}s"
            )
        except Exception as e:
            raw_out = RawEngineOutput(
                engine_id=engine.engine_id(),
                success=False,
                duration_ms=0,
                error_message=str(e)
            )

        norm_res = engine.normalize(raw_out, target, target_type, scan_id, org_id)
        return raw_out, norm_res
